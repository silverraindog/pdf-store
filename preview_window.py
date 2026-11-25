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
from tkinter import ttk, filedialog as fd
from tkinter.messagebox import showinfo, askyesno
from functions import PdfPreview


class PreviewWindow:
    """Window for displaying PDF preview."""
    
    def __init__(self):
        self.preview_window = tk.Tk()
        self.preview_window.title("PDF Preview")
        self.preview_window.geometry("800x600")
        self.preview_window.resizable(True, True)
        
        # Create main frame
        main_frame = ttk.Frame(self.preview_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Status label
        status_label = ttk.Label(main_frame, text="Previewing PDF...")
        status_label.pack(pady=(0, 10))
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, length=200)
        self.progress_bar.pack(pady=(0, 5))
        
        # Status message
        self.status_message = ttk.Label(main_frame, text="Loading PDF...")
        self.status_message.pack(pady=(0, 10))
        
        # Close button
        close_button = ttk.Button(main_frame, text="Close", command=self.close_preview)
        close_button.pack(side=tk.RIGHT, padx=5)
        
        # Load preview
        self.load_preview()
    
    @logger.catch
    @snoop
    def load_preview(self):
        """Load the PDF preview."""
        filepath = None
        
        # Get file path from selection or use default
        if hasattr(self, 'selected_file'):
            filepath = self.selected_file
        else:
            filepath = fd.askopenfilename(
                title="Select PDF file to preview",
                initialdir=config.file_path,
                filetypes=(("PDF files", "*.pdf"), ("All files", "*.*"))
            )
        
        if not filepath:
            self.close_preview()
            return
        
        self.selected_file = filepath
        
        # Show progress bar
        self.progress_bar['value'] = 0
        self.status_message.config(text="Loading PDF...")
        
        try:
            # Use PyMuPDF to open and display the PDF
            pdf = fitz.open(filepath)
            
            if len(pdf) > 0:
                # Get first page
                page = pdf[0]
                
                # Create a simple preview by showing page info
                self.status_message.config(text=f"Title: {page.title}")
                self.status_message.config(text=f"Author: {page.author}")
                self.status_message.config(text=f"Pages: {len(pdf)}")
                
                # Show preview window
                self.preview_window.mainloop()
            else:
                self.status_message.config(text="No pages found in PDF")
        except Exception as e:
            logger.error(f"Error loading preview: {e}")
            self.status_message.config(text=f"Error: {e}")
    
    @logger.catch
    @snoop
    def close_preview(self):
        """Close the preview window."""
        self.preview_window.destroy()


def main():
    """Run the preview application."""
    app = PreviewWindow()
    app.run()


if __name__ == "__main__":
    main()
