


# log events to files 
class FileLogger:

    def __init__(self, file):
        self.file = open(file, 'w')

    def log(self, event):
        self.file.write(str(event) + "\n")

    def close(self):
        self.file.close()

        
def get_logger(logger):
    if logger is None:
        return None
    # TODO other kinds of loggers, currently logging to a file is the default
    return FileLogger(logger)