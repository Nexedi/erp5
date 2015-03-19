import unittest
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.Utils import convertToUpperCase, convertToMixedCase
from Products.DCWorkflow.DCWorkflow import ValidationFailed

class TestERP5WorkflowMixin(ERP5TypeTestCase):

  def getTestObject(self):
    self.portal = self.getPortal()
    test_object = self.portal.erp5workflow_test_module.newContent(portal_type='ERP5Workflow Test Document')
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
    self.assertEqual(self.getStateFor(new_object), 'validated')
    self.doActionFor(new_object, "invalidate")
    self.assertEqual(self.getStateFor(new_object), 'invalidated')

  def test_04_testDoWorkflowMethodTransition(self):
    """
    Check if workflow methods allows to change of state
    """
    new_object = self.getTestObject()
    self.assertEqual(self.getStateFor(new_object), 'draft')
    new_object.validate()
    self.assertEqual(self.getStateFor(new_object), 'validated')

  def test_05_testCheckHistoryStateAndActionForASingleTransition(self):
    """
    Basic checking of workflow history, only check that state and actions
    are available
    """
    new_object = self.getTestObject()
    self.doActionFor(new_object, "validate")
    history_list = new_object.workflow_history["testing_workflow"]
    # 3 history lines are expected : draft->validation_action->validate
    self.assertEqual(3, len(history_list))
    last_history = history_list[-1]
    self.assertEqual(last_history.get("action", None), "validate")
    self.assertEqual(last_history.get("validation_state", None), "validated")

  def test_06_testCheckPermissionAreWellSet(self):
    new_object = self.getTestObject()
    self.assertEqual(new_object._View_Permission, ('Assignee', 'Assignor',
      'Associate', 'Auditor', 'Author', 'Manager', 'Owner'))
    self.doActionFor(new_object, "validate")
    self.assertEqual(new_object._View_Permission, ('Assignee', 'Assignor',
      'Associate', 'Auditor', 'Manager'))

  def test_07_testUserTransitionRaiseValidationFailed(self):
    """
    perform a fail_action which does nothing but add an error message in the workflow history
    """
    new_object = self.getTestObject()
    exception_raised = False
    try:
      self.doActionFor(new_object, "fail")
    except ValidationFailed:
      exception_raised = True
    self.assertEqual(True, exception_raised)
    history_list = new_object.workflow_history["testing_workflow"]
    self.assertEqual(2, len(history_list))
    last_history = history_list[-1]
    self.assertEqual(last_history.get("error_message", None), "foo error")

  def test_08_testUserActionDisplay(self):
    new_object = self.getTestObject()
    object_pt = new_object.getTypeInfo()
    self.assertTrue(hasattr(object_pt, 'validate'))
    self.doActionFor(new_object, "validate")
    self.assertTrue(hasattr(object_pt, 'invalidate'))

  ### Doesn't exist yet
  def _testSimpleWorklist(self):
    pass
  def _testWorklistWithAnAssignee(self):
    pass

  def beforeTearDown(self):
    self.portal = self.getPortal()
    self.getWorkflowTool().setChainForPortalTypes(['ERP5Workflow Test Document'], ())
    self.workflow_module = self.portal.workflow_module
    self.wf = self.workflow_module._getOb('testing_workflow')
    type_test_object = self.portal.portal_types._getOb('ERP5Workflow Test Document')
    type_test_object.edit(type_base_category_list=('validation_state',))
    type_test_object.edit(type_erp5workflow_list=('testing_workflow',))
    self.getWorkflowTool().setChainForPortalTypes(['ERP5Workflow Test Document'], ())

  def doActionFor(self, document, action):
    user_action = action + '_action'
    self.portal.portal_workflow.doActionFor(document, user_action, wf_id = 'testing_workflow')
    #getattr(document, convertToMixedCase(action))()

class TestERP5Workflow(TestERP5WorkflowMixin):
  """
    Tests ERP5 Workflow.
  """
  def afterSetUp(self):
    self.portal = self.getPortal()
    self.getWorkflowTool().setChainForPortalTypes(['ERP5Workflow Test Document'], ())
    self.workflow_module = self.portal.workflow_module
    self.wf = self.workflow_module._getOb('testing_workflow')
    type_test_object = self.portal.portal_types._getOb('ERP5Workflow Test Document')
    type_test_object.edit(type_base_category_list=('validation_state',))
    type_test_object.edit(type_erp5workflow_list=('testing_workflow',))
    self.resetComponentTool()
    self.assertFalse('testing_workflow' in self.getWorkflowTool().getChainFor(type_test_object.getId()))
    self.login() # as Manager

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
    self.getWorkflowTool().setChainForPortalTypes(['ERP5Workflow Test Document'], ('testing_workflow'))
    self.wf = self.workflow_module._getOb('testing_workflow')
    type_test_object = self.portal.portal_types['ERP5Workflow Test Document']
    type_test_object.edit(type_base_category_list=())
    type_test_object.edit(type_erp5workflow_list=())
    self.resetComponentTool()
    self.assertTrue(self.wf.getId() in self.getWorkflowTool().getChainFor(type_test_object.getId()))
    self.assertEqual(type_test_object.getTypeErp5workflowList(), [])
    self.login()

  def getStateFor(self, document):
    return self.wf._getWorkflowStateOf(document, id_only=True)

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5Workflow))
  suite.addTest(unittest.makeSuite(TestDCWorkflow))
  return suite