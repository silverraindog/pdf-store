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
from tkinter.messagebox import showinfo





class FileImport:

    def select_files():
         filetypes = (
         ('text files', '*.txt'),
         ('All files', '*.*')
        )

        filenames = fd.askopenfilenames(
            title='Open files',
            initialdir='/',
            filetypes=filetypes)

        showinfo(
            title='Selected Files',
            message=filenames
        )


    # open button
    open_button = ttk.Button(
        root,
        text='Open Files',
        command=select_files
    )

    open_button.pack(expand=True)