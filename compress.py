import bz2
import enum
import zlib


class CompressionTypes(enum.Enum):
    # Supported
    STORE           = 0
    DEFLATE         = 8
    BZIP2           = 12

        # Unsupported
    DEFLATE64       = 9
    PKWARE_IMPLODE  = 10
    LZMA            = 14
    IMB_TERSE       = 18
    IMB_LZ77        = 19
    ZSTD            = 93
    MP3             = 94
    XZ              = 95
    JPEG            = 96
    WAVPACK         = 97
    PPMD            = 98

    # Legacy
    SHRUNK          = 1
    REDUCED_1       = 2
    REDUCED_2       = 3
    REDUCED_3       = 4
    REDUCED_4       = 5
    IMPLODED        = 6
    ZSTD_LEGACY     = 20
    IBM_CMPSC       = 16

def Compress(content: str, code: int):
    # Store so just return data
    if code == CompressionTypes.STORE.value:
        return content
    # Deflate using zlib implementation
    elif code == CompressionTypes.DEFLATE.value:
        # Some magic values (compressstrength, deflate, ???)
        compressor = zlib.compressobj(
            9, zlib.DEFLATED, wbits=-zlib.MAX_WBITS)
        return compressor.compress(content) + compressor.flush()
    # Bzip2 using Bzip2
    elif code == CompressionTypes.BZIP2.value:
        return bz2.compress(content)
    else:
        print(CompressionTypes(code).name + " not supported.")


def Decompress(content: str, code: int):
    # Store so just return data
    if code == CompressionTypes.STORE.value:
        return content
    elif code == CompressionTypes.DEFLATE.value:
        # Magic values
        decompress = zlib.decompressobj(wbits=-zlib.MAX_WBITS)
        return decompress.decompress(content)
    # Bzip2 using Bzip2
    elif code == CompressionTypes.BZIP2.value:
        return bz2.decompress(content)
    else:
        print(CompressionTypes(code).name + " not supported.")
