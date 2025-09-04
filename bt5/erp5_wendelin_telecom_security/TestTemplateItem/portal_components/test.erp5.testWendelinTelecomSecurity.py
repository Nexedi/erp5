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
from erp5.component.test.WendelinTelecomMixin import \
                     generateRandomString, TestWendelinTelecomMixin

class TestWendelinTelecomSecurity(TestWendelinTelecomMixin):

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
    ors_enb_cell = self.portal.portal_catalog.getResultValue(
      portal_type='Data Product',
      reference='ors_enb_cell',
      validation_state='validated'
    )
    self.checkDocumentPermissions(user, ors_enb_cell, True, False, False)
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

  def test_wendelinTelecomSecurityModel(self):
    '''
    Test Wendelin Telecom's custom security model:
    check that different users have the correct permissions
    according to their function and project.
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
    ors_a_item_dict['data_supply'].setDestinationProject(
      project_a_item_dict['project'].getRelativeUrl())
    ors_b_item_dict['data_supply'].setDestinationProject(
      project_b_item_dict['project'].getRelativeUrl())

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