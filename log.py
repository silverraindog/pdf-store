import sys


class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout

    def write(self, message):
        with open('pdf-store.log', "a", encoding='utf-8') as self.log:
            self.log.write(message)
        self.terminal.write(message)

    def flush(self):
        # this flush method is needed for python 3 compatibility.
        # this handles the flush command by doing nothing.
        # you might want to specify some extra behavior here.
        pass


sys.stdout = Logger()
