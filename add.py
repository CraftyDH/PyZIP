import os
import pathlib
import time
from zlib import crc32

import structs
from compress import Compress, CompressionTypes
from tools import mkdostime


def add(filename: str, path: pathlib.Path, compresstype: int, offset: int):
    version = 46  # Bzip2
    flags = 0
    extra = b""

    centraldirectory = []

    fileinfo = os.stat(filename)
    f = open(filename, "rb").read()
    filename = os.path.join(path, os.path.basename(filename))
    os.path.abspath(filename)
    # info("Compressing " + filename + "...")

    modtime, moddate = mkdostime(time.localtime(fileinfo.st_ctime))

    compressed = Compress(f, compresstype)

    # Create the checksum for the file
    checksum = crc32(f)

    # Only set compressed if lower
    if len(compressed) < len(f):
        data = compressed
    # Otherwise just store it
    else:
        data = f
        compresstype = CompressionTypes.STORE.value

    # Create the file header
    header = structs.headerStruct.pack(
        b"\x50\x4b\x03\x04",
        version, flags, compresstype,
        modtime, moddate,
        checksum,
        len(data), fileinfo.st_size,
        len(filename), len(extra)
    )
    # Create the file header for the central directory
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
    # Create the central directory object with all metadata
    centraldirectory = {
        "centralheader": centralheader,
        "filename": filename,
        "extra": extra,
        "comment": "Comment"}
    # Return data
    file = header + bytes(filename, 'utf-8') + extra + data
    return (file, centraldirectory)
