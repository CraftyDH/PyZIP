#!/usr/bin/env python
import argparse
import mmap
from struct import *
import structs
import os
from sys import version
import time
from typing import NamedTuple
from zlib import crc32
import argparse


def mktime(ctime: time.struct_time):
    # Time (5 Hour) (6 Minute) (5 Second ( divided by zero ))
    modtime = ctime.tm_hour << 11 | ctime.tm_min << 5 | ctime.tm_sec // 2
    # Date (7 Year) (4 Month) (5 Day)
    moddate = (ctime.tm_year - 1980) << 9 | ctime.tm_mon << 5 | ctime.tm_mday
    return (modtime, moddate)


def flatten(x): return [item for sublist in x for item in sublist]


def checkZIP(path):
    if os.path.exists(path):
        f = open(path, "rb")
        if(f.readline(2) == b'PK'):
            return path
        check = input("File not a ZIP, Overide? ([y]/n): ")
        if not (check == "y" or check == "yes" or check == ""):
            exit()
    return path


def checkFile(path):
    if not os.path.exists(path):
        print('File: "' + path + '", is not readable.')
        exit()
    return path


parser = argparse.ArgumentParser("PyZIP")
parser.add_argument("zip", type=checkZIP, help="the path to the zip file.")

verbosity = parser.add_mutually_exclusive_group()
verbosity.add_argument("-v", default=0, action="count",
                       dest="verbosity", help="Verbosity level, up -vvv")
verbosity.add_argument("-s", action="store_const",
                       const=-1, dest="verbosity", help="Silent")
# options = parser.add_mutually_exclusive_group(required=True)

subparser = parser.add_subparsers(
    dest="action", help="The action to take", required=True)

add = subparser.add_parser("add")

add.add_argument("files", type=checkFile, nargs="+")
add.add_argument("-p", "--path", help="Path to store files in ZIP file")
add.add_argument("-c", "--comment", default="", help="Comment for each file")

remove = subparser.add_parser("remove")
remove.add_argument("files", nargs="+")

move = subparser.add_parser("move")
move.add_argument("file")
move.add_argument("destination")

extract = subparser.add_parser("extract")
extract.add_argument(
    "files", nargs="*", help="The files to extract. If none all files will be extracted")
extract.add_argument(
    "-o", "--output", help="Where to store the extracted files.")

info = subparser.add_parser("info")
info.add_argument("File", nargs="?",
                  help="shows infomation about the file/folder")
info.add_argument("-r", "--recursive",
                  help="shows info recursively through each folder")

args = parser.parse_args()

zip = open(args.zip, "r+b")


def info(text: str, level=0):
    if args.verbosity >= level:
        print(text)


info(args, 3)


def readCentralHeader(mm: mmap):
    # Find the start of central header
    centralstart = mm.rfind(b'\x50\x4b\x05\x06', mm.size()-250)

    # Seek file to that position
    mm.seek(centralstart)

    # Read central header into a namedtuple
    endofcentral = structs.endOfCentral._make(structs.endOfCentralStruct.unpack(
        mm.read(structs.endOfCentralStruct.size)))

    # Print the comment
    print(mm.read(endofcentral.commentlen))

    # Start reading the entries
    centraldirectory = []
    mm.seek(endofcentral.offsetcentral)
    for _ in range(endofcentral.totalentries):
        entry = {}
        centralheader = structs.centralHeader._make(
            structs.centralHeaderStruct.unpack(mm.read(structs.centralHeaderStruct.size)))
        entry["header"] = centralheader
        entry["filename"] = mm.read(centralheader.filenamelen)
        entry["extra"] = mm.read(centralheader.extralen)
        entry["comment"] = mm.read(centralheader.commentlen)
        centraldirectory.append(entry)

    return centraldirectory


if args.action == "add":
    version = 20
    flags = 0
    compression = 0
    extra = ""

    centraldirectory = []
    currentoffset = 0

    for path in args.files:
        fileinfo = os.stat(path)
        f = open(path, "rb").read()
        filename = os.path.basename(path)
        info("Compressing " + filename + "...")

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
        centralheader = structs.centralHeader.pack(
            b"\x50\x4b\x01\x02", 3 << 8 | 23,
            version, flags, compression,
            modtime, moddate,
            checksum,
            fileinfo.st_size, fileinfo.st_size,
            len(filename), len(extra), len(args.comment),
            0, 1, 0,
            currentoffset,
        )
        centraldirectory.append(
            centralheader + bytes(filename + extra + args.comment, 'utf-8'))

        towrite = header + bytes(filename + extra, 'utf-8') + f
        zip.write(towrite)
        currentoffset += len(towrite)

    centraldirectorysize = 0
    for _ in centraldirectory:
        centraldirectorysize += len(_)
        zip.write(_)

    endofcentraldirectory = structs.endOfCentral.pack(
        b'\x50\x4b\x05\x06',
        0, 0,
        *[len(centraldirectory)]*2,
        centraldirectorysize,
        currentoffset,
        len("Made by PyZIP!")
    )
    zip.write(endofcentraldirectory + b"Made by PyZIP!")
    zip.close()
elif args.action == "remove":
    pass
elif args.action == "move":
    pass
elif args.action == "extract":
    mm = mmap.mmap(zip.fileno(), 0)
    files = readCentralHeader(mm)

    # Read files
    for file in files:
        mm.seek(file["header"].localoffset)
        header = structs.header._make(
            structs.headerStruct.unpack(mm.read(structs.headerStruct.size)))
        filename = mm.read(header.filenamelen)
        mm.seek(header.extralen, os.SEEK_CUR)
        with open("output/" + str(filename, 'utf-8'), "w+b") as file:
            file.write(mm.read(header.compressedsize))


elif args.action == "info":
    pass
