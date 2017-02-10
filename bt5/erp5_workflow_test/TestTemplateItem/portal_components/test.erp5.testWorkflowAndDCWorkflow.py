import unittest
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.DCWorkflow.DCWorkflow import ValidationFailed
from DateTime import DateTime

class TestERP5WorkflowMixin(ERP5TypeTestCase):

  def getTestObject(self):
    self.portal = self.getPortal()
    test_object = self.portal.workflow_test_module.newContent(portal_type='Workflow Test Document')
    return test_object

  def doActionFor(self, document, action):
    user_action = action
    self.portal.portal_workflow.doActionFor(document, user_action, wf_id = 'testing_workflow')

  def getWorklistDocumentCountFromActionName(self, action_name):
    self.assertEqual(action_name[-1], ')')
    left_parenthesis_offset = action_name.rfind('(')
    self.assertNotEquals(left_parenthesis_offset, -1)
    return int(action_name[left_parenthesis_offset + 1:-1])

  def checkWorklist(self, result, name, count, url_parameter_dict=None):
    entry_list = [x for x in result if x['name'].startswith(name)]
    self.assertEqual(len(entry_list), count and 1)
    if count:
      self.assertEqual(count,
        self.getWorklistDocumentCountFromActionName(entry_list[0]['name']))
    if not entry_list:
      return
    url = entry_list[0].get('url')
    if url_parameter_dict:
      self.assertTrue(url, 'Can not check url parameters without url')
      url = '%s%s' % (self.portal.getId(), url[len(self.portal.absolute_url()):])
      # Touch URL to save worklist parameters in listbox selection
      self.publish(url, 'manager:') # XXX which user ?
      selection_parameter_dict = self.portal.portal_selections.getSelectionParamsFor(
                                                    self.module_selection_name)
      for parameter, value in url_parameter_dict.iteritems():
        self.assertTrue(parameter in selection_parameter_dict)
        self.assertEqual(value, selection_parameter_dict[parameter])

  def clearCache(self):
    self.portal.portal_caches.clearAllCache()

  def getStateFor(self, document):
    return self.workflow._getWorkflowStateOf(document, id_only=True)

  def resetComponentTool(self):
    # Force reset of portal_components to regenerate accessors
    # Since it is already handled by interactions, we only need to commit
    # to allow component tool to do it's reset
    self.commit()

  def test_01_testAfterScript(self):
    new_object = self.getTestObject()
    self.doActionFor(new_object, "validate_action")
    # self.assertEqual(new_object.getDescription(), "After script was executed.")
    ### zwj: mechanism: validate => validate interaction =>
    ### setTitle => setTitle interaction => setDescription
    self.assertEqual(new_object.getDescription(), "Interaction of setTitle executed. setTitle is appeared in after validate script.")

  def test_02_testBeforeScript(self):
    new_object = self.getTestObject()
    self.doActionFor(new_object, "validate_action")
    self.doActionFor(new_object, "invalidate_action")
    self.assertEqual(new_object.getDescription(), "Before script was executed.")

  def test_03_testChangeOfState(self):
    new_object = self.getTestObject()
    self.doActionFor(new_object, "validate_action")
    self.assertEqual(self.getStateFor(new_object), 'validated')
    self.doActionFor(new_object, "invalidate_action")
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
    self.doActionFor(new_object, "validate_action")
    history_list = new_object.workflow_history["testing_workflow"]
    # 3 history lines are expected : draft->validation_action->validate
    self.assertEqual(3, len(history_list))
    last_history = history_list[-1]
    self.assertEqual(last_history.get("action", None), "validate")
    self.assertEqual(last_history.get("validation_state", None), "validated")
    return new_object

  def test_06_testCheckPermissionAreWellSet(self):
    new_object = self.getTestObject()
    self.assertEqual(new_object._View_Permission, ('Assignee', 'Assignor', 'Associate', 'Auditor', 'Author', 'Manager', 'Owner'))
    self.doActionFor(new_object, "validate_action")
    self.assertEqual(new_object._View_Permission, ('Assignee', 'Assignor', 'Associate', 'Auditor', 'Manager'))

  def test_07_testUserTransitionRaiseValidationFailed(self):
    """
    perform a fail_action which does nothing but add an error message in the workflow history
    """
    new_object = self.getTestObject()
    exception_raised = False
    try:
      self.doActionFor(new_object, "fail_action")
    except ValidationFailed:
      exception_raised = True
    self.assertEqual(True, exception_raised)
    history_list = new_object.workflow_history["testing_workflow"]
    self.assertEqual(2, len(history_list))
    last_history = history_list[-1]
    self.assertEqual(last_history.get("error_message", None), "foo error")

  def test_08_testUserActionDisplay(self):
    new_object = self.getTestObject()
    action_list = self.getWorkflowTool().listActions(object=new_object)
    action = action_list[0]
    def checkExpectedDict(expected_dict, action):
      for key in expected_dict.keys():
        self.assertEqual(expected_dict[key], action.get(key))
    checkExpectedDict({"category": "workflow", "name": "Validate"},
                      action)
    self.doActionFor(new_object, "validate_action")
    action_list = self.getWorkflowTool().listActions(object=new_object)
    action = action_list[0]
    checkExpectedDict({"category": "workflow", "name": "Invalidate"},
                      action)

  def test_09_testBaseGetWorkflowHistoryItemListScript(self):
    """
    Base_getWorkflowHistoryItemList is used for user interface, make sure it is still
    working fine
    """
    new_object = self.getTestObject()
    self.doActionFor(new_object, "validate_action")
    item_list = new_object.Base_getWorkflowHistoryItemList("testing_workflow", display=0)
    self.assertEqual(3, len(item_list))
    def checkLine(expected_data, index):
      line = item_list[index]
      for key in expected_data.keys():
        self.assertEqual(expected_data[key], line.getProperty(key))
    checkLine({'state': 'draft'}, 0)
    checkLine({'state': 'draft'}, 1)
    checkLine({'state': 'validated'}, 2)

  def test_10_testSimpleWorklist(self):
    # check the counter from worklist action_name.
    self.portal.workflow_test_module.updateLocalRolesOnSecurityGroups()
    self.login("workflow_development")
    new_object = self.getTestObject()
    self.portal = self.getPortal()
    workflow_tool = self.portal.portal_workflow
    self.tic() # reindexing for security
    self.clearCache()
    result = workflow_tool.listActions(object=new_object)
    self.checkWorklist(result, 'Document', 1)


  def test_11_testValidationInteraction(self):
    """
    check the validate interaction which changes the title of the object.
    """
    new_object = self.getTestObject()
    new_object.setTitle('nana')
    self.doActionFor(new_object, "validate_action")
    self.assertEqual(new_object.getTitle(), "After validate interaction.")
    self.assertEqual(self.getStateFor(new_object), 'validated')
    new_object.setTitle("tictic")
    self.assertEqual(new_object.getDescription(), "Interaction of setTitle executed. setTitle is appeared in after validate script.")

  def test_12_testIsTransitionPossible(self):
    new_object = self.getTestObject()
    self.portal = self.getPortal()
    workflow_tool = self.portal.portal_workflow
    self.assertEqual(workflow_tool.isTransitionPossible(new_object, 'invalidate'), 0)
    self.doActionFor(new_object, "validate_action")
    self.clearCache()
    self.assertEqual(self.getStateFor(new_object), 'validated')
    self.assertEqual(workflow_tool.isTransitionPossible(new_object, 'invalidate'), 1)

class TestConvertedWorkflow(TestERP5WorkflowMixin):
  """
    Tests Converted Workflow which generated dynamically from DCWorkflow.
  """
  def afterSetUp(self):
    self.portal = self.getPortal()
    module = self.portal.workflow_test_module
    module.manage_delObjects(list(module.objectIds()))
    workflow_module = self.portal.portal_workflow
    dc_workflow_id_list = ['testing_workflow', 'testing_interaction_workflow']
    testing_type_value = self.portal.portal_types._getOb('Workflow Test Document')
    workflow_module.WorkflowTool_convertWorkflow(batch_mode=True, workflow_id_list=dc_workflow_id_list)
    if 'testing_workflow' not in testing_type_value.getTypeWorkflowList():
      testing_type_value.addTypeWorkflowList('testing_workflow')
    if 'testing_interaction_workflow' not in testing_type_value.getTypeWorkflowList():
      testing_type_value.addTypeWorkflowList('testing_interaction_workflow') 
    self.resetComponentTool()
    self.workflow = workflow_module._getOb('testing_workflow')
    self.login()

class TestDCWorkflow(TestERP5WorkflowMixin):
  """
    Check DC Workflow works correctlly in new Workflow Tool.
  """
  def afterSetUp(self):
    self.portal = self.getPortal()
    module = self.portal.workflow_test_module
    module.manage_delObjects(list(module.objectIds()))
    workflow_module = self.portal.portal_workflow
    workflow_module.setChainForPortalTypes(['Workflow Test Document'], ('testing_workflow', 'testing_interaction_workflow', 'edit_workflow', ))
    type_test_object = self.portal.portal_types['Workflow Test Document']
    type_test_object.workflow_list = ()
    self.workflow = workflow_module._getOb('testing_workflow')
    self.resetComponentTool()
    self.login()

  def test_DC01_testWorkflowMigrationForExistingDocument(self):
    """
    We will start some actions with a DC Workflow, then we do migration of
    worklfow, and then we make sure we can continue doing more actions on this
    migrated workflow
    """
    begin_time = DateTime()
    self.portal = self.getPortal()
    workflow_module = self.portal.portal_workflow
    # Move to state "validated"
    document = self.test_05_testCheckHistoryStateAndActionForASingleTransition()
    # Do conversion
    workflow_module.WorkflowTool_convertWorkflow(batch_mode=True, workflow_id_list=["testing_workflow"])
    # Check we can invalidate
    self.doActionFor(document, "invalidate_action")
    # check if history is ok and if we are in state "invalidated"
    # make sure Base_getWorkflowHistoryItemList (check name) returns informations
    end_time = DateTime()
    # for draft, validated, and invalidated
    item_list = document.Base_getWorkflowHistoryItemList("testing_workflow", display=0)
    self.assertEqual(5, len(item_list))
    def checkLine(expected_data, index):
      line = item_list[index]
      for key in expected_data.keys():
        self.assertEqual(expected_data[key], line.getProperty(key))
    checkLine({'state': 'draft'}, 0)
    checkLine({'state': 'draft'}, 1)
    checkLine({'state': 'validated'}, 2)
    checkLine({'state': 'validated'}, 3)
    checkLine({'state': 'invalidated'}, 4)
    expected_validated_item_dict = {'comment': '', 'error_message': '', 'actor': 'ERP5TypeTestCase', 'state': 'validated', 'action': 'validate'}
    expected_invalidated_item_dict = {'comment': '', 'error_message': '', 'actor': 'ERP5TypeTestCase', 'state': 'invalidated', 'action': 'invalidate'}
    # check history keys are identical before and after conversion.
    self.assertEqual(sorted(item_list[2].keys()),sorted(item_list[4].keys()))
    # check key values are shown as expected; 
    for key in expected_invalidated_item_dict:
      self.assertEqual(item_list[2].getProperty(key), expected_validated_item_dict[key])
      self.assertEqual(item_list[4].getProperty(key), expected_invalidated_item_dict[key])
    # check date time is generated
    self.assertTrue(begin_time < item_list[4].getProperty('time') < end_time)

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestDCWorkflow))
  suite.addTest(unittest.makeSuite(TestConvertedWorkflow))
  return suite