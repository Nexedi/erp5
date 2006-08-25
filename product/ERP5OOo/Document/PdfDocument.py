
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
from Products.ERP5OOo.Document.DMSFile import DMSFile, CachingMixin, stripHtml

import tempfile, os


class PdfDocument(DMSFile, CachingMixin):
  """
  PdfDocument - same as file, but has its own getSearchableText method
  (converts via pdftotext)
  """
  # CMF Type Definition
  meta_type = 'ERP5 Pdf Document'
  portal_type = 'Pdf Document'
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
                    , PropertySheet.DMSFile
                    , PropertySheet.Document
                    )

  searchable_attrs=DMSFile.searchable_attrs+('text_content',)

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
    if hasattr(self,'data') and (force==1 or self.getCacheTime('txt')<self.getModificationDate() or self.getTextContent() is None):
      self.log('PdfDocument','regenerating txt')
      tmp=tempfile.NamedTemporaryFile()
      tmp.write(self._unpackData(self.data))
      tmp.seek(0)
      cmd='pdftotext -layout -enc UTF-8 -nopgbrk %s -' % tmp.name
      r=os.popen(cmd)
      self.setTextContent(r.read().replace('\n',' '))
      tmp.close()
      r.close()
      self.cacheUpdate('txt')
    return DMSFile.getSearchableText(self,md)

  SearchableText=getSearchableText

  def getHtmlRepresentation(self, force=0):
    '''
    get simplified html version to display
    '''
    if not hasattr(self,'data'):
      return 'no data'
    if force==1 or self.getCacheTime('html')<self.getModificationDate():
      self.log('PdfDocument','regenerating html')
      tmp=tempfile.NamedTemporaryFile()
      tmp.write(self._unpackData(self.data))
      tmp.seek(0)
      cmd='pdftohtml -enc UTF-8 -stdout -noframes -i %s' % tmp.name
      r=os.popen(cmd)
      h=r.read()
      tmp.close()
      r.close()
      h=stripHtml(h)
      self.cacheSet('html',data=h)
      self.cacheUpdate('html')
    return self.cacheGet('html')[1]

# vim: syntax=python shiftwidth=2 

