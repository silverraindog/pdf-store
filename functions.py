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
import json
import xml.etree.ElementTree as ET
import csv
import shutil
import hashlib
import base64
import sqlite3
from datetime import datetime


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
                logger.info(f"Previewing {filepath}")
                print(f"Title: {page.title}")
                print(f"Author: {page.author}")
                print(f"Pages: {len(pdf)}")
            else:
                print("No pages found in PDF")
        except Exception as e:
            logger.error(f"Error showing preview: {e}")


class BatchProcessor:
    """Class for batch operations on PDF files."""
    
    @staticmethod
    def delete_all_books():
        """Delete all books from the database."""
        db.execute("DELETE FROM ebooks")
        return True
    
    @staticmethod
    def clear_database():
        """Clear the entire database."""
        db.execute("DELETE FROM ebooks")
        return True


class AdvancedSearch:
    """Class for advanced search functionality."""
    
    @staticmethod
    def search_by_author(author):
        """Search for books by author."""
        statements = "SELECT title, author, path, size FROM ebooks WHERE author = ?"
        results = db.retrieve(statements, (author,))
        return results
    
    @staticmethod
    def search_by_size(min_size, max_size=None):
        """Search for books within a size range."""
        statements = "SELECT title, author, path, size FROM ebooks WHERE size >= ?"
        if max_size:
            statements += " AND size <= ?"
            statements += ", " + str(max_size)
        results = db.retrieve(statements, (min_size, max_size))
        return results
    
    @staticmethod
    def search_by_pages(min_pages, max_pages=None):
        """Search for books within a page count range."""
        statements = "SELECT title, author, path, size FROM ebooks WHERE pages >= ?"
        if max_pages:
            statements += " AND pages <= ?"
            statements += ", " + str(max_pages)
        results = db.retrieve(statements, (min_pages, max_pages))
        return results


class Statistics:
    """Class for generating statistics."""
    
    @staticmethod
    def get_total_books():
        """Get total number of books."""
        cursor = db.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM ebooks")
        return cursor.fetchone()[0]
    
    @staticmethod
    def get_total_size():
        """Get total size of all books in KB."""
        cursor = db.connection.cursor()
        cursor.execute("SELECT SUM(size) FROM ebooks")
        total_bytes = cursor.fetchone()[0]
        return total_bytes / 1024 if total_bytes else 0
    
    @staticmethod
    def get_average_size():
        """Get average size of all books in KB."""
        total_size = Statistics.get_total_size()
        total_books = Statistics.get_total_books()
        return total_size / total_books if total_books > 0 else 0
    
    @staticmethod
    def get_book_count_by_author():
        """Get book count by author."""
        cursor = db.connection.cursor()
        cursor.execute("""
            SELECT author, COUNT(*) as count FROM ebooks 
            GROUP BY author ORDER BY count DESC
        """)
        return cursor.fetchall()
    
    @staticmethod
    def get_size_distribution():
        """Get size distribution of books."""
        cursor = db.connection.cursor()
        cursor.execute("""
            SELECT size FROM ebooks
            ORDER BY size
        """)
        sizes = [row[0] for row in cursor.fetchall()]
        return sizes
    
    @staticmethod
    def get_page_distribution():
        """Get page count distribution of books."""
        cursor = db.connection.cursor()
        cursor.execute("""
            SELECT pages FROM ebooks
            ORDER BY pages
        """)
        pages = [row[0] for row in cursor.fetchall()]
        return pages
    
    @staticmethod
    def get_recent_books(limit=10):
        """Get most recently added books."""
        statements = "SELECT title, author, path, size, created_at FROM ebooks ORDER BY created_at DESC LIMIT ?"
        results = db.retrieve(statements, (limit,))
        return results
    
    @staticmethod
    def get_book_details(book_id):
        """Get detailed information about a specific book."""
        statements = "SELECT title, author, path, size, pages FROM ebooks WHERE id = ?"
        results = db.retrieve(statements, (book_id,))
        return results if results else None


class FileValidator:
    """Class for validating PDF files."""
    
    @staticmethod
    def is_valid_pdf(filepath):
        """Check if file is a valid PDF."""
        try:
            pdf = fitz.open(filepath)
            pdf.close()
            return True
        except Exception as e:
            logger.error(f"Invalid PDF file: {e}")
            return False
    
    @staticmethod
    def get_file_size(filepath):
        """Get file size in bytes."""
        try:
            return os.path.getsize(filepath)
        except Exception as e:
            logger.error(f"Cannot get file size: {e}")
            return None


class Logger:
    """Custom logger for the application."""
    
    def __init__(self):
        self.logger = logger
    
    @logger.catch
    @snoop
    def log_info(self, message):
        """Log information message."""
        self.logger.info(message)
    
    @logger.catch
    @snoop
    def log_error(self, message):
        """Log error message."""
        self.logger.error(message)


class ConfigManager:
    """Class for managing application configuration."""
    
    @staticmethod
    def get_file_path():
        """Get the configured file path."""
        return config.file_path
    
    @staticmethod
    def get_database_path():
        """Get the database path."""
        return config.database
    
    @staticmethod
    def set_file_path(filepath):
        """Set the file path configuration."""
        config.file_path = filepath
    
    @staticmethod
    def set_database_path(database):
        """Set the database path configuration."""
        config.database = database
    
    @staticmethod
    def validate_config():
        """Validate configuration settings."""
        if not config.file_path:
            return False, "File path is not configured"
        if not os.path.exists(config.file_path):
            return False, f"Directory {config.file_path} does not exist"
        return True, "Configuration is valid"


class DatabaseManager:
    """Class for managing database operations."""
    
    @staticmethod
    def connect():
        """Connect to the database."""
        db = Db(config.database)
        return db
    
    @staticmethod
    def close(db):
        """Close the database connection."""
        if db:
            db.close()
    
    @staticmethod
    def create_tables(db):
        """Create necessary tables in the database."""
        db.create_table()
    
    @staticmethod
    def execute_query(db, query):
        """Execute a SQL query."""
        try:
            db.execute(query)
            return True
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return False
    
    @staticmethod
    def get_connection():
        """Get database connection."""
        return Db(config.database)


class ExportManager:
    """Class for exporting data to various formats."""
    
    @staticmethod
    def export_to_csv(files):
        """Export books to CSV format."""
        if not files:
            return False
        
        filepath = fd.asksaveasfilename(
            title="Export CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not filepath:
            return False
        
        try:
            with open(filepath, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["ID", "Title", "Author", "Path", "Size (KB)", "Pages"])
                
                for book in files:
                    size_kb = round(book['size'] / 1024, 2)
                    writer.writerow([
                        book['id'],
                        book['title'],
                        book['author'],
                        book['path'],
                        size_kb,
                        book['pages']
                    ])
            
            return True
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return False
    
    @staticmethod
    def export_to_json(files):
        """Export books to JSON format."""
        if not files:
            return False
        
        import json
        
        data = [
            {
                "id": book['id'],
                "title": book['title'],
                "author": book['author'],
                "path": book['path'],
                "size_kb": round(book['size'] / 1024, 2),
                "pages": book['pages']
            }
            for book in files
        ]
        
        filepath = fd.asksaveasfilename(
            title="Export JSON",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not filepath:
            return False
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        return True
    
    @staticmethod
    def export_to_xml(files):
        """Export books to XML format."""
        if not files:
            return False
        
        import xml.etree.ElementTree as ET
        
        root = ET.Element("Books")
        
        for book in files:
            book_elem = ET.SubElement(root, "Book")
            ET.SubElement(book_elem, "ID").text = str(book['id'])
            ET.SubElement(book_elem, "Title").text = book['title']
            ET.SubElement(book_elem, "Author").text = book['author']
            ET.SubElement(book_elem, "Path").text = book['path']
            ET.SubElement(book_elem, "SizeKB").text = str(round(book['size'] / 1024, 2))
            ET.SubElement(book_elem, "Pages").text = str(book['pages'])
        
        filepath = fd.asksaveasfilename(
            title="Export XML",
            defaultextension=".xml",
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
        )
        
        if not filepath:
            return False
        
        ET.indent(root)
        with open(filepath, 'w') as f:
            ET.dump(root, f)
        
        return True


class UtilityFunctions:
    """Utility functions for the application."""
    
    @staticmethod
    def format_size(size_bytes):
        """Format file size in human-readable format."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.2f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.2f} MB"
    
    @staticmethod
    def format_date(timestamp):
        """Format timestamp as human-readable date."""
        from datetime import datetime
        if timestamp:
            return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
        return "N/A"


class ApplicationUtils:
    """Utility class for application-wide operations."""
    
    @staticmethod
    def get_all_books():
        """Get all books from the database."""
        statements = "SELECT title, author, path, size, pages FROM ebooks ORDER BY created_at DESC"
        return db.retrieve(statements)
    
    @staticmethod
    def get_book_by_id(book_id):
        """Get a specific book by ID."""
        statements = "SELECT title, author, path, size, pages FROM ebooks WHERE id = ?"
        results = db.retrieve(statements, (book_id,))
        return results[0] if results else None
    
    @staticmethod
    def get_books_by_title_pattern(pattern):
        """Get books matching a title pattern."""
        statements = "SELECT title, author, path, size, pages FROM ebooks WHERE title LIKE ?"
        results = db.retrieve(statements, (f"%{pattern}%",))
        return results
    
    @staticmethod
    def get_books_by_author_pattern(author_pattern):
        """Get books matching an author pattern."""
        statements = "SELECT title, author, path, size, pages FROM ebooks WHERE author LIKE ?"
        results = db.retrieve(statements, (f"%{author_pattern}%",))
        return results
    
    @staticmethod
    def get_books_by_size_range(min_size, max_size):
        """Get books within a size range."""
        statements = "SELECT title, author, path, size, pages FROM ebooks WHERE size >= ? AND size <= ?"
        results = db.retrieve(statements, (min_size, max_size))
        return results
    
    @staticmethod
    def get_books_by_page_range(min_pages, max_pages):
        """Get books within a page count range."""
        statements = "SELECT title, author, path, size, pages FROM ebooks WHERE pages >= ? AND pages <= ?"
        results = db.retrieve(statements, (min_pages, max_pages))
        return results
    
    @staticmethod
    def get_books_by_date_range(start_date, end_date):
        """Get books added within a date range."""
        statements = "SELECT title, author, path, size, pages FROM ebooks WHERE created_at >= ? AND created_at <= ?"
        results = db.retrieve(statements, (start_date, end_date))
        return results
    
    @staticmethod
    def get_books_by_multiple_criteria(criteria):
        """Get books matching multiple criteria."""
        conditions = []
        values = []
        
        if 'title' in criteria:
            conditions.append("title LIKE ?")
            values.append(f"%{criteria['title']}%")
        
        if 'author' in criteria:
            conditions.append("author LIKE ?")
            values.append(f"%{criteria['author']}%")
        
        if 'min_size' in criteria:
            conditions.append("size >= ?")
            values.append(criteria['min_size'])
        
        if 'max_size' in criteria:
            conditions.append("size <= ?")
            values.append(criteria['max_size'])
        
        if 'min_pages' in criteria:
            conditions.append("pages >= ?")
            values.append(criteria['min_pages'])
        
        if 'max_pages' in criteria:
            conditions.append("pages <= ?")
            values.append(criteria['max_pages'])
        
        if conditions:
            statements = "SELECT title, author, path, size, pages FROM ebooks WHERE " + " AND ".join(conditions)
            results = db.retrieve(statements, values)
            return results
        else:
            return db.get_all_books()
    
    @staticmethod
    def clear_all_data():
        """Clear all data from the database."""
        db.execute("DELETE FROM ebooks")
        return True
    
    @staticmethod
    def backup_database():
        """Create a backup of the database."""
        import shutil
        
        backup_path = f"{config.database}.backup"
        shutil.copy2(config.database, backup_path)
        logger.info(f"Database backed up to {backup_path}")
        return True
    
    @staticmethod
    def restore_database(backup_path):
        """Restore database from backup."""
        if os.path.exists(backup_path):
            db.execute("DELETE FROM ebooks")
            shutil.copy2(backup_path, config.database)
            logger.info(f"Database restored from {backup_path}")
            return True
        else:
            logger.error(f"Backup file not found: {backup_path}")
            return False


class SecurityManager:
    """Class for security-related operations."""
    
    @staticmethod
    def validate_file_path(filepath):
        """Validate that a file path is safe."""
        if not os.path.exists(filepath):
            return False, "File does not exist"
        
        # Check if it's a PDF file
        if not filepath.lower().endswith('.pdf'):
            return False, "Not a PDF file"
        
        # Check for potential path traversal attacks
        if '..' in filepath:
            return False, "Invalid path (path traversal detected)"
        
        return True, "Valid file path"
    
    @staticmethod
    def sanitize_input(input_string):
        """Sanitize user input to prevent injection attacks."""
        # Remove potentially dangerous characters
        safe_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_. ')
        return ''.join(char for char in input_string if char in safe_chars)
    
    @staticmethod
    def escape_sql_query(query):
        """Escape SQL query to prevent injection attacks."""
        # Simple escaping - in production, use parameterized queries
        return query.replace("'", "''")


class NotificationManager:
    """Class for displaying notifications."""
    
    @staticmethod
    def show_info(message):
        """Show information message."""
        from tkinter.messagebox import showinfo
        showinfo("Info", message)
    
    @staticmethod
    def show_error(message):
        """Show error message."""
        from tkinter.messagebox import showerror
        showerror("Error", message)
    
    @staticmethod
    def show_warning(message):
        """Show warning message."""
        from tkinter.messagebox import showwarning
        showwarning("Warning", message)
    
    @staticmethod
    def show_question(message, default_answer="Yes"):
        """Show question with yes/no answer."""
        from tkinter.messagebox import askyesno
        return askyesno("Question", message)


class HistoryManager:
    """Class for managing operation history."""
    
    def __init__(self):
        self.history = []
    
    @staticmethod
    def add_operation(operation, details):
        """Add an operation to the history."""
        entry = {
            'operation': operation,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        HistoryManager.history.append(entry)
    
    @staticmethod
    def get_history(limit=10):
        """Get recent operations."""
        return HistoryManager.history[-limit:]
    
    @staticmethod
    def clear_history():
        """Clear operation history."""
        HistoryManager.history.clear()


class FileOperations:
    """Class for file system operations."""
    
    @staticmethod
    def list_files(directory):
        """List all files in a directory."""
        if not os.path.exists(directory):
            return []
        
        files = []
        for item in os.listdir(directory):
            filepath = os.path.join(directory, item)
            if os.path.isfile(filepath):
                files.append(filepath)
        return files
    
    @staticmethod
    def get_file_size(filepath):
        """Get file size in bytes."""
        try:
            return os.path.getsize(filepath)
        except Exception as e:
            logger.error(f"Cannot get file size: {e}")
            return None
    
    @staticmethod
    def check_file_permissions(filepath):
        """Check file permissions."""
        if not os.path.exists(filepath):
            return False, "File does not exist"
        
        try:
            stat_info = os.stat(filepath)
            return True, f"Permissions: {stat_info.st_mode}"
        except Exception as e:
            logger.error(f"Cannot check permissions: {e}")
            return False, str(e)
    
    @staticmethod
    def move_file(source, destination):
        """Move a file to a new location."""
        if not os.path.exists(source):
            return False, "Source file does not exist"
        
        try:
            os.rename(source, destination)
            return True, "File moved successfully"
        except Exception as e:
            logger.error(f"Cannot move file: {e}")
            return False, str(e)
    
    @staticmethod
    def copy_file(source, destination):
        """Copy a file to a new location."""
        if not os.path.exists(source):
            return False, "Source file does not exist"
        
        try:
            shutil.copy2(source, destination)
            return True, "File copied successfully"
        except Exception as e:
            logger.error(f"Cannot copy file: {e}")
            return False, str(e)
    
    @staticmethod
    def delete_file(filepath):
        """Delete a file."""
        if not os.path.exists(filepath):
            return False, "File does not exist"
        
        try:
            os.remove(filepath)
            return True, "File deleted successfully"
        except Exception as e:
            logger.error(f"Cannot delete file: {e}")
            return False, str(e)
    
    @staticmethod
    def create_directory(directory):
        """Create a directory."""
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
                return True, "Directory created successfully"
            except Exception as e:
                logger.error(f"Cannot create directory: {e}")
                return False, str(e)
    
    @staticmethod
    def remove_directory(directory):
        """Remove a directory."""
        if not os.path.exists(directory):
            return False, "Directory does not exist"
        
        try:
            shutil.rmtree(directory)
            return True, "Directory removed successfully"
        except Exception as e:
            logger.error(f"Cannot remove directory: {e}")
            return False, str(e)


class DataIntegrity:
    """Class for maintaining data integrity."""
    
    @staticmethod
    def verify_database():
        """Verify database integrity."""
        cursor = db.connection.cursor()
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ebooks'")
        tables = cursor.fetchall()
        
        if not tables:
            return False, "ebooks table does not exist"
        
        # Check for foreign key constraints
        cursor.execute("PRAGMA foreign_key_list(ebooks)")
        foreign_keys = cursor.fetchall()
        
        if foreign_keys:
            logger.info(f"Found {len(foreign_keys)} foreign key constraints")
        
        return True, "Database integrity verified"
    
    @staticmethod
    def check_table_size():
        """Check table size."""
        cursor = db.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM ebooks")
        count = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(size) FROM ebooks")
        total_size = cursor.fetchone()[0]
        
        return {
            'count': count,
            'total_size_bytes': total_size,
            'total_size_kb': total_size / 1024 if total_size else 0
        }


class SearchEngine:
    """Class for searching PDF content."""
    
    @staticmethod
    def search_text_in_pdf(filepath, text):
        """Search for text within a PDF file."""
        try:
            pdf = fitz.open(filepath)
            found = False
            
            for page in pdf:
                if text in str(page):
                    found = True
                    break
            
            pdf.close()
            
            if found:
                logger.info(f"Text '{text}' found in {filepath}")
                return True
            else:
                logger.info(f"Text '{text}' not found in {filepath}")
                return False
                
        except Exception as e:
            logger.error(f"Error searching PDF: {e}")
            return False
    
    @staticmethod
    def search_all_pdfs(text, directory):
        """Search for text in all PDF files in a directory."""
        results = []
        
        if not os.path.exists(directory):
            return results
        
        for filepath in FileOperations.list_files(directory):
            if filepath.endswith('.pdf'):
                if SearchEngine.search_text_in_pdf(filepath, text):
                    results.append(filepath)
        
        return results


class ReportGenerator:
    """Class for generating reports."""
    
    @staticmethod
    def generate_library_report():
        """Generate a comprehensive library report."""
        stats = Statistics.get_book_count_by_author()
        total_books = Statistics.get_total_books()
        total_size = Statistics.get_total_size()
        avg_size = Statistics.get_average_size()
        
        report = f"""
PDF Library Report
==================

Total Books: {total_books}
Total Size: {total_size:.2f} KB
Average Size: {avg_size:.2f} KB

Top Authors:
"""
        
        for author, count in stats[:5]:
            report += f"  - {author}: {count} book(s)\n"
        
        return report
    
    @staticmethod
    def generate_size_report():
        """Generate a size distribution report."""
        sizes = Statistics.get_size_distribution()
        
        report = "Size Distribution:\n"
        report += "-" * 40 + "\n"
        
        for size in sorted(set(sizes)):
            count = sizes.count(size)
            report += f"{size} bytes: {count} book(s)\n"
        
        return report
    
    @staticmethod
    def generate_page_report():
        """Generate a page count distribution report."""
        pages = Statistics.get_page_distribution()
        
        report = "Page Count Distribution:\n"
        report += "-" * 40 + "\n"
        
        for page_count in sorted(set(pages)):
            count = pages.count(page_count)
            report += f"{page_count} pages: {count} book(s)\n"
        
        return report


class Application:
    """Main application class."""
    
    def __init__(self):
        self.db = Db()
        self.books = []
        self.window = tk.Tk()
        self.window.title("PDF Library")
        
        # Create main frame
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Search entry
        search_frame = ttk.LabelFrame(main_frame, text="Search", padding="5")
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.search_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.search_var, width=40).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(search_frame, text="Search", command=self.search_books).pack(side=tk.RIGHT, padx=5)
        
        # Book list frame
        book_frame = ttk.Frame(main_frame)
        book_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.tree = ttk.Treeview(book_frame, columns=("title", "author", "path"), show="headings")
        self.tree.heading("title", text="Title")
        self.tree.heading("author", text="Author")
        self.tree.heading("path", text="Path")
        self.tree.column("title", width=200)
        self.tree.column("author", width=150)
        self.tree.column("path", width=300)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(book_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add buttons frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(btn_frame, text="Add PDF", command=self.add_pdf).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Delete", command=self.delete_book).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Export CSV", command=self.export_csv).pack(side=tk.LEFT, padx=5)
        
        # Statistics frame
        stats_frame = ttk.LabelFrame(main_frame, text="Statistics", padding="5")
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.stats_labels = {
            "Total Books": tk.Label(stats_frame, text="0"),
            "Total Size": tk.Label(stats_frame, text="0 KB"),
            "Average Size": tk.Label(stats_frame, text="0 KB")
        }
        
        # Load books
        self.load_books()
    
    @logger.catch
    @snoop
    def load_books(self):
        """Load all books from database."""
        self.books = self.select_books()
        self.update_statistics()
        self.list_books()
    
    @logger.catch
    @snoop
    def list_books(self):
        """Display all books in the treeview."""
        for book in self.books:
            self.tree.insert('', 'end', values=(book['title'], book['author'], book['path']))
    
    @logger.catch
    @snoop
    def delete_book(self, book_id):
        """Delete a book from the database."""
        db.execute("DELETE FROM ebooks WHERE id=?", (book_id,))
        self.books = self.select_books()
        self.list_books()
    
    @logger.catch
    @snoop
    def search_books(self):
        """Search for books matching the query."""
        query = self.search_var.get().lower()
        results = [b for b in self.books if query in b['title'].lower()]
        self.tree.delete(*self.tree.get_children())
        for book in results:
            self.tree.insert('', 'end', values=(book['title'], book['author'], book['path']))
    
    @logger.catch
    @snoop
    def add_pdf(self):
        """Add a new PDF to the library."""
        if not config.file_path:
            showinfo("Error", "Please configure file path in config.py")
            return
        
        self.files = []
        try:
            self.files = fd.askopenfilenames(
                title="Select PDF files",
                initialdir=config.file_path,
                filetypes=(("PDF files", "*.pdf"), ("All files", "*.*"))
            )
            
            if not self.files:
                return
            
            for filepath in self.files:
                info = InsertPdf().get_pdf_info(filepath)
                if info:
                    db.execute("INSERT INTO ebooks (title, author, path, size) VALUES (?, ?, ?, ?)",
                              (info['title'], info['author'], info['path'], info['size']))
                    self.books = self.select_books()
                    self.list_books()
                    showinfo(f"Added {len(self.files)} PDF(s)")
        except Exception as e:
            logger.error(f"Error adding PDFs: {e}")
            showerror("Error", f"Failed to add PDFs: {e}")
    
    @logger.catch
    @snoop
    def export_csv(self):
        """Export library to CSV file."""
        if not self.books:
            showinfo("Info", "No books to export")
            return
        
        try:
            filepath = fd.asksaveasfilename(
                title="Export CSV",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if not filepath:
                return
            
            with open(filepath, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["ID", "Title", "Author", "Path", "Size (KB)", "Pages"])
                
                for book in self.books:
                    size_kb = round(book['size'] / 1024, 2)
                    writer.writerow([
                        book['id'],
                        book['title'],
                        book['author'],
                        book['path'],
                        size_kb,
                        book['pages']
                    ])
            
            showinfo("Success", f"Exported {len(self.books)} books to {filepath}")
        except Exception as e:
            logger.error(f"Error exporting CSV: {e}")
            showerror("Error", f"Failed to export CSV: {e}")
    
    @logger.catch
    @snoop
    def update_statistics(self):
        """Update statistics labels."""
        total_books = len(self.books)
        total_size = sum(book['size'] for book in self.books)
        avg_size = total_size / total_books if total_books > 0 else 0
        
        self.stats_labels["Total Books"].config(text=str(total_books))
        self.stats_labels["Total Size"].config(text=f"{total_size / 1024:.2f} KB")
        self.stats_labels["Average Size"].config(text=f"{avg_size / 1024:.2f} KB")
    
    @logger.catch
    @snoop
    def open_preview(self, event):
        """Open a preview window for the selected book."""
        selection = self.tree.selection()
        if not selection:
            return
        
        book_id = int(self.tree.item(selection[0])['values'][0])
        
        # For now, just show a message
        showinfo("Preview", "PDF preview feature coming soon!")
    
    def run(self):
        """Run the main application loop."""
        self.window.mainloop()


if __name__ == "__main__":
    app = MainWindow()
    app.run()
