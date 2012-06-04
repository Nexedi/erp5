# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
#               2012 Nexedi SA and Contributors. All Rights Reserved.
#                    Romain Courteaud <romain@nexedi.com>
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.Base import removeIContentishInterface
from Products.ERP5.Document.File import File, _MARKER
from Products.ERP5Type.BTreeData import BTreeData
from ZPublisher.HTTPRequest import FileUpload
from ZPublisher import HTTPRangeSupport
from webdav.common import rfc1123_date
from mimetools import choose_boundary
from Products.CMFCore.utils import getToolByName, _setCacheHeaders,\
    _ViewEmulator
import re

class BigFile(File):
  """
  Support storing huge file.
  No convertion is allowed for now.
  """

  meta_type = 'ERP5 Big File'
  portal_type = 'Big File'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Default Properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Version
                    , PropertySheet.Reference
                    , PropertySheet.Document
                    , PropertySheet.Data
                    , PropertySheet.ExternalDocument
                    , PropertySheet.Url
                    , PropertySheet.Periodicity
    )

  # OFS.File has an overloaded __str__ that returns the file content
  __str__ = object.__str__

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getData')
  def getData(self):
    """Read the full btree
    """
    btree = self._baseGetData()
    if isinstance(btree, BTreeData):
      return btree.read(0, len(btree))
    else:
      return btree

  security.declareProtected(Permissions.ModifyPortalContent, 'updateContentMd5')
  def updateContentMd5(self):
    """Update md5 checksum from the original file
    """
    self._setContentMd5(None)

  def _read_data(self, file, data=None):

    n=1 << 20

    if isinstance(file, str):
      # Big string: cut it into smaller chunks
      file = StringIO(file)

    if isinstance(file, FileUpload) and not file:
      raise ValueError, 'File not specified'

    seek=file.seek
    read=file.read

    seek(0,2)
    end=file.tell()

    if data is None:
      btree = BTreeData()
    else:
      btree = data
    seek(0)
    pos = file.tell()
    offset = len(btree)

    while pos < end:
      next = pos + n
      if next > end:
        next = end

      btree.write(read(next-pos), offset+pos)
      pos = file.tell()

    self.serialize()
    return btree, len(btree)

  def _range_request_handler(self, REQUEST, RESPONSE):
    # HTTP Range header handling: return True if we've served a range
    # chunk out of our data.
    range = REQUEST.get_header('Range', None)
    request_range = REQUEST.get_header('Request-Range', None)
    if request_range is not None:
      # Netscape 2 through 4 and MSIE 3 implement a draft version
      # Later on, we need to serve a different mime-type as well.
      range = request_range
    if_range = REQUEST.get_header('If-Range', None)
    if range is not None:
      ranges = HTTPRangeSupport.parseRange(range)

      data = self._baseGetData()

      if if_range is not None:
        # Only send ranges if the data isn't modified, otherwise send
        # the whole object. Support both ETags and Last-Modified dates!
        if len(if_range) > 1 and if_range[:2] == 'ts':
          # ETag:
          if if_range != self.http__etag():
            # Modified, so send a normal response. We delete
            # the ranges, which causes us to skip to the 200
            # response.
            ranges = None
        else:
          # Date
          date = if_range.split( ';')[0]
          try: mod_since=long(DateTime(date).timeTime())
          except: mod_since=None
          if mod_since is not None:
            if data is not None:
              last_mod = long(data._p_mtime)
            else:
              if self._p_mtime:
                last_mod = long(self._p_mtime)
              else:
                last_mod = long(0)
            if last_mod > mod_since:
              # Modified, so send a normal response. We delete
              # the ranges, which causes us to skip to the 200
              # response.
              ranges = None

      if ranges:
        # Search for satisfiable ranges.
        satisfiable = 0
        for start, end in ranges:
          if start < self.getSize():
            satisfiable = 1
            break

        if not satisfiable:
          RESPONSE.setHeader('Content-Range',
              'bytes */%d' % self.getSize())
          RESPONSE.setHeader('Accept-Ranges', 'bytes')
          if data is not None:
            RESPONSE.setHeader('Last-Modified', rfc1123_date(data._p_mtime))
          else:
            RESPONSE.setHeader('Last-Modified', rfc1123_date(self._p_mtime))
          RESPONSE.setHeader('Content-Type', self.content_type)
          RESPONSE.setHeader('Content-Length', self.getSize())
          RESPONSE.setStatus(416)
          return True

        ranges = HTTPRangeSupport.expandRanges(ranges, self.getSize())

        if len(ranges) == 1:
          # Easy case, set extra header and return partial set.
          start, end = ranges[0]
          size = end - start

          if data is not None:
            RESPONSE.setHeader('Last-Modified', rfc1123_date(data._p_mtime))
          else:
            RESPONSE.setHeader('Last-Modified', rfc1123_date(self._p_mtime))
          RESPONSE.setHeader('Content-Type', self.content_type)
          RESPONSE.setHeader('Content-Length', size)
          RESPONSE.setHeader('Accept-Ranges', 'bytes')
          RESPONSE.setHeader('Content-Range',
              'bytes %d-%d/%d' % (start, end - 1, self.getSize()))
          RESPONSE.setStatus(206) # Partial content

          if isinstance(data, str):
            RESPONSE.write(data[start:end])
            return True
          iterator = data.iterate(start, end-start)
          try:
            while 1:
              RESPONSE.write(iterator.next())
          except StopIteration:
            pass
          return True

        else:
          boundary = choose_boundary()

          # Calculate the content length
          size = (8 + len(boundary) + # End marker length
              len(ranges) * (         # Constant lenght per set
                  49 + len(boundary) + len(self.content_type) +
                  len('%d' % self.getSize())))
          for start, end in ranges:
            # Variable length per set
            size = (size + len('%d%d' % (start, end - 1)) +
                end - start)

          data = self._baseGetData()

          # Some clients implement an earlier draft of the spec, they
          # will only accept x-byteranges.
          draftprefix = (request_range is not None) and 'x-' or ''

          RESPONSE.setHeader('Content-Length', size)
          RESPONSE.setHeader('Accept-Ranges', 'bytes')
          if data is not None:
            RESPONSE.setHeader('Last-Modified', rfc1123_date(data._p_mtime))
          else:
            RESPONSE.setHeader('Last-Modified', rfc1123_date(self._p_mtime))
          RESPONSE.setHeader('Content-Type',
              'multipart/%sbyteranges; boundary=%s' % (
                  draftprefix, boundary))
          RESPONSE.setStatus(206) # Partial content

          for start, end in ranges:
            RESPONSE.write('\r\n--%s\r\n' % boundary)
            RESPONSE.write('Content-Type: %s\r\n' %
                self.content_type)
            RESPONSE.write(
                'Content-Range: bytes %d-%d/%d\r\n\r\n' % (
                    start, end - 1, self.getSize()))

            if isinstance(data, str):
              RESPONSE.write(data[start:end])

            else:
              iterator = data.iterate(start, end-start)
              try:
                while 1:
                  RESPONSE.write(iterator.next())
              except StopIteration:
                pass

          RESPONSE.write('\r\n--%s--\r\n' % boundary)
          return True

  security.declareProtected(Permissions.View, 'index_html')
  def index_html(self, REQUEST, RESPONSE, format=_MARKER, inline=_MARKER, **kw):
    """
      Support streaming
    """
    if self._range_request_handler(REQUEST, RESPONSE):
      # we served a chunk of content in response to a range request.
      return ''

    web_cache_kw = kw.copy()
    if format is not _MARKER:
      web_cache_kw['format'] = format
    _setCacheHeaders(_ViewEmulator().__of__(self), web_cache_kw)

    if format is _MARKER and not kw:
      # conversion parameters is mandatory to download the converted content.
      # By default allways return view action.
      # for all WevDAV access return raw content.
      return self.view()

    if format is _MARKER:
      format = None

    data = self._baseGetData()
    mime = self.getContentType()

    RESPONSE.setHeader('Content-Length', len(data))
    RESPONSE.setHeader('Content-Type', mime)
    if inline is _MARKER:
      # by default, use inline for text and image formats
      inline = False
    if not inline:
      # need to return it as attachment
      filename = self.getStandardFilename(format=format)
      RESPONSE.setHeader('Cache-Control', 'Private') # workaround for Internet Explorer's bug
      RESPONSE.setHeader('Accept-Ranges', 'bytes')


    if data is None:
      return ''
    iterator = data.iterate()
    try:
      while 1:
        RESPONSE.write(iterator.next())
    except StopIteration:
      pass
    return ''

  security.declareProtected(Permissions.ModifyPortalContent,'PUT')
  def PUT(self, REQUEST, RESPONSE):
    """Handle HTTP PUT requests"""
    self.dav__init(REQUEST, RESPONSE)
    self.dav__simpleifhandler(REQUEST, RESPONSE, refresh=1)

    type=REQUEST.get_header('content-type', None)

    file=REQUEST['BODYFILE']

    content_range = REQUEST.get_header('Content-Range', None)
    if content_range is None:
      btree = None
    else:
      current_size = int(self.getSize())
      query_range = re.compile('bytes \*/\*')
      append_range = re.compile('bytes (?P<first_byte>[0-9]+)-' \
                                '(?P<last_byte>[0-9]+)/' \
                                '(?P<total_content_length>[0-9]+)')
      if query_range.match(content_range):
        data = self._baseGetData()

        RESPONSE.setHeader('X-Explanation', 'Resume incomplete')
        RESPONSE.setHeader('Range', 'bytes 0-%s' % (current_size-1))
        RESPONSE.setStatus(308)
        return RESPONSE

      if append_range.match(content_range):

        result_dict = append_range.search(content_range).groupdict()
        first_byte = int(result_dict['first_byte'])
        last_byte = int(result_dict['last_byte'])
        total_content_length = int(result_dict['total_content_length'])
        content_length= int(REQUEST.get_header('Content-Length', '0'))

        if (first_byte != current_size):
          RESPONSE.setHeader('X-Explanation', 'Can only append data')
          RESPONSE.setStatus(400)
          return RESPONSE
        elif (last_byte+1 != total_content_length):
          RESPONSE.setHeader('X-Explanation', 'Total size unexpected')
          RESPONSE.setStatus(400)
          return RESPONSE
        elif (last_byte+1-first_byte != content_length):
          RESPONSE.setHeader('X-Explanation', 'Content length unexpected')
          RESPONSE.setStatus(400)
          return RESPONSE

        else:

          btree = self._baseGetData()
          if btree is None:
            btree = BTreeData()

      else:
        RESPONSE.setHeader('X-Explanation', 'Can not parse range')
        RESPONSE.setStatus(400) # Partial content
        return RESPONSE

    data, size = self._read_data(file, data=btree)

    content_type=self._get_content_type(file, data, self.__name__,
                                        type or self.content_type)
    self.update_data(data, content_type, size)

    RESPONSE.setStatus(204)
    return RESPONSE

# CMFFile also brings the IContentishInterface on CMF 2.2, remove it.
removeIContentishInterface(BigFile)

