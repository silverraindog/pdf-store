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
    def __init__(self, database='books.db'):
        self.database = database
        self.connection = None
        self.cursor = None
        self.connect()
    
    @snoop
    def connect(self):
        """Connect to the SQLite3 database."""
        self.connection = sqlite3.connect(self.database)
        self.cursor = self.connection.cursor()
        self.create_tables()
    
    @snoop
    def close(self):
        """Close the SQLite database."""
        if self.connection:
            self.connection.commit()
            self.connection.close()
            self.connection = None
            self.cursor = None
    
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
    
    @snoop
    def execute(self, statements, params=None):
        """Execute a SQL statement."""
        try:
            if params is not None:
                self.cursor.execute(statements, params)
            else:
                self.cursor.execute(statements)
        except sqlite3.Error as error:
            logger.error(f"Failed to execute statement: {error}")
            raise
    
    @snoop
    def insert(self, statements, sql):
        """Insert data into the database."""
        self.cursor.execute(statements, sql)
    
    @snoop
    def retrieve(self, statements):
        """Retrieve data from the database."""
        self.cursor.execute(statements)
        records = self.cursor.fetchall()
        return records
    
    @snoop
    def backup_db(self, backup_path):
        """Backup the database to specified location."""
        import shutil
        try:
            shutil.copy2(self.database, backup_path)
            logger.info(f"Database backed up to {backup_path}")
        except Exception as e:
            logger.error(f"Failed to backup database: {e}")
    
    @snoop
    def restore_db(self, restore_path):
        """Restore the database from specified location."""
        import sqlite3
        
        try:
            # Read the backup file
            with open(restore_path, 'rb') as f:
                backup_data = f.read()
            
            # Create a new connection and execute the backup
            self.connection = sqlite3.connect(self.database)
            self.cursor = self.connection.cursor()
            
            # Execute the backup data
            self.cursor.executescript(backup_data.decode('utf-8'))
            
            logger.info(f"Database restored from {restore_path}")
        except Exception as e:
            logger.error(f"Failed to restore database: {e}")
            raise
    
    @snoop
    def verify_integrity(self):
        """Verify database integrity."""
        try:
            self.cursor.execute("PRAGMA integrity_check")
            result = self.cursor.fetchone()[0]
            if result == "ok":
                logger.info("Database integrity check passed")
                return True
            else:
                logger.warning(f"Database integrity check failed: {result}")
                return False
        except Exception as e:
            logger.error(f"Failed to verify database integrity: {e}")
            return False
