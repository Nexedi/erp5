# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2015 Nexedi SA and Contributors. All Rights Reserved.
#                    Ivan Tyagov <ivan@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet
from erp5.component.document.BigFile import BigFile
from wendelin.bigarray.array_zodb import ZBigArray
from erp5.component.document.File import _MARKER
from wendelin.bigarray.array_ram import RAMArray
from ZPublisher import HTTPRangeSupport
from webdav.common import rfc1123_date
from DateTime import DateTime
from mimetools import choose_boundary
import transaction

class DataArray(BigFile):
  """
  Represents a numpy representation of ndarray
  """

  meta_type = 'ERP5 Data Array'
  portal_type = 'Data Array'
  add_permission = Permissions.AddPortalContent

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.CategoryCore
                    , PropertySheet.SortIndex
                    , PropertySheet.DataArray
                    )

  def initArray(self, shape, dtype):
    """
    Initialise array.
    """
    if self.__module__ == "erp5.temp_portal_type":
      array = RAMArray(shape, dtype)
    else:
      array = ZBigArray(shape, dtype)
    self._setArray(array)
    return array

  def getArray(self, default=None):
    """
    Get numpy array value.
    """
    return getattr(self, 'array', None)

  def _setArray(self, value):
    """
      Set numpy array to this ERP5 Data Array.
    """
    self.array = value

    # ZBigArray requirement: before we can compute it (with subobject
    # .zfile) have to be made explicitly known to connection or current
    # transaction committed (XXX: impossible to use as raises ConflictErrors)
    transaction.commit()

  def getArraySlice(self, start, end):
    """
      Implement array slicing in its most simple list alike form.
      Any other advanced slicing techniques currently possible by getting
      array reference directly.
    """
    return self.getArray()[start:end]

  def getArrayIndex(self, index):
    """
      Implement array indexing in its most simple list alike form.
      Any other advanced indexing techniques currently possible by getting
      array reference directly.
    """
    return self.getArray()[index]

  security.declareProtected(Permissions.AccessContentsInformation, 'getSize')
  def getSize(self):
    """
       Implement getSize interface for ndarray
    """
    array = self.getArray()
    if array is None:
      return 0
    else:
      return array.nbytes

  security.declareProtected(Permissions.AccessContentsInformation, 'getArrayShape')
  def getArrayShape(self):
    """
    Get numpy array shape.
    """
    zarray = self.getArray()
    if zarray is not None:
      return zarray.shape

  security.declareProtected(Permissions.AccessContentsInformation, 'getArrayDtype')
  def getArrayDtype(self):
    """
    Get numpy array dtype.
    """
    zarray = self.getArray()
    if zarray is not None:
      return zarray.dtype
    
  security.declareProtected(Permissions.AccessContentsInformation, 'getArrayDtypeNames')
  def getArrayDtypeNames(self):
    """
    Get numpy array dtype names
    """
    zarray = self.getArray()
    if zarray is not None:
      return zarray.dtype.names

  security.declareProtected(Permissions.View, 'index_html')
  def index_html(self, REQUEST, RESPONSE, format=_MARKER, inline=_MARKER, **kw):
    """
      Support streaming
    """
    if self._range_request_handler(REQUEST, RESPONSE):
      # we served a chunk of content in response to a range request.
      return ''

    # return default view
    return self.view()

  # FIXME this duplicates a lot of code from ERP5's BigFile
  # -> TODO reuse BigFile streaming capability without copying its code
  def _range_request_handler(self, REQUEST, RESPONSE):
    RESPONSE.setHeader("Content-Type", "application/octet-stream")
    # HTTP Range header handling: return True if we've served a range
    # chunk out of our data.
    # convert ranges from bytes to array indices
    slice_index = REQUEST.get('slice_index', None)
    if slice_index is not None:
      slice_index_list = []
      for index in slice_index:
        slice_index_list.append(slice(index.get('start'),
                                      index.get('stop'),
                                      index.get('step')))
      list_index = REQUEST.get('list_index', None)
      if list_index is not None:
        RESPONSE.write(self.getArray()[tuple(slice_index_list)][list_index].tobytes())
      else:
        RESPONSE.write(self.getArray()[tuple(slice_index_list)].tobytes())
      return True

    range = REQUEST.get_header('Range', None)
    request_range = REQUEST.get_header('Request-Range', None)
    if request_range is not None:
      # Netscape 2 through 4 and MSIE 3 implement a draft version
      # Later on, we need to serve a different mime-type as well.
      range = request_range
    if_range = REQUEST.get_header('If-Range', None)
    if range is not None:
      ranges = HTTPRangeSupport.parseRange(range)

      array = self.getArray()

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
            last_mod = self._data_mtime()
            if last_mod is None:
              last_mod = 0
            last_mod = long(last_mod)
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
          RESPONSE.setHeader('Last-Modified', rfc1123_date(self._data_mtime()))
          RESPONSE.setHeader('Content-Type', self.content_type)
          RESPONSE.setHeader('Content-Length', self.getSize())
          RESPONSE.setStatus(416)
          return True

        ranges = HTTPRangeSupport.expandRanges(ranges, self.getSize())


        if len(ranges) == 1:
          # Easy case, set extra header and return partial set.
          start, end = ranges[0]
          size = end - start

          RESPONSE.setHeader('Last-Modified', rfc1123_date(self._data_mtime()))
          RESPONSE.setHeader('Content-Type', self.content_type)
          RESPONSE.setHeader('Content-Length', size)
          RESPONSE.setHeader('Accept-Ranges', 'bytes')
          RESPONSE.setHeader('Content-Range',
              'bytes %d-%d/%d' % (start, end - 1, self.getSize()))
          RESPONSE.setStatus(206) # Partial content

          # convert array to bytes
          data = array[:].view('<b').reshape((-1,))[start:end].tobytes()
          RESPONSE.setBody(data, lock=True)

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

          # Some clients implement an earlier draft of the spec, they
          # will only accept x-byteranges.
          draftprefix = (request_range is not None) and 'x-' or ''

          RESPONSE.setHeader('Content-Length', size)
          RESPONSE.setHeader('Accept-Ranges', 'bytes')
          RESPONSE.setHeader('Last-Modified', rfc1123_date(self._data_mtime()))
          RESPONSE.setHeader('Content-Type',
              'multipart/%sbyteranges; boundary=%s' % (
                  draftprefix, boundary))
          RESPONSE.setStatus(206) # Partial content

          data = ''
          for start, end in ranges:
            data = '{data}\r\n--{boundary}\r\n'\
                   'Content-Type: {content_type}\r\n'\
                   'Content-Range: bytes {start:d}-{end:d}/{size:d}\r\n\r\n'\
                   '{array}'.format(data=data,
                             boundary=boundary,
                             content_type=self.content_type,
                             start=start,
                             end=end-1,
                             size=self.getSize(),
                             array=array[:].view('<b').reshape((-1,))[start:end].tobytes())

          data = '{}\r\n--{}--\r\n'.format(data, boundary)
          RESPONSE.setBody(data, lock=True)
          return True
