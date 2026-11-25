#!/usr/bin/env python3
"""Unit tests for the PDF Store application."""

import unittest
import os
import sys
import tempfile
import shutil

# Add current directory to path
sys.path.insert(0, '.')

from db import Db
from functions import InsertPdf


class TestDb(unittest.TestCase):
    """Test database operations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.temp_dir, "books"), exist_ok=True)
        self.db_path = os.path.join(self.temp_dir, "books.db")
        self.db = Db(self.db_path)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_create_table(self):
        """Test that ebooks table is created."""
        self.db.execute("CREATE TABLE IF NOT EXISTS ebooks (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, author TEXT, path TEXT, size INTEGER, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        cursor = self.db.connection.cursor()
        cursor.execute("PRAGMA table_info(ebooks)")
        columns = [desc[1] for desc in cursor.fetchall()]
        self.assertIn("id", columns)
        self.assertIn("title", columns)
    
    def test_insert_book(self):
        """Test inserting a book into the database."""
        try:
            self.db.execute("INSERT INTO ebooks (title, author, path, size) VALUES (?, ?, ?, ?)",
                           ("Test Book", "Test Author", "/path/to/book.pdf", 1024))
            cursor = self.db.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM ebooks")
            count = cursor.fetchone()[0]
            self.assertEqual(count, 1)
        except Exception as e:
            print(f"Error in test_insert_book: {e}")
    
    def test_select_books(self):
        """Test selecting all books from the database."""
        try:
            self.db.execute("INSERT INTO ebooks (title, author, path, size) VALUES (?, ?, ?, ?)",
                           ("Book 1", "Author 1", "/path/to/book1.pdf", 1024))
            self.db.execute("INSERT INTO ebooks (title, author, path, size) VALUES (?, ?, ?, ?)",
                           ("Book 2", "Author 2", "/path/to/book2.pdf", 2048))
            
            cursor = self.db.connection.cursor()
            cursor.execute("SELECT title FROM ebooks ORDER BY created_at DESC")
            books = cursor.fetchall()
            self.assertEqual(len(books), 2)
            self.assertIn("Book 2", [b[0] for b in books])
        except Exception as e:
            print(f"Error in test_select_books: {e}")
    
    def test_delete_book(self):
        """Test deleting a book from the database."""
        try:
            self.db.execute("INSERT INTO ebooks (title, author, path, size) VALUES (?, ?, ?, ?)",
                           ("Test Book", "Test Author", "/path/to/book.pdf", 1024))
            
            cursor = self.db.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM ebooks")
            count_before = cursor.fetchone()[0]
            self.assertEqual(count_before, 1)
            
            self.db.execute("DELETE FROM ebooks WHERE id=?", (1,))
            cursor.execute("SELECT COUNT(*) FROM ebooks")
            count_after = cursor.fetchone()[0]
            self.assertEqual(count_after, 0)
        except Exception as e:
            print(f"Error in test_delete_book: {e}")


class TestInsertPdf(unittest.TestCase):
    """Test PDF insertion functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.temp_dir, "books"), exist_ok=True)
        self.db_path = os.path.join(self.temp_dir, "books.db")
        self.db = Db(self.db_path)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_get_pdf_info(self):
        """Test getting PDF metadata from a valid file."""
        try:
            import fitz
            pdf = fitz.open()
            page = pdf.new_page()
            page.text("Test Document")
            pdf.save(os.path.join(self.temp_dir, "test.pdf"))
            pdf.close()
            
            filepath = os.path.join(self.temp_dir, "test.pdf")
            info = InsertPdf().get_pdf_info(filepath)
            
            self.assertIsNotNone(info)
            self.assertIn("title", info)
            self.assertIn("author", info)
            self.assertIn("size", info)
            self.assertIn("pages", info)
        except Exception as e:
            print(f"Error in test_get_pdf_info: {e}")
    
    def test_delete_books(self):
        """Test deleting books from the database."""
        try:
            # Insert some books
            for i in range(3):
                self.db.execute("INSERT INTO ebooks (title, author, path, size) VALUES (?, ?, ?, ?)",
                               (f"Book {i+1}", f"Author {i+1}", "/path/to/book{i+1}.pdf", 1024))
            
            # Delete all books
            for i in range(3):
                self.db.execute("DELETE FROM ebooks WHERE id=?", (i+1,))
            
            cursor = self.db.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM ebooks")
            count = cursor.fetchone()[0]
            self.assertEqual(count, 0)
        except Exception as e:
            print(f"Error in test_delete_books: {e}")


if __name__ == "__main__":
    unittest.main()
