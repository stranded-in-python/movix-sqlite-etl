import logging
from contextlib import closing
from dataclasses import astuple
from typing import Sequence, cast

from psycopg2.extensions import connection as ps_connection
from psycopg2.extensions import cursor as ps_cursor

from . import dataclasses as items
from .adapters import ConnectionAdapter
from .exceptions import DataInconsistentError
from .utils import SQLBuilderDataclassMixin, is_data_empty


class Saver(SQLBuilderDataclassMixin):
    def __init__(
        self,
        conn: ConnectionAdapter,
        table: str,
        item: type[items.Item],
        mapping: dict[str, str],
        schema: str,
    ):
        self.connection = conn
        self.cursor = conn.cursor()
        self.table = table
        self.item = item
        self.name_mapping = mapping
        self.schema = schema
        if not self.table or not self.item:
            raise DataInconsistentError

    def prepare_args(self, items: Sequence[items.Item]):
        if issubclass(type(self.cursor), ps_cursor):
            cursor = cast(ps_cursor, self.cursor)
            return ", ".join(
                cursor.mogrify(f"({self.placeholders})", astuple(item)).decode()
                for item in items
            )
        raise NotImplementedError

    def save(self, items: Sequence[items.Item]):
        if not items:
            return

        args = self.prepare_args(items)

        with closing(self.connection.cursor()) as cur:
            cur.execute(
                f"""
                insert into {self.full_table_name} ({self.fields})
                    values {args}
                    """.format()
            )
            self.connection.commit()

    def truncate(self):
        with closing(self.connection.cursor()) as cur:
            logging.debug(f"Trying to truncate {self.full_table_name}")
            cur.execute(
                f"""truncate  table {self.full_table_name}
                            cascade;"""
            )
            self.connection.commit()


class PostgresSaver:
    """Universal interface for saving"""

    def __init__(
        self,
        pg_conn: ps_connection,
        mapping: dict[str, tuple[type[items.Item], dict[str, str], str]],
    ):
        self.connection = pg_conn
        conn = ConnectionAdapter(pg_conn)
        self._tables_truncated = False
        self._savers = {
            table: Saver(conn, table, *params) for table, params in mapping.items()
        }
        self._dictionaries_comitted = False

    def _truncate_tables(self):
        for saver in self._savers.values():
            saver.truncate()
        self._commit()
        self._tables_truncated = True

    def _commit(self):
        self.connection.commit()
        logging.debug("Changes are comitted successfully")

    def commit_dicts(self):
        if not self._dictionaries_comitted:
            self._commit()
            self._dictionaries_comitted = True
            logging.debug("Dictionaries are comitted, going to " "transfer relations")

    def save_all_data(self, data: items.MoviesData):

        if is_data_empty(data):
            return

        if not self._tables_truncated:
            self._truncate_tables()

        if data.persons:
            self._savers["person"].save(data.persons)

        if data.genres:
            self._savers["genre"].save(data.genres)

        if data.film_works:
            self._savers["film_work"].save(data.film_works)

        if data.person_film_works:
            self.commit_dicts()
            self._savers["person_film_work"].save(data.person_film_works)

        if data.genre_film_works:
            self.commit_dicts()
            self._savers["genre_film_work"].save(data.genre_film_works)
