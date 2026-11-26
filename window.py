#!/usr/bin/env python3
__author__ = "Angus Robinson"
__copyright__ = "Copyright 2020, Sargus Networks"
__credits__ = ["All those that provided answers on the internet"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Angus Robinson"
__email__ = "angus@fairhaven.za.net"
__status__ = "Beta"

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo, askyesno
from functions import InsertPdf, PdfPreview, BookManager
from db import Db
import config
import csv
import os


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
