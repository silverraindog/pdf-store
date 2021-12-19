#!/usr/bin/env python3
__author__ = "Angus Robinson"
__copyright__ = "Copyright 2020, Sargus Networks"
__credits__ = ["Angus Robinson", "All those that provided answers and documentation on the internet"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Angus Robinson"
__email__ = "angus@fairhaven.za.net"
__status__ = "Beta"


import tkinter
from tkinter import ttk
from functions import InsertPdf
from loguru import logger
import snoop 
pdf = InsertPdf()
log.Logger()


class MainWindow:
    @logger.catch
    @snoop
    def __init__(self):
        self.window = tkinter.Tk()
        self.window.title("PDF Library")
        self.tree = ttk.Treeview(self.window, height=10, columns=1, show=["headings"])
        self.tree.label = tkinter.Label(self.window, text="Welcome to Pdf Library").pack()
        self.tree["column"] = "PDF"
        self.tree.column("PDF", width=1024, minwidth=800, stretch=tkinter.NO)
        self.tree.heading("PDF", text="PDF Title", anchor=tkinter.W)
        self.books = pdf.selectbooks()
        self.listbooks()
        self.window.mainloop()

    @logger.catch
    @snoop
    def listbooks(self):
        for book in self.books:
            self.tree.insert('', 'end', value=book)
        self.tree.pack(side=tkinter.TOP, fill=tkinter.X)


