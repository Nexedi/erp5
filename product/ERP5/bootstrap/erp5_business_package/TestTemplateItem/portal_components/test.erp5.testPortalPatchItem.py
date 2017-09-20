##############################################################################
#
# Copyright (c) 2002-2017 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

import time
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

class TestPortalPatch(ERP5TypeTestCase):
  """
  Test class to test that Business Package object can export some paths
  and install them on an erp5 site

  Steps:
  - Create BusinessPackage object
  - Add path list to the object
  - Build the package and expect the items mentioned in path list gets
  exported in the build step
  - Remove the objects mentioned in path_list from the site
  - Install the package
  - Expected result should be that it installs the objects on the site
  """

  def getTitle(self):
    return "TestPortalPatch"

  def getBusinessTemplateList(self):
    """
    Tuple of Business Templates we need to install
    """
    return (
      'erp5_base',
      'erp5_core',
      'erp5_dms',
      'erp5_property_sheets',
      'erp5_business_package',
      )

  def afterSetUp(self):
    """
    This is ran before anything, used to set the environment
    """
    # here, you can create the categories and objects your test will depend on
    #self.export_dir = tempfile.mkdtmp(dir=tests_home)
    self.export_dir = ''
    self.portal = self.getPortalObject()

  def beforeTearDown(self):
    pass

  def _createBusinessManager(self, sequence=None, bm_id=None, title=None):
    if not bm_id:
      bm_id = 'manager_%s' % str(time.time())
    if not title:
      title = bm_id
    manager = self.portal.portal_templates.newContent(
                                                id=bm_id,
                                                title=title,
                                                portal_type='Business Manager')
    self.tic()
    return manager

  def test_businessPatchItemForWorkflowChain(self):
    """
    Test if we are able to use PatchItem for adding Workflow Chain ( priority
    doesn't matter )
    """
    portal = self.portal
    manager_A = self._createBusinessManager()
    manager_A.newContent(portal_type='Business Property Item',
                         item_path='portal_types/Business Manager#type_workflow_list')
    manager_A.build()

    # Change the value for object on ZODB
    obj = portal.unrestrictedTraverse('portal_types/Business Manager')
    obj.setWorkflowTypeList('type_workflow_list', ['a', 'b', 'c'])

    manager_B = self._createBusinessManager()

    # Create Business Patch Item for the same property_path as we used in
    # property_item, and use manager_A as a value in dependency_list
    manager_B.newContent(portal_type='Business Patch Item',
                         path='portal_types/Business Manager#type_workflow_list',
                         dependency_list=[manager_A,])

    # Build Business Manager
    manager_B.build()
    # After build, we expect manager_B to have 2 Business Property Item, one for
    # storing new_value(where we do update when we rebuild) and another from
    # old_value(which we take from older version of Business Manager)

    # Change the value for object on ZODB to old again
    obj.setWorkflowTypeList('type_workflow_list', ['a', 'c'])

    # Get the patch item for the given path 
    bm_item = manager_B.getBusinessItemByPath(
                    'portal_types/Business Manager#type_workflow_list',
                    patch=True)

    # Get the old and new value
    old = bm_item.getOldValue()
    new = bm_item.getNewValue()

    # Get Diff Tool
    portal_diff = portal.getDiffTool()
    # Create patch using the old and new values
    patch = portal_diff.diffPortalObject(old, new)
    # Get the patch_operation which we have for this patch
    patch_operation_list = patch.getPortalPatchOperationList()
    for operation in patch_operation_list:
      # Select the operation and apply the patch on the object
      obj.patch(operation)
