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
from functions import InsertPdf
from db import Db
import config


class MainWindow:
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
        
        # Load books
        self.load_books()
        
        # Bind double-click to open preview
        self.tree.bind("<Double-1>", self.open_preview)
        
    @logger.catch
    @snoop
    def load_books(self):
        """Load all books from database."""
        self.books = self.selectbooks()
        self.listbooks()
    
    @logger.catch
    @snoop
    def listbooks(self):
        """Display all books in the treeview."""
        for book in self.books:
            self.tree.insert('', 'end', values=(book['title'], book['author'], book['path']))
    
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
                info = self.get_pdf_info(filepath)
                if info:
                    db.execute("INSERT INTO ebooks (title, author, path, size) VALUES (?, ?, ?, ?)",
                              (info['title'], info['author'], info['path'], info['size']))
                    self.books = self.selectbooks()
                    self.listbooks()
                    showinfo(f"Added {len(self.files)} PDF(s)")
                else:
                    logger.warning(f"Could not read PDF: {filepath}")
        except Exception as e:
            logger.error(f"Error adding PDFs: {e}")
            showerror("Error", f"Failed to add PDFs: {e}")
    
    @logger.catch
    @snoop
    def delete_book(self):
        """Delete a selected book."""
        selection = self.tree.selection()
        if not selection:
            showinfo("Info", "Please select a book to delete")
            return
        
        book_id = int(self.tree.item(selection[0])['values'][0])  # Get ID from values
        if askyesno("Confirm", f"Are you sure you want to delete '{self.tree.item(selection[0])['values'][0]}'?"):
            self.delete_book(book_id)
    
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
    
    @logger.catch
    @snoop
    def open_preview(self, event):
        """Open a preview window for the selected book."""
        selection = self.tree.selection()
        if not selection:
            return
        
        book_id = int(self.tree.item(selection[0])['values'][0])
        # Find the book in the database
        for book in self.books:
            if book['id'] == book_id:
                # Get the original path (need to store it)
                pass
        
        # For now, just show a message
        showinfo("Preview", "PDF preview feature coming soon!")
    
    def run(self):
        """Run the main application loop."""
        self.window.mainloop()


if __name__ == "__main__":
    app = MainWindow()
    app.run()
