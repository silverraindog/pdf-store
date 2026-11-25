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
from ebooklib import epub

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
        """Insert all PDF books into the library."""
        if not os.path.exists(self.filepath):
            logger.warning(f"Directory {self.filepath} does not exist")
            return
        
        self.files = os.listdir(self.filepath)
        
        for book in self.files:
            if self.is_supported_format(book):
                statements = "INSERT INTO ebooks (title, author, path, size) VALUES (?, ?, ?, ?)"
                info = self.get_book_info(book)
                if info:
                    self.db.execute(statements, (info['title'], info['author'], info['path'], info['size']))
    
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
        self.db.execute(statements)
    
    @logger.catch
    @snoop
    def select_books(self):
        """Retrieve all books from the database."""
        statements = "SELECT title, author, path, size FROM ebooks ORDER BY created_at DESC"
        books = db.retrieve(statements)
        return books
    
    @logger.catch
    @snoop
    def get_book_info(self, filepath):
        """Get book metadata from file using appropriate library."""
        if filepath.endswith('.pdf'):
            return self.get_pdf_info(filepath)
        elif filepath.endswith('.epub') or filepath.endswith('.epub3'):
            return self.get_epub_info(filepath)
        elif filepath.endswith('.mobi'):
            return self.get_mobi_info(filepath)
        else:
            logger.warning(f"Unsupported format: {filepath}")
            return None
    
    @logger.catch
    @snoop
    def get_pdf_info(self, filepath):
        """Get PDF metadata from file using PyMuPDF."""
        try:
            pdf = fitz.open(filepath)
            info = {
                'title': pdf[0].title['title'],
                'author': pdf[0].author,
                'size': os.path.getsize(filepath),
                'pages': len(pdf)
            }
            pdf.close()
            return info
        except Exception as e:
            logger.error(f"Error reading PDF: {e}")
            return None
    
    @logger.catch
    @snoop
    def get_epub_info(self, filepath):
        """Get EPUB metadata from file using ebooklib."""
        try:
            book = epub.read_epub(filepath)
            info = {
                'title': book.get_metadata('DC:title')[0]['#text'] if book.get_metadata('DC:title') else "Unknown",
                'author': ', '.join(book.get_metadata('DC:author') or []),
                'size': os.path.getsize(filepath),
                'pages': len(book.get_pages()) if hasattr(book, 'get_pages') else 0
            }
            return info
        except Exception as e:
            logger.error(f"Error reading EPUB: {e}")
            return None
    
    @logger.catch
    @snoop
    def get_mobi_info(self, filepath):
        """Get MOBI metadata from file using ebooklib."""
        try:
            book = epub.read_epub(filepath)
            info = {
                'title': book.get_metadata('DC:title')[0]['#text'] if book.get_metadata('DC:title') else "Unknown",
                'author': ', '.join(book.get_metadata('DC:author') or []),
                'size': os.path.getsize(filepath),
                'pages': len(book.get_pages()) if hasattr(book, 'get_pages') else 0
            }
            return info
        except Exception as e:
            logger.error(f"Error reading MOBI: {e}")
            return None
    
    @snoop
    def is_supported_format(self, filepath):
        """Check if file is a supported format."""
        return filepath.endswith('.pdf') or filepath.endswith('.epub') or filepath.endswith('.epub3') or filepath.endswith('.mobi')


class PdfPreview:
    """Class for displaying PDF preview."""
    
    @staticmethod
    def load_preview(filepath):
        """Load the PDF preview and return page data."""
        try:
            pdf = fitz.open(filepath)
            
            if len(pdf) > 0:
                # Get first page
                page = pdf[0]
                
                # Extract text from first page
                text = page.get_text()
                
                return {
                    'title': page.title,
                    'author': page.author,
                    'pages': len(pdf),
                    'text': text[:500],  # First 500 characters
                    'page_count': len(pdf)
                }
            else:
                return {'error': 'No pages found in PDF'}
        except Exception as e:
            logger.error(f"Error loading preview: {e}")
            return {'error': str(e)}
    
    @staticmethod
    def close_preview():
        """Close the preview window."""
        pass


class PdfExporter:
    """Class for exporting PDF library to various formats."""
    
    @staticmethod
    def export_csv(books, filepath):
        """Export library to CSV file."""
        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["ID", "Title", "Author", "Path", "Size (KB)", "Pages"])
            
            for book in books:
                size_kb = round(book['size'] / 1024, 2)
                writer.writerow([
                    book['id'],
                    book['title'],
                    book['author'],
                    book['path'],
                    size_kb,
                    book['pages']
                ])
    
    @staticmethod
    def export_json(books, filepath):
        """Export library to JSON file."""
        data = {
            'exported_at': datetime.now().isoformat(),
            'total_books': len(books),
            'books': books
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    @staticmethod
    def export_xml(books, filepath):
        """Export library to XML file."""
        root = ET.Element("library")
        
        for book in books:
            book_elem = ET.SubElement(root, "book")
            ET.SubElement(book_elem, "id").text = str(book['id'])
            ET.SubElement(book_elem, "title").text = book['title']
            ET.SubElement(book_elem, "author").text = book['author']
            ET.SubElement(book_elem, "path").text = book['path']
            ET.SubElement(book_elem, "size").text = str(book['size'])
            ET.SubElement(book_elem, "pages").text = str(book['pages'])
        
        with open(filepath, 'w', encoding='utf-8') as f:
            ET.dump(root, f)


class BookManager:
    """Manages book operations in the library."""
    
    def __init__(self):
        self.db = Db()
        self.books = []
        self.window = None
    
    @logger.catch
    @snoop
    def load_books(self):
        """Load all books from database."""
        self.books = self.select_books()
        return self.books
    
    @logger.catch
    @snoop
    def list_books(self, books=None):
        """Display all books in the treeview."""
        if books is None:
            books = self.select_books()
        
        for book in books:
            self.tree.insert('', 'end', values=(book['title'], book['author'], book['path']))
    
    @logger.catch
    @snoop
    def delete_book(self, book_id):
        """Delete a book from the database."""
        self.db.execute("DELETE FROM ebooks WHERE id=?", (book_id,))
        self.books = self.select_books()
        return self.books
    
    @logger.catch
    @snoop
    def search_books(self, query):
        """Search for books matching the query."""
        query = query.lower()
        results = [b for b in self.books if query in b['title'].lower()]
        return results
    
    @logger.catch
    @snoop
    def add_book(self, filepaths):
        """Add new books to the library (PDF, EPUB, MOBI)."""
        added_count = 0
        
        for filepath in filepaths:
            info = InsertPdf().get_book_info(filepath)
            if info:
                self.db.execute("INSERT INTO ebooks (title, author, path, size) VALUES (?, ?, ?, ?)",
                          (info['title'], info['author'], info['path'], info['size']))
                added_count += 1
        
        self.books = self.select_books()
        return added_count
    
    @logger.catch
    @snoop
    def export_library(self, format_type, filepath):
        """Export library to specified format."""
        if format_type == 'csv':
            PdfExporter.export_csv(self.books, filepath)
        elif format_type == 'json':
            PdfExporter.export_json(self.books, filepath)
        elif format_type == 'xml':
            PdfExporter.export_xml(self.books, filepath)
        else:
            raise ValueError(f"Unknown export format: {format_type}")


class MainWindow:
    """Main application window for PDF library."""
    
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
        self.db.execute("DELETE FROM ebooks WHERE id=?", (book_id,))
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
                info = InsertPdf().get_book_info(filepath)
                if info:
                    self.db.execute("INSERT INTO ebooks (title, author, path, size) VALUES (?, ?, ?, ?)",
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
            showerror("Error", f"Failed to export PDFs: {e}")
    
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
        """Open preview window for the selected book."""
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
