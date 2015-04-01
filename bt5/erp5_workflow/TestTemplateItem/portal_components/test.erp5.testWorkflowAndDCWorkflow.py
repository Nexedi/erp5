import unittest
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.DCWorkflow.DCWorkflow import ValidationFailed

class TestERP5WorkflowMixin(ERP5TypeTestCase):

  def getTestObject(self):
    self.portal = self.getPortal()
    test_object = self.portal.erp5workflow_test_module.newContent(portal_type='ERP5Workflow Test Document')
    return test_object

  def getStateFor(self, document):
    """
    Needs to be overidden
    """
    pass

  def doActionFor(self, document, action):
    user_action = action + '_action'
    self.portal.portal_workflow.doActionFor(document, user_action, wf_id = 'testing_workflow')

  def getWorklistDocumentCountFromActionName(self, action_name):
    self.assertEqual(action_name[-1], ')')
    left_parenthesis_offset = action_name.rfind('(')
    self.assertNotEquals(left_parenthesis_offset, -1)
    return int(action_name[left_parenthesis_offset + 1:-1])

  def checkWorklist(self, result, name, count, url_parameter_dict=None):
    entry_list = [x for x in result if x['name'].startswith(name)]
    #raise NotImplementedError (result)
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

  def resetComponentTool(self):
    # Force reset of portal_components to regenerate accessors
    # Since it is already handled by interactions, we only need to commit
    # to allow component tool to do it's reset
    self.commit()

  def test_01_testAfterScript(self):
    new_object = self.getTestObject()
    self.doActionFor(new_object, "validate")
    # self.assertEqual(new_object.getDescription(), "After script was executed.")
    ### zwj: mechanism: validate => validate interaction =>
    ### setTitle => setTitle interaction => setDescription
    self.assertEqual(new_object.getDescription(), "Interaction of setTitle executed.")

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
    action_list = self.getWorkflowTool().listActions(object=new_object)
    self.assertEqual(1, len(action_list))
    action = action_list[0]
    def checkExpectedDict(expected_dict, action):
      for key in expected_dict.keys():
        self.assertEqual(expected_dict[key], action.get(key))
    checkExpectedDict({"category": "workflow", "name": "Validate"},
                      action)
    self.doActionFor(new_object, "validate")
    action_list = self.getWorkflowTool().listActions(object=new_object)
    self.assertEqual(1, len(action_list))
    action = action_list[0]
    checkExpectedDict({"category": "workflow", "name": "Invalidate"},
                      action)

  def test_09_testBaseGetWorkflowHistoryItemListScript(self):
    """
    Base_getWorkflowHistoryItemList is used for user interface, make sure it is still
    working fine
    """
    new_object = self.getTestObject()
    self.doActionFor(new_object, "validate")
    item_list = new_object.Base_getWorkflowHistoryItemList("testing_workflow", display=0)
    self.assertEqual(3, len(item_list))
    def checkLine(expected_data, index):
      line = item_list[index]
      for key in expected_data.keys():
        self.assertEqual(expected_data[key], line.getProperty(key))
    checkLine({'state': 'draft'}, 0)
    checkLine({'state': 'draft'}, 1)
    checkLine({'state': 'validated'}, 2)
  """
  def test_10_testSimpleWorklist(self):
    
    #check the counter from worklist action_name.
    # need another way to check, because worklist update every 5 mins

    self.login("workflow_development")
    self.portal = self.getPortal()
    new_object = self.getTestObject()
    workflow_tool = self.portal.portal_workflow
    self.clearCache()
    new_object.reindexObject()
    self.clearCache()
    result = workflow_tool.listActions(object=new_object)
    self.checkWorklist(result, 'Document', 1)
  """
  def test_11_testValidationInteraction(self):
    """
    check the validate interaction which changes the title of the object.
    """
    new_object = self.getTestObject()
    new_object.setTitle('nana')
    self.doActionFor(new_object, "validate")
    self.assertEqual(new_object.getTitle(), "toto")
    self.assertEqual(self.getStateFor(new_object), 'validated')
    new_object.setTitle("tictic")
    self.assertEqual(new_object.getDescription(), "Interaction of setTitle executed.")

  def test_12_testIsTransitionPossible(self):
    new_object = self.getTestObject()
    self.portal = self.getPortal()
    workflow_tool = self.portal.portal_workflow
    self.assertEqual(workflow_tool.isTransitionPossible(new_object, 'invalidate'), 0)
    self.doActionFor(new_object, "validate")
    self.assertEqual(self.getStateFor(new_object), 'validated')
    self.assertEqual(workflow_tool.isTransitionPossible(new_object, 'invalidate'), 1)

  def test_13_testDCWorkflowMigrationScript(self):
    new_object = self.getTestObject()
    portal_type = new_object.getTypeInfo()
    self.portal = self.getPortal()
    workflow_tool = self.portal.portal_workflow
    workflow_tool.getWorkflowValueListFor(portal_type)
  """
  def beforeTearDown(self):
    self.portal = self.getPortal()
    self.getWorkflowTool().setChainForPortalTypes(['ERP5Workflow Test Document'], ())
    type_test_object = self.portal.portal_types._getOb('ERP5Workflow Test Document')
    type_test_object.edit(type_base_category_list=('validation_state',))
    type_test_object.edit(type_erp5workflow_list=('testing_workflow',))
    #self.commit()
  """

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
    type_test_object.edit(type_erp5workflow_list=('testing_workflow', 'testing_interaction_workflow', ))
    self.resetComponentTool()
    self.assertFalse('testing_workflow' in self.getWorkflowTool().getChainFor(type_test_object.getId()))
    self.login()

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
    self.getWorkflowTool().setChainForPortalTypes(['ERP5Workflow Test Document'], ('testing_workflow', 'testing_interaction_workflow', 'edit_workflow', ))
    self.wf = self.workflow_module._getOb('testing_workflow')
    type_test_object = self.portal.portal_types['ERP5Workflow Test Document']
    type_test_object.edit(type_erp5workflow_list=())
    type_test_object.edit(type_interaction_workflow_list=())
    self.resetComponentTool()
    #self.assertTrue(self.wf.getId() in self.getWorkflowTool().getChainFor(type_test_object.getId()))
    self.assertEqual(type_test_object.getTypeErp5workflowList(), [])
    self.login()

  def getStateFor(self, document):
    return self.wf._getWorkflowStateOf(document, id_only=True)

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5Workflow))
  suite.addTest(unittest.makeSuite(TestDCWorkflow))
  return suite