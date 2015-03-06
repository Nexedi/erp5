import unittest
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.Utils import convertToUpperCase, convertToMixedCase

class TestERP5WorkflowMixin(ERP5TypeTestCase):

  def getTestObject(self):
    self.portal = self.getPortal()
    type_test_object = self.portal.portal_types._getOb('ERP5Workflow Test Object')
    test_object = self.portal.erp5workflow_test_module.newContent(portal_type='ERP5Workflow Test Object')
    return test_object

  def doActionFor():
    """
    Needs to be overidden
    """
    raise NotImplemented

  def getStateFor():
    """
    Needs to be overidden
    """
    raise NotImplemented

  def resetComponentTool(self):
    # Force reset of portal_components to regenerate accessors
    # Since it is already handled by interactions, we only need to commit
    # to allow component tool to do it's reset
    self.commit()

  def test_01_testAfterScript(self):
    new_object = self.getTestObject()
    self.doActionFor(new_object, "validate")
    self.assertEqual(new_object.getDescription(), "After script was executed.")

  def test_02_testBeforeScript(self):
    new_object = self.getTestObject()
    self.doActionFor(new_object, "validate")
    self.doActionFor(new_object, "invalidate")
    self.assertEqual(new_object.getDescription(), "Before script was executed.")

  def test_03_testChangeOfState(self):
    new_object = self.getTestObject()
    self.doActionFor(new_object, "validate")
    self.doActionFor(new_object, "invalidate")
    self.assertEqual(self.getStateFor(new_object), 'invalidated')

  def test_04_testDoWorkflowMethodTransition(self):
    new_object = self.getTestObject()
    self.assertEqual(self.getStateFor(new_object), 'draft')
    # change state through a workflow method
    getattr(new_object, 'validate')()
    self.assertEqual(self.getStateFor(new_object), 'validated')

  def test_05_testCheckHistoryForASingleTransition(self):
    new_object = self.getTestObject()
    self.doActionFor(new_object, "validate")
    #print new_object.workflow_history
    raise NotImplementedError (new_object.workflow_history)

  def test_06_testCheckPermissionAreWellSet(self):
    new_object = self.getTestObject()
    self.assertEqual(new_object._View_Permission, ('Assignee', 'Assignor', 'Associate', 'Auditor', 'Author', 'Manager', 'Owner'))
    self.doActionFor(new_object, "validate")
    self.assertEqual(new_object._View_Permission, ('Assignee', 'Assignor', 'Associate', 'Auditor', 'Manager'))

  ### Doesn't exist yet
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
    self.getWorkflowTool().setChainForPortalTypes(['ERP5Workflow Test Object'], ())
    self.workflow_module = self.portal.workflow_module
    self.wf = self.workflow_module._getOb('erp5_validation_workflow')
    type_test_object = self.portal.portal_types._getOb('ERP5Workflow Test Object')
    type_test_object.edit(type_base_category_list=('validation_state',))
    type_test_object.edit(type_erp5workflow_list=('erp5_validation_workflow',))
    self.resetComponentTool()
    self.login() # as Manager

  def doActionFor(self, document, action):
    # check dc_test_workflow is not in use
    self.assertFalse('dc_test_workflow' in self.getWorkflowTool().getChainFor(document.getTypeInfo().getId()))
    getattr(document, convertToMixedCase(action))()

  def getStateFor(self, document):
    return getattr(document, 'getValidationState')()

class TestDCWorkflow(TestERP5WorkflowMixin):
  """
    Check DC Workflow
  """
  def afterSetUp(self):
    # make sure erp5 workflow list is empty
    self.portal = self.getPortal()
    self.workflow_module = self.portal.portal_workflow
    self.getWorkflowTool().setChainForPortalTypes(['ERP5Workflow Test Object'], ('dc_test_workflow'))
    self.wf = self.workflow_module._getOb('dc_test_workflow')
    type_test_object = self.portal.portal_types._getOb('ERP5Workflow Test Object')
    type_test_object.edit(type_base_category_list=())
    type_test_object.edit(type_erp5workflow_list=())
    self.resetComponentTool()
    self.login()

  def doActionFor(self, document, action):
    self.assertTrue(self.wf.getId() in self.getWorkflowTool().getChainFor(document.getTypeInfo().getId()))
    # check erp5workflow is not in use
    self.assertEqual(document.getTypeInfo().getTypeErp5workflowList(), [])
    user_action = action + '_action'
    self.portal.portal_workflow.doActionFor(document, user_action, wf_id = self.wf.getId())
    #getattr(document, convertToMixedCase(action))()

  def getStateFor(self, document):
    return self.wf._getWorkflowStateOf(document, id_only=True)

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5Workflow))
  suite.addTest(unittest.makeSuite(TestDCWorkflow))
  return suite