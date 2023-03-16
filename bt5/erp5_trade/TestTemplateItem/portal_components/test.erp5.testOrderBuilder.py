# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008 Nexedi SA and Contributors. All Rights Reserved.
#          Łukasz Nowak <lukasz.nowak@ventis.com.pl>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################

from Products.ERP5Type.Utils import ensure_list
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from DateTime import DateTime
from Products.ERP5Type.tests.Sequence import SequenceList
from erp5.component.test.testOrder import TestOrderMixin
from Products.ERP5.tests.testInventoryAPI import InventoryAPITestCase
import six

class TestOrderBuilderMixin(TestOrderMixin, InventoryAPITestCase):

  run_all_test = 1

  order_builder_portal_type = 'Order Builder'

  order_module = 'purchase_order_module'
  order_portal_type = 'Purchase Order'
  order_line_portal_type = 'Purchase Order Line'
  order_cell_portal_type = 'Purchase Order Cell'

  packing_list_portal_type = 'Internal Packing List'
  packing_list_line_portal_type = 'Internal Packing List Line'
  packing_list_cell_portal_type = 'Internal Packing List Cell'

  # hardcoded values
  order_builder_hardcoded_time_diff = 10.0

  # defaults
  decrease_quantity = 1.0
  max_delay = 0.0
  min_flow = 0.0

  def afterSetUp(self):
    """
    Make sure to not use special apparel setting from TestOrderMixin
    """
    self.createCategories()
    self.validateRules()
    InventoryAPITestCase.afterSetUp(self)
    self.node_1 = self.portal.organisation_module.newContent(title="Node 1")
    self.node_2 = self.portal.organisation_module.newContent(title="Node 2")
    self.pinDateTime(None)

  def assertDateAlmostEquals(self, first_date, second_date):
    self.assertTrue(abs(first_date - second_date) < 1.0/86400,
                    "%r != %r" % (first_date, second_date))

  def stepSetMaxDelayOnResource(self, sequence):
    """
    Sets max_delay on resource
    """
    resource = sequence.get('resource')
    resource.edit(purchase_supply_line_max_delay=self.max_delay)

  def stepSetMinFlowOnResource(self, sequence):
    """
    Sets min_flow on resource
    """
    resource = sequence.get('resource')
    resource.edit(purchase_supply_line_min_flow=self.min_flow)

  def stepFillOrderBuilder(self, sequence):
    self.fillOrderBuilder(sequence=sequence)

  def fillOrderBuilder(self, sequence=None):
    """
    Fills Order Builder with proper quantites
    """
    order_builder = self.order_builder
    if sequence is not None:
      organisation = sequence.get('organisation')
    else:
      organisation = None

    order_builder.edit(
      delivery_module = self.order_module,
      delivery_portal_type = self.order_portal_type,
      delivery_line_portal_type = self.order_line_portal_type,
      delivery_cell_portal_type = self.order_cell_portal_type,
      destination_value = organisation,
      resource_portal_type = self.resource_portal_type,
      simulation_select_method_id='generateMovementListForStockOptimisation',
    )
    order_builder.newContent(
      portal_type = 'Category Movement Group',
      collect_order_group='delivery',
      tested_property=['source', 'destination',
                       'source_section', 'destination_section'],
      int_index=1
      )
    order_builder.newContent(
      portal_type = 'Property Movement Group',
      collect_order_group='delivery',
      tested_property=['start_date', 'stop_date'],
      int_index=2
      )

    order_builder.newContent(
      portal_type = 'Category Movement Group',
      collect_order_group='line',
      tested_property=['resource'],
      int_index=1
      )
    order_builder.newContent(
      portal_type = 'Base Variant Movement Group',
      collect_order_group='line',
      int_index=2
      )

    order_builder.newContent(
      portal_type = 'Variant Movement Group',
      collect_order_group='cell',
      int_index=1
      )

  def stepCheckGeneratedDocumentListVariated(self, sequence):
    """
    Checks documents generated by Order Builders with its properties for variated resource
    """
    organisation = sequence.get('organisation')
    resource = sequence.get('resource')

    # XXX: add support for more generated documents
    order, = sequence.get('generated_document_list')
    self.assertEqual(order.getDestinationValue(), organisation)
    self.assertDateAlmostEquals(order.getStartDate(), self.wanted_start_date)
    self.assertDateAlmostEquals(order.getStopDate(), self.wanted_stop_date)

    # XXX: ... and for more lines/cells too
    order_line, = order.contentValues(portal_type=self.order_line_portal_type)
    self.assertEqual(order_line.getResourceValue(), resource)
    self.assertEqual(order_line.getTotalQuantity(),
      sum(six.itervalues(self.wanted_quantity_matrix)))

    quantity_matrix = {}
    for cell in order_line.contentValues(portal_type=self.order_cell_portal_type):
      key = cell.getProperty('membership_criterion_category')
      self.assertNotIn(key, quantity_matrix)
      quantity_matrix[key] = cell.getQuantity()
    self.assertEqual(quantity_matrix, self.wanted_quantity_matrix)

  def stepCheckGeneratedDocumentList(self, sequence):
    """
    Checks documents generated by Order Builders with its properties
    """
    organisation = sequence.get('organisation')
    resource = sequence.get('resource')

    # XXX: add support for more generated documents
    order, = sequence.get('generated_document_list')
    self.assertEqual(order.getDestinationValue(), organisation)
    self.assertDateAlmostEquals(self.wanted_start_date, order.getStartDate())
    self.assertDateAlmostEquals(self.wanted_stop_date, order.getStopDate())

    # XXX: ... and for more lines/cells too
    order_line, = order.contentValues(portal_type=self.order_line_portal_type)
    self.assertEqual(order_line.getResourceValue(), resource)
    self.assertEqual(order_line.getTotalQuantity(), self.wanted_quantity)

  def stepBuildOrderBuilder(self, sequence):
    """
    Invokes build method for Order Builder
    """
    order_builder = sequence.get('order_builder')
    generated_document_list = order_builder.build()
    sequence.set('generated_document_list', generated_document_list)

  def createOrderBuilder(self):
    """
    Creates empty Order Builder
    """
    order_builder = self.portal.portal_orders.newContent(
      portal_type=self.order_builder_portal_type)
    self.order_builder = order_builder
    return order_builder

  def stepCreateOrderBuilder(self, sequence):
    order_builder = self.createOrderBuilder()
    sequence.set('order_builder', order_builder)

  def stepDecreaseOrganisationResourceQuantityVariated(self, sequence):
    """
    Creates movement with variation from organisation to None.
    Using Internal Packing List, confirms it.

    Note: Maybe use InventoryAPITestCase::_makeMovement instead of IPL ?
    """
    organisation = sequence.get('organisation')
    resource = sequence.get('resource')

    packing_list_module = self.portal.getDefaultModule(
      portal_type = self.packing_list_portal_type
    )

    packing_list = packing_list_module.newContent(
      portal_type = self.packing_list_portal_type,
      source_value = organisation,
      start_date = self.datetime+10,
      specialise = self.business_process,
    )

    packing_list_line = packing_list.newContent(
      portal_type = self.packing_list_line_portal_type,
      resource_value = resource,
      quantity = self.decrease_quantity,
    )

    self.decrease_quantity_matrix = {
      'variation/%s/blue' % resource.getRelativeUrl() : 1.0,
      'variation/%s/green' % resource.getRelativeUrl() : 2.0,
    }

    self.wanted_quantity_matrix = self.decrease_quantity_matrix.copy()

    packing_list_line.setVariationCategoryList(
      ensure_list(self.decrease_quantity_matrix.keys()),
    )

    self.tic()

    base_id = 'movement'
    cell_key_list = list(packing_list_line.getCellKeyList(base_id=base_id))
    cell_key_list.sort()

    for cell_key in cell_key_list:
      cell = packing_list_line.newCell(base_id=base_id,
                                portal_type=self.packing_list_cell_portal_type, *cell_key)
      cell.edit(mapped_value_property_list=['price','quantity'],
                quantity=self.decrease_quantity_matrix[cell_key[0]],
                predicate_category_list=cell_key,
                variation_category_list=cell_key)

    packing_list.confirm()

  def stepDecreaseOrganisationResourceQuantity(self, sequence):
    """
    Creates movement from organisation to None.
    Using Internal Packing List, confirms it.

    Note: Maybe use InventoryAPITestCase::_makeMovement instead of IPL ?
    """
    organisation = sequence.get('organisation')
    resource = sequence.get('resource')

    packing_list_module = self.portal.getDefaultModule(
      portal_type = self.packing_list_portal_type
    )

    packing_list = packing_list_module.newContent(
      portal_type = self.packing_list_portal_type,
      source_value = organisation,
      start_date = self.datetime+10,
      specialise = self.business_process,
    )

    packing_list.newContent(
      portal_type = self.packing_list_line_portal_type,
      resource_value = resource,
      quantity = self.decrease_quantity,
    )

    packing_list.confirm()

  def stepCreateVariatedResource(self, sequence=None, sequence_list=None, \
                                 **kw):
    """
      Create a resource with variation
    """
    portal = self.getPortal()
    resource_module = portal.getDefaultModule(self.resource_portal_type)
    resource = resource_module.newContent(portal_type=self.resource_portal_type)
    resource.edit(
      title = "VariatedResource%s" % resource.getId(),
      variation_base_category_list = ['variation'],
    )
    for color in ['blue', 'green']:
      resource.newContent(portal_type='Product Individual Variation',
                          id=color, title=color)
    sequence.edit(resource=resource)

class TestOrderBuilder(TestOrderBuilderMixin, ERP5TypeTestCase):
  """
    Test Order Builder functionality
  """
  run_all_test = 1

  resource_portal_type = "Product"

  common_sequence_string = """
      CreateOrganisation
      CreateNotVariatedResource
      SetMaxDelayOnResource
      SetMinFlowOnResource
      Tic
      DecreaseOrganisationResourceQuantity
      Tic
      CreateOrderBuilder
      FillOrderBuilder
      Tic
      BuildOrderBuilder
      Tic
      CheckGeneratedDocumentList
      """

  def getTitle(self):
    return "Order Builder"

  def test_01_simpleOrderBuilder(self, quiet=0, run=run_all_test):
    """
    Test simple Order Builder
    """
    if not run: return

    self.wanted_quantity = 1.0
    self.wanted_start_date = DateTime(
      str(self.datetime + self.order_builder_hardcoded_time_diff))

    self.wanted_stop_date = self.wanted_start_date

    sequence_list = SequenceList()
    sequence_list.addSequenceString(self.common_sequence_string)
    sequence_list.play(self)

  def test_01a_simpleOrderBuilderVariatedResource(self, quiet=0, run=run_all_test):
    """
    Test simple Order Builder for Variated Resource
    """
    if not run: return

    sequence_string = """
      CreateOrganisation
      CreateVariatedResource
      SetMaxDelayOnResource
      SetMinFlowOnResource
      Tic
      DecreaseOrganisationResourceQuantityVariated
      Tic
      CreateOrderBuilder
      FillOrderBuilder
      Tic
      BuildOrderBuilder
      Tic
      CheckGeneratedDocumentListVariated
      """

    self.wanted_quantity = 1.0
    self.wanted_start_date = DateTime(
      str(self.datetime +
          self.order_builder_hardcoded_time_diff))

    self.wanted_stop_date = self.wanted_start_date

    sequence_list = SequenceList()
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_02_maxDelayResourceOrderBuilder(self, quiet=0, run=run_all_test):
    """
    Test max_delay impact on generated order start date
    """
    if not run: return

    self.max_delay = 4.0

    self.wanted_quantity = 1.0
    self.wanted_start_date = DateTime(
      str(self.datetime - self.max_delay
          + self.order_builder_hardcoded_time_diff))

    self.wanted_stop_date = DateTime(
      str(self.datetime + self.order_builder_hardcoded_time_diff))

    sequence_list = SequenceList()
    sequence_list.addSequenceString(self.common_sequence_string)
    sequence_list.play(self)

  def test_03_minFlowResourceOrderBuilder(self, quiet=0, run=run_all_test):
    """
    Test min_flow impact on generated order line quantity
    """
    if not run: return

    self.wanted_quantity = 1.0
    self.wanted_start_date = DateTime(
      str(self.datetime + self.order_builder_hardcoded_time_diff))

    self.wanted_stop_date = self.wanted_start_date

    sequence_list = SequenceList()
    sequence_list.addSequenceString(self.common_sequence_string)

    # case when min_flow > decreased_quantity
    self.min_flow = 15.0

    self.wanted_quantity = self.min_flow

    sequence_list.play(self)

  def checkOrderBuilderStockOptimisationResult(self, expected_result, **kw):
    result_list = [(x.getResource(), x.getVariationText(), x.getQuantity(),
                    x.getStartDate().strftime("%Y/%m/%d"),
                    x.getStopDate().strftime("%Y/%m/%d")) for x in \
                    self.order_builder.generateMovementListForStockOptimisation(**kw)]
    result_list.sort()
    expected_result.sort()
    self.assertEqual(expected_result, result_list)

  def test_04_generateMovementListWithDateInThePast(self):
    """
    If we can not find a future date for stock optimisation, make sure to
    take current date as default value (before if no date was found, no
    result was returned, introducing risk to forget ordering something, this
    could be big issue in real life)
    """
    node_1 = self.node_1
    fixed_date = DateTime('2016/08/30')
    self.pinDateTime(fixed_date)
    self.createOrderBuilder()
    self.fillOrderBuilder()
    self.checkOrderBuilderStockOptimisationResult([], node_uid=node_1.getUid())
    self._makeMovement(quantity=-3, destination_value=node_1, simulation_state='confirmed')
    resource_url = self.resource.getRelativeUrl()
    self.checkOrderBuilderStockOptimisationResult(
       [(resource_url, '', 3.0, '2016/08/30', '2016/08/30')], node_uid=node_1.getUid())

  def test_05_generateMovementListForStockOptimisationForSeveralNodes(self):
    """
    It's common to have a warehouse composed of subparts, each subpart could have
    it's own subpart, etc. So we have to look at stock optimisation for the whole
    warehouse, since every resource might be stored in several distinct sub parts.
    Make sure that stock optimisation works fine in such case.
    """
    node_1 = self.node_1
    node_2 = self.node_2
    self.createOrderBuilder()
    self.fillOrderBuilder()
    fixed_date = DateTime('2016/08/10')
    self.pinDateTime(fixed_date)
    resource_url = self.resource.getRelativeUrl()
    node_uid_list = [node_1.getUid(), self.node_2.getUid()]
    def checkStockOptimisationForTwoNodes(expected_result):
      self.checkOrderBuilderStockOptimisationResult(expected_result, node_uid=node_uid_list,
                                                    group_by_node=0)
    checkStockOptimisationForTwoNodes([])
    self._makeMovement(quantity=-3, destination_value=node_1, simulation_state='confirmed',
                       start_date=DateTime('2016/08/20'))
    checkStockOptimisationForTwoNodes([(resource_url, '', 3.0, '2016/08/20', '2016/08/20')])
    self._makeMovement(quantity=-2, destination_value=node_1, simulation_state='confirmed',
                       start_date=DateTime('2016/08/18'))
    checkStockOptimisationForTwoNodes([(resource_url, '', 5.0, '2016/08/18', '2016/08/18')])
    self._makeMovement(quantity=-7, destination_value=node_2, simulation_state='confirmed',
                       start_date=DateTime('2016/08/19'))
    checkStockOptimisationForTwoNodes([(resource_url, '', 12.0, '2016/08/18', '2016/08/18')])
    self._makeMovement(quantity=11, destination_value=node_2, simulation_state='confirmed',
                       start_date=DateTime('2016/08/16'))
    checkStockOptimisationForTwoNodes([(resource_url, '', 1.0, '2016/08/20', '2016/08/20')])
    self._makeMovement(quantity=7, destination_value=node_1, simulation_state='confirmed',
                       start_date=DateTime('2016/08/15'))
    checkStockOptimisationForTwoNodes([])

  def checkGenerateMovementListForStockOptimisationWithInventories(self, variation_category_list=None):
    node_1 = self.node_1
    resource_url = self.resource.getRelativeUrl()
    if variation_category_list:
      self.resource.setVariationBaseCategoryList(('colour', 'size'))
      self.resource.setVariationCategoryList(self.VARIATION_CATEGORIES)
    else:
      variation_category_list = []
    variation_text = '\n'.join(variation_category_list)
    self.createOrderBuilder()
    self.fillOrderBuilder()
    fixed_date = DateTime('2018/01/03')
    self.pinDateTime(fixed_date)
    resource_url = self.resource.getRelativeUrl()
    self.checkOrderBuilderStockOptimisationResult([], node_uid=node_1.getUid())
    movement = self._makeMovement(quantity=3, destination_value=node_1, simulation_state='delivered',
                       start_date=DateTime('2018/01/10'), variation_category_list=variation_category_list)
    inventory = self.portal.inventory_module.newContent(portal_type="Inventory",
                     start_date=DateTime('2018/01/12'),
                     destination_value=node_1,
                     full_inventory=1)
    inventory.deliver()
    self.tic()
    # keep in stock only movements coming from inventory. It is intentional to
    # not reindex inventory here.
    self.portal.erp5_sql_connection.manage_test("delete from stock where uid=%s" % movement.getUid())
    self.commit()
    self.checkOrderBuilderStockOptimisationResult(
      [(resource_url, variation_text, 3, '2018/01/12', '2018/01/12')], node_uid=node_1.getUid())

  def test_06a_generateMovementListForStockOptimisationWithInventories(self):
    """
    generateMovementListForStockOptimisation was having issues when inventories here used.
    make this method now works fine with inventories
    """
    self.checkGenerateMovementListForStockOptimisationWithInventories()

  def test_06b_generateMovementListForStockOptimisationWithInventoriesAndVariation(self):
    """
    generateMovementListForStockOptimisation was having issues when inventories here used.
    make this method now works fine with inventories and with variation
    """
    self.checkGenerateMovementListForStockOptimisationWithInventories(
      variation_category_list = ['colour/green', 'size/big'])

  def test_06_checkUpdateOfAutoPlannedMovement(self):
    """
    So we use order builder to create auto planned movements. generateMovementListForStockOptimisation
    should be able to allows us to reduce quantities of auto planned movements when needed
    """
    # changing type_list here is somehow dirty, decision would need to be taken if this is acceptable
    # for everyone to have auto_planned as part of future inventory
    self.portal.portal_workflow.order_workflow.getStateValueByReference('auto_planned').setStateTypeList(('planned_order', 'future_inventory'))
    self.portal.portal_caches.clearAllCache()
    self.assertIn('auto_planned', self.portal.getPortalFutureInventoryStateList())
    # end of patch
    self.createOrderBuilder()
    self.fillOrderBuilder()
    fixed_date = DateTime('2018/09/21')
    self.pinDateTime(fixed_date)
    resource_url = self.resource.getRelativeUrl()
    node_uid_list = [self.node_1.getUid(), self.node_2.getUid()]
    def checkStockOptimisationForTwoNodes(expected_result):
      self.checkOrderBuilderStockOptimisationResult(expected_result, node_uid=node_uid_list,
                                                    group_by_node=0)
    checkStockOptimisationForTwoNodes([])
    self._makeMovement(quantity=-5, destination_value=self.node_1, simulation_state='confirmed',
                       start_date=DateTime('2018/09/21'))
    checkStockOptimisationForTwoNodes([(resource_url, '', 5.0, '2018/09/21', '2018/09/21')])
    self._makeMovement(quantity=3, destination_value=self.node_2, simulation_state='auto_planned',
                       start_date=DateTime('2018/09/18'))
    checkStockOptimisationForTwoNodes([(resource_url, '', 2.0, '2018/09/21', '2018/09/21')])
    self._makeMovement(quantity=2, destination_value=self.node_1, simulation_state='auto_planned',
                       start_date=DateTime('2018/09/19'))
    checkStockOptimisationForTwoNodes([])
    # But if we more stock than expected, auto planned movements should be reduced
    self._makeMovement(quantity=1, destination_value=self.node_1, simulation_state='confirmed',
                       start_date=DateTime('2018/09/29'))
    checkStockOptimisationForTwoNodes([(resource_url, '', -1.0, '2018/09/19', '2018/09/19')])
    self._makeMovement(quantity=4, destination_value=self.node_2, simulation_state='confirmed',
                       start_date=DateTime('2018/09/29'))
    checkStockOptimisationForTwoNodes([(resource_url, '', -3.0, '2018/09/18', '2018/09/18'),
                                       (resource_url, '', -2.0, '2018/09/19', '2018/09/19')])
