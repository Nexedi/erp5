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
from Globals import InitializeClass
from Products.ERP5Type import Permissions
from Products.ERP5Type.Base import Base
from DocumentationHelper import DocumentationHelper, TempObjectLibrary
from DocumentationSection import DocumentationSection
from PortalTypeInstanceDocumentationHelper import PortalTypeInstanceDocumentationHelper

def getPortalType(uri=''):
  """
  Extract portal type from uri to create a temporary object oh that portal_type
  uri must be at the form:
  portal_classes/temp_instance/Person -> a temporary instance "Person"
  portal_classes/temp_instance/Person/submit -> the worfklow method "submit" of a temporary instance "Person"
  """
  portal_type = ''
  uri_list = uri.split('/')
  if len(uri_list) >= 3:
    portal_type = uri_list[3]
  return portal_type

class PortalTypeDocumentationHelper(DocumentationHelper):
  """
    Provides access to all documentation information
    of a portal type. Accessors and methods are documented
    by generating a temporary instance which provides
    an access to the property holder and allows
    reusing PortalTypeInstanceDocumentationHelper
  """

  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  _section_list = (
    dict(
      id='action',
      title='Actions',
      class_name='PortalTypeActionDocumentationHelper',
    ),
    dict(
      id='role',
      title='Role Definitions',
      class_name='PortalTypeRoleDocumentationHelper',
    ),
    dict(
      id='allowed_content_type',
      title='Allowed Content Type',
      class_name='PortalTypeDocumentationHelper',
    ),
    dict(
      id='hidden_content_type',
      title='Hidden Content Type',
      class_name='PortalTypeDocumentationHelper',
    ),
    dict(
      id='property_sheet',
      title='Property Sheet',
      class_name='PortalTypePropertySheetDocumentationHelper',
    ),
    dict(
      id='workflow_method',
      title='Workflow Method',
      class_name='WorkflowMethodDocumentationHelper',
    ),
    dict(
      id='accessor_method',
      title='Accessor',
      class_name='AccessorMethodDocumentationHelper',
    ),
    dict(
      id='class_method',
      title='Class Methods',
      class_name='ClassMethodDocumentationHelper',
    ),
  )

  security.declareProtected(Permissions.AccessContentsInformation, 'getType')
  def getType(self):
    """
    Returns the type of the documentation helper
    """
    return "Portal Type"

  security.declareProtected(Permissions.AccessContentsInformation, 'getTitle')
  def getTitle(self):
    """
    Returns the title of the documentation helper
    """
    return DocumentationHelper.getTitle(self) or self.getId()

  security.declareProtected(Permissions.AccessContentsInformation, 'getClass')
  def getClass(self):
    """
    Returns the Class of the documentation helper
    """
    portal_type = getPortalType(self.uri)
    klass = self.getTempInstance(portal_type).__class__.__bases__[0]
    return str(klass).split("'")[1]

  security.declareProtected(Permissions.AccessContentsInformation, 'getAllowedContentTypeList')
  def getAllowedContentTypeList(self):
    """
    Returns the list of allowed content type of the documentation helper
    """
    return getattr(self.getDocumentedObject(), "allowed_content_types")

  security.declareProtected(Permissions.AccessContentsInformation, 'getAllowedContentTypeUriList')
  def getAllowedContentTypeUriList(self):
    """
    Returns the uri's list of allowed content type of the documentation helper
    """
    allowed_content_type_list = self.getAllowedContentTypeList()
    return map(lambda x: ('%s/%s' % (self.uri, x)), allowed_content_type_list)

  security.declareProtected(Permissions.AccessContentsInformation, 'getHiddenContentTypeList')
  def getHiddenContentTypeList(self):
    """
    Returns the list of hidden content type of the documentation helper
    """
    return getattr(self.getDocumentedObject(), "hidden_content_type_list")

  security.declareProtected(Permissions.AccessContentsInformation, 'getHiddenContentTypeUriList')
  def getHiddenContentTypeUriList(self):
    """
    Returns the uri's list of hidden content type of the documentation helper
    """
    hidden_content_type_list = self.getHiddenContentTypeList()
    return map(lambda x: ('%s/%s' % (self.uri, x)), hidden_content_type_list)

  security.declareProtected(Permissions.AccessContentsInformation, 'getBaseCategoryList')
  def getBaseCategoryList(self):
    """
    Returns the list of base category of the documentation helper
    """
    return getattr(self.getDocumentedObject(), "base_category_list")

  security.declareProtected(Permissions.AccessContentsInformation, 'getAcquireLocalRoles')
  def getAcquireLocalRoles(self):
    """
    Returns the list of allowed content type for the documentation helper
    """
    local_roles = getattr(self.getDocumentedObject(), "acquire_local_roles")
    if local_roles:
      return 'Yes'
    else:
      return 'No'

  security.declareProtected(Permissions.AccessContentsInformation, 'getPropertySheetList')
  def getPropertySheetList(self):
    """
    Returns the list of property sheets for the documentation helper
    """
    temp_object = self.getTempInstance(self.getId())
    property_sheet = [obj.__name__ for obj in temp_object.property_sheets]
    property_sheet += self.getDocumentedObject().property_sheet_list
    return property_sheet

  security.declareProtected(Permissions.AccessContentsInformation, 'getPropertySheetUriList')
  def getPropertySheetUriList(self):
    """
    Returns the uri's list of property sheets for the documentation helper
    """
    property_sheet_list = self.getPropertySheetList()
    return map(lambda x: ('%s/%s.py' % (self.uri, x)), property_sheet_list)

  security.declareProtected(Permissions.AccessContentsInformation, 'getGroupList')
  def getGroupList(self):
    """
    Returns the list of groups for the documentation helper
    """
    return getattr(self.getDocumentedObject(), "group_list")

  security.declareProtected(Permissions.AccessContentsInformation, 'getActionIdList')
  def getActionIdList(self):
    """
    """
    action_list = []
    actions = getattr(self.getDocumentedObject(), "_actions")
    for action in actions:
      action_list.append(action.getId())
    return action_list

  security.declareProtected(Permissions.AccessContentsInformation, 'getActionItemList')
  def getActionItemList(self):
    """
    """
    action_list = []
    TITLE =['No', 'Yes']
    for action in  self.getDocumentedObject()._actions:
      permission = ', '.join(x for x in action.permissions)
      visible = TITLE[action.visible]
      category = action.category
      action_list.append((action.getId(), action.title, action.Description(), permission, visible, category))
    return action_list

  security.declareProtected(Permissions.AccessContentsInformation, 'getActionUriList')
  def getActionUriList(self):
    """
    """
    action_id_list = self.getActionIdList()
    return map(lambda x: ('%s?_actions#%s' % (self.uri, x)), action_id_list)

  security.declareProtected(Permissions.AccessContentsInformation, 'getRoleIdList')
  def getRoleIdList(self):
    """
    """
    role_list = []
    roles = getattr(self.getDocumentedObject(), "_roles")
    for role in roles:
      role_list.append(role.Title())
    return role_list

  security.declareProtected(Permissions.AccessContentsInformation, 'getRoleItemList')
  def getRoleItemList(self):
    """
    """
    role_list = []
    for role in  self.getDocumentedObject()._roles:
      role_list.append((role.__name__, role.Title(), role.Description()))
    return role_list

  security.declareProtected(Permissions.AccessContentsInformation, 'getRoleURIList')
  def getRoleURIList(self):
    """
    """
    role_item_list = self.getRoleItemList()
    klass = self.getDocumentedObject().__class__
    class_name = klass.__name__
    module = klass.__module__
    uri_prefix = '%s.%s.' % (module, class_name)
    return map(lambda x: ('%s%s' % (uri_prefix, x[0]), x[1], x[2]), role_item_list)

  security.declareProtected(Permissions.AccessContentsInformation, 'getRoleUriList')
  def getRoleUriList(self):
    """
    """
    role_id_list = self.getRoleIdList()
    return map(lambda x: ('%s?_roles#%s' % (self.uri, x)), role_id_list)

  def _getPropertyHolder(self):
    portal_type = getPortalType(self.uri)
    temp_object = self.getTempInstance(portal_type)
    dir_temp = dir(temp_object)
    return Base.aq_portal_type[(portal_type, temp_object.__class__)]

  security.declareProtected(Permissions.AccessContentsInformation, 'getWorkflowMethodIdList')
  def getWorkflowMethodIdList(self):
    """
    """
    return self._getPropertyHolder().getWorkflowMethodIdList()

  security.declareProtected(Permissions.AccessContentsInformation, 'getWorkflowMethodUriList')
  def getWorkflowMethodUriList(self):
    """
    Returns a list of URIs to workflow  methods
    """
    method_id_list = self.getWorkflowMethodIdList()
    portal_type = getPortalType(self.uri)
    klass = self.getTempInstance(portal_type).__class__
    class_name = klass.__name__
    module = klass.__module__
    uri_prefix = 'portal_classes/temp_instance/%s' % self.uri.split('/')[-1]
    return map(lambda x: '%s#%s' % (uri_prefix, x), method_id_list)


  security.declareProtected(Permissions.AccessContentsInformation, 'getClassMethodIdList')
  def getClassMethodIdList(self, **kw):
    """
    Return a list of tuple (id, method) for every class method
    """
    portal_type = getPortalType(self.uri)
    klass = self.getTempInstance(portal_type).__class__.__bases__[0]
    return self._getPropertyHolder().getClassMethodIdList(klass, **kw)

  security.declareProtected(Permissions.AccessContentsInformation, 'getClassMethodUriList')
  def getClassMethodUriList(self, inherited=0, **kw):
    """
    Returns a list of URIs to class methods
    """
    method_id_list = self.getClassMethodIdList(inherited=inherited, **kw)
    portal_type = getPortalType(self.uri)
    klass = self.getTempInstance(portal_type).__class__.__bases__[0]
    class_name = klass.__name__
    module = klass.__module__
    uri_prefix = '%s.%s.' % (module, class_name)
    return map(lambda x: '%s%s' % (uri_prefix, x), method_id_list)

  security.declareProtected(Permissions.AccessContentsInformation, 'getAccessorMethodIdList')
  def getAccessorMethodIdList(self):
    """
    """
    return self._getPropertyHolder().getAccessorMethodIdList()

  security.declareProtected(Permissions.AccessContentsInformation, 'getAccessorMethodUriList')
  def getAccessorMethodUriList(self):
    """
    Returns a list of URIs to accessor methods
    """
    method_id_list = self.getAccessorMethodIdList()
    portal_type = getPortalType(self.uri)
    klass = self.getTempInstance(portal_type).__class__.__bases__[0]
    class_name = klass.__name__
    module = klass.__module__
    uri_prefix = self.uri
    return map(lambda x: '%s#%s' % (uri_prefix, x), method_id_list)

InitializeClass(PortalTypeDocumentationHelper)
