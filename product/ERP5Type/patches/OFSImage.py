##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""
  Monkey-patch to fix OFS.Image, which is not capable to detect the SVG
  Content Type format.

  Monkey patch uses 2.12.3 original code.
"""
import OFS.Image
import struct
from io import BytesIO
from zExceptions import Forbidden

def getImageInfo_with_svg_fix(data):
    data = bytes(data)
    size = len(data)
    height = -1
    width = -1
    content_type = ''

    # handle GIFs
    if (size >= 10) and data[:6] in (b'GIF87a', b'GIF89a'):
        # Check to see if content_type is correct
        content_type = 'image/gif'
        w, h = struct.unpack("<HH", data[6:10])
        width = int(w)
        height = int(h)

    # See PNG v1.2 spec (http://www.cdrom.com/pub/png/spec/)
    # Bytes 0-7 are below, 4-byte chunk length, then 'IHDR'
    # and finally the 4-byte width, height
    elif (size >= 24
          and data[:8] == b'\211PNG\r\n\032\n'
          and data[12:16] == b'IHDR'):
        content_type = 'image/png'
        w, h = struct.unpack(">LL", data[16:24])
        width = int(w)
        height = int(h)

    # Maybe this is for an older PNG version.
    elif (size >= 16) and (data[:8] == b'\211PNG\r\n\032\n'):
        # Check to see if we have the right content type
        content_type = 'image/png'
        w, h = struct.unpack(">LL", data[8:16])
        width = int(w)
        height = int(h)

    # handle JPEGs
    elif (size >= 2) and (data[:2] == b'\377\330'):
        content_type = 'image/jpeg'
        jpeg = BytesIO(data)
        jpeg.read(2)
        b = jpeg.read(1)
        try:
            while (b and ord(b) != 0xDA):
                while (ord(b) != 0xFF):
                    b = jpeg.read(1)
                while (ord(b) == 0xFF):
                    b = jpeg.read(1)
                if (ord(b) >= 0xC0 and ord(b) <= 0xC3):
                    jpeg.read(3)
                    h, w = struct.unpack(">HH", jpeg.read(4))
                    break
                else:
                    jpeg.read(int(struct.unpack(">H", jpeg.read(2))[0]) - 2)
                b = jpeg.read(1)
            width = int(w)
            height = int(h)
        except Exception:
            pass

    # MONKEY PATCH START HERE
    # Handle SVG
    elif (b"</svg>" in data):
        content_type = 'image/svg+xml'
    # MONKEY PATCH ENDS HERE

    return content_type, width, height

OFS.Image.getImageInfo = getImageInfo_with_svg_fix

PUT_orig = OFS.Image.File.PUT

def PUT(self, REQUEST, RESPONSE):
  """Handle HTTP PUT requests"""
  if REQUEST.environ['REQUEST_METHOD'] != 'PUT':
    raise Forbidden('REQUEST_METHOD should be PUT.')
  return PUT_orig(self, REQUEST, RESPONSE)

OFS.Image.File.PUT = PUT
