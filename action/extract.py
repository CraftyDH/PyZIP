from argparse import Namespace
from mmap import mmap

def extract(args: Namespace):
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
