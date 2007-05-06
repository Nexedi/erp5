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

import tempfile, os, cStringIO

from AccessControl import ClassSecurityInfo
from Products.CMFCore.WorkflowCore import WorkflowMethod
from Products.CMFCore.utils import getToolByName

from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.Cache import CachingMethod
from Products.ERP5.Document.Image import Image
from Products.ERP5.Document.Document import ConversionCacheMixin
from Products.ERP5.Document.File import _unpackData

from zLOG import LOG

class PDFDocument(Image, ConversionCacheMixin):
  """
  PDFDocument is a subclass of Image which is able to
  extract text content from a PDF file either as text
  or as HTML.
  """
  # CMF Type Definition
  meta_type = 'ERP5 PDF Document'
  portal_type = 'PDF'
  isPortalContent = 1
  isRADContent = 1

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

  searchable_property_list = ('asText', 'title', 'description', 'id', 'reference',
                              'version', 'short_title',
                              'subject', 'source_reference', 'source_project_title',)

  security.declareProtected(Permissions.View, 'index_html')
  def index_html(self, REQUEST, RESPONSE, display=None, format='', quality=75, resolution=None):
    """
      Returns data in the appropriate format (graphical)
      it is always a zip because multi-page pdfs are converted into a zip
      file of many images
    """
    if format is None:
      RESPONSE.setHeader('Content-Type', 'application/pdf')
      return _unpackData(self.data)
    if format in ('html', 'txt', 'text'):
      mime, data = self.convert(format)
      RESPONSE.setHeader('Content-Length', len(data))
      RESPONSE.setHeader('Content-Type', '%s;charset=UTF-8' % mime)
      RESPONSE.setHeader('Accept-Ranges', 'bytes')
      return data
    return Image.index_html(self, REQUEST, RESPONSE, display=display,
                            format=format, quality=quality, resolution=resolution)

  # Conversion API
  security.declareProtected(Permissions.ModifyPortalContent, 'convert')
  def convert(self, format, **kw):
    """
    Implementation of conversion for PDF files
    """
    if format == 'html':
      if not self.hasConversion(format=format):
        data = self._convertToHTML()
        self.setConversion(data, mime='text/html', format=format)
      return self.getConversion(format=format)
    elif format in ('txt', 'text'):
      if not self.hasConversion(format='txt'):
        data = self._convertToText()
        self.setConversion(data, mime='text/plain', format='txt')
      return self.getConversion(format='txt')
    else:
      return Image.convert(self, format, **kw)

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
    tmp = tempfile.NamedTemporaryFile()
    tmp.write(_unpackData(self.data))
    tmp.seek(0)
    cmd = 'pdftotext -layout -enc UTF-8 -nopgbrk %s -' % tmp.name
    r = os.popen(cmd)
    h = r.read()
    tmp.close()
    r.close()
    return h

  security.declarePrivate('_convertToHTML')
  def _convertToHTML(self):
    """
    Convert the PDF text content to HTML with pdftohtml

    NOTE: XXX check that command exists and was executed
    successfully
    """
    tmp = tempfile.NamedTemporaryFile()
    tmp.write(_unpackData(self.data))
    tmp.seek(0)
    cmd = 'pdftohtml -enc UTF-8 -stdout -noframes -i %s' % tmp.name
    r = os.popen(cmd)
    h = r.read()
    tmp.close()
    r.close()
    h = h.replace('<BODY bgcolor="#A0A0A0"', '<BODY ') # Quick hack to remove bg color - XXX
    return h

  security.declareProtected(Permissions.AccessContentsInformation, 'getContentInformation')
  def getContentInformation(self):
    """
    Returns the information about the PDF document with
    pdfinfo.

    NOTE: XXX check that command exists and was executed
    successfully
    """
    tmp = tempfile.NamedTemporaryFile()
    tmp.write(_unpackData(self.data))
    tmp.seek(0)
    cmd = 'pdfinfo -meta -box %s' % tmp.name
    r = os.popen(cmd)
    h = r.read()
    tmp.close()
    r.close()
    result = {}
    for line in h.splitlines():
      item_list = line.split(':')
      key = item_list[0].strip()
      value = ':'.join(item_list[1:]).strip()
      result[key] = value
    return result
