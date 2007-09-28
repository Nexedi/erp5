"""
magic.py

 Initial Author: Jason Petrone <jp@demonseed.net>

 Updated by Gabriel Wicke <groups@gabrielwicke.de>
    Thu Oct 16 23:00:03 CEST 2003
    with magic data from gnome-vfs-mime-magic

"""

import re
import struct
import string
from StringIO import StringIO
from zipfile import ZipFile
from zipfile import BadZipfile
from xml.dom import minidom

__version__ = '$Revision: 1.2 $'[11:-2]

magic = [

    [0L, 'string', '=', '%PDF-', 'application/pdf'],
    [0L, 'string', '=', '\177ELF', 'application/x-executable-binary'],
    [0L, 'string', '=', '\004%!', 'application/postscript'],
    [0L, 'string', '=', '\000\000\001\272', 'video/mpeg'],
    [0L, 'string', '=', '\000\000\001\263', 'video/mpeg'],
    [0L, 'string', '=', '\x47\x3f\xff\x10', 'video/mpeg'],
    [0L, 'string', '=', '\377\330\377', 'image/jpeg'],
    [0L, 'string', '=', '\xed\xab\xee\xdb', 'application/x-rpm'],
    [0L, 'string', '=', 'Rar!', 'application/x-rar'],
    [257L, 'string', '=', 'ustar\0', 'application/x-tar'],
    [257L, 'string', '=', 'ustar\040\040\0', 'application/x-gtar'],
    # the following detection of OOo is according to 
    # http://books.evc-cit.info/oobook/ch01.html
    # and some heuristics found in hexeditor. if theres a better way to detect,
    # we should replace the signatures below.
    # best would to just read and evaluate the manifest file of the zip, but
    # the magic tests are running on the first 8kB, so we cant unzip the 
    # manifest in files >8kB.
    [30L, 'string', '=', 'mimetypeapplication/vnd.sun.xml.writer', 
     'application/vnd.sun.xml.writer'],
    [30L, 'string', '=', 'mimetypeapplication/vnd.sun.xml.calc', 
     'application/vnd.sun.xml.calc'],
    [30L, 'string', '=', 'mimetypeapplication/vnd.sun.xml.draw', 
     'application/vnd.sun.xml.draw'],
    [30L, 'string', '=', 'mimetypeapplication/vnd.sun.xml.impress', 
     'application/vnd.sun.xml.impress'],
    [30L, 'string', '=', 'mimetypeapplication/vnd.sun.xml.chart', 
     'application/vnd.sun.xml.chart'],
    [30L, 'string', '=', 'mimetypeapplication/vnd.sun.xml.global', 
     'application/vnd.sun.xml.global'],
    # zip works now, after we have it with lower priority than OOo
    [0L, 'string', '=', 'PK\003\004', 'application/zip'],
    [0L, 'string', '=', 'GIF8', 'image/gif'],
    [4L, 'string', '=', 'moov', 'video/quicktime'],
    [4L, 'string', '=', 'mdat', 'video/quicktime'],
    [8L, 'string', '=', 'mp42', 'video/quicktime'],
    [12L, 'string', '=', 'mdat', 'video/quicktime'],
    [36L, 'string', '=', 'mdat', 'video/quicktime'],
    [0L, 'belong', '=', '0x3026b275', 'video/x-ms-asf'],
    [0L, 'string', '=', 'ASF ', 'audio/x-ms-asx'],
    [0L, 'string', '=', '<ASX', 'audio/x-ms-asx'],
    [0L, 'string', '=', '<asx', 'audio/x-ms-asx'],
    [0L, 'string', '=', 'MThd', 'audio/x-midi'],
    [0L, 'string', '=', 'IMPM', 'audio/x-it'],
    [2L, 'string', '=', '-lh0-', 'application/x-lha'],
    [2L, 'string', '=', '-lh1-', 'application/x-lha'],
    [2L, 'string', '=', '-lz4-', 'application/x-lha'],
    [2L, 'string', '=', '-lz5-', 'application/x-lha'],
    [2L, 'string', '=', '-lzs-', 'application/x-lha'],
    [2L, 'string', '=', '-lh\40-', 'application/x-lha'],
    [2L, 'string', '=', '-lhd-', 'application/x-lha'],
    [2L, 'string', '=', '-lh2-', 'application/x-lha'],
    [2L, 'string', '=', '-lh3-', 'application/x-lha'],
    [2L, 'string', '=', '-lh4-', 'application/x-lha'],
    [2L, 'string', '=', '-lh5-', 'application/x-lha'],
    [20L, 'string', '=', '\375\304\247\334', 'application/x-zoo'],
    [0L, 'string', '=', 'StuffIt ', 'application/x-stuffit'],
    [11L, 'string', '=', 'must be converted with BinHex', 'application/mac-binhex40'],
    [102L, 'string', '=', 'mBIN', 'application/x-macbinary'],
    [4L, 'string', '=', 'gtktalog ', 'application/x-gtktalog'],
    [0L, 'string', '=', 'diff ', 'text/x-patch'],
    [0L, 'string', '=', 'Index:', 'text/x-patch'],
    [0L, 'string', '=', '*** ', 'text/x-patch'],
    [0L, 'string', '=', 'Only in ', 'text/x-patch'],
    [0L, 'string', '=', 'Common subdirectories: ', 'text/x-patch'],
    [0L, 'string', '=', 'FONT', 'application/x-font-vfont'],
    [0L, 'string', '=', 'IIN1', 'image/tiff'],
    [0L, 'string', '=', 'MM\x00\x2a', 'image/tiff'],
    [0L, 'string', '=', 'II\x2a\x00', 'image/tiff'],
    [0L, 'string', '=', '\x89PNG', 'image/png'],
    [0L, 'string', '=', '8BPS\ \ \000\000\000\000 &0xffffffff0000ffffffff', 'image/x-psd'],
    [0L, 'string', '=', '#LyX', 'text/x-lyx'],
    [0L, 'string', '=', 'DCMw', 'image/x-dcm'],
    [0L, 'string', '=', 'gimp xcf', 'application/x-gimp-image'],
    [0L, 'belong', '=', '0x59a66a95', 'image/x-sun-raster'],
    [0L, 'belong', '=', '0x01da0000 &0xfcfeffff', 'image/x-sgi'],
    [0L, 'belong', '=', '0xb168de3a', 'image/x-pcx'],
    [0L, 'string', '=', '\x28\x00\x00\x00', 'image/x-dib'],
    [0L, 'string', '=', 'SIMPLE  =', 'image/x-fits'],
    [0L, 'belong', '=', '0x46506978', 'image/x-fpx'],
    [0L, 'belong', '=', '0x00000200', 'image/x-icb'],
    [0L, 'belong', '=', '0x53445058', 'image/x-dpx'],
    [0L, 'string', '=', '[Desktop Entry]', 'application/x-gnome-app-info'],
    [0L, 'string', '=', '[X-GNOME-Metatheme]', 'application/x-gnome-theme'],
    [0L, 'string', '=', '<nautilus_object nautilus_link', 'application/x-nautilus-link'],
    [0L, 'string', '=', 'URL:', 'application/x-gmc-link'],
    [0L, 'string', '=', '/* XPM */', 'image/x-xpixmap'],
    [0L, 'string', '=', '<!DOCTYPE xbel', 'application/xbel'],
    [0L, 'string', '=', '<xbel', 'application/xbel'],
    [0L, 'string', '=', '<!DOCTYPE NETSCAPE-Bookmark-file-1\>', 'application/x-mozilla-bookmarks'],
    [0L, 'string', '=', '<!DOCTYPE NETSCAPE-Bookmark-file-1\>', 'application/x-netscape-bookmarks'],
    [0L, 'string', '=', '<ephy_bookmarks        ', 'application/x-epiphany-bookmarks'],
    [0L, 'string', '=', '<!DOCTYPE svg', 'image/svg'],
    [0L, 'string', '=', '<svg', 'image/svg'],
    [0L, 'string', '=', '<?php', 'application/x-php'],
    [0L, 'string', '=', '<smil\>', 'application/x-smil'],
    [0L, 'string', '=', '<SMIL\>', 'application/x-smil'],
    [0L, 'string', '=', '<!DOCTYPE HTML', 'text/html'],
    [0L, 'string', '=', '<!DOCTYPE html', 'text/html'],
    [0L, 'string', '=', '<!doctype html', 'text/html'],
    [0L, 'string', '=', '<!doctype Html', 'text/html'],
    [0L, 'string', '=', '<!doctype HTML', 'text/html'],
    [10L, 'string', '=', '<HEAD', 'text/html'],
    [10L, 'string', '=', '<head', 'text/html'],
    [16L, 'string', '=', '<TITLE', 'text/html'],
    [16L, 'string', '=', '<title', 'text/html'],
    [10L, 'string', '=', '<html', 'text/html'],
    [0L, 'string', '=', '<HTML', 'text/html'],
    [0L, 'string', '=', '<dia:diagram', 'application/x-dia-diagram'],
    [0L, 'string', '=', '<abiword', 'application/x-abiword'],
    [0L, 'string', '=', '<\!DOCTYPE abiword', 'application/x-abiword'],
    [0L, 'string', '=', 'gmr:Workbook', 'application/x-gnumeric'],
    [0L, 'string', '=', '<?xml', 'text/xml'],
    [0L, 'string', '=', '{\\rtf', 'application/rtf'],
    [0L, 'string', '=', '#!/bin/sh', 'text/x-sh'],
    [0L, 'string', '=', '#!/bin/bash', 'text/x-sh'],
    [0L, 'string', '=', '#!/bin/csh', 'text/x-csh'],
    [0L, 'string', '=', '#!/bin/ksh', 'text/x-ksh'],
    [0L, 'string', '=', '#!/bin/perl', 'text/x-perl'],
    [0L, 'string', '=', '#!/bin/zsh', 'text/x-zsh'],
    [1L, 'string', '=', '/bin/sh', 'text/x-sh'],
    [1L, 'string', '=', '/bin/bash', 'text/x-sh'],
    [1L, 'string', '=', '/bin/csh', 'text/x-csh'],
    [1L, 'string', '=', '/bin/ksh', 'text/x-ksh'],
    [1L, 'string', '=', '/bin/perl', 'text/x-perl'],
    [0L, 'string', '=', 'BEGIN:VCARD', 'text/x-vcard'],
    [0L, 'string', '=', 'BEGIN:VCALENDAR', 'text/calendar'],
    [8L, 'string', '=', 'CDR vrsn', 'application/vnd.corel-draw'],
    [8L, 'string', '=', 'AVI ', 'video/x-msvideo'],
    [0L, 'string', '=', 'MOVI', 'video/x-sgi-movie'],
    [0L, 'string', '=', '.snd', 'audio/basic'],
    [8L, 'string', '=', 'AIFC', 'audio/x-aifc'],
    [8L, 'string', '=', 'AIFF', 'audio/x-aiff'],
    [0L, 'string', '=', '.ra\375', 'audio/x-pn-realaudio'],
    [0L, 'belong', '=', '0x2e7261fd', 'audio/x-pn-realaudio'],
    [0L, 'string', '=', '.RMF', 'audio/x-pn-realaudio'],
    [8L, 'string', '=', 'WAVE', 'audio/x-wav'],
    [8L, 'string', '=', 'WAV ', 'audio/x-wav'],
    [0L, 'string', '=', 'ID3', 'audio/mpeg'],
    [0L, 'string', '=', '0xfff0', 'audio/mpeg'],
    [0L, 'string', '=', '\x00\x00\x01\xba', 'video/mpeg'],
    [8L, 'string', '=', 'CDXA', 'video/mpeg'],
    [0L, 'belong', '=', '0x000001ba', 'video/mpeg'],
    [0L, 'belong', '=', '0x000001b3', 'video/mpeg'],
    [0L, 'string', '=', 'RIFF', 'audio/x-riff'],
    [0L, 'string', '=', 'OggS   ', 'application/ogg'],
    [0L, 'string', '=', 'pnm:\/\/', 'audio/x-real-audio'],
    [0L, 'string', '=', 'rtsp:\/\/', 'audio/x-real-audio'],
    [0L, 'string', '=', 'SIT!', 'application/x-stuffit'],
    [0L, 'string', '=', '\312\376\272\276', 'application/x-java-byte-code'],
    [0L, 'string', '=', 'Joy!', 'application/x-pef-executable'],
    [4L, 'string', '=', '\x11\xAF', 'video/x-fli'],
    [4L, 'string', '=', '\x12\xAF', 'video/x-flc'],
    [0L, 'string', '=', '\x31\xbe\x00\x00', 'application/msword'],
    [0L, 'string', '=', 'PO^Q`', 'application/msword'],
    [0L, 'string', '=', '\376\067\0\043', 'application/msword'],
    [0L, 'string', '=', '\320\317\021\340\241\261', 'application/msword'],
    [0L, 'string', '=', '\333\245-\0\0\0', 'application/msword'],
    [0L, 'string', '=', 'Microsoft Excel 5.0 Worksheet', 'application/vnd.ms-excel'],
    [0L, 'string', '=', 'Biff5', 'application/vnd.ms-excel'],
    [0L, 'string', '=', '*BEGIN SPREADSHEETS    ', 'application/x-applix-spreadsheet'],
    [0L, 'string', '=', '*BEGIN SPREADSHEETS    ', 'application/x-applix-spreadsheet'],
    [0L, 'string', '=', '\x00\x00\x02\x00', 'application/vnd.lotus-1-2-3'],
    [0L, 'belong', '=', '0x00001a00', 'application/vnd.lotus-1-2-3'],
    [0L, 'belong', '=', '0x00000200', 'application/vnd.lotus-1-2-3'],
    [0L, 'string', '=', 'PSID', 'audio/prs.sid'],
    [31L, 'string', '=', 'Oleo', 'application/x-oleo'],
    [0L, 'string', '=', 'FFIL', 'application/x-font-ttf'],
    [65L, 'string', '=', 'FFIL', 'application/x-font-ttf'],
    [0L, 'string', '=', 'LWFN', 'application/x-font-type1'],
    [65L, 'string', '=', 'LWFN', 'application/x-font-type1'],
    [0L, 'string', '=', 'StartFont', 'application/x-font-sunos-news'],
    [0L, 'string', '=', '\x13\x7A\x29', 'application/x-font-sunos-news'],
    [8L, 'string', '=', '\x13\x7A\x2B', 'application/x-font-sunos-news'],
    [0L, 'string', '=', '%!PS-AdobeFont-1.', 'application/x-font-type1'],
    [6L, 'string', '=', '%!PS-AdobeFont-1.', 'application/x-font-type1'],
    [0L, 'string', '=', '%!FontType1-1.', 'application/x-font-type1'],
    [6L, 'string', '=', '%!FontType1-1.', 'application/x-font-type1'],
    [0L, 'string', '=', 'STARTFONT\040', 'application/x-font-bdf'],
    [0L, 'string', '=', '\001fcp', 'application/x-font-pcf'],
    [0L, 'string', '=', 'D1.0\015', 'application/x-font-speedo'],
    [0L, 'string', '=', '\x14\x02\x59\x19', 'application/x-font-libgrx'],
    [0L, 'string', '=', '\xff\x46\x4f\x4e', 'application/x-font-dos'],
    [7L, 'string', '=', '\x00\x45\x47\x41', 'application/x-font-dos'],
    [7L, 'string', '=', '\x00\x56\x49\x44', 'application/x-font-dos'],
    [0L, 'string', '=', '\<MakerScreenFont', 'application/x-font-framemaker'],
    [0L, 'string', '=', '\000\001\000\000\000', 'application/x-font-ttf'],
    [1L, 'string', '=', 'WPC', 'application/x-wordperfect'],
    [0L, 'string', '=', 'ID;', 'text/spreadsheet'],
    [0L, 'string', '=', 'MZ', 'application/x-ms-dos-executable'],
    [0L, 'string', '=', '%!', 'application/postscript'],
    [0L, 'string', '=', 'BZh', 'application/x-bzip'],
    [0L, 'string', '=', '\x1f\x8b', 'application/x-gzip'],
    [0L, 'string', '=', '\037\235', 'application/x-compress'],
    [0L, 'string', '=', '\367\002', 'application/x-dvi'],
    [0L, 'string', '=', '\367\203', 'application/x-font-tex'],
    [0L, 'string', '=', '\367\131', 'application/x-font-tex'],
    [0L, 'string', '=', '\367\312', 'application/x-font-tex'],
    [2L, 'string', '=', '\000\022', 'application/x-font-tex-tfm'],
    [0L, 'string', '=', '\x36\x04', 'application/x-font-linux-psf'],
    [0L, 'string', '=', 'FWS', 'application/x-shockwave-flash'],
    [0L, 'string', '=', 'CWS', 'application/x-shockwave-flash'],
    [0L, 'string', '=', 'NSVf', 'video/x-nsv'],
    [0L, 'string', '=', 'BMxxxx\000\000 &0xffff00000000ffff', 'image/bmp'],
    [0L, 'string', '=', 'Return-Path:', 'message/rfc822'],
    [0L, 'string', '=', 'Path:', 'message/news'],
    [0L, 'string', '=', 'Xref:', 'message/news'],
    [0L, 'string', '=', 'From:', 'message/rfc822'],
    [0L, 'string', '=', 'Article', 'message/news'],
    [0L, 'string', '=', 'Received:', 'message/rfc822'],
    [0L, 'string', '=', '[playlist]', 'audio/x-scpls'],
    [0L, 'string', '=', '[Reference]', 'video/x-ms-asf'],
    [0L, 'string', '=', 'fLaC', 'application/x-flac'],
    [32769L, 'string', '=', 'CD001', 'application/x-iso-image'],
    [37633L, 'string', '=', 'CD001', 'application/x-iso-image'],
    [32776L, 'string', '=', 'CDROM', 'application/x-iso-image'],
    [0L, 'string', '=', 'OTTO', 'application/x-font-otf'],
    [54L, 'string', '=', 'S T O P', 'application/x-ipod-firmware'],
    [0L, 'string', '=', 'BLENDER', 'application/x-blender'],
    [20L, 'string', '=', 'import', 'text/python-source'],
]

magicNumbers = []

def strToNum(n):
    val = 0
    col = long(1)
    if n[:1] == 'x': n = '0' + n
    if n[:2] == '0x':
        # hex
        n = string.lower(n[2:])
        while len(n) > 0:
            l = n[len(n) - 1]
            val = val + string.hexdigits.index(l) * col
            col = col * 16
            n = n[:len(n)-1]
    elif n[0] == '\\':
        # octal
        n = n[1:]
        while len(n) > 0:
            l = n[len(n) - 1]
            if ord(l) < 48 or ord(l) > 57: break
            val = val + int(l) * col
            col = col * 8
            n = n[:len(n)-1]
    else:
        val = string.atol(n)
    return val

class magicTest:
    def __init__(self, offset, t, op, value, msg, mask = None):
        if t.count('&') > 0:
            mask = strToNum(t[t.index('&')+1:])
            t = t[:t.index('&')]
        if type(offset) == type('a'):
            self.offset = strToNum(offset)
        else:
            self.offset = offset
        self.type = t
        self.msg = msg
        self.subTests = []
        self.op = op
        self.mask = mask
        self.value = value

    def test(self, data):
        if self.mask:
            data = data & self.mask
        if self.op == '=':
            if self.value == data: return self.msg
        elif self.op ==  '<':
            pass
        elif self.op ==  '>':
            pass
        elif self.op ==  '&':
            pass
        elif self.op ==  '^':
            pass
        return None

    def compare(self, data):
    #print str([self.type, self.value, self.msg])
        try:
            if self.type == 'string':
                c = ''; s = ''
                for i in range(0, len(self.value)+1):
                    if i + self.offset > len(data) - 1: break
                    s = s + c
                    [c] = struct.unpack('c', data[self.offset + i])
                data = s
            elif self.type == 'short':
                [data] = struct.unpack('h', data[self.offset : self.offset + 2])
            elif self.type == 'leshort':
                [data] = struct.unpack('<h', data[self.offset : self.offset + 2])
            elif self.type == 'beshort':
                [data] = struct.unpack('>H', data[self.offset : self.offset + 2])
            elif self.type == 'long':
                [data] = struct.unpack('l', data[self.offset : self.offset + 4])
            elif self.type == 'lelong':
                [data] = struct.unpack('<l', data[self.offset : self.offset + 4])
            elif self.type == 'belong':
                [data] = struct.unpack('>l', data[self.offset : self.offset + 4])
            else:
                #print 'UNKNOWN TYPE: ' + self.type
                pass
        except:
            return None

#    print str([self.msg, self.value, data])
        return self.test(data)


def guessMime(data):
    for test in magicNumbers:
        m = test.compare(data)
        if m: 
            return m
    # no matching, magic number.
    return

#import sys
for m in magic:
    magicNumbers.append(magicTest(m[0], m[1], m[2], m[3], m[4]))
