##############################################################################
#
# Copyright (c) 2004, 2005 Nexedi SARL and Contributors. All Rights Reserved.
#          Sebastien Robin <seb@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
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

import unittest

from DateTime import DateTime
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import reindex
from AccessControl.SecurityManagement import newSecurityManager
from Products.ERP5Type.tests.Sequence import SequenceList
from Products.ERP5.tests.testInvoice import TestSaleInvoiceMixin
from Products.ERP5.tests.utils import newSimulationExpectedFailure
from Products.ERP5Type.UnrestrictedMethod import UnrestrictedMethod
from Products.ERP5Type.Base import Base


def checkMovementAggregateQuantityConstraint(document):
  # Base.checkConsistency is used here in order to avoid recursive check
  message_list = Base.checkConsistency(
      document, filter={'reference': 'movement_aggregate_quantity'})
  if len(message_list) == 0:
    return True
  return False


class TestItemMixin(TestSaleInvoiceMixin):
  item_portal_type = 'Item'

  def afterSetUp(self):
    super(TestItemMixin, self).afterSetUp()
    self._addPropertySheet(
        'Purchase Packing List Line', 'MovementAggregateQuantityConstraint')
    self._addPropertySheet(
        'Purchase Packing List Cell', 'MovementAggregateQuantityConstraint')
    self._addPropertySheet(
        'Internal Packing List Line', 'MovementAggregateQuantityConstraint')
    self._addPropertySheet(
        'Internal Packing List Cell', 'MovementAggregateQuantityConstraint')
    self.commit()

  def assertMovementAggregateQuantityConstraintConsistent(self, document):
    self.assertTrue(checkMovementAggregateQuantityConstraint(document))

  def assertMovementAggregateQuantityConstraintInconsistent(self, document):
    self.assertFalse(checkMovementAggregateQuantityConstraint(document))

  def createOrganisation(self, title=None):
    organisation_portal_type = 'Organisation'
    organisation_module = self.portal.getDefaultModule(
                                   portal_type=organisation_portal_type)
    organisation = organisation_module.newContent(
                                   portal_type=organisation_portal_type)
    if title is None:
      organisation.edit(title='organisation%s' % organisation.getId())
    else:
      organisation.edit(title=title)
    return organisation

  def createNotVariatedResource(self,title=None):
    """
      Create a resource with no variation
    """
    resource_portal_type = 'Product'
    resource_module = self.portal.getDefaultModule(resource_portal_type)
    resource = resource_module.newContent(portal_type=resource_portal_type)
    resource.edit(
      title = "NotVariatedResource%s" % resource.getId(),
      quantity_unit='unit/piece',
      aggregated_portal_type_list=['Item'],
      required_aggregated_portal_type_list=['Item']
    )
    return resource

  def createVariatedResource(self,title=None):
    resource_portal_type = 'Product'
    resource_module = self.portal.getDefaultModule(resource_portal_type)
    resource = resource_module.newContent(portal_type=resource_portal_type)
    resource.edit(
      title = "VariatedResource%s" % resource.getId(),
    )
    resource.setIndividualVariationBaseCategoryList(('size',))
    resource.setQuantityUnit('unit/piece')
    resource.setAggregatedPortalTypeList('Item')
    resource.setRequiredAggregatedPortalTypeList('Item')

    # Add size variation
    size_variation_count = 3
    for i in range(size_variation_count):
      variation_portal_type = 'Product Individual Variation'
      variation = resource.newContent(portal_type = variation_portal_type)
      variation.edit(
        title = 'SizeVariation%s' % str(i)
      )

    return resource

  def createPackingList(self,
                        resource=None,
                        organisation=None,
                        portal_type='Purchase Packing List'):
    portal = self.portal
    packing_list_module = portal.getDefaultModule(portal_type=portal_type)
    pac_list = packing_list_module.newContent(portal_type=portal_type)
    pac_list.edit(
      title = "PPL%s" % pac_list.getId(),
      start_date = self.datetime + 20,
      stop_date = self.datetime + 10,
      specialise_value = portal.business_process_module.erp5_default_business_process,
    )

    if organisation is not None:
      pac_list.edit(source_value=organisation,
                 source_section_value=organisation,
                 destination_value=organisation,
                 destination_section_value=organisation,
                 source_decision_value=organisation,
                 destination_decision_value=organisation,
                 source_administration_value=organisation,
                 destination_administration_value=organisation,
                 )
    return pac_list

  def createPackingListLine(self,
                            packing_list=None,
                            resource=None,
                            portal_type='Purchase Packing List Line'):
    packing_list_line = packing_list.newContent(portal_type=portal_type)
    packing_list_line.edit(
      title = "Packing List Line"
    )
    packing_list_line.setResourceValue(resource)
    return packing_list_line

  def stepCreateItemList(self, sequence=None, sequence_list=None, **kw):
    """ Create some items """
    item_module = self.getPortal().item_module
    resource = sequence.get('resource')
    item = item_module.newContent(portal_type=self.item_portal_type)

    sequence.edit(item_list=[item])

  def stepOrderLineSetAggregationList(self, sequence=None,
                                          sequence_list=None, **kw):
    """  Aggregate Items """
    order_line = sequence.get('order_line')
    item_list = sequence.get('item_list')
    order_line.setAggregateValueList(item_list)

  def stepOrderSetAggregationList(self, sequence=None,
                                          sequence_list=None, **kw):
    """  Aggregate Items """
    order = sequence.get('order')
    item_module = self.getPortal().item_module
    item_list = item_module.contentValues()
    # this step expect that number of order lines
    # and number of item list is same.
    order_line_list = order.contentValues(portal_type=self.order_line_portal_type)
    self.assertEqual(len(order_line_list), len(item_list))
    for order_line, item in zip(order_line_list, item_list):
      order_line.setAggregateValueList([item])


  def stepCheckOrderLineAggregate(self, sequence=None,
                                          sequence_list=None, **kw):
    """ Check items """
    order_line = sequence.get('order_line')
    self.checkAggregate(line=order_line, sequence=sequence)

  def stepCheckSimulationAggregate(self, sequence=None,
                                          sequence_list=None, **kw):
    """ Check items """
    order_line = sequence.get('order_line')
    simulation_movement = order_line.getDeliveryRelatedValue()
    self.assertFalse(simulation_movement is None)
    self.checkAggregate(line=simulation_movement, sequence=sequence)

  def stepCheckPackingListLineAggregate(self, sequence=None,
                                          sequence_list=None, **kw):
    """ Check items """
    packing_list_line = sequence.get('packing_list_line')
    self.checkAggregate(line=packing_list_line, sequence=sequence)

  def stepCheckPackingListLineAggregateList(self, sequence=None,
                                          sequence_list=None, **kw):
    """ Check items """
    packing_list_line = sequence.get('packing_list_line')
    self.checkAggregateList(line=packing_list_line, sequence=sequence)


  def stepCheckInvoiceLineAggregate(self, sequence=None,
                                          sequence_list=None, **kw):
    """ Check items """
    invoice = sequence.get('invoice')
    invoice_line_list = invoice.contentValues(
                         portal_type=self.invoice_line_portal_type)
    self.checkAggregate(line=invoice_line_list[0], sequence=sequence)

  def stepCheckToRender_Delivery_viewAggregatedItemList(self, sequence=None,
                                                        sequence_list=None, **kw):
    """Check to render the view"""
    packing_list = sequence.get('packing_list')
    packing_list.Delivery_viewAggregatedItemList()

  def stepCheckPackingListStartDateAfterStartDateAdopt(self,sequence=None, sequence_list=None, **kw):
    """
      Check that start date is adopted.
    """
    packing_list = sequence.get('packing_list')
    self.assertEqual(packing_list.getStartDate(),self.datetime+15)


  @UnrestrictedMethod
  def stepModifyOrderLinesQuantity(self,sequence=None, sequence_list=None, **kw):
    """
      modify order line quantities
    """
    order = sequence.get('order')
    order_line_list = order.contentValues(portal_type=self.order_line_portal_type)
    for order_line in order_line_list:
      order_line.edit(quantity=self.default_quantity-1)

  @UnrestrictedMethod
  def stepModifyOneOrderLineStartDate(self,sequence=None, sequence_list=None, **kw):
    """
      modify order line start date
    """
    order = sequence.get('order')
    resource_list = sequence.get('resource_list')
    order_line_list = order.contentValues(portal_type=self.order_line_portal_type)
    self.assertEqual(len(order_line_list),len(resource_list))
    order_line_list[-1].edit(start_date=self.datetime+15)


  @UnrestrictedMethod
  def stepModifyOrderLinesDate(self,sequence=None, sequence_list=None, **kw):
    """
      modify order line date
    """
    order = sequence.get('order')
    for order_line in order.contentValues(portal_type=self.order_line_portal_type):
      order_line.edit(start_date=self.datetime+15)

  def checkAggregate(self, line=None, sequence=None):
    """ Check items """
    item_list = sequence.get('item_list')
    self.assertEqual(len(line.getAggregateList()),1)
    self.assertTrue(item_list[0] in line.getAggregateValueList())

  def checkAggregateList(self, line=None, sequence=None):
    """ Check items """
    item_list = self.portal.item_module.contentValues(portal_type='Item')
    self.assertTrue(line.getAggregateValueList()[0] in item_list)


  DEFAULT_ITEM_WITH_ORDER_SEQUENCE = \
                      'stepCreateEntities \
                       stepCreateCurrency \
                       stepCreateItemList \
                       stepCreateOrder \
                       stepSetOrderProfile \
                       stepSetOrderPriceCurrency \
                       stepCreateNotVariatedResource \
                       stepTic \
                       stepCreateOrderLine \
                       stepSetOrderLineResource \
                       stepSetOrderLineDefaultValues \
                       stepOrderLineSetAggregationList \
                       '
  DEFAULT_ITEM_WITH_PACKING_LIST_SEQUENCE = DEFAULT_ITEM_WITH_ORDER_SEQUENCE + '\
                       stepOrderOrder \
                       stepTic \
                       stepConfirmOrder \
                       stepTic \
                       stepPackingListBuilderAlarm \
                       stepTic \
                       stepCheckOrderRule \
                       stepCheckOrderLineAggregate \
                       stepCheckOrderSimulation \
                       stepCheckSimulationAggregate \
                       stepCheckDeliveryBuilding \
                       stepCheckPackingListIsNotDivergent \
                       stepCheckPackingListLineAggregate \
                       stepCheckToRender_Delivery_viewAggregatedItemList \
                       '
  DEFAULT_ITEM_WITH_PACKING_LIST_SEQUENCE_AND_SAME_RESOURCE_LINES = DEFAULT_ITEM_WITH_ORDER_SEQUENCE + '\
                       stepCreateItemList \
                       stepCreateOrderLine \
                       stepSetOrderLineResource \
                       stepSetOrderLineDefaultValues \
                       stepOrderSetAggregationList \
                       stepOrderOrder \
                       stepTic \
                       stepConfirmOrder \
                       stepTic \
                       stepPackingListBuilderAlarm \
                       stepTic \
                       stepCheckOrderSimulation \
                       stepCheckDeliveryBuilding \
                       stepCheckPackingListIsNotDivergent \
                       stepCheckOrderPackingList \
                       stepCheckPackingListLineAggregateList \
                       '

class TestItem(TestItemMixin, ERP5TypeTestCase):

  quiet = 0
  run_all_test= 1

  def getTitle(self):
    return "Item"

  def beforeTearDown(self):
    self.abort()
    for module in (self.portal.organisation_module,
                   self.portal.item_module,
                   self.portal.sale_packing_list_module,
                   self.portal.purchase_packing_list_module,
                   self.portal.product_module,
                   self.portal.portal_simulation,):
      module.manage_delObjects(list(module.objectIds()))
    self.tic()


  def test_01_ItemSimpleTest(self, quiet=quiet):
    sequence_list = SequenceList()

    # Test with a simply order without cell
    sequence_string = 'stepCreateOrganisation1 \
                       stepCreateOrganisation2 \
                       stepCreateOrganisation3 \
                       stepCreateItemList \
                       stepCreateOrder \
                       stepSetOrderProfile \
                       stepCreateNotVariatedResource \
                       stepTic \
                       stepCreateOrderLine \
                       stepSetOrderLineResource \
                       stepSetOrderLineDefaultValues \
                       stepOrderLineSetAggregationList \
                       stepConfirmOrder \
                       stepTic \
                       stepPackingListBuilderAlarm \
                       stepTic \
                       stepCheckOrderLineAggregate \
                       stepCheckOrderSimulation \
                       stepCheckSimulationAggregate \
                       stepCheckDeliveryBuilding \
                       stepCheckPackingListLineAggregate \
                       stepCheckPackingListIsNotDivergent '

    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)


  def test_02_ItemWithInvoice(self, quiet=quiet):
    sequence_list = SequenceList()

    sequence_string = 'stepCreateEntities \
                       stepCreateCurrency \
                       stepCreateItemList \
                       stepCreateSaleInvoiceTransactionRule \
                       stepCreateOrder \
                       stepSetOrderProfile \
                       stepSetOrderPriceCurrency \
                       stepCreateNotVariatedResource \
                       stepTic \
                       stepCreateOrderLine \
                       stepSetOrderLineResource \
                       stepSetOrderLineDefaultValues \
                       stepOrderLineSetAggregationList \
                       stepConfirmOrder \
                       stepTic \
                       stepPackingListBuilderAlarm \
                       stepTic \
                       stepCheckOrderRule \
                       stepCheckOrderLineAggregate \
                       stepCheckOrderSimulation \
                       stepCheckSimulationAggregate \
                       stepCheckDeliveryBuilding \
                       stepCheckPackingListLineAggregate \
                       stepAddPackingListContainer \
                       stepAddPackingListContainerLine \
                       stepSetContainerLineFullQuantity \
                       stepTic \
                       stepCheckPackingListIsPacked \
                       stepSetReadyPackingList \
                       stepTic \
                       stepStartPackingList \
                       stepCheckInvoicingRule \
                       stepTic \
                       stepInvoiceBuilderAlarm \
                       stepTic \
                       stepCheckInvoiceBuilding \
                       stepRebuildAndCheckNothingIsCreated \
                       stepCheckInvoicesConsistency \
                       stepCheckInvoiceLineAggregate \
                      '

    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)


  def test_03_CreateItemsFromPackingListLine(self):
    organisation = self.createOrganisation(title='Organisation I')
    self.tic()
    resource = self.createVariatedResource()
    size_base = 'size/%s' % (resource.getRelativeUrl(),)
    self.tic()
    packing_list = self.createPackingList(resource=resource,organisation=organisation)
    packing_list_line= self.createPackingListLine(packing_list=packing_list,
                                                  resource=resource)
    self.tic()

    # make sure we can render the dialog
    packing_list_line.DeliveryLine_viewItemCreationDialog()

    # create a listbox
    listbox = ({ 'listbox_key': '000',
              'title': 'Lot A',
              'reference': '20_05_09_LA',
              'quantity': 20.0,
              'line_variation_category_list': size_base + '/3',
              },
              { 'listbox_key': '001',
              'title': 'Lot B',
              'reference': '20_05_09_LB',
              'quantity': 10.0,
              'line_variation_category_list': size_base + '/2',
              },
              { 'listbox_key': '002',
              'title': 'Lot C',
              'reference': '20_05_09_LC',
              'quantity': 15.0,
              'line_variation_category_list': size_base + '/1',
              },
              )

    packing_list_line.DeliveryLine_createItemList(type='Item', listbox=listbox)
    self.tic()
    self.assertEqual(
           len([x.getObject() for x in self.portal.portal_catalog(
                                          portal_type='Item',
                                          title='Lot A')]) ,1)
    self.assertEqual(
           len([x.getObject() for x in self.portal.portal_catalog(
                                          portal_type='Item',
                                          title='Lot B')]), 1)
    self.assertEqual(
           len([x.getObject() for x in self.portal.portal_catalog(
                                          portal_type='Item',
                                          title='Lot C')]), 1)

    self.assertEqual(packing_list_line.getTotalQuantity(), 0.0)
    self.assertMovementAggregateQuantityConstraintConsistent(packing_list_line)
    self.assertEqual(sorted(packing_list_line.getVariationCategoryList()),
                      sorted([size_base + '/3',
                              size_base + '/2',
                              size_base + '/1']))
    self.assertEqual(packing_list_line.getAggregateTitleList(), [])

    movement_cell_list = packing_list_line.contentValues(
                                    portal_type='Purchase Packing List Cell')
    self.assertEqual(3, len(movement_cell_list))

    cell = packing_list_line.getCell(base_id='movement',
                                     *(size_base + '/3', ))
    self.assertEqual(cell.getQuantity(), 0.0)
    self.assertMovementAggregateQuantityConstraintInconsistent(cell)
    self.assertEqual(['Lot A'], cell.getAggregateTitleList())

    cell = packing_list_line.getCell(base_id='movement',
                                     *(size_base + '/2', ))
    self.assertEqual(cell.getQuantity(), 0.0)
    self.assertMovementAggregateQuantityConstraintInconsistent(cell)
    self.assertEqual(['Lot B'], cell.getAggregateTitleList())

    cell = packing_list_line.getCell(base_id='movement',
                                     *(size_base + '/1', ))
    self.assertEqual(cell.getQuantity(), 0.0)
    self.assertMovementAggregateQuantityConstraintInconsistent(cell)
    self.assertEqual(['Lot C'], cell.getAggregateTitleList())


  def test_04_CreateItemsFromPackingListLineWithVariationDefined(self):
    organisation = self.createOrganisation(title='Organisation II')
    self.tic()
    resource = self.createVariatedResource()
    size_base = 'size/%s' % (resource.getRelativeUrl(),)
    self.tic()
    packing_list = self.createPackingList(resource=resource,organisation=organisation)

    packing_list_line= self.createPackingListLine(packing_list=packing_list,
                                                  resource=resource)
    self.tic()
    # create a listbox
    listbox = ({ 'listbox_key': '000',
              'title': 'Lot A2',
              'reference': '25_05_09_LA2',
              'quantity': 20.0,
              'line_variation_category_list': size_base + '/3',
              },
              )
    packing_list_line.DeliveryLine_createItemList(type='Item', listbox=listbox)
    self.assertEqual(packing_list_line.getVariationCategoryList(),
                      [size_base + '/3'])
    self.assertEqual(packing_list_line.getTotalQuantity(), 0.0)
    self.assertMovementAggregateQuantityConstraintConsistent(packing_list_line)

    # create listbox a second time
    listbox = ({ 'listbox_key': '000',
              'title': 'Lot B2',
              'reference': '25_05_09_LB2',
              'quantity': 20.0,
              'line_variation_category_list': size_base + '/1',
              },
              { 'listbox_key': '001',
              'title': 'Lot C2',
              'reference': '25_05_09_LC2',
              'quantity': 15.0,
              'line_variation_category_list': size_base + '/2',
              },
              )
    packing_list_line.DeliveryLine_createItemList(type='Item', listbox=listbox)
    self.tic()

    self.assertEqual(packing_list_line.getTotalQuantity(), 0.0)
    self.assertMovementAggregateQuantityConstraintConsistent(packing_list_line)
    self.assertEqual(sorted(packing_list_line.getVariationCategoryList()),
                      sorted([size_base + '/1',
                              size_base + '/2',
                              size_base + '/3']))

    movement_cell_list = packing_list_line.contentValues(
                                    portal_type='Purchase Packing List Cell')
    self.assertEqual(3, len(movement_cell_list))

    cell = packing_list_line.getCell(base_id='movement',
                                     *(size_base + '/3', ))
    self.assertEqual(cell.getQuantity(), 0.0)
    self.assertMovementAggregateQuantityConstraintInconsistent(cell)
    self.assertEqual(['Lot A2'], cell.getAggregateTitleList())

    cell = packing_list_line.getCell(base_id='movement',
                                     *(size_base + '/1', ))
    self.assertEqual(cell.getQuantity(), 0.0)
    self.assertMovementAggregateQuantityConstraintInconsistent(cell)
    self.assertEqual(['Lot B2'], cell.getAggregateTitleList())

    cell = packing_list_line.getCell(base_id='movement',
                                     *(size_base + '/2', ))
    self.assertEqual(cell.getQuantity(), 0.0)
    self.assertMovementAggregateQuantityConstraintInconsistent(cell)
    self.assertEqual(['Lot C2'], cell.getAggregateTitleList())


  def test_05_CreateItemsFromPackingListLineWithNotVariatedResource(self):
    organisation = self.createOrganisation(title='Organisation III')
    self.tic()
    resource = self.createNotVariatedResource()
    self.tic()
    packing_list = self.createPackingList(resource=resource,
                                          organisation=organisation)

    packing_list_line= self.createPackingListLine(packing_list=packing_list,
                                                  resource=resource)
    packing_list_line.setQuantity(32)
    self.tic()
    # create a listbox
    listbox = ({ 'listbox_key': '000',
              'title': 'Lot A3',
              'reference': '25_05_09_LA3',
              'quantity': 10.0,
              },
              { 'listbox_key': '001',
              'title': 'Lot B3',
              'reference': '25_05_09_LB3',
              'quantity': 5.0,
              },
              { 'listbox_key': '002',
              'title': 'Lot C3',
              'reference': '25_05_09_LC3',
              'quantity': 15.0,
              },
              )
    packing_list_line.DeliveryLine_createItemList(type='Item', listbox=listbox)
    self.tic()
    self.assertEqual(
           len([x.getObject() for x in self.portal.portal_catalog(
                                          portal_type='Item',
                                          title='Lot A3')]), 1)
    self.assertEqual(
           len([x.getObject() for x in self.portal.portal_catalog(
                                          portal_type='Item',
                                          title='Lot B3')]), 1)
    self.assertEqual(
           len([x.getObject() for x in self.portal.portal_catalog(
                                          portal_type='Item',
                                          title='Lot C3')]), 1)
    self.assertEqual(packing_list_line.getQuantity(),32.0)
    self.assertMovementAggregateQuantityConstraintInconsistent(packing_list_line)

    self.assertEqual(packing_list_line.getVariationCategoryList(), [])
    self.assertEqual(packing_list_line.getAggregateTitleList(),
                      ['Lot A3', 'Lot B3', 'Lot C3'])
    movement_cell_list = packing_list_line.contentValues(
                                    portal_type='Purchase Packing List Cell')
    self.assertEqual(movement_cell_list,[])

  @newSimulationExpectedFailure
  def test_06_VerifyHavingSameItemTwiceOnMovementCausesNoBug(self):
    """
    """
    organisation = self.createOrganisation(title='Organisation VI')
    self.tic()
    resource = self.createVariatedResource()
    size_base = 'size/%s' % (resource.getRelativeUrl(),)
    self.tic()
    packing_list = self.createPackingList(resource=resource,organisation=organisation)

    packing_list_line= self.createPackingListLine(packing_list=packing_list,
                                                  resource=resource)
    self.tic()
    packing_list_line.DeliveryLine_viewItemCreationDialog()
    # create a listbox
    listbox = ({ 'listbox_key': '000',
              'title': 'Lot A10',
              'reference': '1070110000015',
              'quantity': 20.0,
              'line_variation_category_list': size_base + '/3'
              },
              )

    packing_list_line.DeliveryLine_createItemList(type='Item', listbox=listbox)
    self.tic()
    item = [x.getObject() for x in self.portal.portal_catalog(
                                    portal_type='Item',
                                    reference = '1070110000015'
                                    )][0]
    packing_list_cell_list = packing_list_line.contentValues(portal_type='Purchase Packing List Cell')
    for packing_list_cell in packing_list_cell_list:
      packing_list_cell.setAggregateValueList(packing_list_cell.getAggregateValueList()+[item])
    self.portal.portal_workflow.doActionFor(packing_list,
               'confirm_action')
    self.assertEqual(packing_list.getSimulationState(),
              'confirmed')
    self.tic()
    self.assertEqual(packing_list.getCausalityState(),'solved')

  def test_07_WithPackingListChangePackingListQuantityAndAccept(self, quiet=quiet, run=run_all_test):
    """
      Create order and add items, then Change the quantity
      on an delivery line, after that see if the packing list is
      divergent and then split and defer the packing list
    """
    sequence_list = SequenceList()
    sequence_string = self.DEFAULT_ITEM_WITH_PACKING_LIST_SEQUENCE + '\
                      stepDecreasePackingListLineQuantity \
                      stepCheckPackingListIsCalculating \
                      stepTic \
                      stepCheckPackingListIsDiverged \
                      stepSplitAndDeferPackingList \
                      stepTic \
                      stepCheckPackingListIsSolved \
                      stepCheckPackingListSplitted \
                      '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_08_ChangePackingListDateAndAccept(self, quiet=quiet, run=run_all_test):
    """
      Create order and add items, then Change the date
      on an delivery line, after that see if the packing list is
      divergent and then accept decision on the packing list
    """
    sequence_list = SequenceList()

    sequence_string = self.DEFAULT_ITEM_WITH_PACKING_LIST_SEQUENCE + '\
                      stepChangePackingListStartDate \
                      stepCheckPackingListIsCalculating \
                      stepTic \
                      stepCheckPackingListIsDiverged \
                      stepUnifyStartDateWithDecision \
                      stepTic \
                      stepCheckPackingListIsSolved \
                      stepCheckPackingListIsNotDivergent \
                      stepCheckSimulationStartDateUpdated \
                      '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  @newSimulationExpectedFailure
  def test_09_ChangeOrderDateAndAcceptOnPackingList(self, quiet=quiet, run=run_all_test):
    """
      Create order and add items, then Change the order date
      on an order line, after that see if the packing list is
      divergent and then adopt prevision on the packing list
    """
    sequence_list = SequenceList()
    sequence_string = self.DEFAULT_ITEM_WITH_PACKING_LIST_SEQUENCE + '\
                      stepModifyOneOrderLineStartDate \
                      stepTic \
                      stepCheckPackingListIsDiverged \
                      stepCheckPackingListIsDivergent \
                      stepUnifyStartDateWithPrevision \
                      stepTic \
                      stepCheckPackingListIsNotDivergent \
                      stepCheckPackingListIsSolved \
                      stepCheckNewPackingListAfterStartDateAdopt \
                      '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_10_ChangeOrderQuantityAndAdoptOnPackingList(self, quiet=quiet, run=run_all_test):
    """
      Create order and add items, then Change the quantity
      on an order line, after that see if the packing list is
      divergent and then adopt prevision on the packing list
    """
    sequence_list = SequenceList()
    sequence_string = self.DEFAULT_ITEM_WITH_PACKING_LIST_SEQUENCE + '\
                      stepModifyOrderLinesQuantity \
                      stepTic \
                      stepCheckPackingListIsDiverged \
                      stepAdoptPrevisionQuantity \
                      stepTic \
                      stepCheckPackingListIsNotDivergent \
                      stepCheckPackingListIsSolved \
                      stepCheckPackingListLineWithNewQuantityPrevision \
                      '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_11_ChangeOrderQuantityAndAcceptOnPackingList(self, quiet=quiet, run=run_all_test):
    """
      Create order and add items, then Change the quantity
      on an order line, after that see if the packing list is
      divergent and then accept decision on the packing list
    """
    sequence_list = SequenceList()
    sequence_string = self.DEFAULT_ITEM_WITH_PACKING_LIST_SEQUENCE + '\
                      stepModifyOrderLinesQuantity \
                      stepTic \
                      stepCheckPackingListIsDiverged \
                      stepAcceptDecisionQuantity \
                      stepTic \
                      stepCheckPackingListIsNotDivergent \
                      stepCheckPackingListIsSolved \
                      stepCheckSimulationQuantityUpdated \
                      '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  @newSimulationExpectedFailure
  def test_12_CreteSameResourceDifferentItemOrderLines(self, quiet=quiet, run=run_all_test):
    """
      Create order lines with same resouces and add items into them, then Change the quantity
      on the order lines, after that see if the packing list is
      divergent and then adopt prevision on the packing list
    """
    sequence_list = SequenceList()
    sequence_string = ''
    sequence_string = self.DEFAULT_ITEM_WITH_PACKING_LIST_SEQUENCE_AND_SAME_RESOURCE_LINES + '\
                      stepModifyOrderLinesQuantity \
                      stepTic \
                      stepCheckPackingListIsDiverged \
                      stepAdoptPrevisionQuantity \
                      stepTic \
                      stepCheckPackingListIsNotDivergent \
                      stepCheckPackingListIsSolved \
                      stepCheckPackingListLineWithNewQuantityPrevision \
                      '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  @newSimulationExpectedFailure
  def test_13_CreateSameResourceDiffrentItemOrderLinesThenChangeTheOrderLinesDate(
           self, quiet=quiet, run=run_all_test):
    sequence_list = SequenceList()
    sequence_string = self.DEFAULT_ITEM_WITH_PACKING_LIST_SEQUENCE_AND_SAME_RESOURCE_LINES + '\
                      stepModifyOrderLinesDate \
                      stepTic \
                      stepCheckPackingListIsDiverged \
                      stepUnifyStartDateWithPrevision \
                      stepTic \
                      stepCheckPackingListIsNotDivergent \
                      stepCheckPackingListIsSolved \
                      stepCheckPackingListStartDateAfterStartDateAdopt \
                      '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_14_ManuallyAddPackingListWithItem(self, quiet=quiet, run=run_all_test):
    """
    Checks that adding invoice lines and accounting lines to one invoice
    generates correct simulation
    """
    if not quiet:
      self.logMessage('Invoice with Manually Added Movements')
    sequence_list = SequenceList()
    sequence_string = self.DEFAULT_ITEM_WITH_PACKING_LIST_SEQUENCE + '\
          stepSetReadyPackingList \
          stepTic \
          stepStartPackingList \
          stepCheckInvoicingRule \
          stepTic \
          stepInvoiceBuilderAlarm \
          stepTic \
          stepCheckInvoiceBuilding \
          stepRebuildAndCheckNothingIsCreated \
          stepCheckInvoicesConsistency \
          stepAddInvoiceLines \
          stepTic \
          stepStartInvoice \
          stepTic \
          stepCheckSimulationTrees \
          '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_15_ThreeOrderLines(self, quiet=quiet, run=run_all_test):
    """
    Check that item with three order lines.
    """
    sequence_list = SequenceList()
    sequence_string = self.DEFAULT_ITEM_WITH_ORDER_SEQUENCE + '\
                       stepCreateItemList \
                       stepCreateOrderLine \
                       stepSetOrderLineResource \
                       stepSetOrderLineDefaultValues \
                       stepCreateItemList \
                       stepCreateOrderLine \
                       stepSetOrderLineResource \
                       stepSetOrderLineDefaultValues \
                       stepOrderSetAggregationList \
                       stepTic \
                       stepOrderOrder \
                       stepTic \
                       stepConfirmOrder \
                       stepTic \
                       stepPackingListBuilderAlarm \
                       stepTic \
                       stepCheckOrderSimulation \
                       stepCheckDeliveryBuilding \
                       stepCheckPackingListIsNotDivergent \
                       stepCheckPackingListLineAggregateList \
                       stepCheckOrderPackingList '

    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  # Note that: Item with Inventory API tests exsist in
  # testInventoryModule(tested getInventory) and testInventoryAPI(tested getTrackingList).
  #
  # def test_WithInventoryAPI(self):
  #   pass

  def test_select_item_dialog_no_variation(self):
    organisation = self.createOrganisation(title='Organisation III')
    resource = self.createNotVariatedResource()

    # create one item that is in organisation
    packing_list = self.createPackingList(resource=resource,
                                          organisation=organisation)
    packing_list.edit(source_section=None, source=None)
    packing_list_line = self.createPackingListLine(packing_list=packing_list,
                                                   resource=resource)
    item = self.portal.item_module.newContent(
                                    portal_type='Item',
                                    title='Test Item',
                                    reference='TI',
                                    quantity=12)
    packing_list_line.setAggregateValue(item)
    packing_list.confirm()
    packing_list.stop()
    self.assertEqual('stopped', packing_list.getSimulationState())
    self.tic()


    packing_list = self.createPackingList(resource=resource,
                                          organisation=organisation,
                                          portal_type='Internal Packing List')
    packing_list_line = self.createPackingListLine(
                              packing_list=packing_list,
                              resource=resource,
                              portal_type='Internal Packing List Line')
    packing_list_line.setQuantity(32)

    # we can view the dialog
    packing_list_line.DeliveryLine_viewSelectItemListDialog()

    # the listbox contains the items physically in the source of the packing
    # list
    self.assertEqual([item],
                      packing_list_line.DeliveryLine_getSelectableItemList())

    packing_list_line.DeliveryLine_selectItemList(
              list_selection_name='select_item_fast_input_selection',
              listbox_uid=(item.getUid(),),
              uids=(item.getUid(),))

    self.assertEqual([item], packing_list_line.getAggregateValueList())
    self.assertEqual(32.0, packing_list_line.getQuantity())
    self.assertMovementAggregateQuantityConstraintInconsistent(packing_list_line)


  def test_select_item_dialog_variation(self):
    organisation = self.createOrganisation(title='Organisation IV')
    resource = self.createVariatedResource()
    variation_category_list = [ 'size/%s' % variation.getRelativeUrl()
                                 for variation in resource.contentValues() ]

    # create one item that is in organisation
    packing_list = self.createPackingList(resource=resource,
                                          organisation=organisation)
    packing_list.edit(source_section=None, source=None)
    packing_list_line = self.createPackingListLine(packing_list=packing_list,
                                                   resource=resource)
    packing_list_line.setVariationCategoryList(variation_category_list)

    variation = variation_category_list[0]
    cell = packing_list_line.newCell(base_id='movement',
                                     *(variation,))
    cell.edit(mapped_value_property_list=('quantity,'),
              quantity=1,
              variation_category_list=[variation])

    item = self.portal.item_module.newContent(
                                      portal_type='Item',
                                      title='Test Item %s' % variation,
                                      reference='TI%s' % variation,
                                      quantity=12)
    cell.setAggregateValue(item)

    packing_list.confirm()
    packing_list.stop()
    self.assertEqual('stopped', packing_list.getSimulationState())
    self.tic()


    packing_list = self.createPackingList(resource=resource,
                                          organisation=organisation,
                                          portal_type='Internal Packing List')
    packing_list_line = self.createPackingListLine(
                              packing_list=packing_list,
                              resource=resource,
                              portal_type='Internal Packing List Line')
    packing_list_line.setQuantity(32)

    # we can view the dialog
    packing_list_line.DeliveryLine_viewSelectItemListDialog()

    # the listbox contains the items physically in the source of the packing
    # list, and have matching variations
    self.assertEqual([item],
                      packing_list_line.DeliveryLine_getSelectableItemList())

    packing_list_line.DeliveryLine_selectItemList(
              list_selection_name='select_item_fast_input_selection',
              listbox_uid=(item.getUid(),),
              uids=(item.getUid(),))

    self.assertEqual([variation],
                      packing_list_line.getVariationCategoryList())
    self.assertEqual(0.0, packing_list_line.getTotalQuantity())
    self.assertMovementAggregateQuantityConstraintConsistent(packing_list_line)
    self.assertEqual([], packing_list_line.getAggregateValueList())

    self.assertEqual(1,
        len(packing_list_line.getCellValueList(base_id='movement')))

    cell = packing_list_line.getCell(base_id='movement', *(variation, ))
    self.assertEqual(0.0, cell.getQuantity())
    self.assertMovementAggregateQuantityConstraintInconsistent(cell)
    self.assertEqual([item], cell.getAggregateValueList())


  def test_16_CreateItemsFromPackingListWithVariationDefined(self):
    quantity = 2
    organisation = self.createOrganisation()
    self.tic()

    resource = self.createVariatedResource()
    resource_relative_url = resource.getRelativeUrl()
    self.tic()

    packing_list = self.createPackingList(organisation=organisation)
    packing_list_line = self.createPackingListLine(
        packing_list=packing_list,
        resource=resource)
    packing_list_line.setVariationCategoryList(
        ['size/%s/3' % (resource_relative_url,)])
    # XXX: Setting cell quantity without any API
    base_id = 'movement'
    cell_key_list = list(packing_list_line.getCellKeyList(base_id=base_id))
    self.assertEqual(1, len(cell_key_list))
    cell_key = cell_key_list[0]
    packing_list_cell = packing_list_line.newCell(
      base_id=base_id, portal_type='Purchase Packing List Cell', *cell_key)
    packing_list_cell.edit(mapped_value_property_list=['quantity'], quantity=quantity,
              predicate_category_list=cell_key, variation_category_list=cell_key)
    self.tic()

    packing_list.Delivery_createItemList()
    self.tic()

    item_value_list = packing_list_cell.getAggregateValueList()
    self.assertEqual(2, len(item_value_list))

    item_1 = item_value_list[0]
    item_2 = item_value_list[1]

    item_1_title = item_1.getTitle()
    item_2_title = item_2.getTitle()

    self.assertTrue(item_1_title.startswith(resource.getTitle()))
    self.assertTrue(item_2_title.startswith(resource.getTitle()))
    self.assertTrue('SizeVariation2' in item_1_title)
    self.assertTrue('SizeVariation2' in item_2_title)

    self.assertNotEqual(item_1.getTitle(), item_2.getTitle())
    self.assertNotEqual(item_1.getReference(), item_2.getReference())

    self.assertEqual(packing_list_line.getTotalQuantity(), quantity)


  def test_17_CreateItemsFromPackingListWithNotVariatedResource(self):
    quantity = 2
    organisation = self.createOrganisation()
    self.tic()
    resource = self.createNotVariatedResource()
    self.tic()
    packing_list = self.createPackingList(resource=resource,
                                          organisation=organisation)

    packing_list_line = self.createPackingListLine(packing_list=packing_list,
                                                   resource=resource)
    packing_list_line.setQuantity(quantity)
    self.tic()

    # make sure we can render the dialog
    packing_list.Delivery_viewCreateItemListDialog()

    # generate items
    packing_list.Delivery_createItemList()

    self.tic()

    item_value_list = packing_list_line.getAggregateValueList()
    self.assertEqual(2, len(item_value_list))

    item_1 = item_value_list[0]
    item_2 = item_value_list[1]

    self.assertTrue(item_1.getTitle().startswith(resource.getTitle()))
    self.assertTrue(item_2.getTitle().startswith(resource.getTitle()))

    self.assertEqual(packing_list_line.getVariationCategoryList(), [])
    movement_cell_list = packing_list_line.contentValues(
                                    portal_type='Purchase Packing List Cell')
    self.assertEqual(movement_cell_list,[])

    self.assertNotEqual(item_1.getTitle(), item_2.getTitle())
    self.assertNotEqual(item_1.getReference(), item_2.getReference())

    self.assertEqual(packing_list_line.getTotalQuantity(), quantity)


  def test_18_CreateItemsFromPackingListWithExistingItem(self):
    quantity = 2
    title = self.id()
    reference = self.id()
    organisation = self.createOrganisation()
    self.tic()
    resource = self.createNotVariatedResource()
    self.tic()
    packing_list = self.createPackingList(resource=resource,
                                          organisation=organisation)

    packing_list_line = self.createPackingListLine(packing_list=packing_list,
                                                   resource=resource)
    packing_list_line.setQuantity(quantity)
    self.tic()

    # Associate Item with delivery line
    packing_list_line.DeliveryLine_createItemList(
      type=self.item_portal_type,
      listbox=[
        {
          'listbox_key': '001',
          'reference': reference,
          'title': title,
          'quantity': 1.0
        }
      ]
    )
    self.tic()

    # Reset quantity to 2
    packing_list_line.setQuantity(quantity)

    # generate items
    packing_list.Delivery_createItemList()
    self.tic()

    item_by_hand_value_list = [q for q in
        packing_list_line.getAggregateValueList()
        if q.getReference() == reference]
    item_by_dialog_value_list = [q for q in
        packing_list_line.getAggregateValueList()
        if q.getReference() != reference]

    self.assertEqual(1, len(item_by_hand_value_list))
    self.assertEqual(1, len(item_by_dialog_value_list))

    item_by_hand = item_by_hand_value_list[0]
    item_by_dialog = item_by_dialog_value_list[0]

    self.assertTrue(item_by_dialog.getTitle().startswith(resource.getTitle()))

    self.assertEqual(packing_list_line.getVariationCategoryList(), [])
    movement_cell_list = packing_list_line.contentValues(
                                    portal_type='Purchase Packing List Cell')
    self.assertEqual(movement_cell_list,[])
    self.assertEqual(packing_list_line.getTotalQuantity(), quantity)


  def test_19_CreateItemsFromPackingListWithMoreItemThanQuantity(self):
    quantity = 1
    title = self.id()
    reference = self.id()
    organisation = self.createOrganisation()
    self.tic()
    resource = self.createNotVariatedResource()
    self.tic()
    packing_list = self.createPackingList(resource=resource,
                                          organisation=organisation)

    packing_list_line = self.createPackingListLine(packing_list=packing_list,
                                                   resource=resource)
    packing_list_line.setQuantity(quantity)
    self.tic()

    # Associate Items with delivery line
    packing_list_line.DeliveryLine_createItemList(
      type=self.item_portal_type,
      listbox=[
        {
          'listbox_key': '001',
          'reference': reference,
          'title': title,
          'quantity': 1.0
        },
        {
          'listbox_key': '002',
          'reference': reference+'B',
          'title': title+'B',
          'quantity': 1.0
        }
      ]
    )
    self.tic()

    # Reset quantity to 1
    packing_list_line.setQuantity(quantity)
    self.tic()

    # generate items, expect no-op
    packing_list.Delivery_createItemList()
    self.tic()

    item_value_list = [q for q in
        packing_list_line.getAggregateValueList()
        if q.getReference() == reference]
    item_2_value_list = [q for q in
        packing_list_line.getAggregateValueList()
        if q.getReference() == reference+'B']

    self.assertEqual(1, len(item_value_list))
    self.assertEqual(1, len(item_2_value_list))

    self.assertEqual(packing_list_line.getTotalQuantity(), quantity)


class TestItemScripts(ERP5TypeTestCase):
  """Test scripts from erp5_item.
  """
  def afterSetUp(self):
    self.validateRules()
    size_category = self.portal.portal_categories.size
    if 'big' not in size_category.objectIds():
      size_category.newContent(portal_type='Category',
                               id='big',
                               title='Big')
    if 'small' not in size_category.objectIds():
      size_category.newContent(portal_type='Category',
                               id='small',
                               title='Small')

    self.node = self.portal.organisation_module.newContent(
                              portal_type='Organisation',
                              title='Node')
    self.section = self.portal.organisation_module.newContent(
                              portal_type='Organisation',
                              title='Section')
    self.mirror_node = self.portal.organisation_module.newContent(
                              portal_type='Organisation',
                              title='Mirror Node')
    self.mirror_section = self.portal.organisation_module.newContent(
                              portal_type='Organisation',
                              title='Mirror Section')
    self.product = self.portal.product_module.newContent(
                              portal_type='Product',
                              title='Product')
    self.variated_product = self.portal.product_module.newContent(
                              portal_type='Product',
                              title='Variated Product',
                              variation_base_category_list=('size',),
                              variation_category_list=('size/big',
                                                       'size/small'))
    self.item = self.portal.item_module.newContent(
                              portal_type='Item',
                              title='Item')
    self.tic()

  def beforeTearDown(self):
    self.abort()
    for module in (self.portal.organisation_module,
                   self.portal.item_module,
                   self.portal.sale_packing_list_module,
                   self.portal.purchase_packing_list_module,
                   self.portal.product_module,
                   self.portal.portal_simulation,):
      module.manage_delObjects(list(module.objectIds()))
    self.tic()

  @reindex
  def _makeSalePackingListLine(self, start_date=None):
    if start_date is None:
      start_date = DateTime() - 1
    packing_list = self.portal.sale_packing_list_module.newContent(
                  portal_type='Sale Packing List',
                  source_value=self.mirror_node,
                  source_section_value=self.mirror_section,
                  destination_value=self.node,
                  destination_section_value=self.section,
                  specialise_value=self.portal.business_process_module.erp5_default_business_process,
                  start_date=start_date,)
    line = packing_list.newContent(
                  portal_type='Sale Packing List Line',
                  quantity=1,
                  resource_value=self.product,
                  aggregate_value=self.item,)
    packing_list.confirm()
    packing_list.start()
    packing_list.deliver()
    return line

  # with line
  def test_Item_getResourceValue(self):
    self.assertEqual(None, self.item.Item_getResourceValue())
    line = self._makeSalePackingListLine()
    self.assertEqual(self.product, self.item.Item_getResourceValue())
    self.assertEqual(None, self.item.Item_getResourceValue(
                                at_date=DateTime() - 2))

  def test_Item_getResourceTitle(self):
    self.assertEqual(None, self.item.Item_getResourceTitle())
    line = self._makeSalePackingListLine()
    self.assertEqual('Product', self.item.Item_getResourceTitle())
    self.assertEqual(None, self.item.Item_getResourceTitle(
                                at_date=DateTime() - 2))

  def test_Item_getCurrentOwnerValue(self):
    self.assertEqual(None, self.item.Item_getCurrentOwnerValue())
    line = self._makeSalePackingListLine()
    self.assertEqual(self.section, self.item.Item_getCurrentOwnerValue())
    self.assertEqual(None,
        self.item.Item_getCurrentOwnerValue(at_date=DateTime() - 2))

  def test_Item_getCurrentOwnerTitle(self):
    self.assertEqual(None, self.item.Item_getCurrentOwnerTitle())
    line = self._makeSalePackingListLine()
    self.assertEqual('Section', self.item.Item_getCurrentOwnerTitle())
    self.assertEqual(None,
        self.item.Item_getCurrentOwnerTitle(at_date=DateTime() - 2))

  def test_Item_getCurrentSiteValue(self):
    self.assertEqual(None, self.item.Item_getCurrentSiteValue())
    line = self._makeSalePackingListLine()
    self.assertEqual(self.node, self.item.Item_getCurrentSiteValue())
    self.assertEqual(None, self.item.Item_getCurrentSiteValue(
                                            at_date=DateTime() - 2))

  def test_Item_getCurrentSiteTitle(self):
    self.assertEqual(None, self.item.Item_getCurrentSiteTitle())
    line = self._makeSalePackingListLine()
    self.assertEqual('Node', self.item.Item_getCurrentSiteTitle())
    self.assertEqual(None,
          self.item.Item_getCurrentSiteTitle(at_date=DateTime() - 2))

  def test_Item_getTrackingList_empty(self):
    self.assertEqual([], self.item.Item_getTrackingList())

  def test_Item_getTrackingList_explanation_brain_attribute(self):
    line = self._makeSalePackingListLine(start_date=DateTime(2001, 2, 3))
    line.setTitle('explanation title')
    self.tic()

    history_item, = self.item.Item_getTrackingList()
    self.assertEqual(DateTime(2001, 2, 3), history_item.date)
    self.assertEqual('Node', history_item.node_title)
    self.assertEqual('Mirror Node', history_item.source_title)
    self.assertEqual('Section', history_item.section_title)
    self.assertEqual('Product', history_item.resource_title)
    self.assertEqual('explanation title', history_item.explanation)
    self.assertEqual('Sale Packing List Line', history_item.translated_portal_type)
    self.assertEqual(1, history_item.quantity)
    self.assertEqual(line.getId(), history_item.getId())
    self.assertEqual(line.getParentValue(), history_item.getParentValue())
    self.assertEqual((), history_item.variation_category_item_list)
    self.assertEqual('Delivered', history_item.simulation_state)

  def test_Item_getTrackingList_default_sort(self):
    # Item_getTrackingList returns lines sorted in chronological order
    implicit_movement = self.portal.implicit_item_movement_module.newContent(
      portal_type='Implicit Item Movement',
      destination_value=self.mirror_node,
      destination_section_value=self.mirror_section,
      stop_date=DateTime(2016, 1, 1),
      aggregate_value=self.item,
    )
    implicit_movement.deliver()
    self._makeSalePackingListLine(start_date=DateTime(2017, 1, 1))

    self.assertEqual(
        [DateTime(2016, 1, 1), DateTime(2017, 1, 1)],
        [brain.date for brain in self.item.Item_getTrackingList()])
    self.assertEqual(
        ['Mirror Node', 'Node'],
        [brain.node_title for brain in self.item.Item_getTrackingList()])

  def test_item_current_location_and_transit_movement(self):
    # a started packing list is still in transit, so we do not know its
    # current location until it is delivered.
    # https://lab.nexedi.com/nexedi/erp5/merge_requests/70

    implicit_movement = self.portal.implicit_item_movement_module.newContent(
      portal_type='Implicit Item Movement',
      destination_value=self.mirror_node,
      destination_section_value=self.mirror_section,
      stop_date=DateTime() - 2,
      aggregate_value=self.item,
    )
    implicit_movement.deliver()

    packing_list = self.portal.sale_packing_list_module.newContent(
      portal_type='Sale Packing List',
      source_value=self.mirror_node,
      source_section_value=self.mirror_section,
      destination_value=self.node,
      destination_section_value=self.section,
      specialise_value=self.portal.business_process_module.erp5_default_business_process,
      start_date=DateTime() - 1,)
    line = packing_list.newContent(
      portal_type='Sale Packing List Line',
      quantity=1,
      resource_value=self.product,
      aggregate_value=self.item,)
    packing_list.confirm()
    self.tic()
    self.assertEqual(self.mirror_node, self.item.Item_getCurrentSiteValue())
    self.assertEqual('Mirror Node', self.item.Item_getCurrentSiteTitle())
    self.assertEqual(self.mirror_section, self.item.Item_getCurrentOwnerValue())
    self.assertEqual('Mirror Section', self.item.Item_getCurrentOwnerTitle())

    packing_list.start()
    self.tic()
    # When movement is started, the item is still moving so we do not know it's location / ownership.
    # In this case we just return None.
    self.assertEqual(None, self.item.Item_getCurrentSiteValue())
    self.assertEqual(None, self.item.Item_getCurrentSiteTitle())
    self.assertEqual(None, self.item.Item_getCurrentOwnerValue())
    self.assertEqual(None, self.item.Item_getCurrentOwnerTitle())

    packing_list.stop()
    self.tic()
    self.assertEqual(self.node, self.item.Item_getCurrentSiteValue())
    self.assertEqual('Node', self.item.Item_getCurrentSiteTitle())
    self.assertEqual(self.section, self.item.Item_getCurrentOwnerValue())
    self.assertEqual('Section', self.item.Item_getCurrentOwnerTitle())

  # with cells
  @reindex
  def _makeSalePackingListCellWithVariation(self):
    packing_list = self.portal.sale_packing_list_module.newContent(
                  portal_type='Sale Packing List',
                  source_value=self.mirror_node,
                  source_section_value=self.mirror_section,
                  destination_value=self.node,
                  destination_section_value=self.section,
                  specialise_value=self.portal.business_process_module.erp5_default_business_process,
                  start_date=DateTime() - 1,)
    line = packing_list.newContent(
                  portal_type='Sale Packing List Line',
                  resource_value=self.variated_product,)
    line.setVariationCategoryList(['size/small'])
    cell = line.newCell(portal_type='Sale Packing List Cell',
                 base_id='movement', *('size/small',))
    cell.edit(mapped_value_property_list=['price','quantity'],
              quantity=1,
              variation_category_list=['size/small'],
              aggregate_value=self.item)
    packing_list.confirm()
    packing_list.start()
    packing_list.deliver()
    return cell

  def test_Item_getVariationCategoryList(self):
    self.assertEqual([], self.item.Item_getVariationCategoryList())
    self._makeSalePackingListCellWithVariation()
    self.assertEqual(['size/small'], self.item.Item_getVariationCategoryList())
    self.assertEqual([],
        self.item.Item_getVariationCategoryList(at_date=DateTime() - 2))

  def test_Item_getVariationRangeCategoryItemList(self):
    self.assertEqual([], self.item.Item_getVariationRangeCategoryItemList())
    self._makeSalePackingListCellWithVariation()
    self.assertEqual([['Big', 'size/big'],
                       ['Small', 'size/small']],
        self.item.Item_getVariationRangeCategoryItemList())
    self.assertEqual([],
        self.item.Item_getVariationRangeCategoryItemList(
                          at_date=DateTime() - 2))

  def test_Item_getLabelPrice(self):
    raise NotImplementedError

  def test_Item_getLabelTitle(self):
    raise NotImplementedError


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestItem))
  suite.addTest(unittest.makeSuite(TestItemScripts))
  return suite

