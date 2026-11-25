#!/usr/bin/env python3
__author__ = "Angus Robinson"
__copyright__ = "Copyright 2020, Sargus Networks"
__credits__ = ["All those that provided answers on the internet"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Angus Robinson"
__email__ = "angus@fairhaven.za.net"
__status__ = "Beta"

import sqlite3
from loguru import logger
import snoop


class Db(object):
    @logger.catch
    @snoop
    def __init__(self, database='books.db'):
        self.database = database
        self.connection = None
        self.cursor = None
        self.connect()

    @logger.catch
    @snoop
    def connect(self):
        """Connect to the SQLite3 database."""
        self.connection = sqlite3.connect(self.database)
        self.cursor = self.connection.cursor()
        # Create tables if they don't exist
        self.create_tables()

    @logger.catch
    @snoop
    def close(self):
        """Close the SQLite database."""
        if self.connection:
            self.connection.commit()
            self.connection.close()
            self.connection = None
            self.cursor = None

    @logger.catch
    @snoop
    def create_tables(self):
        """Create ebooks table if it doesn't exist."""
        statements = """CREATE TABLE IF NOT EXISTS ebooks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT,
            path TEXT,
            size INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )"""
        self.cursor.execute(statements)

    @logger.catch
    @snoop
    def execute(self, statements):
        """Execute a SQL statement."""
        try:
            self.cursor.execute(statements)
        except sqlite3.Error as error:
            logger.error(f"Failed to execute statement: {error}")
            raise

    @logger.catch
    @snoop
    def insert(self, statements, sql):
        """Insert data into the database."""
        self.cursor.execute(statements, sql)

    @logger.catch
    @snoop
    def retrieve(self, statements):
        """Retrieve data from the database."""
        self.cursor.execute(statements)
        records = self.cursor.fetchall()
        return records
