import binascii
import struct
import numpy as np
from cStringIO import StringIO

MAGIC_PREFIX = b'\x92WEN'
MAGIC_LEN = len(MAGIC_PREFIX) +2
CR32_LEN = 4
HEADER_LEN = MAGIC_LEN + CR32_LEN

# check that it is wendelin data
magic_str = data[0:MAGIC_LEN]
assert magic_str[:-2] == MAGIC_PREFIX
major, minor = map(ord, magic_str[-2:]) #python2
#major, minor = magic_str[-2:] #python 3
assert major == 0 and minor == 1

# verify crc32 checksum
checksum = struct.unpack('<i', data[MAGIC_LEN:HEADER_LEN])[0]
assert checksum == binascii.crc32(data[HEADER_LEN:])
io = StringIO()
io.write(data[HEADER_LEN:])
io.seek(0)
array = np.load(io)
io.close()
return array
