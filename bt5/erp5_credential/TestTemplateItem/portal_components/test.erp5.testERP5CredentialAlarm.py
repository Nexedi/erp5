# Copyright (c) 2002-2012 Nexedi SA and Contributors. All Rights Reserved.
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase


class TestERP5CredentialAlarmMixin(ERP5TypeTestCase):
  def afterSetUp(self):
    """Prepare the test."""
    super(TestERP5CredentialAlarmMixin, self).afterSetUp()
    self.__previous_configuration = self.portal.portal_preferences.getPreferredAssignmentRequestAlarmAutomaticCall()
    if not self.__previous_configuration:
      system_preference = self.getPreferenceTool().getActiveSystemPreference()
      if system_preference is None:
        system_preference = self.portal.portal_preferences.newContent(
          portal_type='System Preference'
        )
        system_preference.enable()
      self.__system_preference = system_preference
      self.__system_preference.setPreferredAssignmentRequestAlarmAutomaticCall(True)
      self.tic()
      # reset the cache
      self.portal.portal_caches.clearAllCache()

  def beforeTearDown(self):
    super(TestERP5CredentialAlarmMixin, self).beforeTearDown()
    if not self.__previous_configuration:
      self.__system_preference.setPreferredAssignmentRequestAlarmAutomaticCall(False)
      self.tic()
      # reset the cache
      self.portal.portal_caches.clearAllCache()

  def createNewOrganisation(self):
    return self.portal.organisation_module.newContent()

  def createNewProject(self):
    # As the erp5_project bt5 is probably not installed (as not a dependency),
    # let's use another portal type.
    # It will not change the test behaviour
    return self.portal.organisation_module.newContent()

  def getCustomerFunctionCategoryValue(self):
    # As the category does not exist,
    # let's use another portal type.
    # It will not change the test behaviour
    return self.portal.organisation_module

  def getManagerFunctionCategoryValue(self):
    # As the category does not exist,
    # let's use another portal type.
    # It will not change the test behaviour
    return self.portal.person_module

  def stabilizeAssignmentRequestAlarm(self):
    self.tic()
    # As the alarm check ALL objects, try to stabilise before running the test
    self.portal.portal_alarms.credential_create_missing_assignment_request_alarm.activeSense()
    self.portal.portal_alarms.credential_handle_assignment_request_alarm.activeSense()
    self.tic()
    # Run the alarms twice, as the first run will not lead to a good state
    # example: first run create missing Assignment Request
    # second run create missing Assignment
    # or the contrary
    self.portal.portal_alarms.credential_create_missing_assignment_request_alarm.activeSense()
    self.portal.portal_alarms.credential_handle_assignment_request_alarm.activeSense()
    self.tic()

class TestCreateMissingAssignmentRequestAlarm(TestERP5CredentialAlarmMixin):

  #################################################################
  # credential_create_missing_assignment_request_alarm
  #################################################################
  def test_Assignment_createMissingAssignmentRequest_alarm_openAssignmentWithoutRequest(self):
    self.stabilizeAssignmentRequestAlarm()

    with self.changeContextByDisablingPortalAlarm():
      person = self.portal.person_module.newContent(
        portal_type='Person'
      )
      assignment = person.newContent(
        portal_type='Assignment'
      )
      assignment.open()

      self.tic()
      self.assertAlarmVisitingDocument(
        self.portal.portal_alarms.credential_create_missing_assignment_request_alarm,
        assignment,
        'Assignment_createMissingAssignmentRequest'
      )

  def test_Assignment_createMissingAssignmentRequest_alarm_openAssignmentWithRequest(self):
    self.stabilizeAssignmentRequestAlarm()

    with self.changeContextByDisablingPortalAlarm():
      person = self.portal.person_module.newContent(
        portal_type='Person'
      )
      assignment = person.newContent(
        portal_type='Assignment'
      )
      assignment.open()

      person2 = self.portal.person_module.newContent(
        portal_type='Person'
      )
      # Created to have one more assignment request
      assignment_request = self.portal.assignment_request_module.newContent(
        portal_type='Assignment Request',
        destination_decision_value=person2
      )
      assignment_request.submit()
      assignment_request.validate()

      self.tic()
      self.assertAlarmNotVisitingDocument(
        self.portal.portal_alarms.credential_create_missing_assignment_request_alarm,
        assignment,
        'Assignment_createMissingAssignmentRequest'
      )

  """
  def test_Assignment_createMissingAssignmentRequest_alarm_draft(self):
    assignment_request = self.portal.assignment_request_module.newContent(
      portal_type='Assignment Request'
    )

    self.tic()
    self.assertAlarmNotVisitingDocument(
      self.portal.portal_alarms.credential_create_missing_assignment_request_alarm,
      assignment_request,
      'Assignment_createMissingAssignmentRequest'
    )
"""


  def test_Assignment_createMissingAssignmentRequest_alarm_validatedRequestWithoutAssignment(self):
    person = self.portal.person_module.newContent(
      portal_type='Person'
    )
    self.stabilizeAssignmentRequestAlarm()

    with self.changeContextByDisablingPortalAlarm():
      assignment_request = self.portal.assignment_request_module.newContent(
        portal_type='Assignment Request',
        destination_decision_value=person
      )
      self.portal.portal_workflow._jumpToStateFor(assignment_request,
          'validated')

      self.tic()
      self.assertAlarmVisitingDocument(
        self.portal.portal_alarms.credential_create_missing_assignment_request_alarm,
        assignment_request,
        'AssignmentRequest_changeAssignment'
      )

  def test_Assignment_createMissingAssignmentRequest_alarm_validatedRequestWithAssignment(self):
    self.stabilizeAssignmentRequestAlarm()

    with self.changeContextByDisablingPortalAlarm():
      person = self.portal.person_module.newContent(
        portal_type='Person'
      )
      assignment_request = self.portal.assignment_request_module.newContent(
        portal_type='Assignment Request',
        destination_decision_value=person
      )
      self.portal.portal_workflow._jumpToStateFor(assignment_request,
          'submitted')
      assignment_request.AssignmentRequest_changeAssignment()
      self.assertEqual(assignment_request.getSimulationState(), 'validated')

      self.tic()
      self.assertAlarmNotVisitingDocument(
        self.portal.portal_alarms.credential_create_missing_assignment_request_alarm,
        assignment_request,
        'AssignmentRequest_changeAssignment'
      )

  #################################################################
  # Assignment_createMissingAssignmentRequest
  #################################################################
  def test_Assignment_createMissingAssignmentRequest_script_openWithoutRequest(self):
    project = self.createNewProject()
    organisation = self.createNewOrganisation()
    function_category = self.getCustomerFunctionCategoryValue()
    person = self.portal.person_module.newContent(
      portal_type='Person'
    )
    assignment = person.newContent(
      portal_type='Assignment',
      destination_project_value=project,
      destination_value=organisation,
      function_value=function_category
    )
    assignment.open()
    assignment_request = assignment.Assignment_createMissingAssignmentRequest()
    self.assertNotEqual(None, assignment_request)
    self.assertEqual('validated', assignment_request.getSimulationState())
    self.assertEqual(person.getRelativeUrl(), assignment_request.getDestinationDecision())
    self.assertEqual(project.getRelativeUrl(), assignment_request.getDestinationProject())
    self.assertEqual(organisation.getRelativeUrl(), assignment_request.getDestination())
    self.assertEqual(function_category.getRelativeUrl(), assignment_request.getFunction())

  def test_Assignment_createMissingAssignmentRequest_script_closedWithoutRequest(self):
    project = self.createNewProject()
    organisation = self.createNewOrganisation()
    function_category = self.getCustomerFunctionCategoryValue()
    person = self.portal.person_module.newContent(
      portal_type='Person'
    )
    assignment = person.newContent(
      portal_type='Assignment',
      destination_project_value=project,
      destination_value=organisation,
      function_value=function_category
    )
    assignment.open()
    assignment.close()
    assignment_request = assignment.Assignment_createMissingAssignmentRequest()
    self.assertEqual(None, assignment_request)

  def test_Assignment_createMissingAssignmentRequest_script_openWithRequest(self):
    project = self.createNewProject()
    organisation = self.createNewOrganisation()
    function_category = self.getCustomerFunctionCategoryValue()
    person = self.portal.person_module.newContent(
      portal_type='Person'
    )
    assignment_request = self.portal.assignment_request_module.newContent(
      portal_type='Assignment Request',
      destination_decision_value=person,
      destination_project_value=project,
      destination_value=organisation,
      function_value=function_category
    )
    assignment_request.submit()
    assignment_request.validate()
    self.tic()

    assignment = person.newContent(
      portal_type='Assignment',
      destination_project_value=project,
      destination_value=organisation,
      function_value=function_category
    )
    assignment.open()

    assignment_request = assignment.Assignment_createMissingAssignmentRequest()
    self.assertEqual(None, assignment_request)

  def test_Assignment_createMissingAssignmentRequest_script_openWithNotMatchingRequest(self):
    project = self.createNewProject()
    organisation = self.createNewOrganisation()
    function_category = self.getCustomerFunctionCategoryValue()
    person = self.portal.person_module.newContent(
      portal_type='Person'
    )
    assignment_request = self.portal.assignment_request_module.newContent(
      portal_type='Assignment Request',
      destination_decision_value=person,
      destination_project_value=project,
      destination_value=organisation
    )
    assignment_request.submit()
    assignment_request.validate()
    self.tic()

    assignment = person.newContent(
      portal_type='Assignment',
      destination_project_value=project,
      destination_value=organisation,
      function_value=function_category
    )
    assignment.open()

    assignment_request = assignment.Assignment_createMissingAssignmentRequest()
    self.assertNotEqual(None, assignment_request)
    self.assertEqual('validated', assignment_request.getSimulationState())
    self.assertEqual(person.getRelativeUrl(), assignment_request.getDestinationDecision())
    self.assertEqual(project.getRelativeUrl(), assignment_request.getDestinationProject())
    self.assertEqual(organisation.getRelativeUrl(), assignment_request.getDestination())
    self.assertEqual(function_category.getRelativeUrl(), assignment_request.getFunction())

  def test_Assignment_createMissingAssignmentRequest_script_openWithNotMatchingRequest_noProject(self):
    organisation = self.createNewOrganisation()
    function_category = self.getCustomerFunctionCategoryValue()
    person = self.portal.person_module.newContent(
      portal_type='Person'
    )
    assignment_request = self.portal.assignment_request_module.newContent(
      portal_type='Assignment Request',
      destination_decision_value=person,
      destination_value=organisation
    )
    assignment_request.submit()
    assignment_request.validate()
    self.tic()

    assignment = person.newContent(
      portal_type='Assignment',
      destination_value=organisation,
      function_value=function_category
    )
    assignment.open()

    assignment_request = assignment.Assignment_createMissingAssignmentRequest()
    self.assertNotEqual(None, assignment_request)
    self.assertEqual('validated', assignment_request.getSimulationState())
    self.assertEqual(person.getRelativeUrl(), assignment_request.getDestinationDecision())
    self.assertEqual(organisation.getRelativeUrl(), assignment_request.getDestination())
    self.assertEqual(function_category.getRelativeUrl(), assignment_request.getFunction())

class TestSlapOSHandleAssignmentRequestAlarm(TestERP5CredentialAlarmMixin):

  #################################################################
  # credential_handle_assignment_request_alarm
  #################################################################
  def test_AssignmentRequest_changeAssignment_alarm_submitted(self):
    person = self.portal.person_module.newContent(
      portal_type='Person'
    )
    assignment_request = self.portal.assignment_request_module.newContent(
      portal_type='Assignment Request',
      destination_decision_value=person
    )
    self.portal.portal_workflow._jumpToStateFor(assignment_request,
        'submitted')

    self.tic()
    self.assertAlarmVisitingDocument(
      self.portal.portal_alarms.credential_handle_assignment_request_alarm,
      assignment_request,
      'AssignmentRequest_changeAssignment'
    )

  def test_AssignmentRequest_changeAssignment_alarm_suspended(self):
    person = self.portal.person_module.newContent(
      portal_type='Person'
    )
    assignment_request = self.portal.assignment_request_module.newContent(
      portal_type='Assignment Request',
      destination_decision_value=person
    )
    self.portal.portal_workflow._jumpToStateFor(assignment_request,
        'suspended')

    self.tic()
    self.assertAlarmVisitingDocument(
      self.portal.portal_alarms.credential_handle_assignment_request_alarm,
      assignment_request,
      'AssignmentRequest_changeAssignment'
    )

  #################################################################
  # AssignmentRequest_changeAssignment
  #################################################################
  def test_AssignmentRequest_changeAssignment_script_submittedWithoutAssignment(self):
    project = self.createNewProject()
    organisation = self.createNewOrganisation()
    function_category = self.getCustomerFunctionCategoryValue()
    person = self.portal.person_module.newContent(
      portal_type='Person'
    )
    assignment_request = self.portal.assignment_request_module.newContent(
      portal_type='Assignment Request',
      destination_decision_value=person,
      destination_project_value=project,
      destination_value=organisation,
      function_value=function_category
    )
    assignment_request.submit()
    assignment = assignment_request.AssignmentRequest_changeAssignment()
    self.assertEqual('open', assignment.getValidationState())
    self.assertEqual(person.getRelativeUrl(), assignment.getParentValue().getRelativeUrl())
    self.assertEqual(project.getRelativeUrl(), assignment.getDestinationProject())
    self.assertEqual(organisation.getRelativeUrl(), assignment.getDestination())
    self.assertEqual(function_category.getRelativeUrl(), assignment.getFunction())
    self.assertEqual('validated', assignment_request.getSimulationState())

  def test_AssignmentRequest_changeAssignment_script_submittedWithoutMatchingAssignment(self):
    project = self.createNewProject()
    function_category = self.getCustomerFunctionCategoryValue()
    manager_category = self.getManagerFunctionCategoryValue()
    person = self.portal.person_module.newContent(
      portal_type='Person'
    )
    assignment = person.newContent(
      portal_type='Assignment',
      destination_project_value=project,
      function_value=manager_category
    )
    assignment.open()
    self.tic()
    assignment_request = self.portal.assignment_request_module.newContent(
      portal_type='Assignment Request',
      destination_decision_value=person,
      destination_project_value=project,
      function_value=function_category
    )
    assignment_request.submit()
    assignment2 = assignment_request.AssignmentRequest_changeAssignment()
    self.assertNotEqual(assignment.getRelativeUrl(), assignment2.getRelativeUrl())
    self.assertEqual('open', assignment.getValidationState())
    self.assertEqual(person.getRelativeUrl(), assignment.getParentValue().getRelativeUrl())
    self.assertEqual(project.getRelativeUrl(), assignment.getDestinationProject())
    self.assertEqual(manager_category.getRelativeUrl(), assignment.getFunction())
    self.assertEqual('open', assignment2.getValidationState())
    self.assertEqual(person.getRelativeUrl(), assignment2.getParentValue().getRelativeUrl())
    self.assertEqual(project.getRelativeUrl(), assignment2.getDestinationProject())
    self.assertEqual(function_category.getRelativeUrl(), assignment2.getFunction())
    self.assertEqual('validated', assignment_request.getSimulationState())

  def test_AssignmentRequest_changeAssignment_script_submittedWithoutMatchingAssignment_destination(self):
    organisation = self.createNewOrganisation()
    function_category = self.getCustomerFunctionCategoryValue()
    manager_category = self.getManagerFunctionCategoryValue()
    person = self.portal.person_module.newContent(
      portal_type='Person'
    )
    assignment = person.newContent(
      portal_type='Assignment',
      destination_value=organisation,
      function_value=manager_category
    )
    assignment.open()
    self.tic()
    assignment_request = self.portal.assignment_request_module.newContent(
      portal_type='Assignment Request',
      destination_decision_value=person,
      destination_value=organisation,
      function_value=function_category
    )
    assignment_request.submit()
    assignment2 = assignment_request.AssignmentRequest_changeAssignment()
    self.assertNotEqual(assignment.getRelativeUrl(), assignment2.getRelativeUrl())
    self.assertEqual('open', assignment.getValidationState())
    self.assertEqual(person.getRelativeUrl(), assignment.getParentValue().getRelativeUrl())
    self.assertEqual(organisation.getRelativeUrl(), assignment.getDestination())
    self.assertEqual(manager_category.getRelativeUrl(), assignment.getFunction())
    self.assertEqual('open', assignment2.getValidationState())
    self.assertEqual(person.getRelativeUrl(), assignment2.getParentValue().getRelativeUrl())
    self.assertEqual(organisation.getRelativeUrl(), assignment2.getDestination())
    self.assertEqual(function_category.getRelativeUrl(), assignment2.getFunction())
    self.assertEqual('validated', assignment_request.getSimulationState())

  def test_AssignmentRequest_changeAssignment_script_submittedWithMatchingAssignment(self):
    project = self.createNewProject()
    function_category = self.getCustomerFunctionCategoryValue()
    person = self.portal.person_module.newContent(
      portal_type='Person'
    )
    assignment = person.newContent(
      portal_type='Assignment',
      destination_project_value=project,
      function_value=function_category
    )
    assignment.open()
    self.tic()
    assignment_request = self.portal.assignment_request_module.newContent(
      portal_type='Assignment Request',
      destination_decision_value=person,
      destination_project_value=project,
      function_value=function_category
    )
    assignment_request.submit()
    assignment2 = assignment_request.AssignmentRequest_changeAssignment()
    self.assertEqual(None, assignment2)
    self.assertEqual('invalidated', assignment_request.getSimulationState())

  def test_AssignmentRequest_changeAssignment_script_validatedWithMatchingAssignment(self):
    project = self.createNewProject()
    function_category = self.getCustomerFunctionCategoryValue()
    person = self.portal.person_module.newContent(
      portal_type='Person'
    )
    assignment = person.newContent(
      portal_type='Assignment',
      destination_project_value=project,
      function_value=function_category
    )
    assignment.open()
    self.tic()
    assignment_request = self.portal.assignment_request_module.newContent(
      portal_type='Assignment Request',
      destination_decision_value=person,
      destination_project_value=project,
      function_value=function_category
    )
    assignment_request.submit()
    assignment_request.validate()
    assignment2 = assignment_request.AssignmentRequest_changeAssignment()
    self.assertEqual(None, assignment2)
    self.assertEqual('validated', assignment_request.getSimulationState())
    self.assertEqual('open', assignment.getValidationState())

  def test_AssignmentRequest_changeAssignment_script_validatedWithoutMatchingAssignment(self):
    project = self.createNewProject()
    function_category = self.getCustomerFunctionCategoryValue()
    person = self.portal.person_module.newContent(
      portal_type='Person'
    )
    assignment_request = self.portal.assignment_request_module.newContent(
      portal_type='Assignment Request',
      destination_decision_value=person,
      destination_project_value=project,
      function_value=function_category
    )
    assignment_request.submit()
    assignment_request.validate()
    assignment2 = assignment_request.AssignmentRequest_changeAssignment()
    self.assertEqual(None, assignment2)
    self.assertEqual('invalidated', assignment_request.getSimulationState())

  def test_AssignmentRequest_changeAssignment_script_suspendedWithMatchingAssignment(self):
    project = self.createNewProject()
    function_category = self.getCustomerFunctionCategoryValue()
    person = self.portal.person_module.newContent(
      portal_type='Person'
    )
    assignment = person.newContent(
      portal_type='Assignment',
      destination_project_value=project,
      function_value=function_category
    )
    assignment.open()
    self.tic()
    assignment_request = self.portal.assignment_request_module.newContent(
      portal_type='Assignment Request',
      destination_decision_value=person,
      destination_project_value=project,
      function_value=function_category
    )
    self.portal.portal_workflow._jumpToStateFor(assignment_request,
        'suspended')
    assignment = assignment_request.AssignmentRequest_changeAssignment()
    self.assertEqual('closed', assignment.getValidationState())
    self.assertEqual(person.getRelativeUrl(), assignment.getParentValue().getRelativeUrl())
    self.assertEqual('invalidated', assignment_request.getSimulationState())

  def test_AssignmentRequest_changeAssignment_script_suspendedWithoutMatchingAssignment(self):
    project = self.createNewProject()
    function_category = self.getCustomerFunctionCategoryValue()
    manager_category = self.getManagerFunctionCategoryValue()
    person = self.portal.person_module.newContent(
      portal_type='Person'
    )
    assignment = person.newContent(
      portal_type='Assignment',
      destination_project_value=project,
      function_value=manager_category
    )
    assignment.open()
    self.tic()
    assignment_request = self.portal.assignment_request_module.newContent(
      portal_type='Assignment Request',
      destination_decision_value=person,
      destination_project_value=project,
      function_value=function_category
    )
    self.portal.portal_workflow._jumpToStateFor(assignment_request,
        'suspended')
    assignment2 = assignment_request.AssignmentRequest_changeAssignment()
    self.assertEqual('open', assignment.getValidationState())
    self.assertEqual(None, assignment2)
    self.assertEqual('invalidated', assignment_request.getSimulationState())
