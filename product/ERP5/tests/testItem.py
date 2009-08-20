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
from AccessControl.SecurityManagement import newSecurityManager
from Products.ERP5Type.tests.Sequence import SequenceList
from testInvoice import TestSaleInvoiceMixin

class TestItemMixin(TestSaleInvoiceMixin):
  item_portal_type = 'Item'

  def getBusinessTemplateList(self):
    """
    """
    return TestSaleInvoiceMixin.getBusinessTemplateList(self) + ('erp5_item',)
  
  def login(self):
    uf = self.getPortal().acl_users
    uf._doAddUser('rc', '', ['Manager', 'Member', 'Assignee'], [])
    user = uf.getUserById('rc').__of__(uf)
    newSecurityManager(None, user)
    
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
    preference = self.portal.portal_preferences
    portal_workflow = self.portal.portal_workflow
    pref = preference.newContent(portal_type='System Preference')
    pref.setPreferredProductIndividualVariationBaseCategoryList(['size'])
    portal_workflow.doActionFor(pref, 'enable_action')
    transaction.commit()
    self.tic()
    
    resource_portal_type = 'Product'
    resource_module = self.portal.getDefaultModule(resource_portal_type)
    resource = resource_module.newContent(portal_type=resource_portal_type)
    resource.edit(
      title = "VariatedResource%s" % resource.getId(),
    )
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
    

class TestItem(TestItemMixin, ERP5TypeTestCase):

  quiet = 0

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
    
  
  def test_03_CreateItemsFromPackingListLine(self):
    organisation = self.createOrganisation(title='Organisation I')
    transaction.commit()
    self.tic()
    resource = self.createVariatedResource()
    # XXX this tests depends on the relative url of the resource
    self.assertEquals('product_module/1', resource.getRelativeUrl())

    transaction.commit()
    self.tic()
    packing_list = self.createPackingList(resource=resource,organisation=organisation)
    packing_list_line= self.createPackingListLine(packing_list=packing_list,
                                                  resource=resource)
    transaction.commit()
    self.tic()
    
    # make sure we can render the dialog
    packing_list_line.DeliveryLine_viewItemCreationDialog()

    # create a listbox 
    listbox = ({ 'listbox_key': '000',
              'title': 'Lot A',
              'reference': '20_05_09_LA',
              'quantity': 20.0,
              'line_variation_category_list': 'size/product_module/1/3',
              },
              { 'listbox_key': '001',
              'title': 'Lot B',
              'reference': '20_05_09_LB',
              'quantity': 10.0,
              'line_variation_category_list': 'size/product_module/1/2',
              },
              { 'listbox_key': '002',
              'title': 'Lot C',
              'reference': '20_05_09_LC',
              'quantity': 15.0,
              'line_variation_category_list': 'size/product_module/1/1',
              },
              )

    self.portal.REQUEST.set('type', 'Item')
    packing_list_line.DeliveryLine_createItemList(listbox=listbox)
    transaction.commit()
    self.tic()
    self.assertEquals(
           len([x.getObject() for x in self.portal.portal_catalog(
                                          portal_type='Item',
                                          title='Lot A')]) ,1)
    self.assertEquals(
           len([x.getObject() for x in self.portal.portal_catalog(
                                          portal_type='Item',
                                          title='Lot B')]), 1)
    self.assertEquals(
           len([x.getObject() for x in self.portal.portal_catalog(
                                          portal_type='Item',
                                          title='Lot C')]), 1)

    self.assertEquals(packing_list_line.getTotalQuantity(), 45.0)
    self.assertEquals(sorted(packing_list_line.getVariationCategoryList()),
                      sorted(['size/product_module/1/3',
                              'size/product_module/1/2',
                              'size/product_module/1/1']))
    self.assertEquals(packing_list_line.getAggregateTitleList(), [])

    movement_cell_list = packing_list_line.contentValues(
                                    portal_type='Purchase Packing List Cell')
    self.assertEquals(3, len(movement_cell_list))

    cell = packing_list_line.getCell(base_id='movement',
                                     *('size/product_module/1/3', ))
    self.assertEquals(cell.getQuantity(), 20)
    self.assertEquals(['Lot A'], cell.getAggregateTitleList())

    cell = packing_list_line.getCell(base_id='movement',
                                     *('size/product_module/1/2', ))
    self.assertEquals(cell.getQuantity(), 10)
    self.assertEquals(['Lot B'], cell.getAggregateTitleList())

    cell = packing_list_line.getCell(base_id='movement',
                                     *('size/product_module/1/1', ))
    self.assertEquals(cell.getQuantity(), 15)
    self.assertEquals(['Lot C'], cell.getAggregateTitleList())
    
     
  def test_04_CreateItemsFromPackingListLineWithVariationDefined(self):
    organisation = self.createOrganisation(title='Organisation II')
    transaction.commit()
    self.tic()
    resource = self.createVariatedResource()
    # XXX this tests depends on the relative url of the resource
    self.assertEquals('product_module/2', resource.getRelativeUrl())

    transaction.commit()
    self.tic()
    packing_list = self.createPackingList(resource=resource,organisation=organisation)
   
    packing_list_line= self.createPackingListLine(packing_list=packing_list,
                                                  resource=resource)
    transaction.commit()
    self.tic()
    # create a listbox 
    listbox = ({ 'listbox_key': '000',
              'title': 'Lot A2',
              'reference': '25_05_09_LA2',
              'quantity': 20.0,
              'line_variation_category_list': 'size/product_module/2/3',
              },
              )
    self.portal.REQUEST.set('type', 'Item')
    packing_list_line.DeliveryLine_createItemList(listbox=listbox)
    self.assertEquals(packing_list_line.getVariationCategoryList(),
                      ['size/product_module/2/3'])
    self.assertEquals(packing_list_line.getTotalQuantity(), 20)

    # create listbox a second time
    listbox = ({ 'listbox_key': '000',
              'title': 'Lot B2',
              'reference': '25_05_09_LB2',
              'quantity': 20.0,
              'line_variation_category_list': 'size/product_module/2/1',
              },
              { 'listbox_key': '001',
              'title': 'Lot C2',
              'reference': '25_05_09_LC2',
              'quantity': 15.0,
              'line_variation_category_list': 'size/product_module/2/2',
              },
              )
    self.portal.REQUEST.set('type', 'Item')
    packing_list_line.DeliveryLine_createItemList(listbox=listbox)
    transaction.commit()
    self.tic()

    self.assertEquals(packing_list_line.getTotalQuantity(), 55.0)
    self.assertEquals(sorted(packing_list_line.getVariationCategoryList()),
                      sorted(['size/product_module/2/1',
                              'size/product_module/2/2',
                              'size/product_module/2/3']))

    movement_cell_list = packing_list_line.contentValues(
                                    portal_type='Purchase Packing List Cell')
    self.assertEquals(3, len(movement_cell_list))

    cell = packing_list_line.getCell(base_id='movement',
                                     *('size/product_module/2/3', ))
    self.assertEquals(cell.getQuantity(), 20)
    self.assertEquals(['Lot A2'], cell.getAggregateTitleList())

    cell = packing_list_line.getCell(base_id='movement',
                                     *('size/product_module/2/1', ))
    self.assertEquals(cell.getQuantity(), 20)
    self.assertEquals(['Lot B2'], cell.getAggregateTitleList())

    cell = packing_list_line.getCell(base_id='movement',
                                     *('size/product_module/2/2', ))
    self.assertEquals(cell.getQuantity(), 15)
    self.assertEquals(['Lot C2'], cell.getAggregateTitleList())
 

  def test_05_CreateItemsFromPackingListLineWithNotVariatedResource(self):
    organisation = self.createOrganisation(title='Organisation III')
    transaction.commit()
    self.tic()
    resource = self.createNotVariatedResource()
    transaction.commit()
    self.tic()
    packing_list = self.createPackingList(resource=resource,
                                          organisation=organisation)
   
    packing_list_line= self.createPackingListLine(packing_list=packing_list,
                                                  resource=resource)
    packing_list_line.setQuantity(32)
    transaction.commit()
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
    self.portal.REQUEST.set('type', 'Item')
    packing_list_line.DeliveryLine_createItemList(listbox=listbox)
    transaction.commit()
    self.tic()
    self.assertEquals(
           len([x.getObject() for x in self.portal.portal_catalog(
                                          portal_type='Item',
                                          title='Lot A3')]), 1)
    self.assertEquals(
           len([x.getObject() for x in self.portal.portal_catalog(
                                          portal_type='Item',
                                          title='Lot B3')]), 1)
    self.assertEquals(
           len([x.getObject() for x in self.portal.portal_catalog(
                                          portal_type='Item',
                                          title='Lot C3')]), 1)
    self.assertEquals(packing_list_line.getQuantity(),30.0)
    
    self.assertEquals(packing_list_line.getVariationCategoryList(), [])
    self.assertEquals(packing_list_line.getAggregateTitleList(),
                      ['Lot A3', 'Lot B3', 'Lot C3'])
    movement_cell_list = packing_list_line.contentValues(
                                    portal_type='Purchase Packing List Cell')
    self.assertEquals(movement_cell_list,[])
    

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
    self.assertEquals('stopped', packing_list.getSimulationState())
    transaction.commit()
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
    self.assertEquals([item],
                      packing_list_line.DeliveryLine_getSelectableItemList())
    
    packing_list_line.DeliveryLine_selectItemList(
              list_selection_name='select_item_fast_input_selection',
              listbox_uid=(item.getUid(),),
              uids=(item.getUid(),))

    self.assertEquals([item], packing_list_line.getAggregateValueList())
    self.assertEquals(12, packing_list_line.getQuantity())


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
    self.assertEquals('stopped', packing_list.getSimulationState())
    transaction.commit()
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
    self.assertEquals([item],
                      packing_list_line.DeliveryLine_getSelectableItemList())
    
    packing_list_line.DeliveryLine_selectItemList(
              list_selection_name='select_item_fast_input_selection',
              listbox_uid=(item.getUid(),),
              uids=(item.getUid(),))

    self.assertEquals([variation],
                      packing_list_line.getVariationCategoryList())
    self.assertEquals(12, packing_list_line.getTotalQuantity())
    self.assertEquals([], packing_list_line.getAggregateValueList())

    self.assertEquals(1,
        len(packing_list_line.getCellValueList(base_id='movement')))
    
    cell = packing_list_line.getCell(base_id='movement', *(variation, ))
    self.assertEquals(12, cell.getQuantity())
    self.assertEquals([item], cell.getAggregateValueList())


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
    self.assertEquals(None, self.item.Item_getResourceValue(
                                at_date=DateTime() - 2))

  def test_Item_getResourceTitle(self):
    self.assertEquals(None, self.item.Item_getResourceTitle())
    line = self._makeSalePackingListLine()
    self.assertEquals('Product', self.item.Item_getResourceTitle())
    self.assertEquals(None, self.item.Item_getResourceTitle(
                                at_date=DateTime() - 2))

  def test_Item_getCurrentOwnerValue(self):
    self.assertEquals(None, self.item.Item_getCurrentOwnerValue())
    line = self._makeSalePackingListLine()
    self.assertEquals(self.section, self.item.Item_getCurrentOwnerValue())
    self.assertEquals(None,
        self.item.Item_getCurrentOwnerValue(at_date=DateTime() - 2))

  def test_Item_getCurrentOwnerTitle(self):
    self.assertEquals(None, self.item.Item_getCurrentOwnerTitle())
    line = self._makeSalePackingListLine()
    self.assertEquals('Section', self.item.Item_getCurrentOwnerTitle())
    self.assertEquals(None,
        self.item.Item_getCurrentOwnerTitle(at_date=DateTime() - 2))

  def test_Item_getCurrentSiteValue(self):
    self.assertEquals(None, self.item.Item_getCurrentSiteValue())
    line = self._makeSalePackingListLine()
    self.assertEquals(self.node, self.item.Item_getCurrentSiteValue())
    self.assertEquals(None, self.item.Item_getCurrentSiteValue(
                                            at_date=DateTime() - 2))

  def test_Item_getCurrentSiteTitle(self):
    self.assertEquals(None, self.item.Item_getCurrentSiteTitle())
    line = self._makeSalePackingListLine()
    self.assertEquals('Node', self.item.Item_getCurrentSiteTitle())
    self.assertEquals(None,
          self.item.Item_getCurrentSiteTitle(at_date=DateTime() - 2))

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
    self.assertEquals([],
        self.item.Item_getVariationCategoryList(at_date=DateTime() - 2))

  def test_Item_getVariationRangeCategoryItemList(self):
    self.assertEquals([], self.item.Item_getVariationRangeCategoryItemList())
    self._makeSalePackingListCellWithVariation()
    self.assertEquals([['Big', 'size/big'],
                       ['Small', 'size/small']],
        self.item.Item_getVariationRangeCategoryItemList())
    self.assertEquals([],
        self.item.Item_getVariationRangeCategoryItemList(
                          at_date=DateTime() - 2))

    
def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestItem))
  suite.addTest(unittest.makeSuite(TestItemScripts))
  return suite

