##############################################################################
#
# Copyright (c) 2007-2008 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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
from Acquisition import aq_base
from Products.ERP5Type.Globals import InitializeClass
from DocumentationHelper import DocumentationHelper
from Products.ERP5Type import Permissions

class SkinFolderDocumentationHelper(DocumentationHelper):
  """
    Provides documentation about a property sheet of a skin folder
  """
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  _section_list = (
    dict(
      id='erp5_form',
      title='ERP5 Form',
      class_name='ERP5FormDocumentationHelper',
    ),
    dict(
      id='zsql_method',
      title='Z SQL Method',
      class_name='ZSQLMethodDocumentationHelper',
    ),
    dict(
      id='page_template',
      title='Page Template',
      class_name='PageTemplateDocumentationHelper',
    ),
    dict(
      id='script_python',
      title='Script (Python)',
      class_name='ScriptPythonDocumentationHelper',
    ),
  )

  security.declareProtected(Permissions.AccessContentsInformation, 'getType')
  def getType(self):
    """
    Returns the type of the documentation helper
    """
    return "Skin Folder"

  security.declareProtected(Permissions.AccessContentsInformation, 'getMetaTypeList')
  def getMetaTypeList(self):
    return sorted(set(obj.meta_type
                      for obj in self.getDocumentedObject().objectValues()))

  def getFileValueList(self, meta_type=None):
    return (obj for obj in self.getDocumentedObject().objectValues()
                if meta_type in (None, obj.meta_type))

  security.declareProtected(Permissions.AccessContentsInformation, 'getFileIdList')
  def getFileIdList(self, meta_type=None):
    """
    Returns the list of sub-objects ids of the documentation helper
    """
    return [obj.id for obj in self.getFileValueList(meta_type)]

  security.declareProtected(Permissions.AccessContentsInformation, 'getFileItemList')
  def getFileItemList(self, meta_type=None):
    """
    Returns the list of sub-objects items of the documentation helper
    """
    obj_list = []
    for obj in self.getFileValueList(meta_type):
      obj = aq_base(obj)
      obj_list.append((obj.id,
                       getattr(obj, "title", ""),
                       getattr(obj, "description", ""),
                       getattr(obj, "meta_type", "")))
    return obj_list

  security.declareProtected(Permissions.AccessContentsInformation, 'getFileUriList')
  def getFileUriList(self, meta_type=None):
    """
    """
    prefix = self.uri + '/'
    return [prefix + obj.id for obj in self.getFileValueList(meta_type)]

  def getSectionUriList(self, title, **kw):
    return self.getFileUriList(title)


InitializeClass(SkinFolderDocumentationHelper)
