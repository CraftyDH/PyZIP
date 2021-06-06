import argparse
import os
from typing import Union


def checkZIP(path: str):
    """
    Check if file is not a zip to avoid overriding a file.
    Exit program if fail
    """
    if os.path.exists(path):
        f = open(path, "r+b")
        if(f.readline(2) == b'PK'):
            return path
        check = input("File not a ZIP, Overide? ([y]/n): ")
        if not (check == "y" or check == "yes" or check == ""):
            exit()
    return path


def checkFile(path: str):
    """
    Checks if a file exists, exists program if not readable
    Only used if a file needs to exist
    """
    if not os.path.exists(path):
        print('File: "' + path + '", is not readable.')
        exit()
    return path


parser = argparse.ArgumentParser("PyZIP")
parser.add_argument("zip", help="the path to the zip file.")

# Verbosity counter
__verbosity = parser.add_mutually_exclusive_group()
__verbosity.add_argument("-v", default=0, action="count",
                         dest="verbosity", help="Verbosity level, up -vvv")
__verbosity.add_argument("-s", action="store_const",
                         const=-1, dest="verbosity", help="Silent")

# Subparse to find which action is used
__subparser = parser.add_subparsers(
    dest="action", help="The action to take", required=True)

# Set args for add action
__add = __subparser.add_parser("add")
__add.add_argument("files", type=checkFile, nargs="+")
__add.add_argument("-p", "--path", help="Path to store files in ZIP file")
__add.add_argument("-c", "--comment", default="", help="Comment for each file")

# Set args for remove action
__remove = __subparser.add_parser("remove")
__remove.add_argument("files", nargs="+")

# Set args for extract action
__extract = __subparser.add_parser("extract")
__extract.add_argument(
    "files", nargs="*", help="The files to extract. If none all files will be extracted")
__extract.add_argument(
    "-o", "--output", help="Where to store the extracted files.")

# Set args for info action
__info = __subparser.add_parser("info")
__info.add_argument("File", nargs="?",
                    help="shows infomation about the file/folder")
__info.add_argument("-r", "--recursive",
                    help="shows info recursively through each folder")
