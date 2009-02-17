
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
from DocumentationHelper import DocumentationHelper
from DocumentationSection import DocumentationSection
from Products.ERP5Type import Permissions

class BusinessTemplateDocumentationHelper(DocumentationHelper):
  """
    Provides access to all documentation information
    of a business template.
  """
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  _section_list = (
    dict(
      id='portal_type',
      title='Portal Types',
      class_name='PortalTypeDocumentationHelper',
    ),
    dict(
      id='dc_workflow',
      title='DC Workflows',
      class_name='DCWorkflowDocumentationHelper',
    ),
    dict(
      id='interaction_workflow',
      title='Interaction Workflows',
      class_name='InteractionWorkflowDocumentationHelper',
    ),
    dict(
      id='skin_folder',
      title='Skin Folders',
      class_name='SkinFolderDocumentationHelper',
    ),
    dict(
      id='module',
      title='Module',
      class_name='PortalTypeInstanceDocumentationHelper',
    ),
    dict(
      id='catalog_method',
      title='Catalog Method',
      class_name='CatalogMethodDocumentationHelper',
    ),
    dict(
      id='base_category',
      title='Base Category',
      class_name='BaseCategoryDocumentationHelper',
    ),
  )

  security.declareProtected(Permissions.AccessContentsInformation, 'getType')
  def getType(self):
    """
    Returns the type of the documentation helper
    """
    return "Business Template"

  security.declareProtected(Permissions.AccessContentsInformation, 'getVersion')
  def getVersion(self):
    """
    Returns the version of the business template
    """
    return getattr(self.getDocumentedObject(), 'version', '')

  security.declareProtected(Permissions.AccessContentsInformation, 'getRevisionNumber')
  def getRevisionNumber(self):
    """
    Returns the revision number of the documentation helper
    """
    return getattr(self.getDocumentedObject(), 'revision', '')

  security.declareProtected(Permissions.AccessContentsInformation, 'getBuildingState')
  def getBuildingState(self):
    """
    Returns the building_state of the documentation helper
    """
    return self.getDocumentedObject().getBuildingState()

  security.declareProtected(Permissions.AccessContentsInformation, 'getInstallationState')
  def getInstallationState(self):
    """
    Returns the installation_state of the documentation helper
    """
    return self.getDocumentedObject().getInstallationState()

  security.declareProtected(Permissions.AccessContentsInformation, 'getMaintainerList')
  def getMaintainerList(self):
    """
    Returns the list of maintainers of the business template
    """
    return  getattr(self.getDocumentedObject(), 'maintainer', '')

  security.declareProtected(Permissions.AccessContentsInformation, 'getDependencyList')
  def getDependencyList(self):
    """
    Returns the list of dependencies of the business template
    """
    return getattr(self.getDocumentedObject(), 'dependency', '')


  security.declareProtected(Permissions.AccessContentsInformation, 'getPortalTypeIdList')
  def getPortalTypeIdList(self):
    """
    """
    return getattr(self.getDocumentedObject(), 'template_portal_type_id', [])

  security.declareProtected(Permissions.AccessContentsInformation, 'getPortalTypeUriList')
  def getPortalTypeUriList(self):
    """
    """
    portal_type_list = self.getPortalTypeIdList()
    base_uri = '/'+self.uri.split('/')[1]+'/portal_types'
    return map(lambda x: ('%s/%s' % (base_uri, x)), portal_type_list)

  security.declareProtected(Permissions.AccessContentsInformation, 'getSkinFolderIdList')
  def getSkinFolderIdList(self):
    """
    """
    return getattr(self.getDocumentedObject(), 'template_skin_id', [])

  security.declareProtected(Permissions.AccessContentsInformation, 'getSkinFolderUriList')
  def getSkinFolderUriList(self):
    """
    """
    skin_folder_list = self.getSkinFolderIdList()
    base_uri = '/' + self.getPortalObject().id + '/portal_skins'
    return map(lambda x: ('%s/%s' % (base_uri, x)), skin_folder_list)

  security.declareProtected(Permissions.AccessContentsInformation, 'getDcWorkflowIdList')
  def getDcWorkflowIdList(self):
    """
    """
    dc_workflow_list = []
    template_workflow_id_list = getattr(self.getDocumentedObject(), 'template_workflow_id', [])
    for wf in template_workflow_id_list:
      url = '/' + self.getPortalObject().id + '/portal_workflow/' + wf
      wf_object = self.getPortalObject().unrestrictedTraverse(url)
      if wf_object.__class__.__name__ == 'DCWorkflowDefinition':
        dc_workflow_list.append(wf)
    return dc_workflow_list

  security.declareProtected(Permissions.AccessContentsInformation, 'getDcWorkflowUriList')
  def getDcWorkflowUriList(self):
    """
    """
    workflow_list = self.getDcWorkflowIdList()
    base_uri = '/'+self.uri.split('/')[1]+'/portal_workflow'
    return map(lambda x: ('%s/%s' % (base_uri, x)), workflow_list)

  security.declareProtected(Permissions.AccessContentsInformation, 'getInteractionWorkflowIdList')
  def getInteractionWorkflowIdList(self):
    """
    """
    workflow_list = []
    template_workflow_id_list = getattr(self.getDocumentedObject(), 'template_workflow_id', [])
    for wf in template_workflow_id_list:
      url = '/' + self.getPortalObject().id + '/portal_workflow/' + wf
      wf_object = self.getPortalObject().unrestrictedTraverse(url)
      if wf_object.__class__.__name__ == 'InteractionWorkflowDefinition':
        workflow_list.append(wf)
    return workflow_list

  security.declareProtected(Permissions.AccessContentsInformation, 'getInteractionWorkflowUriList')
  def getInteractionWorkflowUriList(self):
    """
    """
    workflow_list = self.getInteractionWorkflowIdList()
    base_uri = '/'+self.uri.split('/')[1]+'/portal_workflow'
    return map(lambda x: ('%s/%s' % (base_uri, x)), workflow_list)

  security.declareProtected(Permissions.AccessContentsInformation, 'getBaseCategoryList')
  def getBaseCategoryList(self):
    """
    """
    return getattr(self.getDocumentedObject(), 'template_base_category', '')

  security.declareProtected(Permissions.AccessContentsInformation, 'getBaseCategoryUriList')
  def getBaseCategoryUriList(self):
    """
    """
    base_category_list = self.getBaseCategoryList()
    base_uri = '/'+self.uri.split('/')[1]+'/portal_categories'
    return map(lambda x: ('%s/%s' % (base_uri, x)), base_category_list)

  security.declareProtected(Permissions.AccessContentsInformation, 'getModuleIdList')
  def getModuleIdList(self):
    """
    """
    return getattr(self.getDocumentedObject(), 'template_module_id', [])

  security.declareProtected(Permissions.AccessContentsInformation, 'getModuleUriList')
  def getModuleUriList(self):
    """
    """
    module_list = self.getModuleIdList()
    base_uri = '/'+self.uri.split('/')[1]
    return map(lambda x: ('%s/%s' % (base_uri, x)), module_list)

  security.declareProtected(Permissions.AccessContentsInformation, 'getCatalogMethodIdList')
  def getCatalogMethodIdList(self):
    """
    """
    return getattr(self.getDocumentedObject(), 'template_catalog_method_id', [])

  security.declareProtected(Permissions.AccessContentsInformation, 'getCatalogMethodUriList')
  def getCatalogMethodUriList(self):
    """
    """
    catalog_method_list = self.getCatalogMethodIdList()
    base_uri = '/'+self.uri.split('/')[1]+'/portal_catalog'
    return map(lambda x: ('%s/%s' % (base_uri, x)), catalog_method_list)

  security.declareProtected(Permissions.AccessContentsInformation, 'getTemplatePathList')
  def getTemplatePathList(self):
    """
    """
    return self.getDocumentedObject().getTemplatePathList()

InitializeClass(BusinessTemplateDocumentationHelper)
