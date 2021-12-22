#!/usr/bin/env python3
__author__ = "Angus Robinson"
__copyright__ = "Copyright 2020, Sargus Networks"
__credits__ = ["All those that provided answers on the internet"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Angus Robinson"
__email__ = "angus@fairhaven.za.net"
__status__ = "Beta"

import os
import sys
import config
from loguru import logger
import snoop
from db import Db

db = Db()


class InsertPdf:
    @logger.catch
    @snoop
    def __init__(self):
        self.filepath = config.file_path
        self.book = []
        self.files = []
        self.files = os.listdir(self.filepath)
        self.insertbooks()
        self.createtable()
        self.selectbooks()
        self.log = Logger()

    @logger.catch
    @snoop
    def insertbooks(self):
        for self.book in self.files:
            statements = "INSERT INTO ebooks (books) VALUES ('{}')" .format(
                self.book)
            db.execute(statements)

    @logger.catch
    @snoop
    def createtable(self):
        statements = "CREATE TABLE  IF NOT EXISTS ebooks (books TEXT)"
        db.execute(statements)

    @logger.catch
    @snoop
    def selectbooks(self):
        statements = """SELECT * from ebooks"""
        books = db.retreive(statements)
        return books
