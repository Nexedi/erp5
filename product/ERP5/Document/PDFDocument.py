
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

from AccessControl import ClassSecurityInfo
from Products.CMFCore.WorkflowCore import WorkflowMethod
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.Cache import CachingMethod
from Products.ERP5.Document.Image import Image
from Products.ERP5.Document.File import File, stripHtml
from Products.ERP5.Document.Document import ConversionCacheMixin
from zLOG import LOG

import tempfile, os, glob, zipfile, cStringIO, re


class PDFDocument(File, ConversionCacheMixin):
  """
  PdfDocument - same as file, but has its own getSearchableText method
  (converts via pdftotext)
  in effect it has two separate caches - from CachingMixin for txt and html
  and for image formats from Image
  """
  # CMF Type Definition
  meta_type = 'ERP5 PDF'
  portal_type = 'PDF'
  isPortalContent = 1
  isRADContent = 1

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Default Properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Version
                    , PropertySheet.Reference
                    , PropertySheet.Document
                    , PropertySheet.Data
                    )


  def index_html(self, REQUEST, RESPONSE, format, force=0):
    """
      Returns data in the appropriate format
    """
    mime = 'image/'+format.lower()
    if force or not self.hasConversion(format = format):
      self.setConversion(self._makeFile(format), 'application/zip', format=format)
    RESPONSE.setHeader('Content-Type', 'application/zip')
    return self.getConversion(format = format)

  def _makeFile(self,format):
    tempfile.tempdir = os.path.join(os.getenv('INSTANCE_HOME'), 'tmp')
    os.putenv('TMPDIR', '/tmp') # because if we run zope as root, we have /root/tmp here and convert goes crazy
    if not os.path.exists(tempfile.tempdir):
      os.mkdir(tempfile.tempdir, 0775)
    fr = tempfile.mktemp(suffix='.pdf')
    to = tempfile.mktemp(suffix = '.' + format)
    file_fr = open(fr, 'w')
    file_fr.write(self._unpackData(self.data))
    file_fr.close()
    cmd = 'convert %s %s' % (fr, to)
    os.system(cmd)
    # pack it
    f = cStringIO.StringIO()
    z = zipfile.ZipFile(f, 'a')
    for fname in glob.glob(to.replace('.', '*')):
      base = os.path.basename(fname)
      pg = re.match('.*(\d+)\.'+format, base).groups()
      if pg:
        pg = pg[0]
        arcname = '%s/page-%s.%s' % (format, pg, format)
      else:
        arcname = base
      z.write(fname, arcname)
    z.close()
    f.seek(0)
    return f.read()

  searchable_property_list = File.searchable_property_list + ('text_content',)

  ### Content indexing methods
  security.declareProtected(Permissions.View, 'getSearchableText')
  def getSearchableText(self, md=None, force=0):
    """
    Used by the catalog for basic full text indexing
    we get text content by using pdftotext
    but we have to do it only once after uplad
    for simplicity we check only modification_date, which means we rebuild txt and html after every edit
    but that shouldn't hurt too much
    """
    if hasattr(self, 'data') and (force == 1 or not self.hasConversion(format = 'txt') or self.getTextContent() is None):
      # XXX-JPS accessing attribute data is bad
      self.log('PdfDocument', 'regenerating txt')
      tmp = tempfile.NamedTemporaryFile()
      tmp.write(self._unpackData(self.data))
      tmp.seek(0)
      cmd = 'pdftotext -layout -enc UTF-8 -nopgbrk %s -' % tmp.name
      r = os.popen(cmd)
      self.setTextContent(r.read().replace('\n', ' '))
      tmp.close()
      r.close()
      self.setConversion('empty', format = 'txt') # we don't need to store it twice, just mark we have it
    return File.getSearchableText(self, md)

  SearchableText=getSearchableText

  security.declareProtected(Permissions.View, 'getHtmlRepresentation')
  def getHtmlRepresentation(self, force=0):
    '''
    get simplified html version to display
    '''
    if not hasattr(self, 'data'):
      return 'no data'
    if force==1 or not self.hasConversion(format = 'html'):
      self.log('PDF', 'regenerating html')
      tmp = tempfile.NamedTemporaryFile()
      tmp.write(self._unpackData(self.data))
      tmp.seek(0)
      cmd = 'pdftohtml -enc UTF-8 -stdout -noframes -i %s' % tmp.name
      r = os.popen(cmd)
      h = r.read()
      tmp.close()
      r.close()
      h = stripHtml(h)
      self.setConversion(h, format = 'html')
      self.updateConversion(format = 'html')
    return self.getConversion(format = 'html')[1]

# vim: syntax=python shiftwidth=2 

