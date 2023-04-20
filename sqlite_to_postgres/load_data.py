"""Loading data from sqlite3 to postgres db."""
import logging
from contextlib import closing
from os import environ
from sqlite3 import Connection as SQLiteConnection
from sqlite3 import Error as SQLiteError
from sqlite3 import connect as sqlite_connect

import fire
from psycopg2 import Error as PGError
from psycopg2 import connect as pg_connect
from psycopg2.extensions import connection as pg_connection
from psycopg2.extras import DictCursor

from sqlite_to_postgres.extractors import DBExtractor
from sqlite_to_postgres.savers import PostgresSaver
from sqlite_to_postgres.utils import get_mapping

PACK_SIZE = 1000
PG_NAME_MAPPING = {"genre_film_work": "film_work_genre"}
PG_SCHEMA = "content"

SQLITE_NAME_MAPPING = {"created": "created_at", "modified": "updated_at"}
SQLITE_SCHEMA = ""

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def load_from_sqlite(
    connection: SQLiteConnection,
    pg_conn: pg_connection,
    sqlite_name_mapping,
    sqlite_schema,
    postgres_name_mapping,
    postgres_schema,
    pack_size: int,
    do_if_empty: bool,
):
    """Основной метод загрузки данных из SQLite в Postgres"""

    postgres_mapping = get_mapping(postgres_name_mapping, postgres_schema)
    postgres_saver = PostgresSaver(pg_conn, postgres_mapping)

    sqlite_mapping = get_mapping(sqlite_name_mapping, sqlite_schema)
    sqlite_extractor = DBExtractor(connection, pack_size, sqlite_mapping)

    try:
        cur = pg_conn.cursor()
        try:
            cur.execute("SELECT count(*) FROM content.film_work")
            count = int(cur.fetchone()[0])  # type: ignore
            if count and do_if_empty:
                logging.error("DB is not empty. Aborting...")
                return

        except Exception:
            ...

        for data in sqlite_extractor.extract_movies():
            postgres_saver.save_all_data(data)
        logging.debug("Data extracted")

        logging.info("Data extracted successfully!")

    except SQLiteError as e:
        logging.error("SQLite: " + str(e))
    except PGError as e:
        logging.error("Postgres: " + str(e))
    return


def main(do_if_empty=False):
    dsl = {
        "dbname": environ.get("POSTGRES_DB"),
        "user": environ.get("POSTGRES_USER"),
        "password": environ.get("POSTGRES_PASSWORD"),
        "host": environ.get("POSTGRES_HOST"),
        "port": environ.get("POSTGRES_PORT"),
    }

    logging.debug("Beginning the extraction process...")
    logging.debug("Trying to establsh connection with db...")

    try:
        with closing(sqlite_connect("db.sqlite")) as sqlite_conn, closing(
            pg_connect(**dsl, cursor_factory=DictCursor)
        ) as pg_conn:
            logging.debug("Connected")
            load_from_sqlite(
                sqlite_conn,
                pg_conn,
                SQLITE_NAME_MAPPING,
                SQLITE_SCHEMA,
                PG_NAME_MAPPING,
                PG_SCHEMA,
                PACK_SIZE,
                do_if_empty,
            )
    except SQLiteError as sq_e:
        logging.error("SQLite: " + str(sq_e))

    except PGError as ps_e:
        logging.error("Postgres: " + str(ps_e))

    logging.debug("Connection closed")


if __name__ == "__main__":
    fire.Fire(main)
