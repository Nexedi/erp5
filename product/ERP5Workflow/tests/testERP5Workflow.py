##############################################################################
#
# Copyright (c) 2007 Nexedi SA and Contributors. All Rights Reserved.
#                    Jerome Perrin <jerome@nexedi.com>
#               2015 Wenjie ZHENG <wenjie.zheng@tiolive.com>
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
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl import Unauthorized
from AccessControl import SpecialUsers

class TestERP5Workflow(ERP5TypeTestCase):
  """
    Tests ERP5 Workflow.
  """

  def getBusinessTemplateList(self):
    """Returns list of BT to be installed."""
    return ('erp5_workflow',)

  def changeToAnonymous(self):
    """
    Change the current user to Anonymous
    """
    newSecurityManager(None, SpecialUsers.nobody)

  def afterSetUp(self):
    self.portal = self.getPortal()
    #self.portal.migrateToPortalWorkflowClass()
    self.workflow_module = self.portal.portal_workflow
    self.login() # as Manager


  def test_SimpleWorkflow(self):
    workflow = self.workflow_module.newContent(
                                portal_type='Workflow')
    workflow.setReference('wf')
    # state variable
    workflow.setStateVariable('current_state')
    s1 = workflow.newContent(portal_type='State',
                             title='State 1')
    s2 = workflow.newContent(portal_type='State',
                             title='State 2')
    s1.setReference('s1')
    s2.setReference('s2')
    t1 = workflow.newContent(portal_type='Transition',
                             title='Transition 1',
                             )
    t1.setReference('t1')
    s1.setDestinationValue(t1)
    t1.setDestinationValue(s2)
    # set initial state
    workflow.setSourceValue(s1)
    # create a document and associate it to this workflow
    self.getPortalObject().portal_types._getOb('Folder').edit(type_workflow_list=('wf'))
    doc = self.portal.newContent(portal_type='Folder', id='test_doc')
    self.assertEqual('s1', workflow._getWorkflowStateOf(doc, id_only=1))

    # pass a transition
    workflow._executeTransition(doc, t1)
    self.assertEqual('s2', workflow._getWorkflowStateOf(doc, id_only=1))


  def test_getAvailableTransitionList(self):
    workflow = self.workflow_module.newContent(
                                portal_type='Workflow')
    workflow.setReference('wf')
    workflow.setStateVariable('current_state')
    s1 = workflow.newContent(portal_type='State',
                             title='State 1')
    s1.setReference('s1')
    workflow.setSourceValue(s1)
    t1 = workflow.newContent(portal_type='Transition',
                             title='Transition 1')
    t1.setReference('t1')
    t2 = workflow.newContent(portal_type='Transition',
                             title='Transition 2',
                             guard_expression='python: False')
    t2.setReference('t2')
    s1.setDestinationValueList([t1, t2])

    self.getPortalObject().portal_types._getOb('Folder').edit(type_workflow_list=('wf'))
    doc = self.portal.newContent(portal_type='Folder', id='test_doc')
    self.assertEqual([t1, t2], s1.getDestinationValueList())


  def test_WorkflowVariables(self):
    workflow = self.workflow_module.newContent(
                                portal_type='Workflow')
    workflow.setReference('wf')
    workflow.setStateVariable('current_state')
    s1 = workflow.newContent(portal_type='State',
                             title='State 1')
    s1.setReference('s1')
    workflow.setSourceValue(s1)
    t1 = workflow.newContent(portal_type='Transition',
                             title='Transition 1',
                             destination_value=s1)
    t1.setReference('t1')
    s1.setDestinationValue(t1)

    v1 = workflow.newContent(portal_type='Variable',
                             title='actor')
    v1.setReference('actor')
    v1.default_expr = 'user/getUserName'
    self.getPortalObject().portal_types._getOb('Folder').edit(type_workflow_list=('wf'))
    doc = self.portal.newContent(portal_type='Folder', id='test_doc')
    workflow._executeTransition(doc,t1)
    current_state = workflow.getCurrentStatusDict(doc)
    self.assertTrue(isinstance(current_state, dict))
    self.assertEqual(s1.getReference(), current_state.get('current_state'))
    self.assertEqual('ERP5TypeTestCase', current_state.get('actor'))

    history = doc.workflow_history['wf']
    self.assertEqual(len(history), 2)# create, t1


  def test_afterScript(self):
    workflow = self.workflow_module.newContent(
                                portal_type='Workflow',
                                state_base_category='current_state')
    workflow.setReference('wf')
    s1 = workflow.newContent(portal_type='State',
                             title='State 1')
    s2 = workflow.newContent(portal_type='State',
                             title='State 2')
    s1.setReference('s1')
    s2.setReference('s2')
    t1 = workflow.newContent(portal_type='Transition',
                             title='Transition 1',
                             after_script_id='Document_testAfterScript',
                             )
    t1.setReference('t1')
    s1.setDestinationValue(t1)
    t1.setDestinationValue(s2)
    workflow.setSourceValue(s1)
    script = workflow.newContent(portal_type='Workflow Script', id='Document_testAfterScript')
    script.setParameterSignature("state_change")
    script.setParameterSignature("state_change")
    script.setBody("state_change['object'].setDescription('After script was executed.')")
    self.getPortalObject().portal_types._getOb('Folder').edit(type_workflow_list=('wf'))
    doc = self.portal.newContent(portal_type='Folder', id='test_doc')

    workflow._executeTransition(doc, t1)
    self.assertEqual('After script was executed.', doc.getDescription())
    # FIXME: not passing parameter to an after script is probably too
    # restrictive

  def test_BeforeScript(self):
    workflow = self.workflow_module.newContent(
                                portal_type='Workflow')
    workflow.setReference('wf')
    workflow.setStateVariable('current_state')
    s1 = workflow.newContent(portal_type='State',
                             title='State 1')
    s2 = workflow.newContent(portal_type='State',
                             title='State 2')
    s1.setReference('s1')
    s2.setReference('s2')
    t1 = workflow.newContent(portal_type='Transition',
                             title='Transition 1',
                             before_script_id='Document_testBeforeScript',
                             )
    t1.setReference('t1')
    s1.setDestinationValue(t1)
    t1.setDestinationValue(s2)
    workflow.setSourceValue(s1)
    script = workflow.newContent(portal_type='Workflow Script', id='Document_testBeforeScript')
    script.setParameterSignature("state_change")
    script.setBody("state_change['object'].setDescription('Before script was executed.')")

    self.getPortalObject().portal_types._getOb('Folder').edit(type_workflow_list=('wf'))
    doc = self.portal.newContent(portal_type='Folder', id='test_doc')

    workflow._executeTransition(doc, t1)
    self.assertEqual('Before script was executed.', doc.getDescription())
    # FIXME: not passing parameter to an before script is probably too
    # restrictive

  def test_WorkflowSecurity(self):
    """
     Test workflow security. Should be test with other methods. To be finished.
    """
    workflow_module = self.portal.portal_workflow

    def createWorkflowInstance():
      workflow = workflow_module.newContent(portal_type='Workflow')
      workflow.setReference('wf')
      return workflow

    workflow_instance = createWorkflowInstance()

    # Anonymous User must not be able to access workflow module
    # or workflow instances
    self.changeToAnonymous()
    #self.assertRaises(Unauthorized, workflow_module.view)
    #self.assertRaises(Unauthorized, createWorkflowInstance)
    #self.assertRaises(Unauthorized, lambda: workflow_instance.view())


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5Workflow))
  return suite
