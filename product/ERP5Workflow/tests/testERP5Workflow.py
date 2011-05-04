##############################################################################
#
# Copyright (c) 2007 Nexedi SA and Contributors. All Rights Reserved.
#                     Jerome Perrin <jerome@nexedi.com>
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
    self.workflow_module = self.portal.workflow_module
    self.login() # as Manager


  def test_SimpleWorkflow(self):
    workflow = self.workflow_module.newContent(
                                portal_type='Workflow')
    s1 = workflow.newContent(portal_type='State',
                             title='State 1')
    s2 = workflow.newContent(portal_type='State',
                             title='State 2')
    t1 = workflow.newContent(portal_type='Transition',
                             title='Transition 1')
    s1.setDestinationValue(t1)
    t1.setDestinationValue(s2)
    # set initial state
    workflow.setSourceValue(s1)
    # state variable
    workflow.setStateBaseCategory('current_state')
    
    # create a document and associate it to this workflow
    doc = self.portal.newContent(portal_type='Folder', id='test_doc')
    workflow.initializeDocument(doc)
    self.assertEquals(s1.getRelativeUrl(),
              doc._getDefaultAcquiredCategoryMembership('current_state'))
    
    # pass a transition
    t1.execute(doc)
    self.assertEquals(s2.getRelativeUrl(),
              doc._getDefaultAcquiredCategoryMembership('current_state'))
    

  def test_getAvailableTransitionList(self):
    workflow = self.workflow_module.newContent(
                                portal_type='Workflow',
                                state_base_category='current_state')
    s1 = workflow.newContent(portal_type='State',
                             title='State 1')
    workflow.setSourceValue(s1)
    t1 = workflow.newContent(portal_type='Transition',
                             title='Transition 1')
    t2 = workflow.newContent(portal_type='Transition',
                             title='Transition 2',
                             guard_expression='python: False')
    s1.setDestinationValueList([t1, t2])

    doc = self.portal.newContent(portal_type='Folder', id='test_doc')
    workflow.initializeDocument(doc)
    self.assertEquals([t1], s1.getAvailableTransitionList(doc))
    

  def test_WorkflowVariables(self):
    workflow = self.workflow_module.newContent(
                                portal_type='Workflow',
                                state_base_category='current_state')
    s1 = workflow.newContent(portal_type='State',
                             title='State 1')
    workflow.setSourceValue(s1)
    t1 = workflow.newContent(portal_type='Transition',
                             title='Transition 1',
                             destination_value=s1)
    s1.setDestinationValue(t1)
    
    v1 = workflow.newContent(portal_type='Variable',
                             title='actor',
                             initial_value='member/getUserName')

    doc = self.portal.newContent(portal_type='Folder', id='test_doc')
    workflow.initializeDocument(doc)
    t1.execute(doc)
    
    current_state = workflow.getCurrentStatusDict(doc)
    self.failUnless(isinstance(current_state, dict))
    self.assertEquals(s1.getRelativeUrl(), current_state.get('current_state'))
    self.assertEquals('ERP5TypeTestCase', current_state.get('actor'))
    self.assertEquals(0, current_state.get('undo'))
    
    # XXX workflow history is a method on State ?
    history = s1.getWorkflowHistory(doc)
    self.assertEquals(len(history), 2)


  def test_afterScript(self):
    workflow = self.workflow_module.newContent(
                                portal_type='Workflow',
                                state_base_category='current_state')
    s1 = workflow.newContent(portal_type='State',
                             title='State 1')
    s2 = workflow.newContent(portal_type='State',
                             title='State 2')
    t1 = workflow.newContent(portal_type='Transition',
                             title='Transition 1',
                             after_script_id='Document_testAfterScript'
                             )
    s1.setDestinationValue(t1)
    t1.setDestinationValue(s2)
    workflow.setSourceValue(s1)

    doc = self.portal.newContent(portal_type='Folder', id='test_doc')
    
    called = []
    def Document_testAfterScript(**kw):
      called.append('called %s' % kw)
    doc.Document_testAfterScript = Document_testAfterScript
    
    workflow.initializeDocument(doc)
    t1.execute(doc)
    self.assertEquals(['called {}'], called)
    # FIXME: not passing parameter to an after script is probably too
    # restrictive

  def test_BeforeScript(self):
    workflow = self.workflow_module.newContent(
                                portal_type='Workflow',
                                state_base_category='current_state')
    s1 = workflow.newContent(portal_type='State',
                             title='State 1')
    s2 = workflow.newContent(portal_type='State',
                             title='State 2')
    t1 = workflow.newContent(portal_type='Transition',
                             title='Transition 1',
                             before_script_id='Document_testBeforeScript'
                             )
    s1.setDestinationValue(t1)
    t1.setDestinationValue(s2)
    workflow.setSourceValue(s1)

    doc = self.portal.newContent(portal_type='Folder', id='test_doc')

    called = []
    def Document_testBeforeScript(**kw):
      called.append('called %s' % kw)
    doc.Document_testBeforeScript = Document_testBeforeScript

    workflow.initializeDocument(doc)
    t1.execute(doc)
    self.assertEquals(['called {}'], called)
    # FIXME: not passing parameter to an before script is probably too
    # restrictive

  def test_WorkflowSecurity(self):
    """
     Test workflow security.
    """
    workflow_module = self.portal.workflow_module

    def createWorkflowInstance():
      return workflow_module.newContent(portal_type='Workflow')
 
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

