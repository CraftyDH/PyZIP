import structs


def readFile(fp, offset):
    # Set file pointer to start of file
    fp.seek(offset)
    # Read the header
    header = structs.header._make(
        structs.headerStruct.unpack(fp.read(structs.headerStruct.size)))

    # Read the other metadata
    fname = fp.read(header.filenamelen)
    extra = fp.read(header.extralen)
    
    # Read the file
    file = fp.read(header.compressedsize)

    #? FIX: Read again for some reason. It doesn't work otherwise.
    _ = fp.read(header.compressedsize)

    return(header, fname, extra, file)
