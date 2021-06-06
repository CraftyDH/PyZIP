import structs


def readFile(fp, offset):
    fp.seek(offset)
    header = structs.header._make(
        structs.headerStruct.unpack(fp.read(structs.headerStruct.size)))

    fname = fp.read(header.filenamelen)
    extra = fp.read(header.extralen)

    file = fp.read(header.compressedsize)

    # Read again for some reason ???
    _ = fp.read(header.compressedsize)

    return(header, fname, extra, file)
