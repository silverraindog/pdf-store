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
        for book in self.files:
            statements = "INSERT INTO ebooks (title, author, path, size) VALUES (?, ?, ?, ?)"
            info = self.get_pdf_info(book)
            if info:
                db.execute(statements, (info['title'], info['author'], info['path'], info['size']))

    @logger.catch
    @snoop
    def createtable(self):
        statements = """CREATE TABLE IF NOT EXISTS ebooks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT,
            path TEXT,
            size INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )"""
        db.execute(statements)

    @logger.catch
    @snoop
    def selectbooks(self):
        statements = "SELECT title, author, path, size FROM ebooks ORDER BY created_at DESC"
        books = db.retrieve(statements)
        return books

    @logger.catch
    @snoop
    def get_pdf_info(self, filepath):
        """Get PDF metadata from file."""
        import fitz
        try:
            pdf = fitz.open(filepath)
            info = {
                'title': pdf[0].title,
                'author': pdf[0].author,
                'size': os.path.getsize(filepath),
                'pages': len(pdf)
            }
            pdf.close()
            return info
        except Exception as e:
            logger.error(f"Error reading PDF: {e}")
            return None
