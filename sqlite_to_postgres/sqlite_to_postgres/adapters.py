from logging import ERROR, log
from sqlite3 import Connection as SQLiteConnection
from sqlite3 import Cursor as SQLiteCursor

from psycopg2.extensions import connection as pg_connection
from psycopg2.extensions import cursor as pg_cursor

from .exceptions import ConnectionFailedError


class ConnectionAdapter:
    def __init__(self, connection: SQLiteConnection | pg_connection):
        self.connection = connection

    def cursor(self) -> pg_cursor | SQLiteCursor:
        if type(self.connection) is pg_connection:
            return self.connection.cursor()

        if type(self.connection) is SQLiteConnection:
            return self.connection.cursor()

        conn_type_str = str(type(self.connection))
        log(ERROR, "Failed to create cursor: " f"connection type is {conn_type_str}")
        raise ConnectionFailedError

    def commit(self):
        self.connection.commit()

    def get_connection(self) -> SQLiteConnection | pg_connection:
        return self.connection
