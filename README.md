# PDF Store

A Python-based PDF library application that allows you to store, search, and manage PDF files with a Tkinter GUI.

## Features

### Core Features
- **PDF Metadata Extraction**: Automatically extracts title, author, page count, and file size from PDFs using PyMuPDF
- **Search Functionality**: Search for books by title in the library
- **Delete Capability**: Remove books from the library
- **CSV Export**: Export entire library to CSV format
- **Statistics Dashboard**: View total books, storage usage, and average file size

### Advanced Features (Phase 3)
- **PDF Preview**: Display PDF content using PyMuPDF
- **JSON Export**: Export library to JSON format
- **XML Export**: Export library to XML format
- **Database Backup & Restore**: Backup and restore the SQLite database
- **Advanced Search**: Search by author, size range, page count
- **Security Features**: Input sanitization and path validation
- **Operation History**: Track recent operations
- **File System Operations**: Move, copy, delete files
- **Data Integrity Checks**: Verify database integrity
- **PDF Content Search**: Search for text within PDF files
- **Reports Generation**: Generate comprehensive library reports

### Technical Details
- **GUI Framework**: Tkinter
- **Database**: SQLite (ebooks table)
- **PDF Processing**: PyMuPDF (fitz)
- **Testing**: Comprehensive unit test suite with pytest
- **Logging**: Loguru for structured logging
- **Code Quality**: Snoop decorator for debugging

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Edit `config.py` to configure:
- `file_path`: Directory where PDF files are stored
- `database`: Path to the SQLite database
- `MAX_FILE_SIZE_MB`: Maximum file size in MB (default: 100)
- `DEFAULT_EXPORT_FORMAT`: Default export format (csv, json, xml)
- `LOG_LEVEL`: Logging level (INFO, DEBUG, WARNING, ERROR)

## Usage

1. Run the application:
   ```bash
   python window.py
   ```

2. Add PDF files by clicking "Add PDF" button
3. Search for books using the search bar
4. Delete unwanted books
5. Export library to CSV, JSON, or XML
6. View statistics in the Statistics panel
7. Open PDF preview for selected books
8. Backup and restore the database

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

All tests should pass.

## Security Features

- Input sanitization to prevent injection attacks
- Path traversal protection
- File validation before operations
- Database backup and restore functionality

## Project Structure

```
pdf-store/
├── window.py          # Main GUI application
├── functions.py       # Core functionality (PDF metadata extraction, exports, security)
├── db.py              # Database operations with backup/restore
├── config.py          # Configuration settings
├── test_window.py     # Unit test suite
├── preview_window.py  # PDF preview window
└── README.md          # This file
```

## License

GPL - All those that provided answers on the internet
