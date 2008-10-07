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

from Acquisition import Implicit
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from DocumentationHelper import DocumentationHelper
from DocumentationSection import DocumentationSection
from Products.ERP5Type import Permissions

class SkinFolderDocumentationHelper(DocumentationHelper):
  """
    Provides documentation about a property sheet of a skin folder
  """
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  def __init__(self, uri):
    self.uri = uri

  security.declareProtected( Permissions.AccessContentsInformation, 'getSectionList' )
  def getSectionList(self):
    """
    Returns a list of documentation sections
    """
    section_list = []
    if self.getFileURIList(meta_type='ERP5 Form') != []:
      section_list.append(
        DocumentationSection(
          id='erp5_form',
          title='ERP5 Form',
          class_name='ERP5FormDocumentationHelper',
          uri_list=self.getFileURIList(meta_type='ERP5 Form'),
        )
      )
    if self.getFileURIList(meta_type='Z SQL Method') != []: 
      section_list.append(
        DocumentationSection(
          id='zsql_method',
          title='Z SQL Method',
          class_name='ZSQLMethodDocumentationHelper',
          uri_list=self.getFileURIList(meta_type='Z SQL Method'),
        )
      )
    if self.getFileURIList(meta_type='Page Template') != []:  
      section_list.append(
        DocumentationSection(
          id='page_template',
          title='Page Template',
          class_name='PageTemplateDocumentationHelper',
          uri_list=self.getFileURIList(meta_type='Page Template'),
        )
      )
    if self.getFileURIList(meta_type='Script (Python)') != []:
      section_list.append(
        DocumentationSection(
          id='script_python',
          title='Script (Python)',
          class_name='ScriptPythonDocumentationHelper',
          uri_list=self.getFileURIList(meta_type='Script (Python)'),
        )
      )
    return map(lambda x: x.__of__(self), section_list)

  security.declareProtected(Permissions.AccessContentsInformation, 'getType' )
  def getType(self):
    """
    Returns the type of the documentation helper
    """
    return "Skin Folder"

  security.declareProtected(Permissions.AccessContentsInformation, 'getId' )
  def getId(self):
    """
    Returns the id of the documentation helper
    """
    return getattr(self.getDocumentedObject(), "id", '')

  security.declareProtected(Permissions.AccessContentsInformation, 'getTitle' )
  def getTitle(self):
    """
    Returns the title of the documentation helper
    """
    return getattr(self.getDocumentedObject(), "title", '')

  security.declareProtected(Permissions.AccessContentsInformation, 'getMetaTypeList' )
  def getMetaTypeList(self):
    meta_type_dict = {}
    for file in self.getDocumentedObject().objectValues():
      meta_type_dict[file.meta_type] = None
    type_list = meta_type_dict.keys()
    type_list.sort()
    return type_list

  security.declareProtected(Permissions.AccessContentsInformation, 'getFileIdList' )
  def getFileIdList(self, meta_type=None):
    """
    Returns the list of sub-objects ids of the documentation helper
    """
    file_list = []
    files = self.getDocumentedObject()
    if files is not None:
      for file in files.objectValues():
        if not meta_type or file.meta_type == meta_type:
          file_list.append(file.id)
    return file_list

  security.declareProtected(Permissions.AccessContentsInformation, 'getFileItemList' )
  def getFileItemList(self, meta_type=None):
    """
    Returns the list of sub-objects items of the documentation helper
    """
    file_list = []
    files = self.getDocumentedObject()
    if files is not None:
      for file in files.objectValues():
        if not meta_type or file.meta_type == meta_type:
          file_list.append((file.id, file.title, file.meta_type))
    return file_list
  security.declareProtected( Permissions.AccessContentsInformation, 'getFileURIList' )
  def getFileURIList(self, meta_type=None):
    """
    """
    file_list = self.getFileIdList(meta_type)
    base_uri = '/%s/portal_skins/%s' % (self.getPortalObject().id, self.getDocumentedObject().id)
    return map(lambda x: ('%s/%s' % (base_uri, x)), file_list)


InitializeClass(SkinFolderDocumentationHelper)
