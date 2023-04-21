from contextlib import closing
from os import environ
from sqlite3 import Connection as SQLiteConnection
from sqlite3 import connect as sqlite_connect

import pytest
from psycopg2 import connect as pg_connect
from psycopg2.extensions import connection as pg_connection
from psycopg2.extras import DictCursor

from sqlite_to_postgres.extractors import DBExtractor
from sqlite_to_postgres.utils import get_mapping


@pytest.fixture(scope="session")
def sqlite_conn():
    with closing(sqlite_connect("db.sqlite")) as conn:
        yield conn


@pytest.fixture(scope="session")
def pg_conn():
    dsl = {
        "dbname": environ.get("POSTGRES_DB"),
        "user": environ.get("POSTGRES_USER"),
        "password": environ.get("POSTGRES_PASSWORD"),
        "host": environ.get("POSTGRES_HOST"),
        "port": environ.get("POSTGRES_PORT"),
    }
    with closing(pg_connect(**dsl, cursor_factory=DictCursor)) as pg_conn:
        yield pg_conn


@pytest.fixture()
def pack_size():
    return 1000


@pytest.fixture()
def sqlite_mapping():
    return get_mapping({"created": "created_at", "modified": "updated_at"}, "")


@pytest.fixture()
def pg_mapping():
    return get_mapping({"genre_film_work": "film_work_genre"}, "content")


@pytest.fixture()
def tables():
    return ("person", "genre", "film_work", "genre_film_work", "person_film_work")


def test_rows_number(
    sqlite_conn: SQLiteConnection, pg_conn: pg_connection, tables: tuple[str, ...]
):
    with closing(sqlite_conn.cursor()) as sqlite_cursor, closing(
        pg_conn.cursor()
    ) as pg_cursor:

        for table_name in tables:
            sqlite_cursor.execute(f"select count(*) from {table_name};")
            sqlite_rows = int(sqlite_cursor.fetchone()[0])

            if table_name == "genre_film_work":
                table_name = "film_work_genre"
            pg_cursor.execute(f"select count(*) from content.{table_name};")
            pg_rows = int(pg_cursor.fetchone()[0])  # type: ignore
            assert sqlite_rows
            assert pg_rows
            assert sqlite_rows == pg_rows


def test_contents(
    sqlite_conn: SQLiteConnection,
    pg_conn: pg_connection,
    sqlite_mapping,
    pg_mapping,
    pack_size: int,
):
    sqlite_extractor = DBExtractor(
        sqlite_conn, pack_size, sqlite_mapping
    ).extract_movies()
    pg_extractor = DBExtractor(pg_conn, pack_size, pg_mapping).extract_movies()

    sqlite_data = None
    pg_data = None

    while True:
        try:
            sqlite_data = next(sqlite_extractor)
            pg_data = next(pg_extractor)
            assert sqlite_data == pg_data

        except StopIteration:
            assert sqlite_data == pg_data
            break
