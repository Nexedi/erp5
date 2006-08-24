
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
from Products.ERP5OOo.Document.DMSFile import DMSFile

import tempfile, os


class PdfDocument(DMSFile):
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
    but we have to do it only once
    """
    if hasattr(self,'data') and (force==1 or self.getTextContent() is None):
      tmp=tempfile.NamedTemporaryFile()
      tmp.write(self._unpackData(self.data))
      tmp.seek(0)
      cmd='pdftotext -layout -enc UTF-8 -nopgbrk %s -' % tmp.name
      r=os.popen(cmd)
      self.setTextContent(r.read().replace('\n',' '))
      tmp.close()
      r.close()
    return DMSFile.getSearchableText(self,md)

  SearchableText=getSearchableText

  def getHtmlRepresentation(self):
    '''
    get simplified html version to display
    '''
    # XXX use caching method
    if not hasattr(self,'data'):
      return 'no data'
    tmp=tempfile.NamedTemporaryFile()
    tmp.write(self._unpackData(self.data))
    tmp.seek(0)
    cmd='pdftohtml -enc UTF-8 -stdout -noframes -i %s' % tmp.name
    r=os.popen(cmd)
    h=r.read()
    tmp.close()
    r.close()
    return h

# vim: syntax=python shiftwidth=2 

