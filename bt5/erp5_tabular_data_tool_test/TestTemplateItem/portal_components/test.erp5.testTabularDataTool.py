# coding: utf-8
##############################################################################
#
# Copyright (c) 2002-2020 Nexedi SA and Contributors. All Rights Reserved.
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

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.Sequence import SequenceList
from Products.ERP5Type.tests.utils import createZODBPythonScript
import math

class TestTabularDataTool(ERP5TypeTestCase):
  """
  Test for Tabular Data Tool
  """

  #maxDiff = None

  def getTitle(self):
    return "TestTabularDataTool"

  def getBusinessTemplateList(self):
    """
    Tuple of Business Templates we need to install
    """
    return ('erp5_trade',)

  def beforeTearDown(self):
    """
    Remove this test related documents (for livetest in the real environment)
    """
    organisation_module = self.portal.organisation_module
    internal_packing_list_module = self.portal.internal_packing_list_module
    product_module = self.portal.product_module
    delete_module_list = [organisation_module, internal_packing_list_module, product_module]
    def isDelete(document):
      if document.getTitle() is None:
        return False
      return document.getTitle().startswith(self._getTestDocumentTitlePrefix())
    for module in delete_module_list:
      delete_id_list = [id_ for id_ in module.objectIds() if isDelete(module[id_])]
      module.manage_delObjects(delete_id_list)
    rule_reference_script = 'InternalPackingList_getRuleReference'
    if self.portal.portal_skins.custom.get(rule_reference_script, None) is not None:
      self.portal.portal_skins.custom.manage_delObjects([rule_reference_script])
    self.commit()

  def _getTestDocumentTitlePrefix(self):
    return self.getTitle()

  def _getTestDocumentTitle(self, reference):
    return "{}_{}".format(self._getTestDocumentTitlePrefix(), reference)

  def testSearchResults(self):
    """
      Test portal_tabular.searchResults() which uses portal_catalog.searchResults()
      as the given data.
    """
    organisationA_title = self._getTestDocumentTitle('organisationA')
    organisation_description = '(description default value is empty string)'
    self.portal.organisation_module.newContent(
                      portal_type='Organisation',
                      description=organisation_description,
                      title=organisationA_title)
    self.portal.organisation_module.newContent(
                      portal_type='Organisation',
                      description=organisation_description,
                      title=self._getTestDocumentTitle('organisationB'))
    self.tic()
    result_list = self.portal.portal_catalog(portal_type='Organisation',
                                     title=self._getTestDocumentTitle('organisation%'))
    self.assertEqual(len(result_list), 2)
    organisation_tabular = self.portal.portal_tabular.searchResults(portal_type='Organisation',
                                     title=self._getTestDocumentTitle('organisation%'),
                                     fillna_on_string=None)
    self.assertEqual(len(organisation_tabular), 2)

    self.assertIn('title', organisation_tabular.columns.tolist())
    organisationA_tabular = organisation_tabular[
                                organisation_tabular['title'] == organisationA_title]
    self.assertEqual(len(organisationA_tabular), 1)
    # only 'description' has empty string default value, so check this separatedly
    self.assertEqual(organisationA_tabular.iloc[0]['description'], organisation_description)

    catalog_column_list = ['uid', 'security_uid','owner','viewable_owner','path','relative_url',
                           'parent_uid','id',
                           'description',
                           'title','meta_type','portal_type','opportunity_state',
                           'corporate_registration_code','ean13_code',
                           'validation_state','simulation_state','causality_state',
                           'invoice_state','payment_state','event_state',
                           'immobilisation_state','reference',
                           'grouping_reference','grouping_date','source_reference',
                           'destination_reference','string_index','int_index',
                           'float_index','has_cell_content','creation_date',
                           'modification_date', 'indexation_timestamp']
    self.assertTrue(len(organisationA_tabular.columns.tolist()) >= len(catalog_column_list))
    # catalog result has both uid and path by default so ignore them
    select_dict = dict.fromkeys(set(catalog_column_list) - set(['uid','path']), None)
    catalog_search_result = self.portal.portal_catalog.searchResults(
                              portal_type='Organisation',
                              title=self._getTestDocumentTitle('organisation%'),
                              select_dict=select_dict)
    organisationA_result = [r for r in catalog_search_result if r.getTitle() == organisationA_title][0]
    for catalog_column in catalog_column_list:
      self.assertEqual(organisationA_tabular.iloc[0][catalog_column],
                       organisationA_result.getProperty(catalog_column),
                       "Not equal on {} expect:{}, result:{}".format(
                         catalog_column,
                         organisationA_tabular.iloc[0][catalog_column],
                         organisationA_result.getProperty(catalog_column)
                       ))

  def stepSetTestDocumentTitleNode1(self, sequence=None, sequence_list=None, **kw):
    sequence.edit(node_title=self._getTestDocumentTitle('node1'))

  def stepSetTestDocumentTitleResource1(self, sequence=None, sequence_list=None, **kw):
    sequence.edit(resource_title=self._getTestDocumentTitle('resource1'))

  def stepAddNode(self, sequence=None, sequence_list=None, **kw):
    node_title = sequence.get('node_title')
    node_value = self.portal.organisation_module.newContent(portal_type='Organisation',
                                                            title=node_title)
    sequence.edit(node_value=node_value)

  def stepAddResource(self, sequence=None, sequence_list=None, **kw):
    resource_title = sequence.get('resource_title')
    resource_value = self.portal.product_module.newContent(
      portal_type='Product', title=resource_title)
    sequence.edit(resource_value=resource_value)

  def stepSetTestDocumentTitleMovement1(self, sequence=None, sequence_list=None, **kw):
    sequence.edit(movement_title=self._getTestDocumentTitle('movement1'))

  def stepAddInternalPackingList(self, sequence=None, sequence_list=None, **kw):
    movement_title = sequence.get('movement_title')
    resource_value = sequence.get('resource_value')
    node_value = sequence.get('node_value')
    ipl = self.portal.internal_packing_list_module.newContent(
      portal_type='Internal Packing List', source_value=node_value, title=movement_title)
    ipl.newContent(portal_type='Internal Packing List Line',
                   title=movement_title, quantity=10, resource_value=resource_value)
    sequence.edit(internal_packing_list=ipl)

  def stepConfirmInternalPackingList(self, sequence=None, sequence_list=None, **kw):
    internal_packing_list = sequence.get('internal_packing_list')
    internal_packing_list.confirm()
    self.assertEqual(internal_packing_list.getSimulationState(),'confirmed')

  def stepGetInventoryList(self, sequence=None, sequence_list=None, **kw):
    resource_value = sequence.get('resource_value')
    node_value = sequence.get('node_value')
    title_prefix = sequence.get('title_prefix', None)
    if title_prefix is None:
      title_prefix = self._getTestDocumentTitlePrefix()
    inventory_list = self.portal.portal_simulation.getInventoryList(
                       title="{}%".format(title_prefix),
                       portal_type='Internal Packing List Line',
                       resource_uid=resource_value.getUid(), node_uid=node_value.getUid())
    sequence.edit(inventory_list=inventory_list)

  def stepGetAllResourceInventoryList(self, sequence=None, sequence_list=None, **kw):
    title_prefix = sequence.get('title_prefix', None)
    node_value = sequence.get('node_value')
    if title_prefix is None:
      title_prefix = self._getTestDocumentTitlePrefix()
    inventory_list = self.portal.portal_simulation.getInventoryList(
                       title="{}%".format(title_prefix),
                       portal_type='Internal Packing List Line', node_uid=node_value.getUid())
    sequence.edit(inventory_list=inventory_list)

  def stepCheckWithGetFromDocumentListAgainstInventoryList(self, sequence=None, sequence_list=None, **kw):
    node_title = sequence.get('node_title')
    movement_title = sequence.get('movement_title')
    inventory_list = sequence.get('inventory_list')
    self.assertEqual(len(inventory_list), 1)
    inventory_tabular = self.portal.portal_tabular.getFromDocumentList(
                          inventory_list, property_name_list=["node_title", "title"])
    self.assertEqual(len(inventory_tabular), 1)
    self.assertIn('node_title', inventory_tabular.columns.tolist())
    self.assertIn('title', inventory_tabular.columns.tolist())

    # if explicitly specifies property_name_list,
    # the tabular only has the specified columns
    self.assertEqual(len(inventory_tabular.columns.tolist()), 2)
    self.assertEqual(inventory_tabular.iloc[0]['node_title'], node_title)
    self.assertEqual(inventory_tabular.iloc[0]['title'], movement_title)

    default_inventory_tabular = self.portal.portal_tabular.getFromDocumentList(inventory_list)
    self.assertEqual(len(default_inventory_tabular), 1)

    # The inventory list is ragarged as Internal Packing Line List, so does not have node_title
    self.assertNotIn('node_title', default_inventory_tabular.columns.tolist())
    self.assertIn('title', default_inventory_tabular.columns.tolist())

    # If do not specify the property_names, it automatically add
    # all the Sale Packing List Line property and category names based on the portal type
    # configuration, so the number of columns is bigger than 2. (can be > 200)
    self.assertTrue(len(default_inventory_tabular.columns.tolist()) > 2)

    self.assertEqual(default_inventory_tabular.iloc[0]['title'], movement_title)
    self.assertIn('source_title', default_inventory_tabular.columns.tolist())
    # The inventory list is regarded as Sale Packing Line List, so it has source_title
    self.assertEqual(default_inventory_tabular.iloc[0]['source_title'], node_title)

  def stepCheckWithGetTabularAgainstInventoryList(self, sequence=None, sequence_list=None, **kw):
    inventory_list = sequence.get('inventory_list')
    node_title = sequence.get('node_title')
    node_value = sequence.get('node_value')
    resource_value = sequence.get('resource_value')
    resource_title = sequence.get('resource_title')
    movement_title = sequence.get('movement_title')

    # Test with portal_tabular() whitch is an alias of portal_tabular.getTabular()

    # at first check without passing additonal_property_name_list parameter
    inventory_tabular_without_name = self.portal.portal_tabular(inventory_list)
    property_name_list = ['node_title','title','resource_title']
    self.assertEqual(len(inventory_tabular_without_name), 1)
    for property_name in property_name_list:
      self.assertTrue(property_name not in inventory_tabular_without_name.columns.tolist(),
                     "{} is in the columns:{}".format(
                       property_name,
                       inventory_tabular_without_name.columns.tolist()))
    # They have uid because Resource_zGetInventoryList returns them in the brain
    self.assertEqual(inventory_tabular_without_name.iloc[0]['node_uid'],
                     node_value.getUid())
    self.assertEqual(inventory_tabular_without_name.iloc[0]['resource_uid'],
                     resource_value.getUid())

    # check with additional_property_name_list parameter
    inventory_tabular_with_name = self.portal.portal_tabular(
                                    inventory_list,
                                    additional_property_name_list=property_name_list)
    self.assertEqual(len(inventory_tabular_with_name), 1)
    self.assertEqual(len(inventory_tabular_with_name.columns.tolist()),
                    len(inventory_tabular_without_name.columns.tolist())
                  + len(property_name_list))
    for property_name in property_name_list:
      self.assertTrue(property_name in inventory_tabular_with_name.columns.tolist(),
                     "{} is not in the columns:{}".format(
                       property_name,
                       inventory_tabular_with_name.columns.tolist()))
    self.assertEqual(inventory_tabular_with_name.iloc[0]['node_title'], node_title)
    self.assertEqual(inventory_tabular_with_name.iloc[0]['title'], movement_title)
    self.assertEqual(inventory_tabular_with_name.iloc[0]['resource_title'], resource_title)

  def testGetInventoryList(self):
    sequence_list = SequenceList()
    sequence_string = """
    DisableSimulationOnInternalPackingList
    SetTestDocumentTitleNode1
    AddNode
    SetTestDocumentTitleResource1
    AddResource
    SetTestDocumentTitleMovement1
    AddInternalPackingList
    ConfirmInternalPackingList
    Tic
    GetInventoryList
    CheckWithGetFromDocumentListAgainstInventoryList
    CheckWithGetTabularAgainstInventoryList
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def testFillnaOnString(self):
    """
    Test fillna_on_string parameter
    """
    dict_list = [{"test":"a"},
                 {"test":None},
                 {"test":""},
                 {"test":"d"},
                 {"test":None}]
    # by default it is empty
    df1 = self.portal.portal_tabular(dict_list)
    empty_value = ""
    self.assertEqual(df1.iloc[0]["test"], "a")
    self.assertEqual(df1.iloc[1]["test"], empty_value)
    self.assertEqual(df1.iloc[2]["test"], "")
    self.assertEqual(df1.iloc[3]["test"], "d")
    self.assertEqual(df1.iloc[4]["test"], empty_value)
    empty_value_2 = """[No Value]"""
    df2 = self.portal.portal_tabular(dict_list, fillna_on_string=empty_value_2)
    self.assertEqual(df2.iloc[0]["test"], "a")
    self.assertEqual(df2.iloc[1]["test"], empty_value_2)
    self.assertEqual(df2.iloc[2]["test"], "")
    self.assertEqual(df2.iloc[3]["test"], "d")
    self.assertEqual(df2.iloc[4]["test"], empty_value_2)

  def testFillnaOnNumber(self):
    """
    Test fillna_on_number
    """
    dict_list = [{"test":0},
                 {"test":None},
                 {"test":2},
                 {"test":3},
                 {"test":None}]
    # by default it is empty
    df1 = self.portal.portal_tabular(dict_list)
    empty_value = 0.0
    self.assertEqual(df1.iloc[0]["test"], 0)
    self.assertEqual(df1.iloc[1]["test"], empty_value)
    self.assertEqual(df1.iloc[2]["test"], 2)
    self.assertEqual(df1.iloc[3]["test"], 3)
    self.assertEqual(df1.iloc[4]["test"], empty_value)
    empty_value_2 = -1
    df2 = self.portal.portal_tabular(dict_list, fillna_on_number=empty_value_2)
    self.assertEqual(df2.iloc[0]["test"], 0)
    self.assertEqual(df2.iloc[1]["test"], empty_value_2)
    self.assertEqual(df2.iloc[2]["test"], 2)
    self.assertEqual(df2.iloc[3]["test"], 3)
    self.assertEqual(df2.iloc[4]["test"], empty_value_2)

  def testGetFromDocumentList(self):
    """
     Check to specify accessor
    """
    organisation_list = []
    for _title in ('testAccesssor1', 'testAccesssor2'):
      organisation_title = self._getTestDocumentTitle(_title)
      organisation = self.portal.organisation_module.newContent(
                        portal_type='Organisation', title=organisation_title,
                        activity_code='test activity code')
      organisation_list.append(organisation)
    organisation_tabular = self.portal.portal_tabular.getFromDocumentList(organisation_list)
    self.assertEqual(len(organisation_tabular), 2)
    self.assertEqual(organisation_tabular.iloc[0]['activity_code'], 'test activity code')

  def testFillnaOnUid(self):
    """
    Check fillna_on_uid parameter
    """
    node_title = self._getTestDocumentTitle("test_node_fillna_on_uid_1")
    node_value = self.portal.organisation_module.newContent(
                   portal_type='Organisation',title=node_title)
    spl_title = self._getTestDocumentTitle("test_spl_fillna_on_uid_1")
    spl = self.portal.sale_packing_list_module.newContent(
            portal_type='Sale Packing List', source_value=node_value, title=spl_title)
    sale_packing_list_list = [spl]
    sale_packing_list_tabular = self.portal.portal_tabular.getFromDocumentList(
                                   sale_packing_list_list)
    self.assertEqual(len(sale_packing_list_tabular), 1)
    self.assertEqual(sale_packing_list_tabular.iloc[0]['destination_uid'], -1)
    self.assertEqual(sale_packing_list_tabular.iloc[0]['source_uid'], node_value.getUid())

    empty_uid = -99999999
    sale_packing_list_tabular2 = self.portal.portal_tabular.getFromDocumentList(
                                   sale_packing_list_list, fillna_on_uid=empty_uid)
    self.assertEqual(len(sale_packing_list_tabular2), 1)
    self.assertEqual(sale_packing_list_tabular2.iloc[0]['destination_uid'], empty_uid)
    self.assertEqual(sale_packing_list_tabular2.iloc[0]['source_uid'], node_value.getUid())


  def testFillna(self):
    """
    Test portal_tabular.fillna() method
    """
    dict_list = [{'test':0},
                 {'test':None},
                 {'test':2},
                 {'test':3},
                 {'test':None}]
    # by default it is empty
    df1 = self.portal.portal_tabular(dict_list)
    numeric_empty_value = 0.0
    self.assertEqual(df1.iloc[0]['test'], 0)
    self.assertEqual(df1.iloc[1]['test'], numeric_empty_value)
    self.assertEqual(df1.iloc[2]['test'], 2)
    self.assertEqual(df1.iloc[3]['test'], 3)
    self.assertEqual(df1.iloc[4]['test'], numeric_empty_value)

    # add new column into the dataframe
    df1['test_numeric'] = [None, 100, None, 200, 300]
    # So by default Na value of numeric is NaN in pandas dataframe
    self.assertTrue(math.isnan(df1.iloc[0]['test_numeric']))
    self.assertEqual(df1.iloc[1]['test_numeric'], 100)
    self.assertTrue(math.isnan(df1.iloc[2]['test_numeric']))
    self.assertEqual(df1.iloc[3]['test_numeric'], 200)
    self.assertEqual(df1.iloc[4]['test_numeric'], 300)

    df1['test_string'] = ['x', None, 'y', None, 'z']
    # The default Na value of string is None in pandas dataframe
    self.assertEqual(df1.iloc[0]['test_string'], 'x')
    self.assertEqual(df1.iloc[1]['test_string'], None)
    self.assertEqual(df1.iloc[2]['test_string'], 'y')
    self.assertEqual(df1.iloc[3]['test_string'], None)
    self.assertEqual(df1.iloc[4]['test_string'], 'z')

    # Fill Na/NaN values with portal_tabular.fillna()
    df2 = self.portal.portal_tabular.fillna(df1)
    self.assertEqual(df2.iloc[0]['test_numeric'], numeric_empty_value)
    self.assertEqual(df2.iloc[1]['test_numeric'], 100)
    self.assertEqual(df2.iloc[2]['test_numeric'], numeric_empty_value)
    self.assertEqual(df2.iloc[3]['test_numeric'], 200)
    self.assertEqual(df2.iloc[4]['test_numeric'], 300)

    string_empty_value = ''
    # Test they are filled with the default string filler ''
    self.assertEqual(df2.iloc[0]['test_string'], 'x')
    self.assertEqual(df2.iloc[1]['test_string'], string_empty_value)
    self.assertEqual(df2.iloc[2]['test_string'], 'y')
    self.assertEqual(df2.iloc[3]['test_string'], string_empty_value)
    self.assertEqual(df2.iloc[4]['test_string'], 'z')

    # portal_tabular.fillna() with specifying the empty values
    numeric_empty_value_2 = -1
    string_empty_value_2 = """[No Value]"""
    df3 = self.portal.portal_tabular.fillna(df1,
                                            fillna_on_number=numeric_empty_value_2,
                                            fillna_on_string=string_empty_value_2)
    # Test with the specified filler
    self.assertEqual(df3.iloc[0]['test_numeric'], numeric_empty_value_2)
    self.assertEqual(df3.iloc[1]['test_numeric'], 100)
    self.assertEqual(df3.iloc[2]['test_numeric'], numeric_empty_value_2)
    self.assertEqual(df3.iloc[3]['test_numeric'], 200)
    self.assertEqual(df3.iloc[4]['test_numeric'], 300)

    self.assertEqual(df3.iloc[0]['test_string'], 'x')
    self.assertEqual(df3.iloc[1]['test_string'], string_empty_value_2)
    self.assertEqual(df3.iloc[2]['test_string'], 'y')
    self.assertEqual(df3.iloc[3]['test_string'], string_empty_value_2)
    self.assertEqual(df3.iloc[4]['test_string'], 'z')

  def stepDisableSimulationOnInternalPackingList(self, sequence=None, sequence_list=None, **kw):
    # Do not care simulation in this test, so return None
    # for the rule reference of Internal Packing List
    script_container = self.portal.portal_skins.custom
    code = 'return None'
    createZODBPythonScript(script_container, 'InternalPackingList_getRuleReference', '**kw', code)

  def stepSetTestDocumentTitleNode2(self, sequence=None, sequence_list=None, **kw):
    sequence.edit(node_title=self._getTestDocumentTitle('node2'))

  def stepSetTestDocumentTitleResource2(self, sequence=None, sequence_list=None, **kw):
    sequence.edit(resource_title=self._getTestDocumentTitle('resource2'))

  def stepSetTestDocumentTitleTestReportMovement1(self, sequence=None, sequence_list=None, **kw):
    sequence.edit(movement_title=self._getTestDocumentTitle('test_report_movement1'))

  def stepSetTestDocumentTitleTestReportMovement2(self, sequence=None, sequence_list=None, **kw):
    sequence.edit(movement_title=self._getTestDocumentTitle('test_report_movement2'))

  def stepSetTestDocumentTitleTestReportMovement3(self, sequence=None, sequence_list=None, **kw):
    sequence.edit(movement_title=self._getTestDocumentTitle('test_report_movement3'))

  def stepSetTestDocumentTitleTestReportMovement4(self, sequence=None, sequence_list=None, **kw):
    sequence.edit(movement_title=self._getTestDocumentTitle('test_report_movement4'))

  def stepConfirmAllInternalPackingList(self, sequence=None, sequence_list=None, **kw):
    title = "{}_{}%".format(self._getTestDocumentTitlePrefix(), 'test_report_movement')
    result = self.portal.portal_catalog(portal_type='Internal Packing List',
                                        title=title)
    for r in result:
      internal_packing_list = r.getObject()
      internal_packing_list.confirm()
      self.assertEqual(internal_packing_list.getSimulationState(),'confirmed')

  def stepSetTitlePrefix(self, sequence=None, sequence_list=None, **kw):
    title_prefix = "{}_{}".format(self._getTestDocumentTitlePrefix(), 'test_report_movement')
    sequence.edit(title_prefix=title_prefix)

  def stepCheckToCreateReport(self, sequence=None, sequence_list=None, **kw):
    inventory_list = sequence.get('inventory_list')
    additional_property_name_list = ['resource_title', 'node_title', 'title']
    inventory_tabular = self.portal.portal_tabular(
                          inventory_list,
                          additional_property_name_list=additional_property_name_list)
    self.assertEqual(len(inventory_tabular), 4)
    node_value = sequence.get('node_value')
    for i in range(4):
      self.assertEqual(inventory_tabular.iloc[i]['node_title'],node_value.getTitle())
      self.assertEqual(inventory_tabular.iloc[i]['inventory'], -10)

    """
    node1, resource1, movement1, -10
    node1, resource1, movement2, -10
    node1, resource2, movement3, -10
    node1, resource2, movement4, -10
    """

    # Aggregate the result grouping by resource_title and node_title,
    # then sorting by resource_title, and summing the inventory.
    report_tabular = inventory_tabular.groupby(
      ['resource_title',
       'node_title',
       ]
      ).agg(dict(inventory='sum')).reset_index().sort_values(
          by=['resource_title'])

    self.assertEqual(len(report_tabular), 2)
    self.assertEqual(report_tabular.iloc[0]['inventory'], -20)
    self.assertEqual(report_tabular.iloc[1]['inventory'], -20)

    title_prefix = self._getTestDocumentTitlePrefix()
    # The result is ordered by resource title
    self.assertEqual(report_tabular.iloc[0]['resource_title'],
                     "{}_{}".format(title_prefix, 'resource1'))
    self.assertEqual(report_tabular.iloc[1]['resource_title'],
                     "{}_{}".format(title_prefix, 'resource2'))

    # Turn into dict to show in listbox for example
    report_dict_list = report_tabular.to_dict("records")
    for report_dict in report_dict_list:
      self.assertTrue(isinstance(report_dict, dict))
      self.assertEqual(report_dict['node_title'], node_value.getTitle())
      self.assertEqual(report_dict['inventory'], -20)
      self.assertIn('resource_title', report_dict)

  def testReport(self):
    """
    Test tabular data result for reports such as groupby, join, and sorting
    """
    sequence_list = SequenceList()
    sequence_string = """
    DisableSimulationOnInternalPackingList
    Tic
    SetTestDocumentTitleNode1
    AddNode
    SetTestDocumentTitleResource1
    AddResource
    SetTestDocumentTitleTestReportMovement1
    AddInternalPackingList
    SetTestDocumentTitleTestReportMovement2
    AddInternalPackingList
    SetTestDocumentTitleResource2
    AddResource
    SetTestDocumentTitleTestReportMovement3
    AddInternalPackingList
    SetTestDocumentTitleTestReportMovement4
    AddInternalPackingList
    ConfirmAllInternalPackingList
    Tic
    SetTitlePrefix
    GetAllResourceInventoryList
    CheckToCreateReport
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def testEncoding(self):
    """
    Test portal_tabular returns utf-8 string not unicode string
    """
    dict_list = [{'test':None},
                 {'test':'あ'},
                 {'test':''},
                 {'test':'ç'},
                 {'test':None}]
    # by default it is empty
    df1 = self.portal.portal_tabular(dict_list)
    string_empty_value = ''
    self.assertEqual(df1.iloc[0]['test'], string_empty_value)
    self.assertEqual(df1.iloc[1]['test'], 'あ')
    self.assertEqual(df1.iloc[2]['test'], string_empty_value)
    self.assertEqual(df1.iloc[3]['test'], 'ç')
    self.assertEqual(df1.iloc[4]['test'], string_empty_value)

  def testEmptyTabular(self):
    """
    Test updating empty tabular does not update different empty tabular
    """
    empty_tabular = self.portal.portal_tabular(data_list=[])
    empty_tabular['a'] = [1,2,3]
    empty_tabular2 = self.portal.portal_tabular(data_list=[])
    self.assertNotEqual(len(empty_tabular.columns), len(empty_tabular2.columns))
    self.assertNotEqual(len(empty_tabular), len(empty_tabular2))
