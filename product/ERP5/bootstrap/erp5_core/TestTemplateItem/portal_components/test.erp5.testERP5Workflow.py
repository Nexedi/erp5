##############################################################################
#
# Copyright (c) 2014 Nexedi SA and Contributors. All Rights Reserved.
#                     Wenjie ZHENG <wenjie.zheng@tiolive.com>
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

import unittest
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

class TestERP5Workflow(ERP5TypeTestCase):
  """
    Tests ERP5 Workflow.
  """
  def getBusinessTemplateList(self):
    """Returns list of BT to be installed."""
    return ('erp5_workflow',)

  def afterSetUp(self):
    self.portal = self.getPortal()
    self.workflow_module = self.portal.workflow_module
    self.login() # as Manager

  def test_SimpleWorkflow(self):
    """Default test."""
    # Create a workflow
    workflow = self.workflow_module.newContent(portal_type='Workflow')
    s1 = workflow.newContent(portal_type='State',title='State 1')
    s2 = workflow.newContent(portal_type='State',title='State 2')
    t1 = workflow.newContent(portal_type='Transition',title='Transition 1')
    s1.setDestinationValue(t1)
    t1.setDestinationValue(s2)

    # set initial state
    workflow.setSourceValue(s1)

    # set state variable
    workflow.setStateBaseCategory('validation_state')

    # Create a document connected to the workflow
    doc = self.portal.newContent(portal_type='Folder', id='test_doc')
    workflow.initializeDocument(doc)
    self.assertEqual(s1.getRelativeUrl(),
              doc._getDefaultAcquiredCategoryMembership('validation_state'))

  def test_Erp5Workflow(self):
    """Tests the connection between ERP5Workflow and Objects."""
    # Create a base category as the intermidiate
    self.portal.portal_categories.newContent('category_state')

    # Create a workflow
    new_workflow = self.workflow_module.newContent(portal_type='Workflow',
                                                   id='new_workflow')
    s1 = new_workflow.newContent(portal_type='State',title='State 1')
    s2 = new_workflow.newContent(portal_type='State',title='State 2')
    t1 = new_workflow.newContent(portal_type='Transition',title='Transition 1')
    s1.setDestinationValue(t1)
    t1.setDestinationValue(s2)

    # set initial state
    new_workflow.setSourceValue(s1)

    # state variable
    new_workflow.setStateBaseCategory('category_state')

    # create a portal type
    type_object = self.portal.portal_types.newContent(
      portal_type='Base Type',
      id='Object Type',
      type_class='XMLObject',
      type_base_category_list=('category_state')
      )

    type_object.setErp5WorkflowValue(new_workflow)

    self.assertEqual(type_object.getBaseCategoryList(), ['erp5_workflow'])
    self.assertEqual(type_object.getErp5Workflow(), 'workflow_module/new_workflow')
    self.assertEqual(len(type_object.getErp5WorkflowValueList()), 1)

    # create a module
    self.portal.portal_types.newContent(
      'Module Type', 'Base Type',
      type_class='Folder',
      type_filter_content_type=1,
      type_allowed_content_type_list=('Object Type',))

    self.portal.newContent(portal_type='Module Type', id='new_module')

    # create an object based on new-created portal type in the module
    new_object = self.portal.new_module.newContent(portal_type='Object Type',
                                                    id='new_object')
    self.assertTrue(new_object is not None)
    self.assertEqual(new_object.getPortalType(), "Object Type")
    self.assertEqual(new_object.getPortalType(), 'Object Type')
    self.assertEqual(new_object.getCategoryStateTitle(), 'State 1')

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5Workflow))
  return suite