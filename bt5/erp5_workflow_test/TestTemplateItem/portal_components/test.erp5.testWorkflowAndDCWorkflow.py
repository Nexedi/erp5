import unittest
from erp5.component.test.testWorkflowMixin import testWorkflowMixin
from Products.DCWorkflow.DCWorkflow import ValidationFailed
from DateTime import DateTime

class TestERP5WorkflowMixin(testWorkflowMixin, object):

  initial_dc_workflow_id = "testing_initial_dc_workflow"
  initial_dc_interaction_workflow_id = "testing_initial_dc_interaction_workflow"

  def afterSetUp(self):
    test_module = self.portal.workflow_test_module
    test_module.updateLocalRolesOnSecurityGroups()

    module = self.portal.workflow_test_module
    module.manage_delObjects(list(module.objectIds()))

    self.copyWorkflow(self.portal.portal_workflow, self.initial_dc_workflow_id, self.workflow_id)
    self.copyWorkflow(self.portal.portal_workflow, self.initial_dc_interaction_workflow_id, self.interaction_workflow_id)

  def copyWorkflow(self, portal_workflow, old_wf_id, new_wf_id):
    portal_workflow.copyWorkflow(old_wf_id, new_wf_id)
    self.commit()

  def getTestObject(self):
    self.portal = self.getPortal()
    test_object = self.portal.workflow_test_module.newContent(portal_type='Workflow Test Document')
    return test_object

  def doActionFor(self, document, action):
    self.portal.portal_workflow.doActionFor(document, action, wf_id=self.workflow_id)

  def clearCache(self):
    self.portal.portal_caches.clearAllCache()

  def checkDocumentState(self, document, state_id):
    self.assertEqual(self.workflow._getWorkflowStateOf(document, id_only=True), state_id)
    self.assertEqual(document.getValidationState(), state_id)

  def resetComponentTool(self):
    # Force reset of portal_components to regenerate accessors
    # Since it is already handled by interactions, we only need to commit
    # to allow component tool to do it's reset
    self.commit()

  def test_01_testAfterScriptAndInteractionOnTransition(self):
    """
    This test uses workflow and interaction workflow
    """
    new_object = self.getTestObject()
    self.assertEqual(new_object.getDescription(), "")

    self.doActionFor(new_object, "validate_action")

    self.assertEqual(new_object.getDescription(), "After script was executed.")
    ### mechanism: validate (after_script: changes description) => validate interaction
    ### (setTitle: changes title ; afterSetTitle: changes comment)
    self.assertEqual(new_object.getComment(), "Interaction of setTitle executed. setTitle is appeared in after validate script.")

  def test_02_testBeforeScript(self):
    new_object = self.getTestObject()
    self.assertEqual(new_object.getDescription(), "")
    # required to be in validated state in order to be invalidated
    self.doActionFor(new_object, "validate_action")
    self.doActionFor(new_object, "invalidate_action")
    self.assertEqual(new_object.getDescription(), "Before script was executed.")

  def test_03_testChangeOfState(self):
    new_object = self.getTestObject()
    self.doActionFor(new_object, "validate_action")
    self.checkDocumentState(new_object, 'validated')
    self.doActionFor(new_object, "invalidate_action")
    self.checkDocumentState(new_object, 'invalidated')

  def test_04_testDoWorkflowMethodTransition(self):
    """
    Check if workflow methods allows to change of state
    """
    new_object = self.getTestObject()
    self.checkDocumentState(new_object, 'draft')
    new_object.validate()
    self.checkDocumentState(new_object, 'validated')

  def test_05_testCheckHistoryStateAndActionForASingleTransition(self, workflow_id=None):
    """
    Basic checking of workflow history, only check that state and actions
    are available
    """
    if workflow_id is None:
      workflow_id = self.workflow_id

    new_object = self.getTestObject()
    self.doActionFor(new_object, "validate_action")
    # 3 history lines are expected : draft->validation_action->validate
    history_list = new_object.workflow_history[workflow_id]
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
    self.assertRaises(ValidationFailed, self.doActionFor, new_object, "fail_action")
    history_list = new_object.workflow_history[self.workflow_id]
    self.assertEqual(2, len(history_list))
    last_history = history_list[-1]
    self.assertEqual(last_history.get("error_message", None), "foo error")

  def test_08_testUserActionDisplay(self):
    """
    Check the list of actions available to users
    """
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
    item_list = new_object.Base_getWorkflowHistoryItemList(self.workflow_id, display=0)
    self.assertEqual(3, len(item_list))
    def checkLine(expected_data, index):
      line = item_list[index]
      for key in expected_data.keys():
        self.assertEqual(expected_data[key], line.getProperty(key))
    checkLine({'state': 'draft'}, 0)
    checkLine({'state': 'draft'}, 1)
    checkLine({'state': 'validated'}, 2)

  def test_10_testSimpleWorklist(self):
    self.loginByUserName("workflow_development")
    new_object = self.getTestObject()
    workflow_tool = self.portal.portal_workflow
    self.tic() # reindexing for security
    self.clearCache()
    result = workflow_tool.listActions(object=new_object)
    self.checkWorklist(result, 'Document', 1, workflow_id=self.workflow_id)

  def test_11_testValidationInteraction(self):
    """
    check the validate interaction which changes the title of the object.
    """
    new_object = self.getTestObject()
    new_object.setTitle('nana')
    self.doActionFor(new_object, "validate_action")
    self.assertEqual(new_object.getTitle(), "After validate interaction.")
    self.checkDocumentState(new_object, 'validated')
    new_object.setTitle("tictic")
    self.assertEqual(new_object.getComment(), "Interaction of setTitle executed. setTitle is appeared in after validate script.")

  def test_12_testIsTransitionPossible(self):
    new_object = self.getTestObject()
    workflow_tool = self.portal.portal_workflow
    self.assertEqual(workflow_tool.isTransitionPossible(new_object, 'invalidate'), 0)
    self.doActionFor(new_object, "validate_action")
    # XXX required ????, it should not be called: self.clearCache()
    self.checkDocumentState(new_object, 'validated')
    self.assertEqual(workflow_tool.isTransitionPossible(new_object, 'invalidate'), 1)

class TestConvertedWorkflow(TestERP5WorkflowMixin):
  """
    Tests Converted Workflow which generated dynamically from DCWorkflow.
  """
  def createERP5Workflow(self, original_workflow_id, new_workflow_id):
    portal_workflow = self.portal.portal_workflow
    self.copyWorkflow(portal_workflow, original_workflow_id,
                      new_workflow_id)
    # XXX(WORFKLOW): remove this code block once merged into erp5 master
    # and DC Workflows are converted to ERP5 Workflows
    workflow = portal_workflow._getOb(new_workflow_id)
    if workflow.getPortalType() != 'Workflow':
      portal_workflow.WorkflowTool_convertWorkflow(
        batch_mode=True,
        workflow_id_list=[new_workflow_id]
      )
      self.tic()
      workflow = portal_workflow._getOb(new_workflow_id)
    return workflow

  def afterSetUp(self):
    self.workflow_id = 'testing_erp5_workflow'
    self.interaction_workflow_id = 'testing_erp5_interaction_workflow'
    super(TestConvertedWorkflow, self).afterSetUp()
    portal_workflow = self.portal.portal_workflow

    portal_type_value = self.portal.portal_types._getOb('Workflow Test Document')
    portal_workflow.WorkflowTool_convertWorkflow(batch_mode=True,
                                                 workflow_id_list=[self.workflow_id, self.interaction_workflow_id])

    portal_type_value.setTypeWorkflowList([self.workflow_id, self.interaction_workflow_id, 'edit_workflow'])

    self.workflow = portal_workflow._getOb(self.workflow_id)
    self.resetComponentTool()
    self.login()

  def test_13_permission(self):
    """
    test permission/role mapping on states (ERP5 Workflow only)
    """

    text_portal_type = self.portal.portal_types._getOb('Workflow Test Document')
    temporary_workflow_id = 'temporary_edit_workflow'

    workflow = self.createERP5Workflow('edit_workflow', temporary_workflow_id)
    text_portal_type.setTypeWorkflowList([temporary_workflow_id])

    # some permission to be added in the test
    permission = 'View management screens'
    permission_key = '_' + permission.replace(' ', '_') + '_Permission'

    # create a Workflow Test document: it will have the usual permissions
    # defined by edit_workflow
    text_document = self.getTestObject()

    # Verify that the permission 'View management screens' is not declared on
    # the text document yet
    self.assertFalse(getattr(text_document, permission_key, False))

    self.assertEqual(workflow.getPortalType(), 'Workflow')

    workflow.setWorkflowManagedPermissionList([permission])

    # Verify permission roles dict on 'current' state"
    permission_roles_dict = workflow.state_current\
                              .getStatePermissionRolesDict()
    self.assertIn(permission, permission_roles_dict)

    # Update document permissions/roles mapping
    # By default, there should be acquisition on the state for the new
    # permission
    self.assertEqual(workflow.state_current.getAcquirePermissionList(), [permission])

    # change roles and update permission/roles mapping on text_document
    # and check document permissions/roles mapping was updated
    # it should now be a tuple, as there is no acquisition (otherwise a list)
    permission_roles_dict[permission] = ['Assignor']
    workflow.state_current.setAcquirePermissionList([])
    workflow.updateRoleMappingsFor(text_document)
    self.assertEqual(getattr(text_document, permission_key), ('Assignor',))

    # set acquisition and verify that permission/roles mapping is now a list
    workflow.state_current.setAcquirePermissionList([permission])
    workflow.updateRoleMappingsFor(text_document)
    self.assertEqual(getattr(text_document, permission_key), ['Assignor'])

    # add role for permission, and verify it was changed on the text document
    permission_roles_dict[permission] = ['Assignor', 'Auditor']
    workflow.updateRoleMappingsFor(text_document)
    self.assertEqual(getattr(text_document, permission_key), ['Assignor', 'Auditor'])

    # remove permission from the workflow, it should be removed from state
    workflow.setWorkflowManagedPermissionList([])
    self.assertEqual(workflow.state_current.getAcquirePermissionList(), [])


  def test_14_multiple_workflow_different_permission_roles(self):
    workflow1 = self.createERP5Workflow('edit_workflow', 'temporary_workflow1')
    workflow2 = self.createERP5Workflow('edit_workflow', 'temporary_workflow2')
    self.copyWorkflow(self.portal.portal_workflow, self.initial_dc_workflow_id, 'temporary_dc_workflow')
    dc_workflow = self.portal.portal_workflow._getOb('temporary_dc_workflow')
    text_portal_type = self.portal.portal_types._getOb('Workflow Test Document')

    permission = 'View management screens'
    permission_key = '_' + permission.replace(' ', '_') + '_Permission'

    # set permission managed by the workflows
    workflow1.setWorkflowManagedPermissionList([permission])
    workflow2.setWorkflowManagedPermissionList([permission])
    dc_workflow.permissions = [permission]

    # no acquisition
    workflow1.state_current.setAcquirePermissionList([])
    workflow2.state_current.setAcquirePermissionList([])

    # create document
    text_document = self.getTestObject()

    permission_roles_dict1 = workflow1.state_current.getStatePermissionRolesDict()
    permission_roles_dict1[permission] = ['Assignor', 'Assignee', 'Auditor', 'Author']
    text_portal_type.setTypeWorkflowList(['temporary_workflow1'])
    workflow1.updateRoleMappingsFor(text_document)
    self.assertEqual(getattr(text_document, permission_key),
                     ('Assignee', 'Assignor', 'Auditor', 'Author'))

    # a few workflows define different roles for the same permission, it should
    # perform an intersection of the role sets to get the common values of the
    # sets
    permission_roles_dict2 = workflow2.state_current.getStatePermissionRolesDict()
    permission_roles_dict2[permission] = ['Auditor', 'Author', 'Manager', 'Member', 'Owner', 'Reviewer']
    text_portal_type.setTypeWorkflowList(['temporary_workflow1',
                                          'temporary_workflow2'])
    workflow2.updateRoleMappingsFor(text_document)
    self.assertEqual(getattr(text_document, permission_key),
                     ('Auditor', 'Author'))

    dc_workflow.states.draft.permission_roles = {permission: ('Assignor', 'Auditor', 'Owner', 'Reviewer')}
    text_portal_type.setTypeWorkflowList(['temporary_workflow1',
                                          'temporary_workflow2',
                                          'temporary_dc_workflow'])
    dc_workflow.updateRoleMappingsFor(text_document)
    self.assertEqual(getattr(text_document, permission_key), ('Auditor',))

    # add role to workflow1 should change the roles on text document
    permission_roles_dict1[permission].append('Owner')
    # also add acquisition
    workflow1.state_current.setAcquirePermissionList([permission])
    workflow1.updateRoleMappingsFor(text_document)
    self.assertEqual(getattr(text_document, permission_key),
                     ['Auditor', 'Owner'])

  def test_15_testGuardsAreNotMessingUpBase_viewDict(self):
    # check Base_viewDict is available on workflow's transition
    self.workflow.transition_delete_action.Base_viewDict()

  def test_16_testWorklistViewIsAccessible(self):
    # check worklist view is available on workflow
    self.workflow.worklist_1_draft_test_workflow_document_list.view()

class TestDCWorkflow(TestERP5WorkflowMixin):
  """
    Check DC Workflow works correctly in new Workflow Tool.
  """
  def afterSetUp(self):
    self.workflow_id = 'testing_dc_workflow'
    self.interaction_workflow_id = 'testing_dc_interaction_workflow'
    super(TestDCWorkflow, self).afterSetUp()
    portal_workflow = self.portal.portal_workflow

    type_test_object = self.portal.portal_types['Workflow Test Document']

    type_test_object.setTypeWorkflowList([
      'edit_workflow', self.workflow_id, self.initial_dc_workflow_id,
      self.initial_dc_interaction_workflow_id,
    ])

    self.workflow = portal_workflow._getOb(self.workflow_id)
    self.resetComponentTool()
    self.login()

  def test_DC01_testWorkflowMigrationForExistingDocument(self):
    """
    We will start some actions with a DC Workflow, then we do migration of
    workflow, and then we make sure we can continue doing more actions on this
    migrated workflow
    """
    begin_time = DateTime()
    self.portal = self.getPortal()
    workflow_module = self.portal.portal_workflow

    # Move to state "validated"
    document = self.test_05_testCheckHistoryStateAndActionForASingleTransition()

    # Migrate to ERP5 Workflows
    workflow_module.WorkflowTool_convertWorkflow(batch_mode=True, workflow_id_list=[self.workflow_id])
    self.tic()

    # Check we can invalidate
    self.doActionFor(document, "invalidate_action")
    end_time = DateTime()

    # for draft, validated, and invalidated
    item_list = document.Base_getWorkflowHistoryItemList(self.workflow_id, display=0)
    self.assertEqual(5, len(item_list))
    def checkLine(expected_data, index):
      line = item_list[index]
      for key in expected_data.keys():
        self.assertEqual(expected_data[key], line.getProperty(key))
    checkLine({'state':       'draft'}, 0)
    checkLine({'state':       'draft'}, 1)
    checkLine({'state':   'validated'}, 2)
    checkLine({'state':   'validated'}, 3)
    checkLine({'state': 'invalidated'}, 4)
    expected_validated_item_dict   = {'comment': '', 'error_message': '', 'actor': 'ERP5TypeTestCase', 'state':   'validated', 'action':   'validate'}
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
