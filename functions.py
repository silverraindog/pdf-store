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
import fitz


class InsertPdf:
    """Class for inserting PDF files into the library."""
    
    def __init__(self):
        self.filepath = config.file_path
        self.book = None
        self.files = []
        self.insert_books()
        self.create_table()
        self.select_books()
    
    @logger.catch
    @snoop
    def insert_books(self):
        """Insert all PDF books into the database."""
        if not os.path.exists(self.filepath):
            logger.warning(f"Directory {self.filepath} does not exist")
            return
        
        self.files = os.listdir(self.filepath)
        
        for book in self.files:
            if book.endswith('.pdf'):
                statements = "INSERT INTO ebooks (title, author, path, size) VALUES (?, ?, ?, ?)"
                info = self.get_pdf_info(book)
                if info:
                    db.execute(statements, (info['title'], info['author'], info['path'], info['size']))
    
    @logger.catch
    @snoop
    def create_table(self):
        """Create ebooks table if it doesn't exist."""
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
    def select_books(self):
        """Retrieve all books from the database."""
        statements = "SELECT title, author, path, size FROM ebooks ORDER BY created_at DESC"
        books = db.retrieve(statements)
        return books
    
    @logger.catch
    @snoop
    def get_pdf_info(self, filepath):
        """Get PDF metadata from file using PyMuPDF."""
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


class PdfPreview:
    """Class for displaying PDF preview."""
    
    @staticmethod
    def show_preview(filepath):
        """Show a preview of the PDF file."""
        try:
            pdf = fitz.open(filepath)
            if len(pdf) > 0:
                page = pdf[0]
                # For now, just show info about the PDF
                logger.info(f"Previewing {filepath}")
                print(f"Title: {page.title}")
                print(f"Author: {page.author}")
                print(f"Pages: {len(pdf)}")
            else:
                print("No pages found in PDF")
        except Exception as e:
            logger.error(f"Error showing preview: {e}")
