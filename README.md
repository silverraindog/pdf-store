# PDF Store - A Python-based PDF Library Application

A desktop application for storing, managing, and viewing PDF files.

## Features

- **PDF Storage**: Store PDF files with metadata (title, author, size, pages)
- **Database**: SQLite database for persistent storage
- **GUI**: Tkinter-based graphical user interface
- **Search**: Browse and search through stored PDFs

## Installation

```bash
pip install pymupdf
```

## Usage

1. Run the application: `python pdf-store.py`
2. The GUI will display all stored PDFs
3. Use the "Open Files" button to add new PDFs to the library

## Project Structure

```
pdf-store/
├── config.py          # Configuration settings
├── db.py              # Database connection and operations
├── functions.py       # Core functionality (PDF reading, CRUD operations)
├── files.py           # File selection dialog
├── window.py          # Main GUI window
└── pdf-store.py       # Application entry point
```

## License

GPL - See LICENSE file for details.
