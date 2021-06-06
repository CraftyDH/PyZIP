#!/usr/bin/env python
import os
from typing import Union
from action.info import info
from action.extract import extract
from action.move import move
from action.remove import remove
from action.add import add
from action.read import readFile
import argparser
import mmap
from struct import *
import structs
import tempfile
import shutil
import time
from tools import writeChanges


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
    origin: open = None

    centralDirectory = []

    # Check if zip file is empty
    if not os.path.exists(args.zip):
        # If action is add an empty file is allowed
        if args.action != "add":
            print("There is no file named: " + args.zip + "\nQuiting...")
            exit(0)
        # Therefore create the file
        else:
            origin = open(args.zip, "x+b")
    # Open the file
    else:
        shutil.move(args.zip, args.zip + ".bak.zip")
        origin = open(args.zip + ".bak.zip", "r+b")

        test = origin.readline(2)

        # Check if zip file
        if test != b"PK":
            if args.action != "add" and test == None:
                print("File " + args.zip + " is not a zip file. \nQuiting...")
                exit(0)
        else:
            # Read central header use MMAP to find central header
            zipmm = mmap.mmap(origin.fileno(), 0, access=mmap.ACCESS_READ)

            # Find start of central directory
            centralstart = zipmm.rfind(b'\x50\x4b\x05\x06')

            # Seek file to that position
            zipmm.seek(centralstart)

            # Read central header into a namedtuple
            endofcentral = structs.endOfCentral._make(structs.endOfCentralStruct.unpack(
                zipmm.read(structs.endOfCentralStruct.size)))

            # Print the comment
            print(zipmm.read(endofcentral.commentlen))

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
        offset = 0
        newfile = tempfile.NamedTemporaryFile("w+b")

        # Read into
        for file in centralDirectory:
            header, fname, extra, file = readFile(
                origin, file["header"].localoffset)

            towrite = structs.headerStruct.pack(
                *header) + fname + extra + file
            offset += len(towrite)
            newfile.write(towrite)

        for file in args.files:
            write, header = add(file, offset)
            offset += len(write)
            newfile.write(write)
            centralDirectory.append(header)
        writeDirectory(newfile, centralDirectory, offset)

        # origin.close()

        # with open(origin.name, "wb") as origin:
        writeChanges(args.zip, newfile)

        # shutil.move(newfile.name, args.zip)

    elif args.action == "remove":
        offset = 0
        newfile = tempfile.NamedTemporaryFile("w+b")

        newCentralDirectory = []
        # Read into
        for file in centralDirectory:
            if file["filename"] not in args.files:
                header, fname, extra, content = readFile(
                    origin, file["header"].localoffset)

                towrite = structs.headerStruct.pack(
                    *header) + fname + extra + content

                newDirectory = file
                newHeader: structs.centralHeader = file["header"]
                newHeader = newHeader._replace(localoffset=offset)
                newDirectory["header"] = newHeader
                newCentralDirectory.append(newDirectory)

                offset += len(towrite)
                newfile.write(towrite)

        if not newCentralDirectory:
            print("Removed all files")
            quit(0)

        writeDirectory(newfile, newCentralDirectory, offset)
        writeChanges(args.zip, newfile)

    elif args.action == "move":
        move(args)
    elif args.action == "extract":
        for file in centralDirectory:
            # origin.seek(file["header"].localoffset)
            # header = structs.header._make(
            #     structs.headerStruct.unpack(origin.read(structs.headerStruct.size)))
            # filename = origin.read(header.filenamelen)
            # origin.seek(header.extralen, os.SEEK_CUR)
            header, fname, extra, content = readFile(
                origin, file["header"].localoffset)
            print(fname)

            with open("output/" + str(fname, 'utf-8'), "w+b") as _file:
                _file.write(content)

    elif args.action == "info":
        info(args)

    # def info(text: str, level=0):
    #     if args.verbosity >= level:
    #         print(text)

    # info(args, 3)

    # origin.truncate()
    # origin.close()


if __name__ == "__main__":
    run()
