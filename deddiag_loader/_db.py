from contextlib import contextmanager
from typing import Union

import pandas as pd
import sqlalchemy.pool as pool


class Connection(object):
    """Connection Manager"""
    def __init__(self, host: str = "localhost",
                 port: Union[int, str] = 5432,
                 db_name: str = "postgres",
                 user: str = "postgres",
                 password: str = ""):
        """
        Database connection object

        Connection object is to be used as a contextmanager:

        Examples
        --------
        >>> con = Connection()
        >>> with con as c:


        :param host: Hostname
        :param port: Port
        :param db_name: Database Name
        :param user: Username
        :param password: Password
        """
        self._password = password
        self._host = host
        self._port = port
        self._user = user
        self._db_name = db_name
        self.__connection_pool = pool.QueuePool(self._get_conn, pool_size=5)

    def _get_conn(self):
        import psycopg2
        c = psycopg2.connect(host=self._host,
                             port=self._port,
                             dbname=self._db_name,
                             user=self._user,
                             password=self._password)
        return c

    def from_psql(self, query: str):
        with self.connection() as con:
            return pd.read_sql_query(query, con)

    @contextmanager
    def connection(self):
        con = self.__connection_pool.connect()
        try:
            yield con
        finally:
            con.close()
