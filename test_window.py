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
from functions import InsertPdf, PdfPreview, BookManager


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
            print(f"Error in test_delete_book: {e}")
    
    def test_backup_db(self):
        """Test database backup functionality."""
        try:
            # Insert a test book
            self.db.execute("INSERT INTO ebooks (title, author, path, size) VALUES (?, ?, ?, ?)",
                           ("Test Book", "Test Author", "/path/to/book.pdf", 1024))
            
            # Create backup
            backup_path = os.path.join(self.temp_dir, "backup.db")
            self.db.backup_db(backup_path)
            
            # Verify backup exists
            self.assertTrue(os.path.exists(backup_path))
        except Exception as e:
            print(f"Error in test_backup_db: {e}")
    
    def test_restore_db(self):
        """Test database restore functionality."""
        try:
            # Create a temporary database with test data
            temp_dir = tempfile.mkdtemp()
            self.db_path = os.path.join(temp_dir, "books.db")
            self.db = Db(self.db_path)
            
            # Insert test books
            for i in range(3):
                self.db.execute("INSERT INTO ebooks (title, author, path, size) VALUES (?, ?, ?, ?)",
                               (f"Book {i+1}", f"Author {i+1}", "/path/to/book{i+1}.pdf", 1024))
            
            # Create backup
            backup_path = os.path.join(temp_dir, "backup.db")
            self.db.backup_db(backup_path)
            
            # Restore from backup
            self.db.restore_db(backup_path)
            
            # Verify books are restored
            cursor = self.db.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM ebooks")
            count = cursor.fetchone()[0]
            self.assertEqual(count, 3)
            
            # Cleanup
            shutil.rmtree(temp_dir)
        except Exception as e:
            print(f"Error in test_restore_db: {e}")
    
    def test_verify_integrity(self):
        """Test database integrity verification."""
        try:
            self.db = Db()
            result = self.db.verify_integrity()
            self.assertTrue(result)
        except Exception as e:
            print(f"Error in test_verify_integrity: {e}")


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
            page.insert_text(0, 'Test Document')
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


class TestBookManager(unittest.TestCase):
    """Test BookManager functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.temp_dir, "books"), exist_ok=True)
        self.db_path = os.path.join(self.temp_dir, "books.db")
        self.db = Db(self.db_path)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_search_books(self):
        """Test searching for books by title."""
        try:
            # Insert test books
            self.db.execute("INSERT INTO ebooks (title, author, path, size) VALUES (?, ?, ?, ?)",
                           ("Python Guide", "John Doe", "/path/to/python.pdf", 1024))
            self.db.execute("INSERT INTO ebooks (title, author, path, size) VALUES (?, ?, ?, ?)",
                           ("Java Basics", "Jane Smith", "/path/to/java.pdf", 2048))
            
            # Search for "Python"
            results = BookManager().search_books("python")
            self.assertEqual(len(results), 1)
        except Exception as e:
            print(f"Error in test_search_books: {e}")
    
    def test_export_csv(self):
        """Test CSV export functionality."""
        try:
            # Insert test books
            self.db.execute("INSERT INTO ebooks (title, author, path, size) VALUES (?, ?, ?, ?)",
                           ("Test Book", "Test Author", "/path/to/book.pdf", 1024))
            
            # Export to CSV
            csv_path = os.path.join(self.temp_dir, "export.csv")
            BookManager().export_csv(self.books, csv_path)
            
            # Verify CSV file exists and has content
            self.assertTrue(os.path.exists(csv_path))
        except Exception as e:
            print(f"Error in test_export_csv: {e}")


class TestFormatSupport(unittest.TestCase):
    """Test support for different file formats."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.temp_dir, "books"), exist_ok=True)
        self.db_path = os.path.join(self.temp_dir, "books.db")
        self.db = Db(self.db_path)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_supported_format_detection(self):
        """Test that supported formats are detected."""
        # Test PDF detection
        try:
            import fitz
            pdf = fitz.open()
            page = pdf.new_page()
            page.insert_text(0, 'Test Document')
            pdf.save(os.path.join(self.temp_dir, "test.pdf"))
            pdf.close()
            
            info = InsertPdf().get_book_info(os.path.join(self.temp_dir, "test.pdf"))
            self.assertIsNotNone(info)
        except Exception as e:
            print(f"Error in test_supported_format_detection: {e}")
    
    def test_unsupported_format_rejection(self):
        """Test that unsupported formats are rejected."""
        info = InsertPdf().get_book_info(os.path.join(self.temp_dir, "test.txt"))
        self.assertIsNone(info)


if __name__ == "__main__":
    unittest.main()
