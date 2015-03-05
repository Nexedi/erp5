import unittest
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.Utils import convertToUpperCase, convertToMixedCase

class TestERP5WorkflowMixin(ERP5TypeTestCase):
  def getBusinessTemplateList(self):
    """Returns list of BT to be installed."""
    return ('erp5_workflow',)

  def getTestObject(self):
    self.portal = self.getPortal()
    type_test_object = self.portal.portal_types._getOb('ERP5Workflow Test Object')
    test_object = self.portal.erp5workflow_test_module.newContent(portal_type='ERP5Workflow Test Object', id='erp5_test_object')
    return test_object

  def doActionFor():
    """
    Needs to be overidden
    """
    raise NotImplemented

  def test_01_testAfterScript(self):
    new_object = self.getTestObject()
    self.doActionFor(new_object, "validate")
    self.assertEqual(new_object.getDescription(), "After script was executed.")
    #self.assertEqual(new_object.getValidationState(), "validated")

  def test_02_testBeforeScript(self):
    new_object = self.getTestObject()
    self.doActionFor(new_object, "validate")
    self.doActionFor(new_object, "invalidate")
    #new_object.invalidate()
    self.assertEqual(new_object.getDescription(), "Before script was executed.")
    #self.assertEqual(new_object.getValidationState(), "invalidated")

  def checkPermissionAreWellSet(self):
    pass

  # what should be test?
  def test_03_testChangeOfState(self):
    pass

  # Doesn't exist yet
  def _testUserAction(self):
    organisation = self.getOrganisation()
    self.doActionFor(organisation, "validate_action")
    self.assertEqual(organisation.getDescription(), "before script has been called")

  def checkRaiseValidationFailed(self):
    pass

  def _testSimpleWorklist(self):
    pass

  def _testWorklistWithAnAssignee(self):
    pass

class TestERP5Workflow(TestERP5WorkflowMixin):
  """
    Tests ERP5 Workflow.
  """
  def afterSetUp(self):
    self.portal = self.getPortal()
    self.workflow_module = self.portal.workflow_module
    self.wf = self.workflow_module._getOb('erp5_validation_workflow')
    type_test_object = self.portal.portal_types._getOb('ERP5Workflow Test Object')
    type_test_object.edit(type_base_category_list=('validation_state',))
    type_test_object.edit(type_erp5workflow_list=('erp5_validation_workflow',))
    self.login() # as Manager

  def doActionFor(self, document, action):
    #self.wf._getOb(action).execute(document)
    getattr(document, convertToMixedCase(action))()

class TestDCWorkflow(TestERP5WorkflowMixin):
  """
    Check DC Workflow
  """
  def afterSetUp(self):
    # make sure erp5 workflow list is empty
    self.portal = self.getPortal()
    self.workflow_module = self.portal.portal_workflow
    self.wf = self.workflow_module._getOb('dc_test_workflow')
    self.login()

  def doActionFor(self, document, action):
    #self.wf.DCWorkflowDefinition_executeTransition(document, )
    user_action = action + '_action'
    self.portal.portal_workflow.doActionFor(document, user_action, wf_id =self.wf.getId())


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5Workflow))
  suite.addTest(unittest.makeSuite(TestDCWorkflow))
  return suite
