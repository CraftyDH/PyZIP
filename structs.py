# See https://users.cs.jmu.edu/buchhofp/forensics/formats/pkzip.html
from collections import namedtuple
from struct import *

header = namedtuple("header", ['signature', 'version', 'flags', 'compression', 'modtime',
                    'moddate', 'checksum', 'compressedsize', 'uncommpressedsize', 'filenamelen', 'extralen'])
headerStruct = Struct('<4s5H3L2H')
#     Signature b"\x50\x4b\x03\x04", # 4S
#     version,                       # H
#     flags,                         # H
#     compression,                   # H
#     modtime,                       # H
#     moddate,                       # H
#     crc32,                         # L
#     compressed size,               # L
#     uncompressed size              # L
#     filename length,               # H
#     extra field length             # H
centralHeader = namedtuple("CentralHeader", ['signature', 'version', 'zipv', 'flags', 'compression', 'modtime', 'moddate', 'checksum',
                           'compressedsize', 'uncommpressedsize', 'filenamelen', 'extralen', 'commentlen', 'diskstart', 'internal', 'external', 'localoffset'])
centralHeaderStruct = Struct('<4s6H3L5H2L')
# Signature b"\x50\x4b\x01\x02",    # 4S
# Version (Host OS) | (Version)     # H
# ZIP Version                       # H
# Flags                             # H
# Compression                       # H
# modtime,                          # H
# moddate,                          # H
# crc32,                            # L
# compressed size                   # L
# uncompressed size                 # L
# filename length                   # H
# extra length                      # H
# comment length                    # H
# Disk start                        # H
# internal attributes               # H
# External Attributes               # L
# Offset of matching localheader    # L


endOfCentral = namedtuple('EndOfCentral', ['signature', 'disknum', 'disknumcentral',
                          'entries', 'totalentries', 'centralsize', 'offsetcentral', 'commentlen'])
endOfCentralStruct = Struct("<4s4H2LH")

# Signature b'\x50\x4b\x05\x06',    # 4s
# This Disk Number                  # H
# DSK Number of central directory   # H
# Entries of this disk              # H
# Total entries                     # H
# centraldirectorysize              # L
# offset of directory on 1st disk   # L
# Comment length                    # H
