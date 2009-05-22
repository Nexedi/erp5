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

import transaction
from DateTime import DateTime
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import reindex
from zLOG import LOG
from Products.ERP5Type.tests.Sequence import SequenceList
from testInvoice import TestSaleInvoiceMixin

class TestItemMixin(TestSaleInvoiceMixin):
  """
    Test business template erp5_trade 
  """
  item_portal_type = 'Item'

  def getBusinessTemplateList(self):
    """
    """
    return TestSaleInvoiceMixin.getBusinessTemplateList(self) + ('erp5_item',)
  
  def stepCreateItemList(self, sequence=None, sequence_list=None, **kw):
    """ Create some items """
    item_module = self.getPortal().item_module
    resource = sequence.get('resource')
    item = item_module.newContent(portal_type=self.item_portal_type)

    item.setResourceValue(resource)
    sequence.edit(item_list=[item]) 

  def stepOrderLineSetAggregationList(self, sequence=None,
                                          sequence_list=None, **kw):
    """  Aggregate Items """
    order_line = sequence.get('order_line')
    item_list = sequence.get('item_list')
    order_line.setAggregateValueList(item_list)  

  def stepCheckOrderLineAggregate(self, sequence=None, 
                                          sequence_list=None, **kw):
    """ Check items """
    order_line = sequence.get('order_line')
    self.checkAggregate(line=order_line, sequence=sequence)

  def stepCheckSimulationAggregate(self, sequence=None,
                                          sequence_list=None, **kw):
    """ Check items """
    order_line = sequence.get('order_line')
    simulation_movement = order_line.getOrderRelatedValue()
    self.checkAggregate(line=simulation_movement, sequence=sequence)

  def stepCheckPackingListLineAggregate(self, sequence=None,
                                          sequence_list=None, **kw):
    """ Check items """
    packing_list_line = sequence.get('packing_list_line')
    self.checkAggregate(line=packing_list_line, sequence=sequence)

  def stepCheckInvoiceLineAggregate(self, sequence=None,
                                          sequence_list=None, **kw):
    """ Check items """
    invoice = sequence.get('invoice')
    invoice_line_list = invoice.contentValues(
                         portal_type=self.invoice_line_portal_type)
    self.checkAggregate(line=invoice_line_list[0], sequence=sequence)

  def checkAggregate(self, line=None, sequence=None):
    """ Check items """
    item_list = sequence.get('item_list')
    self.assertEquals(len(line.getAggregateList()),1)
    self.failUnless(item_list[0] in line.getAggregateValueList())    
    

class TestItem(TestItemMixin, ERP5TypeTestCase) :

  run_all_test = 1
  quiet = 0

  def test_01_ItemSimpleTest(self, quiet=quiet, run=run_all_test):
    """
    """
    if not run: return
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
                       stepCheckOrderLineAggregate \
                       stepCheckOrderSimulation \
                       stepCheckSimulationAggregate \
                       stepCheckDeliveryBuilding \
                       stepCheckPackingListLineAggregate \
                       stepCheckPackingListIsNotDivergent '

    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)


  def test_02_ItemWithInvoice(self, quiet=quiet, run=run_all_test):
    """
    """
    if not run: return
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
                       stepCheckInvoiceBuilding \
                       stepRebuildAndCheckNothingIsCreated \
                       stepCheckInvoicesConsistency \
                       stepCheckInvoiceLineAggregate \
                      ' 

    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)


class TestItemScripts(ERP5TypeTestCase):
  """Test scripts from erp5_item.
  """
  def getBusinessTemplateList(self):
    return ('erp5_base', 'erp5_pdm', 'erp5_trade', 'erp5_item',)

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
    transaction.commit()
    self.tic()
  
  def beforeTearDown(self):
    transaction.abort()
    for module in (self.portal.organisation_module,
                   self.portal.item_module,
                   self.portal.sale_packing_list_module,
                   self.portal.purchase_packing_list_module,
                   self.portal.product_module,
                   self.portal.portal_simulation,):
      module.manage_delObjects(list(module.objectIds()))
    transaction.commit()
    self.tic()

  @reindex
  def _makeSalePackingListLine(self):
    packing_list = self.portal.sale_packing_list_module.newContent(
                  portal_type='Sale Packing List',
                  source_value=self.mirror_node,
                  source_section_value=self.mirror_section,
                  destination_value=self.node,
                  destination_section_value=self.section,
                  start_date=DateTime() - 1,)
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
    self.assertEquals(None, self.item.Item_getResourceValue())
    line = self._makeSalePackingListLine()
    self.assertEquals(self.product, self.item.Item_getResourceValue())

  def test_Item_getResourceTitle(self):
    self.assertEquals(None, self.item.Item_getResourceTitle())
    line = self._makeSalePackingListLine()
    self.assertEquals('Product', self.item.Item_getResourceTitle())

  def test_Item_getCurrentOwnerValue(self):
    self.assertEquals(None, self.item.Item_getCurrentOwnerValue())
    line = self._makeSalePackingListLine()
    self.assertEquals(self.section, self.item.Item_getCurrentOwnerValue())

  def test_Item_getCurrentOwnerTitle(self):
    self.assertEquals(None, self.item.Item_getCurrentOwnerTitle())
    line = self._makeSalePackingListLine()
    self.assertEquals('Section', self.item.Item_getCurrentOwnerTitle())

  def test_Item_getCurrentSiteValue(self):
    self.assertEquals(None, self.item.Item_getCurrentSiteValue())
    line = self._makeSalePackingListLine()
    self.assertEquals(self.node, self.item.Item_getCurrentSiteValue())

  def test_Item_getCurrentSiteTitle(self):
    self.assertEquals(None, self.item.Item_getCurrentSiteTitle())
    line = self._makeSalePackingListLine()
    self.assertEquals('Node', self.item.Item_getCurrentSiteTitle())

  # with cells
  @reindex
  def _makeSalePackingListCellWithVariation(self):
    packing_list = self.portal.sale_packing_list_module.newContent(
                  portal_type='Sale Packing List',
                  source_value=self.mirror_node,
                  source_section_value=self.mirror_section,
                  destination_value=self.node,
                  destination_section_value=self.section,
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
    self.assertEquals([], self.item.Item_getVariationCategoryList())
    self._makeSalePackingListCellWithVariation()
    self.assertEquals(['size/small'], self.item.Item_getVariationCategoryList())

  def test_Item_getVariationRangeCategoryItemList(self):
    self.assertEquals([], self.item.Item_getVariationRangeCategoryItemList())
    self._makeSalePackingListCellWithVariation()
    self.assertEquals([['Big', 'size/big'],
                       ['Small', 'size/small']],
        self.item.Item_getVariationRangeCategoryItemList())



def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestItem))
  suite.addTest(unittest.makeSuite(TestItemScripts))
  return suite

