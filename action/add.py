from argparse import Namespace
import os
import time
from tools import mktime
from zlib import crc32
import structs
import mmap


def add(filename, offset, zip):
    version = 20
    flags = 0
    compression = 0
    extra = ""

    centraldirectory = []

    fileinfo = os.stat(filename)
    f = open(filename, "r+b").read()
    filename = os.path.basename(filename)
    # info("Compressing " + filename + "...")

    modtime, moddate = mktime(time.localtime(fileinfo.st_ctime))
    filenamelen = len(filename)

    checksum = crc32(f)

    header = structs.headerStruct.pack(
        b"\x50\x4b\x03\x04",
        version, flags, compression,
        modtime, moddate,
        checksum,
        fileinfo.st_size, fileinfo.st_size,
        len(filename), len(extra)
    )
    centralheader = structs.centralHeader(
        b"\x50\x4b\x01\x02", 3 << 8 | 23,
        version, flags, compression,
        modtime, moddate,
        checksum,
        fileinfo.st_size, fileinfo.st_size,
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
    towrite = header + bytes(filename + extra, 'utf-8') + f
    zip.write(towrite)
    return (centraldirectory, len(towrite))
