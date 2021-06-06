#!/usr/bin/env python
import os
from typing import Union
from action.add import add
from action.read import readFile
import argparser
import mmap
from struct import *
import structs
import tempfile
import shutil
import time
from tools import writeChanges, info, sizeof_fmt


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
    info.set(args.verbosity)
    info.print(args, 3)

    # Check if zip file is empty
    if not os.path.exists(args.zip):
        # If action is add an empty file is allowed
        if args.action != "add":
            info("There is no file named: " + args.zip + "\nQuiting...", 0)
            exit(0)
        # Therefore create the file
        else:
            origin = open(args.zip, "x+b")
    # Open the file
    else:
        if args.action in ["add", "remove"]:
            # Make backup file
            shutil.move(args.zip, args.zip + ".bak.zip")
            # Open zip file
            origin = open(args.zip + ".bak.zip", "r+b")
        else:
            origin = open(args.zip, "r+b")

        # Check if zip file by reading first 2 characters
        test = origin.readline(2)
        if test != b"PK":
            if args.action != "add" and test == None:
                print("File " + args.zip + " is not a zip file. \nQuiting...")
                exit(0)
        else:
            info.print("Reading central header...", 2)
            # Read central header use MMAP to find central header
            zipmm = mmap.mmap(origin.fileno(), 0, access=mmap.ACCESS_READ)

            # Find start of central directory
            centralstart = zipmm.rfind(b'\x50\x4b\x05\x06')

            # Seek file to that position
            zipmm.seek(centralstart)

            # Read central header into a namedtuple
            endofcentral = structs.endOfCentral._make(structs.endOfCentralStruct.unpack(
                zipmm.read(structs.endOfCentralStruct.size)))

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

    # Call function to handle each task case
    if args.action == "add":
        info.print("Adding files...")
        offset = 0
        newfile = tempfile.NamedTemporaryFile("w+b")

        # Read into
        for file in centralDirectory:
            # Check if file is in the zip file allready
            if file["filename"] in args.files:
                info.print('Overriding "' +
                           file["filename"] + '" found in zip file.')
                # remove file from central directory
                centralDirectory.remove(file)
                continue
            info.print('Copying file "' +
                       file["filename"] + '" to zip file...', 1)

            # Read file contents
            header, fname, extra, file = readFile(
                origin, file["header"].localoffset)

            # Write file contents
            towrite = structs.headerStruct.pack(
                *header) + fname + extra + file
            newfile.write(towrite)
            # Increment file offset
            offset += len(towrite)

        for file in args.files:
            info.print('Adding "' + file + '" to zip file.', 1)
            # Get file metadata
            write, header = add(file, offset)
            # Write file
            newfile.write(write)
            # Increment offset
            offset += len(write)
            # Add file to centralDirectory
            centralDirectory.append(header)

        # Write directory to file
        writeDirectory(newfile, centralDirectory, offset)

        writeChanges(args.zip, newfile)

    elif args.action == "remove":
        offset = 0
        newfile = tempfile.NamedTemporaryFile("w+b")

        newCentralDirectory = []
        # Read into
        for file in centralDirectory:
            if file["filename"] not in filenames:
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

    elif args.action == "extract":
        outputpath = os.path.join(args.output)
        os.makedirs(outputpath, exist_ok=True)
        for file in centralDirectory:
            if args.files:
                if file["filename"] not in filenames:
                    continue
            info.print('Extracting: "' + file["filename"])
            # origin.seek(file["header"].localoffset)
            # header = structs.header._make(
            #     structs.headerStruct.unpack(origin.read(structs.headerStruct.size)))
            # filename = origin.read(header.filenamelen)
            # origin.seek(header.extralen, os.SEEK_CUR)
            header, fname, extra, content = readFile(
                origin, file["header"].localoffset)
            with open(os.path.join(outputpath, str(fname, 'utf-8')), "w+b") as _file:
                _file.write(content)

    elif args.action == "info":
        # List in depth info about each file
        if args.file:
            for file in centralDirectory:
                if file["filename"] == os.path.basename(args.file):
                    header = file["header"]
                    info.print("File: " + file["filename"])
                    break
            else:
                print("File not in zip.")
        # List info about zip file
        else:
            info.print("Zip file: " + os.path.basename(args.zip))
            info.print("Files:")
            for file in centralDirectory:
                header = file["header"]
                info.print("⤷ " + file["filename"] +
                           sizeof_fmt(header.uncommpressedsize))
    # def info(text: str, level=0):
    #     if args.verbosity >= level:
    #         print(text)

    # info(args, 3)

    # origin.truncate()
    # origin.close()


if __name__ == "__main__":
    run()
