import zlib
import bz2
import enum
import


class CompressionTypes(enum.Enum):
    # Supported
    STORE = 0
    DEFLATE = 8
    BZIP2 = 46


def Compress(content, code):
    if code == CompressionTypes.STORE.value:
        return content
    elif code == CompressionTypes.DEFLATE.value:
        compressor = zlib.compressobj(
            9, zlib.DEFLATED, -15)
        return compressor.compress(content) + compressor.flush()
    elif code == CompressionTypes.BZIP2.value:
        return bz2.compress(content)
    else:
        print(CompressionTypes(code).name + " not supported.")


def Decompress(content, code):
    if code == CompressionTypes.STORE.value:
        return content
    elif code == CompressionTypes.DEFLATE.value:
        decompress = zlib.decompressobj(wbits=zlib.MAX_WBITS)
        return decompress(content)
    elif code == CompressionTypes.BZIP2.value:
        return bz2.decompress(content)
    else:
        print(CompressionTypes(code).name + " not supported.")
