#!/usr/bin/env python3
__author__ = "Angus Robinson"
__copyright__ = "Copyright 2020, Sargus Networks"
__credits__ = ["All those that provided answers on the internet"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Angus Robinson"
__email__ = "angus@fairhaven.za.net"
__status__ = "Beta"
from loguru import logger
import snoop
import sqlite3


class Db(object):
    @logger.catch
    @snoop
    def __init__(self, database='books.db'):
     self.database = database
     self.connect()

    @logger.catch
    @snoop
    def connect(self):
        """Connect to the SQLite3 database."""
        self.connection = sqlite3.connect(self.database)
        self.cursor = self.connection.cursor()

    @logger.catch
    @snoop
    def close(self):
        """Close the SQLite3 database."""
        self.connection.commit()
        self.connection.close()

    @logger.catch
    @snoop
    def execute(self, statements):
        try:
         self.cursor.execute(statements)
         print("Python Variables inserted successfully into ebooks table")
        except sqlite3.Error as error:
            print("Failed to insert Python variable into sqlite table", error)
       # finally:
       #     if self.connection:
       #         self.connection.close()
       #         print("The SQLite connection is closed")

    @logger.catch
    @snoop
    def insert(self, statements, sql):
        Logger()
        self.cursor.execute(statements, sql)

    @logger.catch
    @snoop
    def retreive(self, statements):
        self.cursor.execute(statements)
        records = self.cursor.fetchall()
        return records
