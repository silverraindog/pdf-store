#!/usr/bin/env python3
__author__ = "Angus Robinson"
__copyright__ = "Copyright 2020, Sargus Networks"
__credits__ = ["All those that provided answers on the internet"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Angus Robinson"
__email__ = "angus@fairhaven.za.net"
__status__ = "Beta"

# Default configuration
DEFAULT_FILE_PATH = "/home/sargus/books/"
DEFAULT_DATABASE = "books.db"

# Advanced settings
MAX_FILE_SIZE_MB = 100  # Maximum file size in MB
DEFAULT_EXPORT_FORMAT = "csv"
LOG_LEVEL = "INFO"

# Module-level variables for easy access
file_path = DEFAULT_FILE_PATH
database = DEFAULT_DATABASE
max_file_size_mb = MAX_FILE_SIZE_MB
default_export_format = DEFAULT_EXPORT_FORMAT
log_level = LOG_LEVEL
