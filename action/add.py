from argparse import Namespace
import os
import time
from tools import mktime
from zlib import crc32
import zlib
import structs
import mmap
from action.compress import CompressionTypes, Compress


# def write(content, header, zip):


def add(filename, path, compresstype, offset):
    version = 46 # Bzip2
    flags = 0
    extra = b""

    centraldirectory = []

    fileinfo = os.stat(filename)
    f = open(filename, "rb").read()
    filename = os.path.join(path, os.path.basename(filename))
    os.path.abspath(filename)
    # info("Compressing " + filename + "...")

    modtime, moddate = mktime(time.localtime(fileinfo.st_ctime))

    compressed = Compress(f, compresstype)

    # Only set compressed if lower
    if len(compressed) < len(f):
        print("Good")
        data = compressed
    # Otherwise just store it
    else:
        data = f
        compresstype = CompressionTypes.STORE.value

    checksum = crc32(f)

    header = structs.headerStruct.pack(
        b"\x50\x4b\x03\x04",
        version, flags, compresstype,
        modtime, moddate,
        checksum,
        len(data), fileinfo.st_size,
        len(filename), len(extra)
    )
    centralheader = structs.centralHeader(
        b"\x50\x4b\x01\x02", 3 << 8 | 23,
        version, flags, compresstype,
        modtime, moddate,
        checksum,
        len(data), fileinfo.st_size,
        len(filename), len(extra), len("Comment"),
        0, 1, 0,
        offset,
    )
    centraldirectory = {
        "centralheader": centralheader,
        "filename": filename,
        "extra": extra,
        "comment": "Comment"}
    print(centraldirectory)
    file = header + bytes(filename, 'utf-8') + extra + data
    return (file, centraldirectory)
