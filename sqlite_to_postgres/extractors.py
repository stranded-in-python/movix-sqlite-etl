from logging import DEBUG, ERROR, log
from sqlite3 import Connection as SQLiteConnection
from sqlite3 import Cursor as SQLiteCursor
from sqlite3 import Error as SQLiteError
from typing import Iterator, Sequence

from psycopg2 import Error as PGError
from psycopg2.extensions import connection as pg_connection
from psycopg2.extensions import cursor as pg_cursor

from . import dataclasses as items
from .adapters import ConnectionAdapter
from .exceptions import DataInconsistentError, InputError
from .utils import SQLBuilderDataclassMixin, is_data_empty


class Extractor(SQLBuilderDataclassMixin):
    def _init_cursor(self):
        sql = f"""SELECT {self.table_fields} from {self.full_table_name}
                order by {self.table_name}.id;"""
        self.cursor.execute(sql)

    def __init__(
        self,
        connection: ConnectionAdapter,
        table: str,
        item: type[items.Item],
        mapping: dict[str, str],
        schema: str,
        pack_size: int = 1000,
    ):
        self.connection: ConnectionAdapter = connection
        self.pack_size: int = pack_size if pack_size > 0 else 0
        self.table = table
        self.schema = schema
        self.item = item
        self.name_mapping = mapping

        self.cursor: SQLiteCursor | pg_cursor = self.connection.cursor()

        try:
            self._init_cursor()
        except SQLiteError as e:
            log(ERROR, str(e))
            raise DataInconsistentError

        except PGError as e:
            log(ERROR, str(e))
            raise DataInconsistentError

    def extract(self) -> Sequence[items.Item]:
        if self.pack_size < 1:
            msg = (
                "Number of rows in pack should be positive, but it is "
                f"{self.pack_size}"
            )
            raise InputError(msg)

        entries = self.cursor.fetchmany(self.pack_size)
        count = len(entries) if entries else 0
        log(DEBUG, f"extracted {count} entries from {self.table}")
        return [self.item(*entry) for entry in entries]

    def close(self):
        self.cursor.close()


class DBExtractor:
    """Universal interface for extraction"""

    def __init__(
        self,
        conn: SQLiteConnection | pg_connection,
        pack_size: int,
        mapping: dict[str, tuple[type[items.Item], dict[str, str], str]],
    ):
        conn_adapter = ConnectionAdapter(conn)
        self._extractors = {
            table: Extractor(conn_adapter, table, *params, pack_size=pack_size)
            for table, params in mapping.items()
        }

    def extract_movies(self) -> Iterator[items.MoviesData]:
        while True:
            dictionary_data = items.MoviesData(
                self._extractors["person"].extract(),
                self._extractors["genre"].extract(),
                self._extractors["film_work"].extract(),
                [],
                [],
            )
            if is_data_empty(dictionary_data):
                break
            yield dictionary_data

        while True:
            foreign_keys = items.MoviesData(
                [],
                [],
                [],
                self._extractors["person_film_work"].extract(),
                self._extractors["genre_film_work"].extract(),
            )
            if is_data_empty(foreign_keys):
                break
            yield foreign_keys

        for extractor in self._extractors.values():
            extractor.close()
