# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002-2006 Nexedi SARL and Contributors. All Rights Reserved.
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

import tempfile, os

from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import _setCacheHeaders, _ViewEmulator

from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5.Document.Image import Image
from Products.ERP5.Document.Document import ConversionError,\
                                            VALID_TEXT_FORMAT_LIST
from subprocess import Popen, PIPE
import errno

class PDFDocument(Image):
  """
  PDFDocument is a subclass of Image which is able to
  extract text content from a PDF file either as text
  or as HTML.
  """
  # CMF Type Definition
  meta_type = 'ERP5 PDF Document'
  portal_type = 'PDF'

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

  # Conversion API
  def _convert(self, format, **kw):
    """
    Implementation of conversion for PDF files
    """
    if format == 'html':
      try:
        return self.getConversion(format=format)
      except KeyError:
        mime = 'text/html'
        data = self._convertToHTML()
        self.setConversion(data, mime=mime, format=format)
        return (mime, data)
    elif format in ('txt', 'text'):
      try:
        return self.getConversion(format='txt')
      except KeyError:
        mime = 'text/plain'
        data = self._convertToText()
        self.setConversion(data, mime=mime, format='txt')
        return (mime, data)
    elif format is None:
      return self.getContentType(), self.getData()
    else:
      if kw.get('frame', None) is None:
        # when converting to image from PDF we care for first page only
        # this will make sure that only first page is used and not whole content of
        # PDF file read & converted which is a performance issue
        kw['frame'] = 0
      return Image._convert(self, format, **kw)

  security.declareProtected(Permissions.ModifyPortalContent, 'populateContent')
  def populateContent(self):
    """
      Convert each page to an Image and populate the
      PDF directory with converted images. May be useful
      to provide online PDF reader
    """
    raise NotImplementedError

  security.declarePrivate('_convertToText')
  def _convertToText(self):
    """
      Convert the PDF text content to text with pdftotext
    """
    if not self.hasData():
      return ''
    mime_type = 'text/plain'
    portal_transforms = self.getPortalObject().portal_transforms
    filename = self.getStandardFilename(format='txt')
    result = portal_transforms.convertToData(mime_type, str(self.getData()),
                                             context=self, filename=filename,
                                             mimetype=self.getContentType())
    if result:
      return result
    else:
      # Try to use OCR
      # As high dpi images are required, it may take some times to convert the
      # pdf. 
      # It may be required to use activities to fill the cache and at the end, 
      # to calculate the final result
      text = ''
      content_information = self.getContentInformation()
      page_count = int(content_information.get('Pages', 0))
      for page_number in range(page_count):
        src_mimetype, png_data = self.convert(
            'png', quality=100, resolution=300,
            frame=page_number, display='identical')
        if not src_mimetype.endswith('png'):
          continue
        content = str(png_data)
        if content is not None:
          filename = self.getStandardFilename(format='png')
          result = portal_transforms.convertToData(mime_type, content,
                                                   context=self,
                                                   filename=filename,
                                                   mimetype=src_mimetype)
          if result is None:
            raise ConversionError('PDFDocument conversion error. '
                                  'portal_transforms failed to convert to %s: %r' % (mime_type, self))
          text += result
      return text

  security.declareProtected(Permissions.View, 'getSizeFromImageDisplay')
  def getSizeFromImageDisplay(self, image_display):
    """
    Return the size for this image display, or None if this image display name
    is not known. If the preference is not set, (0, 0) is returned.
    """
    # identical parameter can be considered as a hack, in order not to
    # resize the image to prevent text distorsion when using OCR.
    # A cleaner API is required.
    if image_display == 'identical':
      return (self.getWidth(), self.getHeight())
    else:
      return Image.getSizeFromImageDisplay(self, image_display)

  security.declarePrivate('_convertToHTML')
  def _convertToHTML(self):
    """
    Convert the PDF text content to HTML with pdftohtml

    NOTE: XXX check that command exists and was executed
    successfully
    """
    if not self.hasData():
      return ''
    tmp = tempfile.NamedTemporaryFile()
    tmp.write(self.getData())
    tmp.seek(0)

    command_result = None
    try:
      command = ['pdftohtml', '-enc', 'UTF-8', '-stdout',
                 '-noframes', '-i', tmp.name]
      try:
        command_result = Popen(command, stdout=PIPE).communicate()[0]
      except OSError, e:
        if e.errno == errno.ENOENT:
          raise ConversionError('pdftohtml was not found')
        raise

    finally:
      tmp.close()
    # Quick hack to remove bg color - XXX
    h = command_result.replace('<BODY bgcolor="#A0A0A0"', '<BODY ')
    # Make links relative
    h = h.replace('href="%s.html' % tmp.name.split(os.sep)[-1],
                                                          'href="asEntireHTML')
    return h

  security.declareProtected(Permissions.AccessContentsInformation, 'getContentInformation')
  def getContentInformation(self):
    """
    Returns the information about the PDF document with
    pdfinfo.

    NOTE: XXX check that command exists and was executed
    successfully
    """
    try:
      return self._content_information.copy()
    except AttributeError:
      pass
    tmp = tempfile.NamedTemporaryFile()
    tmp.write(self.getData())
    tmp.seek(0)
    command_result = None
    try:

      # First, we use pdfinfo to get standard metadata
      command = ['pdfinfo', '-meta', '-box', tmp.name]
      try:
        command_result = Popen(command, stdout=PIPE).communicate()[0]
      except OSError, e:
        if e.errno == errno.ENOENT:
          raise ConversionError('pdfinfo was not found')
        raise

      result = {}
      for line in command_result.splitlines():
        item_list = line.split(':')
        key = item_list[0].strip()
        value = ':'.join(item_list[1:]).strip()
        result[key] = value

      # Then we use pdftk to get extra metadata
      try:
        command = ['pdftk', tmp.name, 'dump_data', 'output']
        command_result = Popen(command, stdout=PIPE).communicate()[0]
      except OSError, e:
        # if pdftk not found, pass
        if e.errno != errno.ENOENT:
          raise
      else:
        line_list = (line for line in command_result.splitlines())
        while True:
          try:
            line = line_list.next()
          except StopIteration:
            break
          if line.startswith('InfoKey'):
            key = line[len('InfoKey: '):]
            line = line_list.next()
            assert line.startswith('InfoValue: '),\
                "Wrong format returned by pdftk dump_data"
            value = line[len('InfoValue: '):]
            result.setdefault(key, value)
    finally:
      tmp.close()

    self._content_information = result
    return result.copy()

  def _setFile(self, data, precondition=None):
    try:
      del self._content_information
    except (AttributeError, KeyError):
      pass
    Image._setFile(self, data, precondition=precondition)
