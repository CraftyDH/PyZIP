#!/usr/bin/env python
import os
from typing import Union
from action.info import info
from action.extract import extract
from action.move import move
from action.remove import remove
from action.add import add
import argparser
import mmap
from struct import *
import structs


def writeDirectory(zip, centraldirectory, offset):
    centraldirectorysize = 0
    for directory in centraldirectory:
        centralheader, filename, extra, comment = directory.values()
        packed = structs.centralHeaderStruct.pack(*centralheader)
        towrite = packed + bytes(filename + extra + comment, "utf-8")
        centraldirectorysize += len(towrite)
        zip.write(towrite)

    endofcentraldirectory = structs.endOfCentralStruct.pack(
        b'\x50\x4b\x05\x06',
        0, 0,
        *[len(centraldirectory)]*2,
        centraldirectorysize,
        offset,
        len("Made by PyZIP!")
    )
    zip.write(endofcentraldirectory + b"Made by PyZIP!")


def run(args: str = None):
    # Get args given to program
    args = argparser.parser.parse_args(args)
    zipfile: open = None
    if not os.path.exists(args.zip):
        if args.action == "add":
            zipfile = open(args.zip, "w+b")
        else:
            print("There is no file named: " + args.zip + "\nQuiting...")
            exit(0)
    else:
        zipfile = open(args.zip, "r+b")

    centralDirectory = []
    centraldirstart = 0

    test = zipfile.readline(2)

    # Check if zip file
    if test != b"PK":
        if args.action != "add" and test == None:
            print("File " + args.zip + " is not a zip file. \nQuiting...")
            exit(0)
    else:
        # Read central header
        zipmm = mmap.mmap(zipfile.fileno(), 0)

        # Find start of central directory
        centralstart = zipmm.rfind(b'\x50\x4b\x05\x06', zipmm.size()-250)

        # Seek file to that position
        zipmm.seek(centralstart)

        # Read central header into a namedtuple
        endofcentral = structs.endOfCentral._make(structs.endOfCentralStruct.unpack(
            zipmm.read(structs.endOfCentralStruct.size)))

        # Print the comment
        print(zipmm.read(endofcentral.commentlen))

        centraldirstart = endofcentral.offsetcentral

        # Start reading the entries
        zipmm.seek(endofcentral.offsetcentral)
        for _ in range(endofcentral.totalentries):
            entry = {}
            centralheader = structs.centralHeader._make(
                structs.centralHeaderStruct.unpack(zipmm.read(structs.centralHeaderStruct.size)))

            entry["header"] = centralheader
            entry["filename"] = str(zipmm.read(
                centralheader.filenamelen), 'utf-8')
            entry["extra"] = str(zipmm.read(
                centralheader.extralen), 'utf-8')
            entry["comment"] = str(zipmm.read(
                centralheader.commentlen), 'utf-8')
            centralDirectory.append(entry)

    print(centralDirectory)
    # Check if empty file

    print(args)
    # Call function to handle each task case
    if args.action == "add":
        offset = centraldirstart
        # centralDirectory = []
        zipfile.seek(centraldirstart, 0)
        for file in args.files:
            header, size = add(file, offset, zipfile)
            offset += size
            centralDirectory.append(header)
        writeDirectory(zipfile, centralDirectory, offset)
    elif args.action == "remove":
        remove(args)
    elif args.action == "move":
        move(args)
    elif args.action == "extract":
        extract(args)
    elif args.action == "info":
        info(args)

    # def info(text: str, level=0):
    #     if args.verbosity >= level:
    #         print(text)

    # info(args, 3)

    # zipfile.truncate()
    # zipfile.close()


if __name__ == "__main__":
    run()
