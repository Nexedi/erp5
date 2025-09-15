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
from erp5.component.test.WendelinTelecomMixin import generateRandomString, TestWendelinTelecomMixin, QCI_COUNT

from six.moves.http_client import NO_CONTENT
import json

class WendelinTelecomTest(TestWendelinTelecomMixin):

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
    self.assertNotEqual(None,
                        ingestion_item_dict['data_acquisition_unit'])
    self.assertNotEqual(None,
                        ingestion_item_dict['data_supply'])
    self.assertNotEqual(None,
                        ingestion_item_dict['data_ingestion'])
    self.assertNotEqual(None,
                        ingestion_item_dict['data_stream'].getData())
    self.assertNotEqual(None,
                        ingestion_item_dict['data_analysis'])

    self.assertTrue(all(data_array is not None for data_array in ingestion_item_dict['data_array_list']))

    self.assertNotEqual(None,
                        ingestion_item_dict['progress_indicator'])

    # Check that the value of the progress indicator is equal to the size of the Data Stream:
    # i.e. that all of the ingested data has been processed into KPIs
    self.assertEqual(
      ingestion_item_dict['progress_indicator'].getIntOffsetIndex(),
      ingestion_item_dict['data_stream'].getSize()
    )

    # Check that the Data Arrays containing the KPI data have correctly been initialized
    self.assertNotEqual(None,
      ingestion_item_dict[
        'data_acquisition_unit'
      ].DataAcquisitionUnit_getDataArrayUrl(data_type='e_rab'))

    self.assertNotEqual(None,
      ingestion_item_dict[
        'data_acquisition_unit'
      ].DataAcquisitionUnit_getDataArrayUrl(data_type='e_utran'))

    self.assertNotEqual(None,
      ingestion_item_dict[
        'data_acquisition_unit'
      ].DataAcquisitionUnit_getDataArrayUrl(data_type='cell_ue_count'))

    self.assertNotEqual(None,
      ingestion_item_dict[
        'data_acquisition_unit'
      ].DataAcquisitionUnit_getDataArrayUrl(data_type='cell_rrc'))

    self.assertNotEqual(None,
      ingestion_item_dict[
        'data_acquisition_unit'
      ].DataAcquisitionUnit_getDataArrayUrl(data_type='cell_rms_rx'))

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

    cell_ue_count_array_shape = None
    cell_ue_count_array_dtype = [
      ('utc', '<f8'),
      ('cell_id', '<f8'),
      ('ue_count_max', '<f8'),
      ('ue_count_min', '<f8'),
      ('ue_count_avg', '<f8')
    ]
    cell_rrc_array_shape = None
    cell_rrc_array_dtype = [
      ('utc', '<f8'),
      ('cell_id', '<f8'),
      ('rrc_con_req', '<f8'),
      ('rrc_paging', '<f8'),
      ('rrc_recon_com', '<f8'),
      ('rrc_sec_command', '<f8'),
      ('rrc_sec_complete', '<f8')
    ]
    cell_rms_rx_array_shape = None
    cell_rms_rx_array_dtype = [
      ('utc', '<f8'),
      ('cell_id', '<f8'),
      ('antenna', '<f8'),
      ('count', '<f8'),
      ('max', '<f8'),
      ('rms', '<f8'),
      ('rms_dbm', '<f8')
    ]

    if data_key in ["valid", "duplicated"]:
      e_rab_array_shape = (82,)
      e_utran_array_shape = (20992,)
      cell_ue_count_array_shape = (84,)
      cell_rrc_array_shape = (84,)
      cell_rms_rx_array_shape = (158,)
    elif data_key == "invalid":
      e_rab_array_shape = (73,)
      e_utran_array_shape = (18688,)
      cell_ue_count_array_shape = (113,)
      cell_rrc_array_shape = (113,)
      cell_rms_rx_array_shape = (216,)
    elif data_key == "empty":
      e_rab_array_dtype = None
      e_utran_array_dtype = None
      cell_ue_count_array_dtype = None
      cell_rrc_array_dtype = None
      cell_rms_rx_array_dtype = None


    # Check the data types and shape of the Data Arrays
    # Also fetch and check the KPI data from the dedicated API endpoint
    for data_array in ingestion_item_dict['data_array_list']:
      if 'e_rab' in data_array.getReference():
        self.assertEqual(data_array.getArrayShape(), e_rab_array_shape)
        self.assertEqual(data_array.getArrayDtype(), e_rab_array_dtype)

        e_rab_kpi_dict = self.getOrsDataArrayAsDict(
          data_array.getRelativeUrl(),
          'e_rab_accessibility'
        )
        if e_rab_array_shape is None:
          self.assertEqual(e_rab_kpi_dict, {})
        else:
          for key in e_rab_kpi_dict:
            self.assertEqual(len(e_rab_kpi_dict[key]),
                             e_rab_array_shape[0])

      elif 'e_utran' in data_array.getReference():
        self.assertEqual(data_array.getArrayShape(),
                         e_utran_array_shape)
        self.assertEqual(data_array.getArrayDtype(),
                         e_utran_array_dtype)

        e_utran_kpi_dict = self.getOrsDataArrayAsDict(
          data_array.getRelativeUrl(),
          'e_utran_ip_throughput'
        )
        if e_utran_array_shape is None:
          self.assertEqual(e_utran_kpi_dict, {})
        else:
          for key in e_utran_kpi_dict:
            if key == 'evt':
              self.assertEqual(
                len(e_utran_kpi_dict[key]),
                e_utran_array_shape[0] // QCI_COUNT
              )
            else:
              self.assertEqual(len(e_utran_kpi_dict[key]), 1)
              if key != 'active_qci':
                self.assertEqual(
                  len(e_utran_kpi_dict[key][0]),
                  e_utran_array_shape[0] // QCI_COUNT
                )

      elif 'cell_ue_count' in data_array.getReference():
        self.assertEqual(data_array.getArrayShape(), cell_ue_count_array_shape)
        self.assertEqual(data_array.getArrayDtype(), cell_ue_count_array_dtype)

        cell_ue_count_dict = self.getOrsDataArrayAsDict(
          data_array.getRelativeUrl(),
          'ue_count'
        )
        if cell_ue_count_array_shape is None:
          self.assertEqual(cell_ue_count_dict, {})
        else:
          for key in cell_ue_count_dict:
            size = cell_ue_count_array_shape[0]
            if key == 'base':
              size = 84
            for col in cell_ue_count_dict[key]:
              # Values are lower then shape because it is processed, so
              # the array is clean before respond.
              self.assertEqual(size,
                               len(cell_ue_count_dict[key][col]), (key, col))

      elif 'cell_rrc' in data_array.getReference():
        self.assertEqual(data_array.getArrayShape(), cell_rrc_array_shape)
        self.assertEqual(data_array.getArrayDtype(), cell_rrc_array_dtype)

        rrc_connection_request_count_dict = self.getOrsDataArrayAsDict(
          data_array.getRelativeUrl(),
          'rrc_connection_request'
        )
        if cell_rrc_array_shape is None:
          self.assertEqual(rrc_connection_request_count_dict, {})
        else:
          for key in rrc_connection_request_count_dict:
            # check number of cells + base
            size = cell_rrc_array_shape[0]
            if key == 'base':
              size = 84
            for col in rrc_connection_request_count_dict[key]:
              self.assertEqual(size,
                len(rrc_connection_request_count_dict[key][col]), (key, col))

        rrc_paging_dict = self.getOrsDataArrayAsDict(
          data_array.getRelativeUrl(),
          'rrc_paging'
        )
        if cell_rrc_array_shape is None:
          self.assertEqual(rrc_paging_dict, {})
        else:
          for key in rrc_paging_dict:
            # check number of cells + base
            for col in rrc_paging_dict[key]:
              # Only rrc_paging has a specific calculation to drop certain values.
              self.assertEqual(len(rrc_paging_dict[key][col]), 70)

        unsuccessful_rrc_con_att_dict = self.getOrsDataArrayAsDict(
          data_array.getRelativeUrl(),
          'unsuccessful_rrc_con_att'
        )
        if cell_rrc_array_shape is None:
          self.assertEqual(unsuccessful_rrc_con_att_dict, {})
        else:

          for key in unsuccessful_rrc_con_att_dict:
            size = cell_rrc_array_shape[0]
            if key == 'base':
              size = 84
            # check number of cells + base
            for col in unsuccessful_rrc_con_att_dict[key]:
              # Only unsucessful_rrc_recon + utc is included
              self.assertEqual(len(unsuccessful_rrc_con_att_dict[key][col]),
                               size, (key, col))

        failure_rrc_security_mode_dict = self.getOrsDataArrayAsDict(
          data_array.getRelativeUrl(),
          'unsuccessful_rrc_con_att'
        )
        if cell_rrc_array_shape is None:
          self.assertEqual(failure_rrc_security_mode_dict, {})
        else:
          for key in failure_rrc_security_mode_dict:
            # check number of cells + base
            size = cell_rrc_array_shape[0]
            if key == 'base':
              size = 84
            for col in failure_rrc_security_mode_dict[key]:
              # Only failure_rate_rrc_sec + utc is included
              self.assertEqual(len(failure_rrc_security_mode_dict[key][col]),
                              size, (key, col))

      elif 'cell_rms_rx' in data_array.getReference():
        self.assertEqual(data_array.getArrayShape(), cell_rms_rx_array_shape)
        self.assertEqual(data_array.getArrayDtype(), cell_rms_rx_array_dtype)

        rms_rx_per_cell_antenna_dict = self.getOrsDataArrayAsDict(
          data_array.getRelativeUrl(),
          'rms_rx'
        )
        if cell_rms_rx_array_shape is None:
          self.assertEqual(rms_rx_per_cell_antenna_dict, {})
        else:
          for key in rms_rx_per_cell_antenna_dict:
            # check number of cells + base
            for col in rms_rx_per_cell_antenna_dict[key]:
              # Only 2 antenas are included
              self.assertEqual(len(rms_rx_per_cell_antenna_dict[key][col]), 2)
              for ant in rms_rx_per_cell_antenna_dict[key][col]:
                # Only 2 antenas are included so consider half of results.
                self.assertEqual(cell_rms_rx_array_shape[0]/2,
                  len(rms_rx_per_cell_antenna_dict[key][col][ant]))


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
