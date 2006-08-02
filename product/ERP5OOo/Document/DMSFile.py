
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
from Products.ERP5.Document.File import File
from Products.ERP5Type.XMLObject import XMLObject
# to overwrite WebDAV methods
from Products.CMFDefault.File import File as CMFFile

class DMSFile(XMLObject,File):
  """
  Special base class, different from File only in that it can contain things 
  (like Role Definition, for example)
  Could (perhaps should) be a parent class for OOoDocument
  Should probably be located somewhere else
  """
  # CMF Type Definition
  meta_type = 'ERP5 DMS File'
  portal_type = 'DMS File'
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
                    )


  # make sure to call the right edit methods
  _edit=File._edit
  edit=File.edit

  ### Content indexing methods
  security.declareProtected(Permissions.View, 'getSearchableText')
  def getSearchableText(self, md=None):
    """\
    Used by the catalog for basic full text indexing
    And so we end up with a strange hybrid of File and Document
    This is the same as in OOoDocument except that no text_content here
    Some people call it 'copy-and-paste programming'
    """
    searchable_attrs=('title','description','id','reference','version',
        'short_title','keywords','subject','original_filename','source_project_title')
    searchable_text = ' '.join(map(lambda x: self.getProperty(x) or ' ',searchable_attrs))
    return searchable_text

  SearchableText=getSearchableText


  # BG copied from File in case
  index_html = CMFFile.index_html
  PUT = CMFFile.PUT
  security.declareProtected('FTP access', 'manage_FTPget', 'manage_FTPstat', 'manage_FTPlist')
  manage_FTPget = CMFFile.manage_FTPget
  manage_FTPlist = CMFFile.manage_FTPlist
  manage_FTPstat = CMFFile.manage_FTPstat


# vim: syntax=python shiftwidth=2 

