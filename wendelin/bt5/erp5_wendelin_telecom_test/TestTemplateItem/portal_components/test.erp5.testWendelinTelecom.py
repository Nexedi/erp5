##############################################################################
#
# Copyright (c) 2002-2024 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################
from io import BytesIO
from six.moves.http_client import NO_CONTENT
import json
import msgpack
import random
import string

from Products.ERP5Type.tests.SecurityTestCase import SecurityTestCase


QCI_COUNT = 256

def generateRandomString(length=24, only_digits=False, hexadecimal=False):
  character_list = string.digits
  if not only_digits:
    if hexadecimal:
      character_list += 'ABCDEF'
    else:
      character_list += string.ascii_letters
  return ''.join([random.choice(character_list) for _ in range(length)])

class WendelinTelecomTest(SecurityTestCase):
  """
  Wendelin Telecom Test
  """

  def getTitle(self):
    return "Wendelin Telecom Test"

  def afterSetUp(self):
    # Set up variables for ORS ingestion testing
    self.ors_enb_log_ingestion = self.portal.portal_ingestion_policies.ors_enb_log_ingestion

    self.ors_enb_kpi_endpoint_path = self.portal.getPath() + '/Base_getOrsEnbKpi'

    self.test_ors_example_log_valid = {
      'log': self.portal.web_page_module.test_example_ors_enb_log_valid.getTextContent()
    }
    self.test_ors_example_log_invalid_split_1 = {
      'log': self.portal.web_page_module.test_example_ors_enb_log_invalid_split_1.getTextContent()
    }
    self.test_ors_example_log_invalid_split_2 = {
      'log': self.portal.web_page_module.test_example_ors_enb_log_invalid_split_2.getTextContent()
    }
    self.test_ors_example_log_with_duplicates = {
      'log': self.portal.web_page_module.test_example_ors_enb_log_with_duplicates.getTextContent()
    }
    self.test_ors_example_log_empty = {'log': ""}

    # Set up ingestor user for performing ingestions
    self.ingestor_user = self.createWendelinTelecomUser(
      'test_ingestor_%s' % generateRandomString(),
      None,
      'ingestor'
    )

  def beforeTearDown(self):
    self.abort()

    # Manually change this to False to keep testing data
    cleanup_data = True
    if cleanup_data:
      # Clean up all test items
      for module, portal_type in (
        (self.portal.project_module, 'Project'),
        (self.portal.person_module, 'Person'),
        (self.portal.data_acquisition_unit_module, 'Data Acquisition Unit'),
        (self.portal.data_supply_module, 'Data Supply'),
        (self.portal.data_stream_module, 'Data Stream'),
        (self.portal.data_ingestion_module, 'Data Ingestion'),
        (self.portal.data_analysis_module, 'Data Analysis'),
        (self.portal.data_array_module, 'Data Array'),
      ):
        object_list = module.objectValues(portal_type=portal_type)
        if object_list:
          test_object_id_list = [
            obj.getId() for obj in object_list \
            if ('test' in obj.getReference().lower() and 'default' not in obj.getId())
          ]
          if test_object_id_list:
            module.manage_delObjects(ids=test_object_id_list)
      self.tic()

  def _removeDocument(self, document_to_remove):
    path = document_to_remove.getRelativeUrl()
    container, _, object_id = path.rpartition('/')
    parent = self.portal.unrestrictedTraverse(container)
    parent.manage_delObjects([object_id])
    self.commit()

  def createWendelinTelecomUser(self, reference, project, function):
    # Create and validate a new Person with an assignment
    # linked to the provided project and function
    # Also generate and validate an ERP5 login for the Person
    user = self.portal.person_module.newContent(
      portal_type='Person',
      reference=reference
    )
    user.newContent(
      portal_type='Assignment',
      destination_project=project,
      function=function
    ).open()
    user.newContent(
      portal_type='ERP5 Login',
      reference=reference,
      password=reference
    ).validate()
    user.validate()
    self.tic()

    return user

  def registerOrs(
    self,
    tag_hostname_seed=None,
    tag_comp_id_seed=None,
    tag_enb_id_seed=None,
    test_suffix=True
  ):
    # Create a Data Acquisition Unit and related Data Supply
    # with a tag constructed from the provided seeds.
    # If any seed is NOT defined, it is generated at random.
    if tag_hostname_seed is None:
      tag_hostname_seed = generateRandomString(length=3, only_digits=True)
    if tag_comp_id_seed is None:
      tag_comp_id_seed = generateRandomString(length=4, only_digits=True)
    if tag_enb_id_seed is None:
      tag_enb_id_seed = generateRandomString(length=5, hexadecimal=True)

    ors_tag = 'ors%s' % tag_hostname_seed
    # Only include a subsequent section if a non-empty string is explicitly provided for it
    if tag_comp_id_seed != '':
      ors_tag += '_COMP-%s' % tag_comp_id_seed
    if tag_enb_id_seed != '':
      ors_tag += '_e0x%s' % tag_enb_id_seed
    # If test suffix is false, manual cleanup will be needed!
    if test_suffix:
      ors_tag += 'Test'

    response = self.portal.ERP5Site_registerOrs(ors_tag)
    self.tic()

    # Fetch created items from the catalog
    data_acquisition_unit = self.portal.portal_catalog.getResultValue(
      portal_type='Data Acquisition Unit',
      reference=ors_tag,
      validation_state='validated'
    )
    data_supply = None
    if data_acquisition_unit is not None:
      data_supply = data_acquisition_unit.DataAcquisitionUnit_createOrsDataSupply(batch=1)

    # Return all associated items
    return {
      'response': response,
      'data_acquisition_unit': data_acquisition_unit,
      'data_supply': data_supply
    }

  def registerOrsClientProject(self, reference_seed=None, client_user_reference_seed=None):
    # Create a client project with the provided reference seed,
    # as well as a related ERP5 Person with the same reference seed, and an ERP5 login.
    # If NOT defined, reference_seed is generated at random.
    # If defined, client_user_reference_seed overrides reference_seed for the client user.
    if reference_seed is None:
      reference_seed = generateRandomString()
    project_reference = 'test_project_%s' % reference_seed
    project_title = 'Test Project %s' % reference_seed
    client_email = 'test_user_%s@test.wendelin-tele.com' \
      % (client_user_reference_seed or reference_seed)
    client_user_reference = client_email.split('@')[0]

    # Call the script responsible for creating the project and the associated user
    # Store the JSON response
    response = self.portal.ProjectModule_registerOrsClientProject(
      project_reference,
      project_title,
      client_email,
      form_id='testing'
    )
    self.tic()

    # Fetch created items from the catalog
    project = self.portal.portal_catalog.getResultValue(
      portal_type='Project',
      reference=project_reference,
      title=project_title,
      validation_state='validated'
    )
    client_user = self.portal.portal_catalog.getResultValue(
      portal_type='Person',
      reference=client_user_reference,
      default_email_text=client_email,
      validation_state='validated'
    )

    # Return all associated items
    return {
      'response': response,
      'project': project,
      'client_user': client_user
    }

  def ingestOrsLogDataFromFluentd(self, log_data, ors_tag):
    # Simulate a fluentd instance sending the provided log data to Wendelin for ingestion
    reference = 'ors.%s' % ors_tag
    body = msgpack.packb([0, log_data], use_bin_type=True)
    env = {'CONTENT_TYPE': 'application/octet-stream'}
    path = self.ors_enb_log_ingestion.getPath() + '/ingest?reference=' + reference
    publish_kw = dict(
      env=env,
      user=self.ingestor_user.Person_getUserId(),
      request_method='POST',
      stdin=BytesIO(body)
    )
    return self.publish(path, **publish_kw)

  def getDataIngestion(self, data_acquisition_unit):
    # Retrieve a Data Ingestion linked to the provided Data Acquisition Unit
    for line in data_acquisition_unit.getAggregateRelatedValueList(
      portal_type='Data Ingestion Line'
    ):
      data_ingestion = line.getParentValue()
      if data_ingestion is not None:
        return data_ingestion

  def getDataStream(self, data_acquisition_unit):
    # Retrieve a Data Stream linked to the provided Data Acquisition Unit
    for line in data_acquisition_unit.getAggregateRelatedValueList(
      portal_type='Data Ingestion Line'
    ):
      data_stream = line.getAggregateValue(portal_type='Data Stream')
      if data_stream is not None:
        return data_stream

  def getDataAnalysis(self, data_supply):
    # Retrieve a Data Analysis linked to the provided Data Supply
    for data_analysis in data_supply.getSpecialiseRelatedValueList(
      portal_type='Data Analysis'
    ):
      if data_analysis is not None:
        return data_analysis

  def getDataArrays(self, data_analysis):
    # Retrieve the Data Arrays linked to the provided Data Analysis
    data_array_list = []
    for line in data_analysis.contentValues(portal_type='Data Analysis Line'):
      data_array = line.getAggregateValue(portal_type='Data Array')
      if data_array is not None:
        data_array_list.append(data_array)
    return data_array_list

  def getProgressIndicator(self, data_analysis):
    # Retrieve the Progress Indicator linked to the provided Data Analysis
    for line in data_analysis.contentValues(portal_type="Data Analysis Line"):
      if line.getResourceValue().getPortalType() == "Data Product" \
        and line.getQuantity() == -1:
        progress_indicator = line.getAggregateProgressIndicatorValue()
        if progress_indicator is not None:
          return progress_indicator

  def getOrsLogIngestionItems(self, log_data, reference, stop_data_analysis=False):
    # Simulate an ingestion of the provided log data
    response = self.ingestOrsLogDataFromFluentd(log_data, reference)
    self.tic()

    # Retrieve all items linked to the ingestion
    data_acquisition_unit = self.portal.portal_catalog.getResultValue(
      portal_type='Data Acquisition Unit',
      reference=reference
    )
    data_supply = data_acquisition_unit.DataAcquisitionUnit_getOrsDataSupply()
    self.tic()

    data_ingestion = self.getDataIngestion(data_acquisition_unit)

    data_stream = self.getDataStream(data_acquisition_unit)

    # Manually call the data analysis alarms to process the data into KPIs ASAP
    self.portal.portal_alarms.wendelin_handle_analysis.activeSense()
    self.tic()
    self.portal.portal_alarms.wendelin_handle_analysis.activeSense()
    self.tic()

    data_analysis = self.getDataAnalysis(data_supply)
    if stop_data_analysis and data_analysis.getSimulationState() == 'started':
      data_analysis.stop()
      self.tic()

    data_array_list = self.getDataArrays(data_analysis)

    progress_indicator = self.getProgressIndicator(data_analysis)

    # Return all associated items
    return {
      'response': response,
      'data_acquisition_unit': data_acquisition_unit,
      'data_supply': data_supply,
      'data_ingestion': data_ingestion,
      'data_stream': data_stream,
      'data_analysis': data_analysis,
      'data_array_list': data_array_list,
      'progress_indicator': progress_indicator
    }

  def getOrsEnbKpiDict(self, data_array_url, kpi_type):
    kpi_path = self.ors_enb_kpi_endpoint_path + '?data_array_url=' + \
      data_array_url + '&kpi_type=' + kpi_type
    publish_kw = dict(
      user='ERP5TypeTestCase'
    )
    response = self.publish(kpi_path, **publish_kw)
    return json.loads(response.getBody())

  def checkDocumentPermissions(
    self, user, document, user_can_view, user_can_modify, user_can_add
  ):
    user_id = user.Person_getUserId()

    # Check if the provided user can access and view the document
    if user_can_view:
      self.assertUserCanAccessDocument(user_id, document)
      self.assertUserCanViewDocument(user_id, document)
    else:
      self.failIfUserCanAccessDocument(user_id, document)
      self.failIfUserCanViewDocument(user_id, document)

    # Check if the provided user can edit the document
    if user_can_modify:
      self.assertUserCanModifyDocument(user_id, document)
    else:
      self.failIfUserCanModifyDocument(user_id, document)

    # Check if the provided user can add a document
    if user_can_add:
      self.assertUserCanAddDocument(user_id, document)
    else:
      self.failIfUserCanAddDocument(user_id, document)

  def checkIngestionDocumentsPermissions(self, user, ingestion_item_dict):
    user_destination_project = None
    user_function_list = None
    for assignment in user.contentValues(portal_type='Assignment'):
      if assignment.getValidationState() == 'open':
        user_destination_project = assignment.getDestinationProject()
        user_function_list = assignment.getFunctionList()

    ors_destination_project = ingestion_item_dict['data_supply'].getDestinationProject()
    same_project = (user_destination_project is not None) \
      and (ors_destination_project is not None) \
      and (user_destination_project == ors_destination_project)

    user_is_admin = 'administrator' in user_function_list
    user_is_ingestor = 'ingestor' in user_function_list

    # A client can only view a Data Acquisition Unit (ORS)
    # if they are related to the same project
    # An administrator can view and edit all of them, as well as add one
    # An ingestor can view any of them
    self.checkDocumentPermissions(
      user,
      ingestion_item_dict['data_acquisition_unit'],
      same_project or user_is_admin or user_is_ingestor,
      user_is_admin,
      user_is_admin
    )

    # Same as above for a Data Supply (required for computing security roles on users)
    # Also the same for Data Supply Lines
    self.checkDocumentPermissions(
      user,
      ingestion_item_dict['data_supply'],
      same_project or user_is_admin or user_is_ingestor,
      user_is_admin,
      user_is_admin
    )
    for data_supply_line in ingestion_item_dict['data_supply'] \
      .contentValues(portal_type='Data Supply Line'):
      self.checkDocumentPermissions(
        user,
        data_supply_line,
        same_project or user_is_admin or user_is_ingestor,
        user_is_admin,
        user_is_admin
      )

    # An administrator has all rights to a Data Ingestion (for management actions)
    # An ingestor also has all rights to a Data Ingestion (for managing ingestions)
    self.checkDocumentPermissions(
      user,
      ingestion_item_dict['data_ingestion'],
      user_is_admin or user_is_ingestor,
      user_is_admin or user_is_ingestor,
      user_is_admin or user_is_ingestor
    )

    # An administrator can view a Data Stream
    # An ingestor has all rights to a Data Stream (to append new log data to it)
    self.checkDocumentPermissions(
      user,
      ingestion_item_dict['data_stream'],
      user_is_admin or user_is_ingestor,
      user_is_ingestor,
      user_is_ingestor
    )

    # A client can only view a Data Analysis
    # if they are related to the same project (for KPI graphing)
    # An administrator can view and edit all of them (for management actions)
    # Same thing for Data Analysis Lines
    self.checkDocumentPermissions(
      user,
      ingestion_item_dict['data_analysis'],
      user_is_admin or same_project,
      user_is_admin,
      user_is_admin
    )
    for data_analysis_line in ingestion_item_dict['data_analysis'] \
      .contentValues(portal_type='Data Analysis Line'):
      self.checkDocumentPermissions(
        user,
        data_analysis_line,
        user_is_admin or same_project,
        user_is_admin,
        user_is_admin
      )

    # A client can only view a Data Array if they are related to the same project
    # An administrator can view all of them
    for data_array in ingestion_item_dict['data_array_list']:
      self.checkDocumentPermissions(
        user,
        data_array,
        user_is_admin or same_project,
        False,
        False
      )
      for data_array_line in data_array \
        .contentValues(portal_type='Data Array Line'):
        self.checkDocumentPermissions(
          user,
          data_array_line,
          user_is_admin or same_project,
          False,
          False
        )

    # Only an administrator can view a Progress Indicator (for management actions)
    self.checkDocumentPermissions(
      user,
      ingestion_item_dict['progress_indicator'],
      user_is_admin,
      False,
      False
    )

  def checkModulePermissions(self, user):
    user_function_list = None
    for assignment in user.contentValues(portal_type='Assignment'):
      if assignment.getValidationState() == 'open':
        user_function_list = assignment.getFunctionList()

    user_is_client = 'user' in user_function_list
    user_is_admin = 'administrator' in user_function_list
    user_is_ingestor = 'ingestor' in user_function_list

    # Everyone can view the Data Product module (for KPI graphing)
    # Everyone can also view the two data products
    # used in the KPI calculation process (for KPI graphing)
    self.checkDocumentPermissions(
      user,
      self.portal.data_product_module,
      True,
      False,
      False
    )
    ors_enb_kpi = self.portal.portal_catalog.getResultValue(
      portal_type='Data Product',
      reference='ors_enb_kpi',
      validation_state='validated'
    )
    self.checkDocumentPermissions(user, ors_enb_kpi, True, False, False)
    ors_enb_log_data = self.portal.portal_catalog.getResultValue(
      portal_type='Data Product',
      reference='ors_enb_log_data',
      validation_state='validated'
    )
    self.checkDocumentPermissions(user, ors_enb_log_data, True, False, False)

    # Only ingestors can view the Data Operation Module,
    # as well as the two Data Operations required for ORS eNB log ingestion
    self.checkDocumentPermissions(
      user,
      self.portal.data_operation_module,
      user_is_ingestor,
      False,
      False
    )
    ingest_ors_enb_log_data = self.portal.portal_catalog.getResultValue(
      portal_type='Data Operation',
      reference='ingest_ors_enb_log_data',
      validation_state='validated'
    )
    self.checkDocumentPermissions(
      user,
      ingest_ors_enb_log_data,
      user_is_ingestor,
      False,
      False
    )
    calculate_ors_kpi = self.portal.portal_catalog.getResultValue(
      portal_type='Data Operation',
      reference='calculate_ors_enb_kpi',
      validation_state='validated'
    )
    self.checkDocumentPermissions(
      user,
      calculate_ors_kpi,
      user_is_ingestor,
      False,
      False
    )

    # Everyone can view the Data Acquisition Unit and Data Supply modules
    # Only administrators can add items to them
    self.checkDocumentPermissions(
      user,
      self.portal.data_acquisition_unit_module,
      True,
      False,
      user_is_admin
    )
    self.checkDocumentPermissions(
      user,
      self.portal.data_supply_module,
      True,
      False,
      user_is_admin
    )

    # Only clients and administrator can view the Data Transformation module
    # (for KPI graphing)
    # Only they can also view the data transformation used to produce the KPIs
    # (for KPI graphing)
    self.checkDocumentPermissions(
      user,
      self.portal.data_transformation_module,
      user_is_client or user_is_admin,
      False,
      False
    )
    data_transformation = self.portal.portal_catalog.getResultValue(
      portal_type='Data Transformation',
      reference='ors_enb_log_data_transformation',
      validation_state='validated'
    )
    self.checkDocumentPermissions(
      user,
      data_transformation,
      user_is_client or user_is_admin,
      False,
      False
    )

    # Only ingestors and administrators can view
    # the Data Ingestion and Data Stream modules
    # Only ingestors can add new Data Ingestions and Data Streams
    self.checkDocumentPermissions(
      user,
      self.portal.data_ingestion_module,
      user_is_ingestor or user_is_admin,
      False,
      user_is_ingestor
    )
    self.checkDocumentPermissions(
      user,
      self.portal.data_stream_module,
      user_is_ingestor or user_is_admin,
      False,
      user_is_ingestor
    )

    # Only administrators can view the Progress Indicator Module
    self.checkDocumentPermissions(
      user,
      self.portal.progress_indicator_module,
      user_is_admin,
      False,
      False
    )

    # Only administrators can view the Data Analysis module
    self.checkDocumentPermissions(
      user,
      self.portal.data_analysis_module,
      user_is_admin,
      False,
      False
    )

    # Only clients and administrators can view the Data Array module
    # (for KPI graphing)
    self.checkDocumentPermissions(
      user,
      self.portal.data_array_module,
      user_is_client or user_is_admin,
      False,
      False
    )

    # Only administrators have access to the Person and Project modules
    # and can add items to them for client management purposes
    self.checkDocumentPermissions(
      user,
      self.portal.project_module,
      user_is_admin,
      False,
      user_is_admin
    )
    self.checkDocumentPermissions(
      user,
      self.portal.person_module,
      user_is_admin,
      False,
      user_is_admin
    )

  def test_01_createOrsDataSupply(self):
    '''
    Test the action which creates an ORS Data Supply from a Data Acquisition Unit.
    Check that the Data Supply is indeed created and validated.
    Also check pathological cases considered by the script:
    - Data Acquisition Unit has no reference
    - Several Data Supplies exist for a Data Acquisition Unit.
    '''
    reference = 'test_%s' % generateRandomString()

    # Create and validate a Data Acquisition Unit
    data_acquisition_unit = self.portal.data_acquisition_unit_module.newContent(
      portal_type='Data Acquisition Unit',
      reference=reference
    )
    data_acquisition_unit.validate()
    self.tic()

    # Call the script which creates a related Data Supply
    created_data_supply = data_acquisition_unit.DataAcquisitionUnit_createOrsDataSupply(batch=1)
    self.tic()

    # Check that the Data Supply exists and is validated
    self.assertTrue(created_data_supply is not None)
    self.assertTrue(created_data_supply.getValidationState() == 'validated')

    # Call the script again to retrieve the same Data Supply
    retrieved_data_supply = data_acquisition_unit.DataAcquisitionUnit_createOrsDataSupply(batch=1)

    # Check that both Data Supplies are identical
    self.assertTrue(retrieved_data_supply == created_data_supply)

    # Pathological case: create another identical Data Supply
    created_data_supply.invalidate()
    self.tic()
    data_acquisition_unit.DataAcquisitionUnit_createOrsDataSupply(batch=1)
    created_data_supply.validate()
    self.tic()

    re_retrieved_data_supply = data_acquisition_unit.DataAcquisitionUnit_createOrsDataSupply(batch=1)

    self.assertTrue(re_retrieved_data_supply == created_data_supply)

    # Pathological case: create a Data Acquisition Unit without a reference
    data_acquisition_unit = self.portal.data_acquisition_unit_module.newContent(
      portal_type='Data Acquisition Unit',
    )
    data_acquisition_unit.validate()
    self.tic()
    self.addCleanup(self._removeDocument, data_acquisition_unit)

    # Call the script which should NOT create a Data Supply (no reference to copy over)
    none_data_supply = data_acquisition_unit.DataAcquisitionUnit_createOrsDataSupply(batch=1)
    self.tic()

    self.assertTrue(none_data_supply is None)

  def test_02_registerOrsClientProject(self):
    '''
    Test the action performed by Administrator users in the Project module
    to register a new client project.
    Check the successful case as well as all error cases.
    '''

    # Generate a random reference seed, call the script and retrieve the associated items
    # This first call should succeed
    reference_seed = generateRandomString()
    project_item_dict = self.registerOrsClientProject(reference_seed=reference_seed)

    # Check that both the project and the client user have been created
    self.assertTrue(project_item_dict['project'] is not None)
    self.assertTrue(project_item_dict['client_user'] is not None)

    # Call the script a second time with the same reference
    # This should not do anything as the project already exists
    repeated_project_item_dict = self.registerOrsClientProject(reference_seed=reference_seed)

    # Check that both the project and the client user are identical to the previous ones
    self.assertTrue(repeated_project_item_dict['project'] \
      == project_item_dict['project'])
    self.assertTrue(repeated_project_item_dict['client_user'] \
      == repeated_project_item_dict['client_user'])

    # Create a new reference seed for the project
    # but reuse the previous reference for the client user account
    new_project_reference_seed = generateRandomString()
    while new_project_reference_seed == reference_seed:
      new_project_reference_seed = generateRandomString()
    # Call the script a third time, keeping the same reference seed as before ONLY for the client user account
    # This should also error out as the client user account already exists
    new_project_item_dict = self.registerOrsClientProject(
      reference_seed=new_project_reference_seed,
      client_user_reference_seed=reference_seed
    )

    # Check that the new project is NOT created
    # and that the client user is the same as previously
    self.assertTrue(new_project_item_dict['project'] is None)
    self.assertTrue(new_project_item_dict['client_user'] \
      == project_item_dict['client_user'])

  def test_03_1_registerOrsValid(self):
    '''
    Test the script called during slave instantiation in SlapOS
    by an ORS to automatically register itself.
    Check the straightforward successful case where an ORS
    changes its radio ID several times and re-registers.
    '''

    # Call the script with an initial seed setup
    tag_hostname_seed = generateRandomString(length=3, only_digits=True)
    tag_comp_id_seed = generateRandomString(length=4, only_digits=True)
    tag_enb_id_seed = generateRandomString(length=5, hexadecimal=True)
    ors_item_dict = self.registerOrs(
      tag_hostname_seed=tag_hostname_seed,
      tag_comp_id_seed=tag_comp_id_seed,
      tag_enb_id_seed=tag_enb_id_seed
    )

    # Parse the JSON response and check that it indicates a success
    response_dict = json.loads(ors_item_dict['response'])
    self.assertTrue(response_dict['status'] == "ok")
    self.assertTrue(
      response_dict['message'] == "ORS with tag %s successfully registered." \
      % ors_item_dict['data_acquisition_unit'].getReference()
    )

    # Check that the Data Acquisition Unit and Data Supply have been created
    self.assertTrue(ors_item_dict['data_acquisition_unit'] is not None)
    self.assertTrue(ors_item_dict['data_supply'] is not None)

    # Call the script a second time with the same seeds
    # This should not do anything as the Data Acquisition Unit already exists
    repeated_ors_item_dict = self.registerOrs(
      tag_hostname_seed=tag_hostname_seed,
      tag_comp_id_seed=tag_comp_id_seed,
      tag_enb_id_seed=tag_enb_id_seed
    )

    # Parse the JSON response and check the status and message
    response_dict = json.loads(repeated_ors_item_dict['response'])
    self.assertTrue(response_dict['status'] == "ok")
    self.assertTrue(
      response_dict['message'] == "ORS with tag %s already exists." \
      % ors_item_dict['data_acquisition_unit'].getReference()
    )

    # Now, link the original Data Supply to a client project
    project_a_item_dict = self.registerOrsClientProject()
    project_a_url = project_a_item_dict['project'].getRelativeUrl()
    ors_item_dict['data_supply'].setDestinationProject(project_a_url)

    # Generate a new valid enb_id seed
    new_tag_enb_id_seed = generateRandomString(length=5, hexadecimal=True)
    # Call the script to simulate the ORS re-registering with another eNB identifier
    new_enb_id_ors_item_dict = self.registerOrs(
      tag_hostname_seed=tag_hostname_seed,
      tag_comp_id_seed=tag_comp_id_seed,
      tag_enb_id_seed=new_tag_enb_id_seed
    )

    # Parse the JSON response and check the status and message
    response_dict = json.loads(new_enb_id_ors_item_dict['response'])
    self.assertTrue(response_dict['status'] == "ok")
    self.assertTrue(
      response_dict['message'] == "ORS with tag %s successfully registered." \
      % new_enb_id_ors_item_dict['data_acquisition_unit'].getReference()
    )

    # Check that the Data Acquisition Unit and Data Supply have been created
    # and that the new Data Supply has automatically been linked to the project
    self.assertTrue(new_enb_id_ors_item_dict['data_acquisition_unit'] is not None)
    self.assertTrue(new_enb_id_ors_item_dict['data_supply'] is not None)
    self.assertTrue(new_enb_id_ors_item_dict['data_supply'].getDestinationProject() == project_a_url)

    # Now, link the above Data Supply to a second project
    project_b_item_dict = self.registerOrsClientProject()
    new_enb_id_ors_item_dict['data_supply'] \
      .setDestinationProject(project_b_item_dict['project'].getRelativeUrl())

    # Generate another valid enb_id seed
    another_tag_enb_id_seed = generateRandomString(length=5, hexadecimal=True)
    while another_tag_enb_id_seed == new_tag_enb_id_seed:
      another_tag_enb_id_seed = generateRandomString(length=5, hexadecimal=True)
    # Call the script to simulate the same ORS
    # registering a third time with another eNB identifier
    another_enb_id_ors_item_dict = self.registerOrs(
      tag_hostname_seed=tag_hostname_seed,
      tag_comp_id_seed=tag_comp_id_seed,
      tag_enb_id_seed=another_tag_enb_id_seed
    )

    # Parse the JSON response and check the status and message
    response_dict = json.loads(another_enb_id_ors_item_dict['response'])
    self.assertTrue(response_dict['status'] == "ok")
    self.assertTrue(
      response_dict['message'] == "ORS with tag %s successfully registered." \
      % another_enb_id_ors_item_dict['data_acquisition_unit'].getReference()
    )

    # Check that the Data Acquisition Unit and Data Supply have been created
    self.assertTrue(another_enb_id_ors_item_dict['data_acquisition_unit'] is not None)
    self.assertTrue(another_enb_id_ors_item_dict['data_supply'] is not None)
    # As the ORS has been linked to two different projects already,
    # it cannot be automatically decided to which project this version should be assigned to
    self.assertTrue(another_enb_id_ors_item_dict['data_supply'].getDestinationProject() is None)

    # Generate a new set of seeds
    new_tag_hostname_seed = generateRandomString(length=3, only_digits=True)
    new_tag_comp_id_seed = generateRandomString(length=4, only_digits=True)
    # Call the script with a tag that does not contain an eNB identifier
    no_enb_id_ors_item_dict = self.registerOrs(
      tag_hostname_seed=new_tag_hostname_seed,
      tag_comp_id_seed=new_tag_comp_id_seed,
      tag_enb_id_seed=''
    )

    # Parse the JSON response and check that it indicates a success
    response_dict = json.loads(no_enb_id_ors_item_dict['response'])
    self.assertTrue(response_dict['status'] == "ok")
    self.assertTrue(
      response_dict['message'] == "ORS with tag %s successfully registered." \
      % no_enb_id_ors_item_dict['data_acquisition_unit'].getReference()
    )

    # Check that the Data Acquisition Unit and Data Supply have been created
    self.assertTrue(no_enb_id_ors_item_dict['data_acquisition_unit'] is not None)
    self.assertTrue(no_enb_id_ors_item_dict['data_supply'] is not None)

  def test_03_2_registerOrsInvalid(self):
    '''
    Test the script called during slave instantiation in SlapOS
    by an ORS to automatically register itself.
    Check all error-returning cases.
    '''

    tag_hostname_seed = generateRandomString(length=3, only_digits=True)
    tag_comp_id_seed = generateRandomString(length=4, only_digits=True)
    tag_enb_id_seed = generateRandomString(length=5, hexadecimal=True)

    # Generate a hostname seed that will cause the tag to have too many underscores
    too_long_tag_hostname_seed = 'invalid_hostname'
    # Call the script with this seed setup
    # This should error out as the tag has too many underscore-separated sections
    too_long_tag_ors_item_dict = self.registerOrs(
      tag_hostname_seed=too_long_tag_hostname_seed,
      tag_comp_id_seed=tag_comp_id_seed,
      tag_enb_id_seed=tag_enb_id_seed
    )

    # Parse the JSON response and check the error message
    response_dict = json.loads(too_long_tag_ors_item_dict['response'])
    self.assertTrue(response_dict['status'] == "error")
    self.assertTrue(
      response_dict['message'] == "Invalid ORS tag ors%s_COMP-%s_e0x%sTest found" \
      % (too_long_tag_hostname_seed, tag_comp_id_seed, tag_enb_id_seed)
    )

    # Check that the Data Acquisition Unit and Data Supply have NOT been created
    self.assertTrue(too_long_tag_ors_item_dict['data_acquisition_unit'] is None)
    self.assertTrue(too_long_tag_ors_item_dict['data_supply'] is None)

    # Now, call the script with only the first section in the tag: 'orsXXX'
    # This should error out as the tag has too few underscore-separated sections
    too_long_tag_ors_item_dict = self.registerOrs(
      tag_hostname_seed=tag_hostname_seed,
      tag_comp_id_seed='',
      tag_enb_id_seed=''
    )

    # Parse the JSON response and check the error message
    response_dict = json.loads(too_long_tag_ors_item_dict['response'])
    self.assertTrue(response_dict['status'] == "error")
    self.assertTrue(response_dict['message'] == "Invalid ORS tag ors%sTest found" % tag_hostname_seed)

    # Check that the Data Acquisition Unit and Data Supply have NOT been created
    self.assertTrue(too_long_tag_ors_item_dict['data_acquisition_unit'] is None)
    self.assertTrue(too_long_tag_ors_item_dict['data_supply'] is None)

  def test_03_3_registerOrsNonStandard(self):
    '''
    Test the script called during slave instantiation in SlapOS
    by an ORS to automatically register itself.
    Check the cases where an ORS re-registers itself
    after the Data Acquisition Unit or the Data Supply is deleted.
    '''

    # Call the script with an initial seed setup
    tag_hostname_seed = generateRandomString(length=3, only_digits=True)
    tag_comp_id_seed = generateRandomString(length=4, only_digits=True)
    tag_enb_id_seed = generateRandomString(length=5, hexadecimal=True)
    ors_item_dict = self.registerOrs(
      tag_hostname_seed=tag_hostname_seed,
      tag_comp_id_seed=tag_comp_id_seed,
      tag_enb_id_seed=tag_enb_id_seed
    )

    # Parse the JSON response and check that it indicates a success
    response_dict = json.loads(ors_item_dict['response'])
    self.assertTrue(response_dict['status'] == "ok")
    self.assertTrue(
      response_dict['message'] == "ORS with tag %s successfully registered." \
      % ors_item_dict['data_acquisition_unit'].getReference()
    )

    # Check that the Data Acquisition Unit and Data Supply have been created
    self.assertTrue(ors_item_dict['data_acquisition_unit'] is not None)
    self.assertTrue(ors_item_dict['data_supply'] is not None)

    # Now, link the original Data Supply to a client project...
    project_a_item_dict = self.registerOrsClientProject()
    project_a_url = project_a_item_dict['project'].getRelativeUrl()
    ors_item_dict['data_supply'].setDestinationProject(project_a_url)

    # ...and delete the Data Acquisition Unit
    ors_item_dict['data_acquisition_unit'].invalidate()
    ors_item_dict['data_acquisition_unit'].delete()
    self.tic()

    # Call the script a second time with the same seeds
    # This should re-create the Data Acquisition Unit and the Data Supply
    repeated_ors_item_dict = self.registerOrs(
      tag_hostname_seed=tag_hostname_seed,
      tag_comp_id_seed=tag_comp_id_seed,
      tag_enb_id_seed=tag_enb_id_seed
    )

    # Parse the JSON response and check the status and message
    response_dict = json.loads(repeated_ors_item_dict['response'])
    self.assertTrue(response_dict['status'] == "ok")
    self.assertTrue(
      response_dict['message'] == "ORS with tag %s successfully registered." \
      % ors_item_dict['data_acquisition_unit'].getReference()
    )

    # Now, link the above Data Supply to the same project...
    repeated_ors_item_dict['data_supply'] \
      .setDestinationProject(project_a_item_dict['project'].getRelativeUrl())

    # ...and delete the Data Supply
    repeated_ors_item_dict['data_supply'].invalidate()
    repeated_ors_item_dict['data_supply'].delete()
    self.tic()

    # Call the script a third time, still with the same seeds
    # This should not do anything as the Data Acquisition Unit already exists
    re_repeated_ors_item_dict = self.registerOrs(
      tag_hostname_seed=tag_hostname_seed,
      tag_comp_id_seed=tag_comp_id_seed,
      tag_enb_id_seed=tag_enb_id_seed
    )

    # Parse the JSON response and check the status and message
    response_dict = json.loads(re_repeated_ors_item_dict['response'])
    self.assertTrue(response_dict['status'] == "ok")
    self.assertTrue(
      response_dict['message'] == "ORS with tag %s already exists." \
      % ors_item_dict['data_acquisition_unit'].getReference()
    )

    # Generate a new valid enb_id seed
    new_tag_enb_id_seed = generateRandomString(length=5, hexadecimal=True)
    # Call the script to simulate the ORS re-registering with another eNB identifier
    # Even with the previously deleted Data Acquisition Unit and Data Supply,
    # this should not error out
    new_enb_id_ors_item_dict = self.registerOrs(
      tag_hostname_seed=tag_hostname_seed,
      tag_comp_id_seed=tag_comp_id_seed,
      tag_enb_id_seed=new_tag_enb_id_seed
    )

    # Parse the JSON response and check the status and message
    response_dict = json.loads(new_enb_id_ors_item_dict['response'])
    self.assertTrue(response_dict['status'] == "ok")
    self.assertTrue(
      response_dict['message'] == "ORS with tag %s successfully registered." \
      % new_enb_id_ors_item_dict['data_acquisition_unit'].getReference()
    )

    # Check that the Data Acquisition Unit and Data Supply have been created
    self.assertTrue(new_enb_id_ors_item_dict['data_acquisition_unit'] is not None)
    self.assertTrue(new_enb_id_ors_item_dict['data_supply'] is not None)
    # As the two first registrations are not in valid states anymore,
    # they should not be considered when deciding project attribution
    # This Data Supply should therefore not be linked to the project
    self.assertTrue(new_enb_id_ors_item_dict['data_supply'].getDestinationProject() is None)

    # Now, link the above Data Supply to the project
    # This should allow the next registration to be linked to it automatically
    new_enb_id_ors_item_dict['data_supply'] \
      .setDestinationProject(project_a_item_dict['project'].getRelativeUrl())

    # Generate another valid enb_id seed
    another_tag_enb_id_seed = generateRandomString(length=5, hexadecimal=True)
    while another_tag_enb_id_seed == new_tag_enb_id_seed:
      another_tag_enb_id_seed = generateRandomString(length=5, hexadecimal=True)
    # Call the script to simulate the same ORS
    # registering a third time with another eNB identifier
    another_enb_id_ors_item_dict = self.registerOrs(
      tag_hostname_seed=tag_hostname_seed,
      tag_comp_id_seed=tag_comp_id_seed,
      tag_enb_id_seed=another_tag_enb_id_seed
    )

    # Parse the JSON response and check the status and message
    response_dict = json.loads(another_enb_id_ors_item_dict['response'])
    self.assertTrue(response_dict['status'] == "ok")
    self.assertTrue(
      response_dict['message'] == "ORS with tag %s successfully registered." \
      % another_enb_id_ors_item_dict['data_acquisition_unit'].getReference()
    )

    # Check that the Data Acquisition Unit and Data Supply have been created
    # and that the new Data Supply has automatically been linked to the project
    self.assertTrue(another_enb_id_ors_item_dict['data_acquisition_unit'] is not None)
    self.assertTrue(another_enb_id_ors_item_dict['data_supply'] is not None)
    self.assertTrue(another_enb_id_ors_item_dict['data_supply'].getDestinationProject() == project_a_url)

  def test_04_registerVirtualOrsAction(self):
    '''
    Test the scripts called by the Register Virtual ORS action which registers a virtual ORS
    used to upload an enb.xlog to the platform through an arbitrary fluentbit instance.
    Check all possible cases.
    '''

    tag_comp_id = generateRandomString(length=4, only_digits=True)
    tag_title = 'Test%s' % generateRandomString(length=3, only_digits=True)

    # Register the virtual ORS with the given tag components
    data_acquisition_unit = self.portal.DataAcquisitionUnitModule_registerVirtualOrs(
      tag_comp_id,
      tag_title,
      batch=1
    )
    self.tic()
    data_supply = data_acquisition_unit.DataAcquisitionUnit_getOrsDataSupply()

    # Cannot check correctness of the timestamp suffix
    expected_tag_start = 'orsVIRT_COMP-%s_%s' % (tag_comp_id, tag_title)
    # Check that the created Data Acquisition Unit has the correct components
    self.assertTrue(data_acquisition_unit.getReference().startswith(expected_tag_start))
    # Also check that the related Data Supply has correctly been created
    self.assertEqual(data_supply.getReference(), data_acquisition_unit.getReference())

  def test_05_1_ingestValidOrsLogDataFromFluentd(self, data_key="valid"):
    '''
    Test a simple valid ORS log ingestion: simulate a fluentd gateway forwarding valid ORS logs to the platform,
    and check that all items related to the ingestion are valid.
    Also check the fetching of KPI values through the dedicated API endpoint.
    The logs are correct here, even though some are expectedly out of chronological order.
    '''

    # Register the ORS
    ors_item_dict = self.registerOrs()
    ors_tag = ors_item_dict['data_acquisition_unit'].getReference()

    # Get the correct data logs according to what is being tested
    test_ors_example_logs = []
    if data_key == "valid":
      test_ors_example_logs = [self.test_ors_example_log_valid]
    elif data_key == "invalid":
      test_ors_example_logs = [
        self.test_ors_example_log_invalid_split_1,
        self.test_ors_example_log_invalid_split_2
      ]
    elif data_key == "duplicated":
      test_ors_example_logs = [self.test_ors_example_log_with_duplicates]
    elif data_key == "empty":
      test_ors_example_logs = [self.test_ors_example_log_empty]

    # Perform ingestions, and keep only the last item dictionary
    # as they are all identical
    ingestion_item_dicts = [
      self.getOrsLogIngestionItems(ors_log, ors_tag) \
      for ors_log in test_ors_example_logs
    ]
    ingestion_item_dict = ingestion_item_dicts[-1]

    # In all cases, check that all items related to the ingestions exist
    self.assertEqual(NO_CONTENT, ingestion_item_dict['response'].getStatus())
    self.assertTrue(ingestion_item_dict['data_acquisition_unit'] is not None)
    self.assertTrue(ingestion_item_dict['data_supply'] is not None)
    self.assertTrue(ingestion_item_dict['data_ingestion'] is not None)
    self.assertTrue(ingestion_item_dict['data_stream'].getData() is not None)
    self.assertTrue(ingestion_item_dict['data_analysis'] is not None)
    self.assertTrue(all(data_array is not None for data_array in ingestion_item_dict['data_array_list']))
    self.assertTrue(ingestion_item_dict['progress_indicator'] is not None)

    # Check that the value of the progress indicator is equal to the size of the Data Stream:
    # i.e. that all of the ingested data has been processed into KPIs
    self.assertTrue(
      ingestion_item_dict['progress_indicator'].getIntOffsetIndex() \
        == ingestion_item_dict['data_stream'].getSize()
    )

    # Check that the Data Arrays containing the KPI data have correctly been initialized
    self.assertTrue(
      ingestion_item_dict['data_acquisition_unit'].DataAcquisitionUnit_getERabDataArrayUrl() \
        is not None
    )
    self.assertTrue(
      ingestion_item_dict['data_acquisition_unit'].DataAcquisitionUnit_getEUtranDataArrayUrl() \
        is not None
    )

    e_rab_array_shape = None
    e_rab_array_dtype = [
      ('vt', '<f8'),
      ('vInitialEPSBEstabSR_lo', '<f8'),
      ('vInitialEPSBEstabSR_hi', '<f8'),
      ('vAddedEPSBEstabSR_lo', '<f8'),
      ('vAddedEPSBEstabSR_hi', '<f8')
    ]
    e_utran_array_shape = None
    e_utran_array_dtype = [
      ('evt', '<f8'),
      ('dl_lo', '<f8'),
      ('dl_hi', '<f8'),
      ('ul_lo', '<f8'),
      ('ul_hi', '<f8')
    ]

    if data_key in ["valid", "duplicated"]:
      e_rab_array_shape = (82,)
      e_utran_array_shape = (20992,)
    elif data_key == "invalid":
      e_rab_array_shape = (73,)
      e_utran_array_shape = (18688,)
    elif data_key == "empty":
      e_rab_array_dtype = None
      e_utran_array_dtype = None

    # Check the data types and shape of the Data Arrays
    # Also fetch and check the KPI data from the dedicated API endpoint
    for data_array in ingestion_item_dict['data_array_list']:
      if 'e_rab' in data_array.getReference():
        self.assertTrue(data_array.getArrayShape() == e_rab_array_shape)
        self.assertTrue(data_array.getArrayDtype() == e_rab_array_dtype)

        e_rab_kpi_dict = self.getOrsEnbKpiDict(
          data_array.getRelativeUrl(),
          'e_rab_accessibility'
        )
        if e_rab_array_shape is None:
          self.assertTrue(e_rab_kpi_dict == {})
        else:
          for key in e_rab_kpi_dict:
            self.assertTrue(len(e_rab_kpi_dict[key]) == e_rab_array_shape[0])

      elif 'e_utran' in data_array.getReference():
        self.assertTrue(data_array.getArrayShape() == e_utran_array_shape)
        self.assertTrue(data_array.getArrayDtype() == e_utran_array_dtype)

        e_utran_kpi_dict = self.getOrsEnbKpiDict(
          data_array.getRelativeUrl(),
          'e_utran_ip_throughput'
        )
        if e_utran_array_shape is None:
          self.assertTrue(e_utran_kpi_dict == {})
        else:
          for key in e_utran_kpi_dict:
            if key == 'evt':
              self.assertTrue(
                len(e_utran_kpi_dict[key]) == e_utran_array_shape[0] // QCI_COUNT
              )
            else:
              self.assertTrue(len(e_utran_kpi_dict[key]) == 1)
              if key != 'active_qci':
                self.assertTrue(
                  len(e_utran_kpi_dict[key][0]) == e_utran_array_shape[0] // QCI_COUNT
                )

  def test_05_2_ingestInvalidOrsLogDataFromFluentd(self):
    '''
    Test an invalid ORS log ingestion: simulate a fluentd gateway forwarding invalid ORS logs to the platform.
    Check that all items are still valid, as log chunks containing invalid measurements are skipped and
    KPIs can continue to be calculated once they are no longer in the calculation window.
    Also check the fetching of KPI values through the dedicated API endpoint.
    '''

    # Call the above test, but test with invalid data
    self.test_05_1_ingestValidOrsLogDataFromFluentd(data_key="invalid")

  def test_05_3_ingestDuplicatedOrsLogDataFromFluentd(self):
    '''
    Test an ORS log ingestion where data lines have been duplicated:
    simulate a fluentd gateway forwarding invalid ORS logs to the platform.
    Check that all items are still valid, as duplicate log lines are removed before
    the KPIs are calculated.
    Also check the fetching of KPI values through the dedicated API endpoint.
    '''

    # Call the above test, but test with invalid data
    self.test_05_1_ingestValidOrsLogDataFromFluentd(data_key="duplicated")

  def test_05_4_ingestEmptyOrsLogDataFromFluentd(self):
    '''
    Test an empty ORS log ingestion: simulate a fluentd gateway forwarding empty ORS logs to the platform.
    Check that all items are valid, but the data arrays remain uninitialized.
    Also check the fetching of KPI values through the dedicated API endpoint.
    '''

    # Call the above test, but test with empty data
    self.test_05_1_ingestValidOrsLogDataFromFluentd(data_key="empty")

  def test_05_5_ingestOrsLogDataWithoutTagPrefix(self):
    '''
    Simulate an entity trying to send data to the platform for ingestion
    without using the 'ors.' tag prefix added by fluentd.
    Check that the ingestion is refused.
    '''

    # No need to register an ORS here
    entity_tag = generateRandomString()

    # Call the script that parses the ingestion tag
    # Check that it raises the expected error
    self.assertRaises(
      ValueError,
      self.portal.IngestionPolicy_parseOrsFluentdTag,
      entity_tag
    )

  def test_06_1_checkOrsItemConsistency(self):
    '''
    Test the Wendelin Telecom constraints defined on standard ORS Data Acquisition Units and Data Supplies.
    Check all cases of both consistency and inconsistency.
    '''

    # Manually create a Data Acquisition Unit without a reference
    # No need to validate it
    inconsistent_data_acquisition_unit = self.portal.data_acquisition_unit_module.newContent(
      portal_type='Data Acquisition Unit'
    )
    self.tic()
    self.addCleanup(self._removeDocument, inconsistent_data_acquisition_unit)

    # Check that there is a consistency error: no reference was found
    consistency_message_list = self.getConsistencyMessageList(inconsistent_data_acquisition_unit)
    self.assertTrue(len(consistency_message_list) == 1)
    self.assertTrue(consistency_message_list[0] == 'Reference has not been set')

    # Now, successively set invalid ORS tags as the reference
    # and check that it is detected as invalid
    invalid_tag_list = [
      'ors123',
      '_COMP-234_e0xABCDE',
      'ors123_COMP-_e0xABCDE',
      'ors123_COMP-456_e0xA'
    ]
    for invalid_tag in invalid_tag_list:
      inconsistent_data_acquisition_unit.setReference(invalid_tag)
      self.tic()
      consistency_message_list = self.getConsistencyMessageList(inconsistent_data_acquisition_unit)
      self.assertTrue(len(consistency_message_list) == 1)
      self.assertTrue(
        consistency_message_list[0] == "Reference '%s' is not a valid ORS tag" % invalid_tag
      )

    # Next, manually create a Data Supply without a reference
    # No need to validate it either, yet
    inconsistent_data_supply = self.portal.data_supply_module.newContent(
      portal_type='Data Supply'
    )
    self.tic()
    self.addCleanup(self._removeDocument, inconsistent_data_supply)

    # Check that there are several consistency errors
    consistency_message_list = self.getConsistencyMessageList(inconsistent_data_supply)
    self.assertTrue(len(consistency_message_list) == 2)
    self.assertTrue(
      consistency_message_list[0] == 'Data Supply is not related to a Data Acquisition Unit'
    )
    self.assertTrue(consistency_message_list[1] == 'Reference has not been set')

    # Now, register an ORS with a valid tag
    ors_item_dict = self.registerOrs(test_suffix=False)
    self.addCleanup(self._removeDocument, ors_item_dict['data_acquisition_unit'])
    self.addCleanup(self._removeDocument, ors_item_dict['data_supply'])

    # Check that the created items are consistent (no error messages)
    for item_key in ['data_acquisition_unit', 'data_supply']:
      consistency_message_list = self.getConsistencyMessageList(ors_item_dict[item_key])
      self.assertFalse(consistency_message_list)

    # Now, change the reference of the Data Supply
    ors_tag = ors_item_dict['data_acquisition_unit'].getReference()
    new_radio_id = generateRandomString(length=5, hexadecimal=True)
    while new_radio_id == ors_tag[20:]:
      new_radio_id = generateRandomString(length=5, hexadecimal=True)
    ors_item_dict['data_supply'].setReference(ors_tag[:20] + new_radio_id)
    self.tic()

    # Check that the Data Supply is now inconsistent
    consistency_message_list = self.getConsistencyMessageList(ors_item_dict['data_supply'])
    self.assertTrue(len(consistency_message_list) == 1)
    self.assertTrue(
      consistency_message_list[0] == \
      "Reference does not match the associated Data Acquisition Unit's reference"
    )

    # Finally, invalidate the Data Supply
    ors_item_dict['data_supply'].invalidate()
    self.tic()

    # Check that there is a new consistency error
    consistency_message_list = self.getConsistencyMessageList(ors_item_dict['data_supply'])
    self.assertTrue(len(consistency_message_list) == 2)
    self.assertTrue(
      consistency_message_list[0] == \
      "Reference does not match the associated Data Acquisition Unit's reference"
    )
    self.assertTrue(
      consistency_message_list[1] == \
      "Validation state does not match that of the associated Data Acquisition Unit"
    )

    # Finally, register a generic eNB device with a non-ORS hostname in its tag
    # This should be valid
    enb_tag = 'edgepod1_COMP-1234_e0x1A2D0'
    enb_data_acquisition_unit = self.portal.data_acquisition_unit_module.newContent(
      portal_type='Data Acquisition Unit',
      reference=enb_tag
    )
    enb_data_acquisition_unit.validate()
    enb_data_supply = enb_data_acquisition_unit.DataAcquisitionUnit_createOrsDataSupply(batch=1)

    # Check that the created items are consistent (no error messages)
    for item in [enb_data_acquisition_unit, enb_data_supply]:
      consistency_message_list = self.getConsistencyMessageList(item)
      self.assertFalse(consistency_message_list)

  def test_06_2_checkOrsIngestionItemConsistency(self):
    '''
    Test the Wendelin Telecom constraints defined on ORS ingestion items,
    namely Data Ingestions and Data Analyses.
    Check all cases of both consistency and inconsistency.
    '''

    # Register an ORS
    ors_item_dict = self.registerOrs()

    # Perform a data ingestion for the ORS
    ingestion_item_dict = self.getOrsLogIngestionItems(
      self.test_ors_example_log_empty,
      ors_item_dict['data_acquisition_unit'].getReference()
    )

    # Check that the Data Ingestion and Data Analysis are consistent
    for item_key in ['data_ingestion', 'data_analysis']:
      consistency_message_list = self.getConsistencyMessageList(
        ingestion_item_dict[item_key]
      )
      self.assertFalse(consistency_message_list)

    # Invalidate the Data Supply
    ors_item_dict['data_supply'].invalidate()
    self.tic()

    # Check that the Data Analysis (and by extension the Data Ingestion)
    # now has a consistency error
    consistency_message_list = self.getConsistencyMessageList(
      ingestion_item_dict['data_analysis']
    )
    self.assertTrue(len(consistency_message_list) == 1)
    self.assertTrue(
      consistency_message_list[0] == "Simulation is started but should be stopped"
    )

    # Now, unlink the Data Supply from the Data Analysis
    saved_specialise_list = ingestion_item_dict['data_analysis'].getSpecialiseValueList()
    ingestion_item_dict['data_analysis'].setSpecialiseValueList([])
    self.tic()

    # Check that the Data Analysis has consistency errors
    consistency_message_list = self.getConsistencyMessageList(
      ingestion_item_dict['data_analysis']
    )
    self.assertTrue(len(consistency_message_list) == 2)
    self.assertTrue(
      consistency_message_list[0] == \
      "Missing Data Supply: %s" % ors_item_dict['data_supply'].getRelativeUrl()
    )
    self.assertTrue(
      consistency_message_list[1] == "Simulation should be delivered"
    )

    # Re-validate and relink the Data Supply and stop the Data Ingestion
    ors_item_dict['data_supply'].validate()
    ingestion_item_dict['data_analysis'].setSpecialiseValueList(saved_specialise_list)
    if ingestion_item_dict['data_ingestion'].getSimulationState() != 'stopped':
      ingestion_item_dict['data_ingestion'].stop()
    self.tic()

    # Check that the Data Ingestion has a consistency error
    consistency_message_list = self.getConsistencyMessageList(
      ingestion_item_dict['data_ingestion']
    )
    self.assertTrue(len(consistency_message_list) == 1)
    self.assertTrue(
      consistency_message_list[0] == "Simulation is stopped but should be started"
    )

    # Restart the ingestion
    ingestion_item_dict['data_ingestion'].start()

    # Register another ORS and link the Data Supply to the ingestion
    new_ors_item_dict = self.registerOrs()
    ingestion_item_dict['data_ingestion'].setSpecialiseValueList([
      ors_item_dict['data_supply'],
      new_ors_item_dict['data_supply']
    ])
    self.tic()

    # Check that the Data Ingestion has another consistency error
    consistency_message_list = self.getConsistencyMessageList(
      ingestion_item_dict['data_ingestion']
    )
    self.assertTrue(len(consistency_message_list) == 1)
    self.assertTrue(
      consistency_message_list[0] == "More than one Data Supply linked to Data Delivery"
    )

    # Finally, remove the aggregate from the Data Analysis's last line
    data_analysis_line_list = ingestion_item_dict['data_analysis'].contentValues(
      portal_type='Data Analysis Line'
    )
    data_analysis_last_line = data_analysis_line_list[-1]
    saved_aggregate_list = data_analysis_last_line.getAggregateValueList()
    data_analysis_last_line.setAggregateValueList([])
    self.tic()

    # Check that the other Data Analysis Lines are consistent
    for line in data_analysis_line_list[:-1]:
      consistency_message_list = self.getConsistencyMessageList(line)
      self.assertFalse(consistency_message_list)

    # Check that the Data Analysis line has a consistency error
    consistency_message_list = self.getConsistencyMessageList(
      data_analysis_last_line
    )
    self.assertTrue(len(consistency_message_list) == 2)
    self.assertTrue(
      consistency_message_list[0] == "Item Type Data Stream is missing"
    )
    self.assertTrue(
      consistency_message_list[1] == "Item Type Progress Indicator is missing"
    )

    data_analysis_last_line.setAggregateValueList(saved_aggregate_list)
    self.tic()

  def test_06_3_checkVirtualOrsItemConsistency(self):
    '''
    Test the Wendelin Telecom constraints defined on virtual ORS Data Acquisition Units and Data Supplies.
    Check that any virtual ORS items created through the action are consistent.
    '''

    # Generate virtual ORS tag components
    tag_comp_id = generateRandomString(length=4, only_digits=True)
    tag_title = 'Test%s' % generateRandomString(length=3, only_digits=True)

    # Register a virtual ORS with the given tag components
    data_acquisition_unit = self.portal.DataAcquisitionUnitModule_registerVirtualOrs(
      tag_comp_id,
      tag_title,
      batch=1
    )
    self.tic()
    data_supply = data_acquisition_unit.DataAcquisitionUnit_getOrsDataSupply()

    # Check that the created items are consistent (no error messages)
    for item in [data_acquisition_unit, data_supply]:
      consistency_message_list = self.getConsistencyMessageList(item)
      self.assertFalse(consistency_message_list)

    # Generate new virtual ORS tag components, now with the default COMP ID value
    new_tag_comp_id = 'XXXX'
    new_tag_title = 'Test%s' % generateRandomString(length=3, only_digits=True)

    # Register another virtual ORS with the new given tag components
    new_data_acquisition_unit = self.portal.DataAcquisitionUnitModule_registerVirtualOrs(
      new_tag_comp_id,
      new_tag_title,
      batch=1
    )
    self.tic()
    new_data_supply = new_data_acquisition_unit.DataAcquisitionUnit_getOrsDataSupply()

    # Check that these newly created items are also consistent (no error messages)
    for item in [new_data_acquisition_unit, new_data_supply]:
      consistency_message_list = self.getConsistencyMessageList(item)
      self.assertFalse(consistency_message_list)

  def test_07_1_updateOrsConfigurationsFastInput(self, username=None):
    '''
    Test the scripts called by the Update ORS Configurations Fast Input action which updates the title
    of Data Acquisition Units, as well as the client project to which they are indirectly linked.
    Check all possible configurations.
    '''

    def checkItemDictState(
      item_dict,
      data_acquisition_unit_validation_state,
      data_supply_validation_state,
      item_simulation_state,
      expected_title=None,
      expected_project=None
    ):
      expected_title = expected_title \
        or item_dict['data_acquisition_unit'].getReference()
      self.assertTrue(
        item_dict['data_acquisition_unit'].getTitle() == expected_title
      )
      self.assertTrue(
        item_dict['data_acquisition_unit'].getValidationState() \
          == data_acquisition_unit_validation_state
      )

      self.assertTrue(
        item_dict['data_supply'].getValidationState() \
          == data_supply_validation_state
      )
      if expected_project:
        self.assertTrue(
          item_dict['data_supply'].getDestinationProject() == expected_project
        )
      else:
        self.assertTrue(
          item_dict['data_supply'].getDestinationProject() is None
      )

      for item_key in ['data_ingestion', 'data_analysis']:
        if item_key not in item_dict:
          continue
        self.assertTrue(
          item_dict['data_ingestion'].getSimulationState() \
            == item_simulation_state
        )
        if expected_project and item_simulation_state == 'started':
          self.assertTrue(
            item_dict[item_key].getDestinationProject() == expected_project
          )
        else:
          self.assertTrue(
            item_dict[item_key].getDestinationProject() is None
        )

    # Register ORS
    ors_count = 10
    ors_item_dict_list = [self.registerOrs() for _ in range(ors_count)]

    # Register client projects
    project_count = 2
    project_item_dict_list = [self.registerOrsClientProject() for _ in range(project_count)]

    # Perform a data ingestion for each ORS
    # except for the last three
    ingestion_item_dict_list = [
      self.getOrsLogIngestionItems(
        self.test_ors_example_log_empty,
        ors_item_dict['data_acquisition_unit'].getReference()
      )
      for ors_item_dict in ors_item_dict_list[:7]
    ]

    # Invalidate the third ORS
    ingestion_item_dict_list[2]['data_acquisition_unit'].invalidate()
    # Delete the fourth ORS
    ingestion_item_dict_list[3]['data_acquisition_unit'].invalidate()
    ingestion_item_dict_list[3]['data_acquisition_unit'].delete()
    # Invalidate the Data Supply for the fifth ORS
    ingestion_item_dict_list[4]['data_supply'].invalidate()
    # Delete the Data Supply for the sixth ORS
    ingestion_item_dict_list[5]['data_supply'].invalidate()
    ingestion_item_dict_list[5]['data_supply'].delete()
    # Deliver the Data Ingestion and Data Analysis for the seventh ORS
    ingestion_item_dict_list[6]['data_ingestion'].deliver()
    ingestion_item_dict_list[6]['data_analysis'].deliver()
    self.tic()

    # Check the initial state of the ingestion items
    checkItemDictState(
      ingestion_item_dict_list[0],
      'validated',
      'validated',
      'started',
    )
    checkItemDictState(
      ingestion_item_dict_list[1],
      'validated',
      'validated',
      'started',
    )
    checkItemDictState(
      ingestion_item_dict_list[2],
      'invalidated',
      'validated',
      'started',
    )
    checkItemDictState(
      ingestion_item_dict_list[3],
      'deleted',
      'validated',
      'started',
    )
    checkItemDictState(
      ingestion_item_dict_list[4],
      'validated',
      'invalidated',
      'started',
    )
    checkItemDictState(
      ingestion_item_dict_list[5],
      'validated',
      'deleted',
      'started',
    )
    checkItemDictState(
      ingestion_item_dict_list[6],
      'validated',
      'validated',
      'delivered',
    )
    checkItemDictState(
      ors_item_dict_list[7],
      'validated',
      'validated',
      'started',
    )
    checkItemDictState(
      ors_item_dict_list[8],
      'validated',
      'validated',
      'started',
    )
    checkItemDictState(
      ors_item_dict_list[9],
      'validated',
      'validated',
      'started',
    )

    # Login as alternate user if username is provided
    if username is not None:
      self.loginByUserName(username)

    # Retrieve the item list that will be used by the Fast Input listbox
    # Check that all registered items are there by their relative URLs, except for:
    # the third one: invalidated Data Acquisition Unit
    # the fourth one: deleted Data Acquisition Unit
    # the fifth one: invalidated ORS Data Supply
    # the sixth one: deleted ORS Data Supply
    initial_listbox_item_list = \
      self.portal.DataAcquisitionUnitModule_getOrsConfigurationFastInputList()
    initial_listbox_item_url_list = [
      item.getRelativeUrl() for item in initial_listbox_item_list
    ]
    self.assertTrue(
      ors_item_dict_list[0]['data_acquisition_unit'].getRelativeUrl() \
        in initial_listbox_item_url_list
    )
    self.assertTrue(
      ors_item_dict_list[1]['data_acquisition_unit'].getRelativeUrl() \
        in initial_listbox_item_url_list
    )
    self.assertTrue(
      ors_item_dict_list[2]['data_acquisition_unit'].getRelativeUrl() \
        not in initial_listbox_item_url_list
    )
    self.assertTrue(
      ors_item_dict_list[3]['data_acquisition_unit'].getRelativeUrl() \
        not in initial_listbox_item_url_list
    )
    self.assertTrue(
      ors_item_dict_list[4]['data_acquisition_unit'].getRelativeUrl() \
        not in initial_listbox_item_url_list
    )
    self.assertTrue(
      ors_item_dict_list[5]['data_acquisition_unit'].getRelativeUrl() \
        not in initial_listbox_item_url_list
    )
    self.assertTrue(
      ors_item_dict_list[6]['data_acquisition_unit'].getRelativeUrl() \
        in initial_listbox_item_url_list
    )
    self.assertTrue(
      ors_item_dict_list[7]['data_acquisition_unit'].getRelativeUrl() \
        in initial_listbox_item_url_list
    )
    self.assertTrue(
      ors_item_dict_list[8]['data_acquisition_unit'].getRelativeUrl() \
        in initial_listbox_item_url_list
    )
    self.assertTrue(
      ors_item_dict_list[9]['data_acquisition_unit'].getRelativeUrl() \
        in initial_listbox_item_url_list
    )

    # Build a listbox item list for updating:
    # The first ORS will be linked to the first project
    # The second will be linked to the second project
    # The fifth will be linked to the first project
    # The sixth will be linked to the second project
    # The seventh will be linked to the first project
    # The eighth will be left as is
    # The ninth will be linked to the second project
    # The tenth will also be left as is
    listbox = (
      {
        'listbox_key': ors_item_dict_list[0]['data_acquisition_unit'].getRelativeUrl(),
        'destination_project': project_item_dict_list[0]['project'].getRelativeUrl(),
        'title': 'First Test ORS'
      },
      {
        'listbox_key': ors_item_dict_list[1]['data_acquisition_unit'].getRelativeUrl(),
        'destination_project': project_item_dict_list[1]['project'].getRelativeUrl(),
        'title': 'Second Test ORS'
      },
      {
        'listbox_key': ors_item_dict_list[6]['data_acquisition_unit'].getRelativeUrl(),
        'destination_project': project_item_dict_list[0]['project'].getRelativeUrl(),
        'title': 'Seventh Test ORS'
      },
      {
        'listbox_key': ors_item_dict_list[7]['data_acquisition_unit'].getRelativeUrl(),
        'destination_project': '',
        'title': ''
      },
      {
        'listbox_key': ors_item_dict_list[8]['data_acquisition_unit'].getRelativeUrl(),
        'destination_project': project_item_dict_list[1]['project'].getRelativeUrl(),
        'title': 'Ninth Test ORS'
      },
      {
        'listbox_key': ors_item_dict_list[9]['data_acquisition_unit'].getRelativeUrl(),
        'destination_project': '',
        'title': ''
      }
    )

    # Call the script to update the items
    self.portal.DataAcquisitionUnitModule_updateOrsConfigurationFastInputList(listbox=listbox)
    self.tic()

    # Check that the properties have been correctly updated
    checkItemDictState(
      ingestion_item_dict_list[0],
      'validated',
      'validated',
      'started',
      expected_title='First Test ORS',
      expected_project=project_item_dict_list[0]['project'].getRelativeUrl(),
    )
    checkItemDictState(
      ingestion_item_dict_list[1],
      'validated',
      'validated',
      'started',
      expected_title='Second Test ORS',
      expected_project=project_item_dict_list[1]['project'].getRelativeUrl(),
    )
    checkItemDictState(
      ingestion_item_dict_list[2],
      'invalidated',
      'validated',
      'started',
    )
    checkItemDictState(
      ingestion_item_dict_list[3],
      'deleted',
      'validated',
      'started',
    )
    checkItemDictState(
      ingestion_item_dict_list[4],
      'validated',
      'invalidated',
      'started',
    )
    checkItemDictState(
      ingestion_item_dict_list[5],
      'validated',
      'deleted',
      'started',
    )
    checkItemDictState(
      ingestion_item_dict_list[6],
      'validated',
      'validated',
      'delivered',
      expected_title='Seventh Test ORS',
      expected_project=project_item_dict_list[0]['project'].getRelativeUrl(),
    )
    checkItemDictState(
      ors_item_dict_list[7],
      'validated',
      'validated',
      'started',
    )
    checkItemDictState(
      ors_item_dict_list[8],
      'validated',
      'validated',
      'started',
      expected_title='Ninth Test ORS',
      expected_project=project_item_dict_list[1]['project'].getRelativeUrl(),
    )
    checkItemDictState(
      ors_item_dict_list[9],
      'validated',
      'validated',
      'started',
    )

  def test_07_2_updateOrsConfigurationsFastInputAsAdministrator(self):
    '''
    Repeat the previous test, but logged in as an Administrator user to make sure it works
    and that the function has the adequate permissions.
    '''

    admin_username = 'test_administrator_%s' % generateRandomString()
    self.createWendelinTelecomUser(
      admin_username,
      None,
      'administrator'
    )

    self.test_07_1_updateOrsConfigurationsFastInput(username=admin_username)

  def test_08_archiveOrsDataIngestionFastInput(self):
    '''
    Test the scripts called by the Archive ORS Data Ingestion Fast Input action which archives
    the selected Data Acquisition Units as well as all related items, in order to restart
    the ingestions anew.
    '''

    archived_reference_marker = 'ARCHIVED'

    def checkIngestionItemDictState(
      ingestion_item_dict,
      data_acquisition_unit_validation_state,
      data_supply_validation_state,
      item_validation_state,
      item_simulation_state,
      archived=False
    ):
      self.assertTrue(
        ingestion_item_dict['data_acquisition_unit'].getValidationState() \
          == data_acquisition_unit_validation_state
      )
      self.assertTrue(
        ingestion_item_dict['data_supply'].getValidationState() \
          == data_supply_validation_state
      )
      for data_supply_line in ingestion_item_dict['data_supply'].contentValues(
        portal_type='Data Supply Line'
      ):
        self.assertTrue(
          data_supply_line.getValidationState() == data_supply_validation_state
        )
      for item_key in ['data_stream', 'progress_indicator']:
        self.assertTrue(
          ingestion_item_dict[item_key].getValidationState() \
            == item_validation_state
        )
      for data_array in ingestion_item_dict['data_array_list']:
        self.assertTrue(
          data_array.getValidationState() == item_validation_state
        )
      for data_simulation_key in ['data_ingestion', 'data_analysis']:
        self.assertTrue(
          ingestion_item_dict[data_simulation_key].getSimulationState() \
            == item_simulation_state
        )

      if archived:
        self.assertTrue(
          ingestion_item_dict['data_acquisition_unit'].getTitle().count(archived_reference_marker) == 1
        )
        for item_key in ['data_acquisition_unit', 'data_supply', 'data_stream']:
          self.assertTrue(
            archived_reference_marker in ingestion_item_dict[item_key].getReference()
          )
        for data_array in ingestion_item_dict['data_array_list']:
          self.assertTrue(
            archived_reference_marker in data_array.getReference()
          )
        for data_simulation_key in ['data_ingestion', 'data_analysis']:
          self.assertTrue(
            archived_reference_marker in ingestion_item_dict[data_simulation_key].getReference()
          )
      else:
        self.assertTrue(
          archived_reference_marker not in ingestion_item_dict['data_acquisition_unit'].getTitle()
        )
        for item_key in ['data_acquisition_unit', 'data_supply', 'data_stream']:
          self.assertTrue(
            archived_reference_marker not in ingestion_item_dict[item_key].getReference()
          )
        for data_array in ingestion_item_dict['data_array_list']:
          self.assertTrue(
            archived_reference_marker not in data_array.getReference()
          )
        for data_simulation_key in ['data_ingestion', 'data_analysis']:
          self.assertTrue(
            archived_reference_marker not in ingestion_item_dict[data_simulation_key].getReference()
          )

    # Register ORS
    ors_count = 9
    ors_item_dict_list = [self.registerOrs() for _ in range(ors_count)]

    # Perform a data ingestion for each ORS
    # except for the last one
    ingestion_item_dict_list = [
      self.getOrsLogIngestionItems(
        self.test_ors_example_log_empty,
        ors_item_dict['data_acquisition_unit'].getReference()
      )
      for ors_item_dict in ors_item_dict_list[:-1]
    ]

    # Leave the first and second set of ingestion items as is
    # For the third: invalidate the Data Acquisition Unit
    ingestion_item_dict_list[2]['data_acquisition_unit'].invalidate()
    # For the fourth: delete the Data Acquisition Unit
    ingestion_item_dict_list[3]['data_acquisition_unit'].invalidate()
    ingestion_item_dict_list[3]['data_acquisition_unit'].delete()
    # For the fifth: invalidate the Data Supply
    ingestion_item_dict_list[4]['data_supply'].invalidate()
    for data_supply_line in ingestion_item_dict_list[4]['data_supply'].contentValues(
      portal_type='Data Supply Line'
    ):
      data_supply_line.invalidate()
    # For the sixth: delete the Data Supply
    ingestion_item_dict_list[5]['data_supply'].invalidate()
    ingestion_item_dict_list[5]['data_supply'].delete()
    for data_supply_line in ingestion_item_dict_list[5]['data_supply'].contentValues(
      portal_type='Data Supply Line'
    ):
      data_supply_line.invalidate()
      data_supply_line.delete()
    # For the seventh: invalidate/deliver everything else
    ingestion_item_dict_list[6]['data_ingestion'].deliver()
    ingestion_item_dict_list[6]['data_stream'].invalidate()
    ingestion_item_dict_list[6]['data_analysis'].deliver()
    for data_array in ingestion_item_dict_list[6]['data_array_list']:
      data_array.invalidate()
    ingestion_item_dict_list[6]['progress_indicator'].invalidate()
    # For the eighth: delete/deliver everything else
    ingestion_item_dict_list[7]['data_ingestion'].deliver()
    ingestion_item_dict_list[7]['data_stream'].invalidate()
    ingestion_item_dict_list[7]['data_stream'].delete()
    ingestion_item_dict_list[7]['data_analysis'].deliver()
    for data_array in ingestion_item_dict_list[7]['data_array_list']:
      data_array.invalidate()
      data_array.delete()
    ingestion_item_dict_list[7]['progress_indicator'].invalidate()
    ingestion_item_dict_list[7]['progress_indicator'].delete()
    self.tic()

    # Check the initial state of the ingestion items
    checkIngestionItemDictState(
      ingestion_item_dict_list[0],
      'validated',
      'validated',
      'validated',
      'started',
    )
    checkIngestionItemDictState(
      ingestion_item_dict_list[1],
      'validated',
      'validated',
      'validated',
      'started',
    )
    checkIngestionItemDictState(
      ingestion_item_dict_list[2],
      'invalidated',
      'validated',
      'validated',
      'started',
    )
    checkIngestionItemDictState(
      ingestion_item_dict_list[3],
      'deleted',
      'validated',
      'validated',
      'started',
    )
    checkIngestionItemDictState(
      ingestion_item_dict_list[4],
      'validated',
      'invalidated',
      'validated',
      'started',
    )
    checkIngestionItemDictState(
      ingestion_item_dict_list[5],
      'validated',
      'deleted',
      'validated',
      'started',
    )
    checkIngestionItemDictState(
      ingestion_item_dict_list[6],
      'validated',
      'validated',
      'invalidated',
      'delivered',
    )
    checkIngestionItemDictState(
      ingestion_item_dict_list[7],
      'validated',
      'validated',
      'deleted',
      'delivered',
    )
    self.assertTrue(
      ors_item_dict_list[8]['data_acquisition_unit'].getValidationState() \
        == 'validated'
    )
    self.assertTrue(
      ors_item_dict_list[8]['data_supply'].getValidationState() \
        == 'validated'
    )

    # Retrieve the item list that will be used by the Fast Input listbox
    # Check that all registered items are there by their relative URLs, except for:
    # the third one: invalidated Data Acquisition Unit
    # the fourth one: deleted Data Acquisition Unit
    # the fifth one: invalidated ORS Data Supply
    # the sixth one: deleted ORS Data Supply
    initial_listbox_item_list = \
      self.portal.DataAcquisitionUnitModule_getOrsIngestionFastInputList()
    initial_listbox_item_url_list = [
      item.getRelativeUrl() for item in initial_listbox_item_list
    ]
    self.assertTrue(
      ors_item_dict_list[0]['data_acquisition_unit'].getRelativeUrl() \
        in initial_listbox_item_url_list
    )
    self.assertTrue(
      ors_item_dict_list[1]['data_acquisition_unit'].getRelativeUrl() \
        in initial_listbox_item_url_list
    )
    self.assertTrue(
      ors_item_dict_list[2]['data_acquisition_unit'].getRelativeUrl() \
        not in initial_listbox_item_url_list
    )
    self.assertTrue(
      ors_item_dict_list[3]['data_acquisition_unit'].getRelativeUrl() \
        not in initial_listbox_item_url_list
    )
    self.assertTrue(
      ors_item_dict_list[4]['data_acquisition_unit'].getRelativeUrl() \
        not in initial_listbox_item_url_list
    )
    self.assertTrue(
      ors_item_dict_list[5]['data_acquisition_unit'].getRelativeUrl() \
        not in initial_listbox_item_url_list
    )
    self.assertTrue(
      ors_item_dict_list[6]['data_acquisition_unit'].getRelativeUrl() \
        in initial_listbox_item_url_list
    )
    self.assertTrue(
      ors_item_dict_list[7]['data_acquisition_unit'].getRelativeUrl() \
        in initial_listbox_item_url_list
    )
    self.assertTrue(
      ors_item_dict_list[8]['data_acquisition_unit'].getRelativeUrl() \
        in initial_listbox_item_url_list
    )

    # Build a listbox item list for updating:
    # All ORS will be selected for archiving
    # except for the second one
    listbox = (
      {
        'listbox_key': ors_item_dict_list[0]['data_acquisition_unit'].getRelativeUrl(),
        'listbox_selected': True
      },
      {
        'listbox_key': ors_item_dict_list[1]['data_acquisition_unit'].getRelativeUrl(),
        'listbox_selected': False
      },
      {
        'listbox_key': ors_item_dict_list[6]['data_acquisition_unit'].getRelativeUrl(),
        'listbox_selected': True
      },
      {
        'listbox_key': ors_item_dict_list[7]['data_acquisition_unit'].getRelativeUrl(),
        'listbox_selected': True
      },
      {
        'listbox_key': ors_item_dict_list[8]['data_acquisition_unit'].getRelativeUrl(),
        'listbox_selected': True
      }
    )

    # Call the script to update the items
    self.portal.DataAcquisitionUnitModule_archiveOrsIngestionFastInputList(listbox=listbox)
    self.tic()

    # Check that only the selected items have been correctly updated
    checkIngestionItemDictState(
      ingestion_item_dict_list[0],
      'deleted',
      'deleted',
      'deleted',
      'delivered',
      archived=True
    )
    checkIngestionItemDictState(
      ingestion_item_dict_list[1],
      'validated',
      'validated',
      'validated',
      'started',
      archived=False
    )
    checkIngestionItemDictState(
      ingestion_item_dict_list[2],
      'invalidated',
      'validated',
      'validated',
      'started',
    )
    checkIngestionItemDictState(
      ingestion_item_dict_list[3],
      'deleted',
      'validated',
      'validated',
      'started',
    )
    checkIngestionItemDictState(
      ingestion_item_dict_list[4],
      'validated',
      'invalidated',
      'validated',
      'started',
    )
    checkIngestionItemDictState(
      ingestion_item_dict_list[5],
      'validated',
      'deleted',
      'validated',
      'started',
    )
    checkIngestionItemDictState(
      ingestion_item_dict_list[6],
      'deleted',
      'deleted',
      'deleted',
      'delivered',
      archived=True
    )
    checkIngestionItemDictState(
      ingestion_item_dict_list[7],
      'deleted',
      'deleted',
      'deleted',
      'delivered',
      archived=True
    )
    self.assertTrue(
      ors_item_dict_list[8]['data_acquisition_unit'].getValidationState() \
        == 'deleted'
    )
    self.assertTrue(
      ors_item_dict_list[8]['data_acquisition_unit'].getTitle().count(archived_reference_marker) == 1
    )
    self.assertTrue(
      archived_reference_marker in ors_item_dict_list[8]['data_acquisition_unit'].getReference()
    )
    self.assertTrue(
      ors_item_dict_list[8]['data_supply'].getValidationState() \
        == 'deleted'
    )
    self.assertTrue(
      archived_reference_marker in ors_item_dict_list[8]['data_supply'].getReference()
    )

    # Retrieve the item list that will be used by the Fast Input listbox again
    # Check that only the second Data Acquisition Unit is there now
    redo_listbox_item_list = \
      self.portal.DataAcquisitionUnitModule_getOrsIngestionFastInputList()
    redo_listbox_item_url_list = [
      item.getRelativeUrl() for item in redo_listbox_item_list
    ]
    self.assertTrue(
      ors_item_dict_list[0]['data_acquisition_unit'].getRelativeUrl() \
      not in redo_listbox_item_url_list
    )
    self.assertTrue(
      ors_item_dict_list[1]['data_acquisition_unit'].getRelativeUrl() \
      in redo_listbox_item_url_list
    )
    self.assertTrue(
      ors_item_dict_list[2]['data_acquisition_unit'].getRelativeUrl() \
      not in redo_listbox_item_url_list
    )
    self.assertTrue(
      ors_item_dict_list[3]['data_acquisition_unit'].getRelativeUrl() \
      not in redo_listbox_item_url_list
    )
    self.assertTrue(
      ors_item_dict_list[4]['data_acquisition_unit'].getRelativeUrl() \
      not in redo_listbox_item_url_list
    )
    self.assertTrue(
      ors_item_dict_list[5]['data_acquisition_unit'].getRelativeUrl() \
      not in redo_listbox_item_url_list
    )
    self.assertTrue(
      ors_item_dict_list[6]['data_acquisition_unit'].getRelativeUrl() \
      not in redo_listbox_item_url_list
    )
    self.assertTrue(
      ors_item_dict_list[7]['data_acquisition_unit'].getRelativeUrl() \
      not in redo_listbox_item_url_list
    )
    self.assertTrue(
      ors_item_dict_list[8]['data_acquisition_unit'].getRelativeUrl() \
      not in redo_listbox_item_url_list
    )

  def test_09_refreshOrsKpiDataAnalysisFastInput(self):
    '''
    Test the scripts called by the Refresh ORS KPI Data Analyses Fast Input action which plans
    a full refresh for the selected ongoing Data Analyses.
    '''

    # Register ORS
    ors_count = 5
    ors_item_dict_list = [self.registerOrs() for _ in range(ors_count)]

    # Perform a data ingestion for each ORS
    ingestion_item_dict_list = [
      self.getOrsLogIngestionItems(
        self.test_ors_example_log_empty,
        ors_item_dict['data_acquisition_unit'].getReference()
      )
      for ors_item_dict in ors_item_dict_list
    ]

    # Leave the first and second Data Analyses started
    # Deliver the third
    ingestion_item_dict_list[2]['data_analysis'].deliver()
    # Stop the fourth
    ingestion_item_dict_list[3]['data_analysis'].stop()
    # Plan a refresh for the fifth
    ingestion_item_dict_list[4]['data_analysis'].planRefresh()
    self.tic()

    # Check the initial state of the Data Analyses
    self.assertTrue(
      ingestion_item_dict_list[0]['data_analysis'].getSimulationState() == 'started' \
      and ingestion_item_dict_list[0]['data_analysis'].getRefreshState() == 'current'
    )
    self.assertTrue(
      ingestion_item_dict_list[1]['data_analysis'].getSimulationState() == 'started' \
      and ingestion_item_dict_list[1]['data_analysis'].getRefreshState() == 'current'
    )
    self.assertTrue(
      ingestion_item_dict_list[2]['data_analysis'].getSimulationState() == 'delivered' \
      and ingestion_item_dict_list[2]['data_analysis'].getRefreshState() == 'current'
    )
    self.assertTrue(
      ingestion_item_dict_list[3]['data_analysis'].getSimulationState() == 'stopped' \
      and ingestion_item_dict_list[3]['data_analysis'].getRefreshState() == 'current'
    )
    self.assertTrue(
      ingestion_item_dict_list[4]['data_analysis'].getSimulationState() == 'started' \
      and ingestion_item_dict_list[4]['data_analysis'].getRefreshState() == 'refresh_planned'
    )

    # Retrieve the item list that will be used by the Fast Input listbox
    # Check that only the first Data Analysis is there by its relative URL
    initial_listbox_item_list = \
      self.portal.DataAnalysisModule_getOrsKpiDataAnalysisFastInputList()
    initial_listbox_item_url_list = [
      item.getRelativeUrl() for item in initial_listbox_item_list
    ]
    self.assertTrue(
      ingestion_item_dict_list[0]['data_analysis'].getRelativeUrl() \
        in initial_listbox_item_url_list
    )
    self.assertTrue(
      ingestion_item_dict_list[1]['data_analysis'].getRelativeUrl() \
        in initial_listbox_item_url_list
    )
    self.assertTrue(
      ingestion_item_dict_list[2]['data_analysis'].getRelativeUrl() \
        not in initial_listbox_item_url_list
    )
    self.assertFalse(
      ingestion_item_dict_list[3]['data_analysis'].getRelativeUrl() \
        in initial_listbox_item_url_list
    )
    self.assertFalse(
      ingestion_item_dict_list[4]['data_analysis'].getRelativeUrl() \
        in initial_listbox_item_url_list
    )

    # Build a listbox item list for planning the refresh:
    # Only the first Data Analysis will be refreshed
    # The second one will be left as is
    listbox = (
      {
        'listbox_key': ingestion_item_dict_list[0]['data_analysis'].getRelativeUrl(),
        'listbox_selected': True
      },
      {
        'listbox_key': ingestion_item_dict_list[1]['data_analysis'].getRelativeUrl(),
        'listbox_selected': False
      }
    )

    # Call the script to perform the refresh
    self.portal.DataAnalysisModule_refreshOrsKpiDataAnalysisFastInputList(listbox=listbox)
    self.tic()

    # Check that only the first Data Analysis have been planned to refresh
    self.assertTrue(
      ingestion_item_dict_list[0]['data_analysis'].getSimulationState() == 'started' \
      and ingestion_item_dict_list[0]['data_analysis'].getRefreshState() == 'refresh_planned'
    )
    self.assertTrue(
      ingestion_item_dict_list[1]['data_analysis'].getSimulationState() == 'started' \
      and ingestion_item_dict_list[1]['data_analysis'].getRefreshState() == 'current'
    )
    self.assertTrue(
      ingestion_item_dict_list[2]['data_analysis'].getSimulationState() == 'delivered' \
      and ingestion_item_dict_list[2]['data_analysis'].getRefreshState() == 'current'
    )
    self.assertTrue(
      ingestion_item_dict_list[3]['data_analysis'].getSimulationState() == 'stopped' \
      and ingestion_item_dict_list[3]['data_analysis'].getRefreshState() == 'current'
    )
    self.assertTrue(
      ingestion_item_dict_list[4]['data_analysis'].getSimulationState() == 'started' \
      and ingestion_item_dict_list[4]['data_analysis'].getRefreshState() == 'refresh_planned'
    )

  def test_10_wendelinTelecomSecurityModel(self):
    '''
    Test Wendelin Telecom's custom security model:
    check that different users have the correct permissions according to their function and project.
    '''

    # Setup two different projects with one linked ORS each
    project_a_item_dict = self.registerOrsClientProject()
    ors_a_item_dict = self.registerOrs()
    ors_a_tag = ors_a_item_dict['data_acquisition_unit'].getReference()

    project_b_item_dict = self.registerOrsClientProject()
    ors_b_item_dict = self.registerOrs()
    ors_b_tag = ors_b_item_dict['data_acquisition_unit'].getReference()

    # Register a third ORS that will not be linked to a project
    ors_n_item_dict = self.registerOrs()
    ors_n_tag = ors_n_item_dict['data_acquisition_unit'].getReference()

    # Perform ingestions for all three ORSs
    ingestion_a_item_dict = self.getOrsLogIngestionItems(
      self.test_ors_example_log_valid,
      ors_a_tag
    )
    ingestion_b_item_dict = self.getOrsLogIngestionItems(
      self.test_ors_example_log_valid,
      ors_b_tag
    )
    ingestion_n_item_dict = self.getOrsLogIngestionItems(
      self.test_ors_example_log_valid,
      ors_n_tag
    )

    # Link the first two ORSs to their project AFTER the ingestion
    # To check that project propagation on ingestion objects works correctly
    ors_a_item_dict['data_supply'].setDestinationProject(project_a_item_dict['project'].getRelativeUrl())
    ors_b_item_dict['data_supply'].setDestinationProject(project_b_item_dict['project'].getRelativeUrl())

    # Create a client user not associated to a project
    client_user_n = self.createWendelinTelecomUser(
      'test_user_%s' % generateRandomString(),
      None,
      'user'
    )

    # Create two administrator users: one associated to Project A
    # and the second not associated to a project
    admin_user_a = self.createWendelinTelecomUser(
      'test_user_%s' % generateRandomString(),
      project_a_item_dict['project'].getRelativeUrl(),
      'administrator'
    )
    admin_user_n = self.createWendelinTelecomUser(
      'test_administrator_%s' % generateRandomString(),
      None,
      'administrator'
    )

    # Check that the client of Project A only has access to Project A documents
    client_user_a = project_a_item_dict['client_user']
    self.checkModulePermissions(client_user_a)
    self.checkIngestionDocumentsPermissions(client_user_a, ingestion_a_item_dict)
    self.checkIngestionDocumentsPermissions(client_user_a, ingestion_b_item_dict)
    self.checkIngestionDocumentsPermissions(client_user_a, ingestion_n_item_dict)

    # Check that the client of project_B only has access to project_B documents
    client_user_b = project_b_item_dict['client_user']
    self.checkModulePermissions(client_user_b)
    self.checkIngestionDocumentsPermissions(client_user_b, ingestion_a_item_dict)
    self.checkIngestionDocumentsPermissions(client_user_b, ingestion_b_item_dict)
    self.checkIngestionDocumentsPermissions(client_user_b, ingestion_n_item_dict)

    # Check that the client without a project does not have access to any document
    self.checkModulePermissions(client_user_n)
    self.checkIngestionDocumentsPermissions(client_user_n, ingestion_a_item_dict)
    self.checkIngestionDocumentsPermissions(client_user_n, ingestion_b_item_dict)
    self.checkIngestionDocumentsPermissions(client_user_n, ingestion_n_item_dict)

    # Check that both administrators, whether assigned to a project, have access to all documents
    self.checkModulePermissions(admin_user_a)
    self.checkIngestionDocumentsPermissions(admin_user_a, ingestion_a_item_dict)
    self.checkIngestionDocumentsPermissions(admin_user_a, ingestion_b_item_dict)
    self.checkIngestionDocumentsPermissions(admin_user_a, ingestion_n_item_dict)

    self.checkModulePermissions(admin_user_a)
    self.checkIngestionDocumentsPermissions(admin_user_n, ingestion_a_item_dict)
    self.checkIngestionDocumentsPermissions(admin_user_n, ingestion_b_item_dict)
    self.checkIngestionDocumentsPermissions(admin_user_n, ingestion_n_item_dict)

    # Check that the ingestor user only has access to documents needed for ingestion
    self.checkModulePermissions(self.ingestor_user)
    self.checkIngestionDocumentsPermissions(self.ingestor_user, ingestion_a_item_dict)
    self.checkIngestionDocumentsPermissions(self.ingestor_user, ingestion_b_item_dict)
    self.checkIngestionDocumentsPermissions(self.ingestor_user, ingestion_n_item_dict)