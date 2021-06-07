#!/usr/bin/env python
import mmap
import os
import shutil
import tempfile
from struct import *

import argparser
import compress as compress
import structs
from add import add
from read import readFile
from tools import *
from zlib import crc32


def writeDirectory(zip, centraldirectory: list, offset: int):
    centraldirectorysize = 0
    for directory in centraldirectory:
        centralheader, filename, extra, comment = directory.values()
        packed = structs.centralHeaderStruct.pack(*centralheader)
        towrite = packed + bytes(filename, "utf-8") + \
            extra + bytes(comment, "utf-8")
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
            info.print("There is no file named: " +
                       args.zip + "\nQuiting...", 0)
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
                # Create entry object
                entry = {}
                # Unpack header from file
                centralheader = structs.centralHeader._make(
                    structs.centralHeaderStruct.unpack(zipmm.read(structs.centralHeaderStruct.size)))

                info.print(centralheader, 3)

                # Unpack other info from the file
                entry["header"] = centralheader
                entry["filename"] = sanitizePath(str(zipmm.read(
                    centralheader.filenamelen), 'utf-8'))
                entry["extra"] = zipmm.read(
                    centralheader.extralen)
                entry["comment"] = str(zipmm.read(
                    centralheader.commentlen), 'utf-8')
                # Add file to central directory
                centralDirectory.append(entry)

    # Call function to handle each task case
    if args.action == "add":
        info.print("Adding files...")
        offset = 0
        newfile = tempfile.NamedTemporaryFile("w+b")
        addpath = sanitizePath(args.path)

        # Read into
        for file in centralDirectory:
            # Check if file is in the zip file allready
            if addpath + os.sep + file["filename"] in [addpath + os.sep + name for name in args.files]:
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
            info.print('Adding "' + file + '" to zip file.')
            # Get file metadata
            write, header = add(file, addpath, args.compresstype, offset)
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
            # Ensure file is not to be removed
            if file["filename"] not in args.files:
                # Read the file
                header, fname, extra, content = readFile(
                    origin, file["header"].localoffset)
                # And write it into the new ZIP file
                towrite = structs.headerStruct.pack(
                    *header) + fname + extra + content

                # Fix offset in central directory
                newDirectory = file
                newHeader: structs.centralHeader = file["header"]
                newHeader = newHeader._replace(localoffset=offset)
                newDirectory["header"] = newHeader
                newCentralDirectory.append(newDirectory)

                # Write all changes
                offset += len(towrite)
                newfile.write(towrite)
            else:
                info.print('Removing "' +
                           file["filename"] + '" from zip file.')

        if not newCentralDirectory:
            print("Removed all files")
            quit(0)

        # Finish writing the ZIP file
        writeDirectory(newfile, newCentralDirectory, offset)
        writeChanges(args.zip, newfile)

    elif args.action == "extract":
        for file in centralDirectory:
            # No folders 7zip!!!
            if file["filename"][-1] == "/":
                continue
            # Only extract the files requested
            if args.files:
                if file["filename"] not in args.files:
                    continue
            info.print('Extracting: "' + file["filename"] + '"')

            # Read the file
            header, fname, extra, content = readFile(
                origin, file["header"].localoffset)

            # Decompress the file
            data = compress.Decompress(content, header.compression)

            # Check that file matches crc32
            if crc32(data) != header.checksum:
                info.print('File: ' + file["filename"] +
                           ' failed crc32. Skipping...')
                continue

            # Make the directories for the file
            outputpath = os.path.join(
                args.output, file["filename"])
            os.makedirs(os.path.dirname(outputpath), exist_ok=True)
            # Write the file
            with open(outputpath, "w+b") as _file:
                _file.write(data)

            # Try to update the time to the modtime
            try:
                time = mktime(header.modtime, header.moddate)
                time = time.timestamp()
                os.utime(outputpath, (time, time))
            # Windows sometimes wont let this operation happen
            except OSError:
                pass

    elif args.action == "info":
        info.print("Zip file: " + os.path.basename(args.zip))
        info.print("Files:")
        # Print basic info from the central directory
        for file in centralDirectory:
            header = file["header"]
            info.print("⤷ " + file["filename"] +
                       " " + compress.CompressionTypes(header.compression).name + sizeof_fmt(header.uncommpressedsize))


if __name__ == "__main__":
    run()
