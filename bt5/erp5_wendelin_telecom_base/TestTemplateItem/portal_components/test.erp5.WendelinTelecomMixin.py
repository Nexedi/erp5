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

class TestWendelinTelecomMixin(SecurityTestCase):

  def afterSetUp(self):
    # Set up variables for ORS ingestion testing
    self.ors_enb_log_ingestion = self.portal.portal_ingestion_policies.ors_enb_log_ingestion

    self.ors_enb_kpi_endpoint_path = self.portal.getPath() + '/Base_getDataArrayForDataTypeAsJSON'

    module = self.portal.web_page_module
    self.test_ors_example_log_valid = {
      'log': module.test_example_ors_enb_log_valid.getTextContent()
    }
    self.test_ors_example_log_invalid_split_1 = {
      'log': module.test_example_ors_enb_log_invalid_split_1.getTextContent()
    }
    self.test_ors_example_log_invalid_split_2 = {
      'log': module.test_example_ors_enb_log_invalid_split_2.getTextContent()
    }
    self.test_ors_example_log_with_duplicates = {
      'log': module.test_example_ors_enb_log_with_duplicates.getTextContent()
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
    cleanup_data = False
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
      data_array_url + '&data_type=' + kpi_type
    publish_kw = dict(
      user='ERP5TypeTestCase'
    )
    response = self.publish(kpi_path, **publish_kw)
    body = response.getBody()
    return json.loads(body)

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
