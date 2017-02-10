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
    state1 = workflow.newContent(portal_type='State',
                             title='State 1')
    state2 = workflow.newContent(portal_type='State',
                             title='State 2')
    state1.setReference('state1')
    state2.setReference('state2')
    transition1 = workflow.newContent(portal_type='Transition',
                             title='Transition 1')
    transition1.setReference('transition1')
    state1.setDestinationValue(transition1)
    transition1.setDestinationValue(state2)
    # set initial state
    workflow.setSourceValue(state1)
    # create a document and associate it to this workflow
    self.getPortalObject().portal_types._getOb('Folder')\
      .edit(type_workflow_list=('wf'))
    doc = self.portal.newContent(portal_type='Folder', id='test_doc')
    self.assertEqual('state1', workflow._getWorkflowStateOf(doc, id_only=1))

    # pass a transition
    workflow._executeTransition(doc, transition1)
    self.assertEqual('state2', workflow._getWorkflowStateOf(doc, id_only=1))


  def test_getAvailableTransitionList(self):
    workflow = self.workflow_module.newContent(portal_type='Workflow')
    workflow.setReference('wf')
    workflow.setStateVariable('current_state')
    state1 = workflow.newContent(portal_type='State',
                             title='State 1')
    state1.setReference('state1')
    workflow.setSourceValue(state1)
    transition1 = workflow.newContent(portal_type='Transition',
                             title='Transition 1')
    transition1.setReference('transition1')
    transition2 = workflow.newContent(portal_type='Transition',
                             title='Transition 2',
                             guard_expression='python: False')
    transition2.setReference('transition2')
    state1.setDestinationValueList([transition1, transition2])

    self.getPortalObject().portal_types._getOb('Folder')\
      .edit(type_workflow_list=('wf'))
    doc = self.portal.newContent(portal_type='Folder', id='test_doc')
    self.assertEqual([transition1, transition2], state1.getDestinationValueList())


  def test_WorkflowVariables(self):
    workflow = self.workflow_module.newContent(
                                portal_type='Workflow')
    workflow.setReference('wf')
    workflow.setStateVariable('current_state')
    state1 = workflow.newContent(portal_type='State',
                             title='State 1')
    state1.setReference('state1')
    workflow.setSourceValue(state1)
    transition1 = workflow.newContent(portal_type='Transition',
                             title='Transition 1',
                             destination_value=state1)
    transition1.setReference('transition1')
    state1.setDestinationValue(transition1)

    variable1 = workflow.newContent(portal_type='Workflow Variable',
                             title='actor')
    variable1.setReference('actor')
    variable1.setVariableExpression('user/getUserName')
    self.getPortalObject().portal_types._getOb('Folder')\
      .edit(type_workflow_list=('wf'))
    doc = self.portal.newContent(portal_type='Folder', id='test_doc')
    workflow._executeTransition(doc,transition1)
    current_state = workflow.getCurrentStatusDict(doc)
    self.assertTrue(isinstance(current_state, dict))
    self.assertEqual(state1.getReference(), current_state.get('current_state'))
    self.assertEqual('ERP5TypeTestCase', current_state.get('actor'))

    history = doc.workflow_history['wf']
    self.assertEqual(len(history), 2)# create, transition1


  def test_afterScript(self):
    workflow = self.workflow_module.newContent(
      portal_type='Workflow',
      state_base_category='current_state'
    )
    workflow.setReference('wf')
    state1 = workflow.newContent(portal_type='State',
                             title='State 1')
    state2 = workflow.newContent(portal_type='State',
                             title='State 2')
    state1.setReference('state1')
    state2.setReference('state2')
    transition1 = workflow.newContent(portal_type='Transition',
                                      title='Transition 1')
    transition1.setReference('transition1')
    state1.setDestinationValue(transition1)
    transition1.setDestinationValue(state2)
    workflow.setSourceValue(state1)
    script = workflow.newContent(portal_type='Workflow Script',
                                 id='Document_testAfterScript')
    script.setParameterSignature("state_change")
    script.setParameterSignature("state_change")
    script.setBody("state_change['object'].setDescription('After script was " +
                   "executed.')")
    transition1.setCategoryList(transition1.getCategoryList() +
                       ['after_script/' + script.getRelativeUrl()])

    self.getPortalObject().portal_types._getOb('Folder')\
      .edit(type_workflow_list=('wf'))
    doc = self.portal.newContent(portal_type='Folder', id='test_doc')

    workflow._executeTransition(doc, transition1)
    self.assertEqual('After script was executed.', doc.getDescription())
    # FIXME: not passing parameter to an after script is probably too
    # restrictive

  def test_beforeScript(self):
    workflow = self.workflow_module.newContent(portal_type='Workflow')
    workflow.setReference('wf')
    workflow.setStateVariable('current_state')
    state1 = workflow.newContent(portal_type='State', title='State 1')
    state2 = workflow.newContent(portal_type='State', title='State 2')
    state1.setReference('state1')
    state2.setReference('state2')
    transition1 = workflow.newContent(portal_type='Transition', title='Transition 1')
    transition1.setReference('transition1')
    state1.setDestinationValue(transition1)
    transition1.setDestinationValue(state2)
    workflow.setSourceValue(state1)
    script = workflow.newContent(portal_type='Workflow Script',
                                 id='Document_testBeforeScript')
    script.setParameterSignature("state_change")
    script.setBody("state_change['object'].setDescription('Before script was " +
                   "executed.')")
    transition1.setCategoryList(transition1.getCategoryList() +
                       ['before_script/' + script.getRelativeUrl()])
    self.getPortalObject().portal_types._getOb('Folder')\
      .edit(type_workflow_list=('wf'))
    doc = self.portal.newContent(portal_type='Folder', id='test_doc')

    workflow._executeTransition(doc, transition1)
    self.assertEqual('Before script was executed.', doc.getDescription())
    # FIXME: not passing parameter to an before script is probably too
    # restrictive

  def test_TransitionGuards(self, transition_type='Transition'):
    workflow_type = 'Workflow' if transition_type == 'Transition' else \
                    'Interaction Workflow'
    workflow = self.workflow_module.newContent(portal_type=workflow_type)
    transition = workflow.newContent(portal_type=transition_type)
    # roles
    transition.setGuardRoleList([])
    self.assertEqual(transition.guard_role, ())
    transition.setGuardRoleList(['Assignor', 'Assignee'])
    self.assertEqual(('Assignor', 'Assignee'), transition.guard_role)
    # permissions
    transition.setGuardPermissionList([])
    self.assertEqual(transition.guard_permission, ())
    transition.setGuardPermissionList(['Modify portal content'])
    self.assertEqual(('Modify portal content',), transition.guard_permission)
    # groups
    transition.setGuardGroupList([])
    self.assertEqual(transition.guard_group, ())
    transition.setGuardGroupList(['Group1', 'Group2'])
    self.assertEqual(transition.guard_group, ('Group1', 'Group2'))
    # expression
    transition.setGuardExpression('python: "Hello, world"')
    self.assertEqual(transition.guard_expression.text, 'python: "Hello, world"')

  def test_InteractionGuards(self):
    self.test_TransitionGuards(transition_type='Interaction')

  def test_Base_viewDict(self):
    """
    verify that Base_viewDict view can be accessed
    """
    workflow = self.workflow_module.newContent(portal_type='Workflow')
    state = workflow.newContent(portal_type='State', title='Some State')
    transition = workflow.newContent(portal_type='Transition',
                                     title='Some Transition')
    transition.setReference('change_something')
    transition.setGuardRoleList(['Assignee', 'Assignor'])
    transition.setCategoryList('destination/' + transition.getPath())
    transition.Base_viewDict()

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
    self.assertRaises(Unauthorized, workflow_module.view)
    self.assertRaises(Unauthorized, createWorkflowInstance)
    self.assertRaises(Unauthorized, lambda: workflow_instance.view())

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5Workflow))
  return suite
