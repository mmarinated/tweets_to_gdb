import os

def read_last_line(fn):
    """took from https://stackoverflow.com/questions/46258499/read-the-last-line-of-a-file-in-python"""
    with open(fn, 'rb') as f:
        f.seek(-2, os.SEEK_END)
        while f.read(1) != b'\n':
            f.seek(-2, os.SEEK_CUR) 
        last_line = f.readline().decode()

    return last_line