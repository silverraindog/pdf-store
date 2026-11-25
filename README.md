# PDF Store

A Python-based PDF library application that allows you to store, search, and manage PDF files with a Tkinter GUI.

## Features

### Core Features
- **PDF Metadata Extraction**: Automatically extracts title, author, page count, and file size from PDFs using PyMuPDF
- **Search Functionality**: Search for books by title in the library
- **Delete Capability**: Remove books from the library
- **CSV Export**: Export entire library to CSV format
- **Statistics Dashboard**: View total books, storage usage, and average file size

### Technical Details
- **GUI Framework**: Tkinter
- **Database**: SQLite (ebooks table)
- **PDF Processing**: PyMuPDF (fitz)
- **Testing**: Comprehensive unit test suite with pytest

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Edit `config.py` to configure:
- `file_path`: Directory where PDF files are stored
- `database`: Path to the SQLite database

## Usage

1. Run the application:
   ```bash
   python window.py
   ```

2. Add PDF files by clicking "Add PDF" button
3. Search for books using the search bar
4. Delete unwanted books
5. Export library to CSV
6. View statistics in the Statistics panel

## Project Structure

```
pdf-store/
├── window.py          # Main GUI application
├── functions.py       # Core functionality (PDF metadata extraction)
├── db.py              # Database operations
├── config.py          # Configuration settings
├── test_window.py     # Unit test suite
└── README.md          # This file
```

## Database Schema

The `ebooks` table contains:
- `id`: Primary key (auto-increment)
- `title`: Book title
- `author`: Author name
- `path`: File path to PDF
- `size`: File size in bytes
- `created_at`: Timestamp when added

## Testing

```bash
python3 -m pytest test_window.py -v
```

All 6 tests should pass.

## License

GPL - All those that provided answers on the internet
