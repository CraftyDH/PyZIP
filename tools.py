import datetime
import time
import os
from datetime import date
INVALID_PATH_PARTS = ('', '.', '..')


class info():
    level = None

    @classmethod
    def set(cls, level):
        cls.level = level

    @classmethod
    def print(cls, text, outputlevel=0):
        # Print if reuqested level is below output level
        if outputlevel <= cls.level:
            print(text)


def sanitizePath(path):
    # Remove drive letters
    path = os.path.splitdrive(path)[1]
    # Incase backwards / for path
    path = path.replace('\\', '/')

    # Get each section of the path
    pathparts = path.split('/')
    path = []
    # Remove all invalid parts from the filename
    for segment in pathparts:
        if segment not in INVALID_PATH_PARTS:
            path.append(segment)

    return os.path.sep.join(path)


def mkdostime(ctime: time.struct_time):
    # Time (5 Hour) (6 Minute) (5 Second ( divided by zero ))
    modtime = ctime.tm_hour << 11 | ctime.tm_min << 5 | ctime.tm_sec // 2
    # Date (7 Year) (4 Month) (5 Day)
    moddate = (ctime.tm_year - 1980) << 9 | ctime.tm_mon << 5 | ctime.tm_mday
    return (modtime, moddate)

def mktime(modtime, moddate):
    # Modtime 
    sec = modtime & 0b11111 * 2
    min = modtime >> 5 & 0b111111
    hour = modtime >> 11

    day = moddate & 0b11111
    month = moddate >> 5 & 0b1111
    year = moddate >> 9
    return datetime.datetime(year, month, day, hour, min, sec)


def writeChanges(name, newfile):
    # Open original file
    origin = open(name, "w+b")

    newfile.flush()
    newfile.seek(0)
    # Read from the new file file
    for chunk in newfile:
        # Write the chunks and increment size
        origin.write(chunk)


# https://stackoverflow.com/questions/1094841/get-human-readable-version-of-file-size
def sizeof_fmt(num):
    for unit in ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB']:
        if abs(num) < 1024.0:
            return "%3.0f %s" % (num, unit)
        num /= 1024.0
