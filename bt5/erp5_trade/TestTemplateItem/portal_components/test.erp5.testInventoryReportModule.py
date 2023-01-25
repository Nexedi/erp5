##############################################################################
#
# Copyright (c) 2004, 2005 Nexedi SARL and Contributors. All Rights Reserved.
#          Sebastien Robin <seb@nexedi.com>
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

import unittest
from Products.ERP5Type.tests.SecurityTestCase import SecurityTestCase
from DateTime import DateTime
from Products.ERP5Type.tests.Sequence import SequenceList
from erp5.component.test.testOrder import TestOrderMixin

class TestInventoryReportModule(TestOrderMixin, SecurityTestCase):
  """
    Test inventory module
  """
  run_all_test = 1
  size_list = ['Child/32','Child/34']

  def getBusinessTemplateList(self):
    """
    """
    return super(TestInventoryReportModule, self).getBusinessTemplateList() + ('erp5_accounting', 'erp5_mrp',)

  def getTitle(self):
    return "Inventory Report Module"

  def getInventoryReportModule(self):
    return getattr(self.getPortal(), 'inventory_report_module',None)

  def stepCreateThreeCurrencys(self, sequence=None,
                                 sequence_list=None, **kw):
    self.login()
    start_date = DateTime('2018/01/01 00:00')
    stop_date = DateTime('3018/01/01 00:00')
    portal_type = 'Currency'
    currency_module = self.portal.currency_module
    rmb = currency_module.newContent(
      portal_type=portal_type,
      title='Yuan',
      reference='RMB')

    dollar = currency_module.newContent(
      portal_type=portal_type,
      title='Dollar',
      reference='USD')

    euro = currency_module.newContent(
      portal_type=portal_type,
      title='Euro',
      reference = 'EUR')



    currency_exchange_line = rmb.newContent(portal_type='Currency Exchange Line')
    currency_exchange_line.edit(
      price_currency_value = dollar,
      base_price = 0.14,
      start_date= start_date,
      stop_date = stop_date)
    currency_exchange_line.validate()

    currency_exchange_line = rmb.newContent(portal_type='Currency Exchange Line')
    currency_exchange_line.edit(
      price_currency_value = euro,
      base_price = 0.13,
      start_date= start_date,
      stop_date = stop_date)
    currency_exchange_line.validate()

    currency_exchange_line = dollar.newContent(portal_type='Currency Exchange Line')
    currency_exchange_line.edit(
      price_currency_value = rmb,
      base_price = 6.95,
      start_date= start_date,
      stop_date = stop_date)
    currency_exchange_line.validate()

    currency_exchange_line =dollar.newContent(portal_type='Currency Exchange Line')
    currency_exchange_line.edit(
      price_currency_value = euro,
      base_price = 0.88,
      start_date= start_date,
      stop_date = stop_date)
    currency_exchange_line.validate()


    currency_exchange_line = euro.newContent(portal_type='Currency Exchange Line')
    currency_exchange_line.edit(
      price_currency_value = dollar,
      base_price = 1.14,
      start_date= start_date,
      stop_date = stop_date)
    currency_exchange_line.validate()

    currency_exchange_line = euro.newContent(portal_type='Currency Exchange Line')
    currency_exchange_line.edit(
      price_currency_value = rmb,
      base_price = 7.9,
      start_date= start_date,
      stop_date = stop_date)
    currency_exchange_line.validate()

    rmb.validate()
    euro.validate()
    dollar.validate()
    sequence.edit(
      rmb = rmb,
      euro = euro,
      dollar = dollar
    )


  def stepCreateThreeOrganisations(self, sequence=None,
                                        sequence_list=None, **kw):
    rmb = sequence.get('rmb')
    euro = sequence.get('euro')
    dollar =sequence.get('dollar')

    self.stepCreateOrganisation(sequence=sequence,
                        sequence_list=sequence_list, **kw)
    organisation_rmb = sequence.get('organisation')
    organisation_rmb.edit(
      price_currency = rmb.getRelativeUrl(),
      title = organisation_rmb.getTitle() + '-rmb')

    self.stepCreateOrganisation(sequence=sequence,
                        sequence_list=sequence_list, **kw)
    organisation_dollar = sequence.get('organisation')

    organisation_dollar.edit(
      price_currency = dollar.getRelativeUrl(),
      title = organisation_dollar.getTitle() + '-dollar')

    self.stepCreateOrganisation(sequence=sequence,
                        sequence_list=sequence_list, **kw)
    organisation_euro = sequence.get('organisation')
    organisation_euro.edit(
      price_currency = euro.getRelativeUrl(),
      title = organisation_euro.getTitle() + '-euro')

    sequence.edit(
          organisation_rmb = organisation_rmb,
          organisation_dollar = organisation_dollar,
          organisation_euro = organisation_euro
        )


  def stepCreateTwoWarehouse(self, sequence=None,
                                    sequence_list=None, **kw):

    self.stepCreateOrganisation(sequence=sequence,
                        sequence_list=sequence_list, **kw)
    warehouseA = sequence.get('organisation')

    self.stepCreateOrganisation(sequence=sequence,
                        sequence_list=sequence_list, **kw)
    warehouseB = sequence.get('organisation')

    sequence.edit(
      warehouseA = warehouseA,
      warehouseB = warehouseB
    )


  def stepCreateSalesPackingListRMBToEURO(self, sequence=None,
                                            sequence_list = None, **kw):
    self.stepCreatePackingList(
      sequence=sequence,
      sequence_list= sequence_list,
      source = sequence.get('organisation_rmb'),
      destination = sequence.get('organisation_euro'),
      quantity = 50,
      price = 50,
      create_line = True,
      at_date = DateTime('2018/06/11 00:00:00 GMT+0'),
      price_currency = sequence.get('rmb'),
      packing_list_type = 'Sale Packing List')

  def stepCreateSalesPackingListEUROToUSD(self, sequence=None,
                                            sequence_list = None, **kw):
    self.stepCreatePackingList(
      sequence=sequence,
      sequence_list= sequence_list,
      source = sequence.get('organisation_euro'),
      destination = sequence.get('organisation_dollar'),
      quantity = 50,
      price = 50,
      create_line = True,
      at_date = DateTime('2018/06/11 05:00:00 GMT+0'),
      price_currency = sequence.get('euro'),
      packing_list_type = 'Sale Packing List')



  def stepCreatePurchasePackingListFromRMBToEURO(self, sequence=None,
                                                   sequence_list=None, **kw):
    self.stepCreatePackingList(
      sequence=sequence,
      sequence_list= sequence_list,
      source = sequence.get('organisation_rmb'),
      destination = sequence.get('organisation_euro'),
      quantity = 80,
      price = 80,
      create_line = True,
      at_date = DateTime('2018/06/11 02:00:00 GMT+0'),
      price_currency = sequence.get('rmb'),
      packing_list_type = 'Purchase Packing List')

  def stepCreatePurchasePackingListFromEUROToUSD(self, sequence=None,
                                                   sequence_list=None, **kw):
    self.stepCreatePackingList(
      sequence=sequence,
      sequence_list= sequence_list,
      source = sequence.get('organisation_euro'),
      destination = sequence.get('organisation_dollar'),
      quantity = 35,
      price = 123,
      create_line = True,
      at_date = DateTime('2018/06/11 03:00:00 GMT+0'),
      price_currency = sequence.get('euro'),
      packing_list_type = 'Purchase Packing List')

  def stepCreateProductionPackingListFromEUROWarehouseAToEuroWarehouseB(self, sequence=None,
                                                            sequence_list=None, **kw):
    self.stepCreatePackingList(
      sequence=sequence,
      sequence_list= sequence_list,
      source_section = sequence.get('organisation_euro'),
      source = sequence.get('warehouseA'),
      destination_section = sequence.get('organisation_euro'),
      destination = sequence.get('warehouseB'),
      quantity = 50,
      price = 50,
      create_line = True,
      at_date = DateTime('2018/06/12 00:00:00 GMT+0'),
      price_currency = sequence.get('euro'),
      packing_list_type = 'Production Packing List')

  def stepCreateInternalPackingListFromEUROWarehouseEuroToEuroWarehouseB(self, sequence=None,
                                                            sequence_list=None, **kw):
    self.stepCreatePackingList(
      sequence=sequence,
      sequence_list= sequence_list,
      source_section = sequence.get('organisation_euro'),
      source = sequence.get('organisation_euro'),
      destination_section = sequence.get('organisation_euro'),
      destination = sequence.get('warehouseB'),
      quantity = 14,
      price = 16,
      create_line = True,
      at_date = DateTime('2018/06/13 00:00:00 GMT+0'),
      price_currency = sequence.get('euro'),
      packing_list_type = 'Internal Packing List')


  def stepCreateSalesPackingListEUROToRMB(self, sequence=None,
                                            sequence_list = None, **kw):
    self.stepCreatePackingList(
      sequence=sequence,
      sequence_list= sequence_list,
      source = sequence.get('organisation_euro'),
      destination = sequence.get('organisation_rmb'),
      create_line = False,
      at_date = DateTime('2018/06/11 04:00:00 GMT+0'),
      price_currency = sequence.get('euro'),
      packing_list_type = 'Sale Packing List')

  def stepCreateSalesPackingListRMBToUSD(self, sequence=None,
                                            sequence_list = None, **kw):
    self.stepCreatePackingList(
      sequence=sequence,
      sequence_list= sequence_list,
      source = sequence.get('organisation_rmb'),
      destination = sequence.get('organisation_dollar'),
      create_line = False,
      at_date = DateTime('2018/06/11 05:00:00 GMT+0'),
      price_currency = sequence.get('rmb'),
      packing_list_type='Sale Packing List')


  def stepCreatePurchasePackingListFromUSDToRMB(self, sequence=None,
                                                   sequence_list=None, **kw):
    self.stepCreatePackingList(
      sequence=sequence,
      sequence_list= sequence_list,
      source = sequence.get('organisation_dollar'),
      destination = sequence.get('organisation_rmb'),
      create_line = False,
      at_date = DateTime('2018/07/11 03:00:00 GMT+0'),
      price_currency = sequence.get('dollar'),
      packing_list_type='Purchase Packing List')


  def stepCreateInternalPackingListFromEUROWarehouseEuroToEuroWarehouseB1(self, sequence=None,
                                                            sequence_list=None, **kw):
    self.stepCreatePackingList(
      sequence=sequence,
      sequence_list= sequence_list,
      source_section = sequence.get('organisation_euro'),
      source = sequence.get('organisation_euro'),
      destination_section = sequence.get('organisation_euro'),
      destination = sequence.get('warehouseB'),
      create_line = False,
      at_date = DateTime('2018/08/01 04:00:00 GMT+0'),
      price_currency = sequence.get('euro'),
      packing_list_type = 'Internal Packing List')

  def stepCreateProductionPackingListFromEUROWarehouseAToEuroWarehouseB1(self, sequence=None,
                                                            sequence_list=None, **kw):
    self.stepCreatePackingList(
      sequence=sequence,
      sequence_list= sequence_list,
      source_section = sequence.get('organisation_euro'),
      source = sequence.get('warehouseA'),
      destination_section = sequence.get('organisation_euro'),
      destination = sequence.get('warehouseB'),
      create_line = False,
      at_date = DateTime('2018/08/02 04:00:00 GMT+0'),
      price_currency = sequence.get('euro'),
      packing_list_type = 'Production Packing List')

  def stepCreatePackingList(self, sequence=None, sequence_list=None, **kw):
    resource_list = sequence.get('resource_list')
    quantity = kw.get('quantity', 100)
    price = kw.get('price', 100)
    price_currency = kw.get('price_currency')
    create_line = kw.get('create_line', False)
    at_date = kw.get('at_date', DateTime())
    packing_list_type = kw.get('packing_list_type')
    source = kw.get('source')
    destination = kw.get('destination')

    source_section=kw.get('source_section', source)
    destination_section=kw.get('destination_section', destination)


    packing_list_module = self.getPortal().getDefaultModule(
                              portal_type=packing_list_type)
    packing_list = packing_list_module.newContent(
                              portal_type=packing_list_type)

    start_date = stop_date = at_date
    packing_list.edit(
                      specialise=self.business_process,
                      source_section_value = source_section,
                      source_value = source,
                      destination_section_value = destination_section,
                      destination_value = destination,
                      start_date = start_date,
                      stop_date = stop_date,
                      price_currency = price_currency.getRelativeUrl()
                     )
    #create with last resource
    if create_line:
      packing_list_line = packing_list.newContent(
                    portal_type=packing_list_type + ' Line')
      packing_list_line.edit(resource_value = resource_list[-1],
                             quantity = quantity,
                             price = price
                            )
    sequence.edit(packing_list=packing_list)


  def stepCreateVariatedSalesPackingListLine(self, sequence=None, sequence_list=None, **kw):
    self.stepCreateVariatedPackingListLine(
      sequence= sequence,
      sequence_list=sequence_list,
      packing_list_type='Sale Packing List')

  def stepCreateVariatedPurchasePackingListLine(self, sequence=None, sequence_list=None, **kw):
    self.stepCreateVariatedPackingListLine(
      sequence= sequence,
      sequence_list=sequence_list,
      packing_list_type='Purchase Packing List',
      quantity= 134,
      price=32)

  def stepCreateVariatedInternalPackingListLine(self, sequence=None, sequence_list=None, **kw):
    self.stepCreateVariatedPackingListLine(
      sequence= sequence,
      sequence_list=sequence_list,
      packing_list_type='Internal Packing List')

  def stepCreateVariatedProductionPackingListLine(self, sequence=None, sequence_list=None, **kw):
    self.stepCreateVariatedPackingListLine(
      sequence= sequence,
      sequence_list=sequence_list,
      packing_list_type='Production Packing List')

  def stepCreateVariatedPackingListLine(self, sequence=None, sequence_list=None, **kw):
    resource_list = sequence.get('resource_list')
    packing_list = sequence.get('packing_list')
    #create with last resource
    packing_list_type = kw.get('packing_list_type')
    packing_list_line = packing_list.newContent(
                  portal_type=packing_list_type + ' Line')
    packing_list_line.edit(resource_value = resource_list[-1])

    resource_vcl = list(resource_list[-1].getVariationCategoryList(
        omit_individual_variation=1, omit_optional_variation=1))
    resource_vcl.sort()
    self.assertEqual(len(resource_vcl),2)
    packing_list_line.setVariationCategoryList(resource_vcl)
    cell_key_list = list(packing_list_line.getCellKeyList(base_id='movement'))
    price = kw.get('price', 50)
    quantity = kw.get('quantity', 200)
    for cell_key in cell_key_list:
      cell = packing_list_line.newCell(base_id='movement',
                                portal_type=packing_list_type +' Cell',
                                *cell_key)
      cell.edit(mapped_value_property_list=['price','quantity'],
                price=price, quantity=quantity,
                predicate_category_list=cell_key,
                variation_category_list=cell_key,)
      price += 1
      quantity += 1
    sequence.edit(packing_list=packing_list)


  def stepDeliverPackingList(self, sequence=None,
                                      sequence_list=None, **kw):
    pl = sequence.get('packing_list')
    pl.confirm()
    pl.setReady()
    pl.start()
    pl.stop()
    pl.deliver()
    self.tic()

  def stepSetResourceUnit(self, sequence=None,
                                 sequence_list=None, **kw):
    resource_list = sequence.get('resource_list')
    resource = resource_list[-1]
    resource.edit(
      quantity_unit = ['unit/piece'])

  def stepTestCalculateProduct(self, sequence=None, sequence_list=None, **kw):
    inventory_report = self.getInventoryReportModule().newContent(portal_type='Inventory Report')
    inventory_report.edit(
      destination_value = sequence.get('organisation_rmb'),
      destination_section_value = sequence.get('organisation_rmb'),
      valuation_method = 'Fifo'
      )
    self.tic()
    inventory_report.InventoryReport_calculateProductStock(batch_mode=True)
    self.assertEqual(inventory_report.getSimulationState(), 'calculating')
    self.tic()
    self.assertEqual(inventory_report.getSimulationState(), 'recorded')
    self.tic()
    inventory_report_line_list = inventory_report.contentValues(portal_type='Inventory Report Line')
    self.assertEqual(len(inventory_report_line_list), 5)
    inventory_report_line_list.sort(key=lambda x: x.total_quantity)
    self.assertEqual(inventory_report_line_list[0].total_quantity, -80-50)
    self.assertEqual(inventory_report_line_list[0].total_asset_price, 0)
    self.assertEqual(inventory_report_line_list[1].total_quantity, 0)
    self.assertEqual(inventory_report_line_list[1].total_asset_price, 0)
    self.assertEqual(inventory_report_line_list[2].total_quantity, 0)
    self.assertEqual(inventory_report_line_list[2].total_asset_price, 0)
    self.assertEqual(inventory_report_line_list[3].total_quantity, 134)
    self.assertAlmostEqual(inventory_report_line_list[3].total_asset_price, 134*32*6.95)
    self.assertEqual(inventory_report_line_list[4].total_quantity, 135)
    self.assertAlmostEqual(inventory_report_line_list[4].total_asset_price, 135*33*6.95)

    inventory_report = self.getInventoryReportModule().newContent(portal_type='Inventory Report')
    inventory_report.edit(
      destination_section_value = sequence.get('organisation_euro'),
      destination_value = sequence.get('warehouseB'),
      valuation_method = 'Fifo'
    )
    self.tic()
    inventory_report.InventoryReport_calculateProductStock(batch_mode=True)
    self.tic()
    inventory_report_line_list = inventory_report.contentValues(portal_type='Inventory Report Line')
    self.assertEqual(len(inventory_report_line_list), 3)
    inventory_report_line_list.sort(key=lambda x: x.total_quantity)
    self.assertEqual(inventory_report_line_list[0].total_quantity, 50+14)
    self.assertEqual(inventory_report_line_list[0].total_asset_price, 50*50 + 14*16)
    self.assertEqual(inventory_report_line_list[1].total_quantity, 200*2)
    self.assertEqual(inventory_report_line_list[1].total_asset_price, 200*50*2)
    self.assertEqual(inventory_report_line_list[2].total_quantity, 201*2)
    self.assertEqual(inventory_report_line_list[2].total_asset_price, 201*51*2)



    inventory_report = self.getInventoryReportModule().newContent(portal_type='Inventory Report')
    inventory_report.edit(
      destination_value = sequence.get('organisation_euro'),
      destination_section_value = sequence.get('organisation_euro'),
      valuation_method = 'Fifo'
    )
    self.tic()
    inventory_report.InventoryReport_calculateProductStock(batch_mode=True)
    self.tic()
    inventory_report_line_list = inventory_report.contentValues(portal_type='Inventory Report Line')
    self.assertEqual(len(inventory_report_line_list), 5)
    inventory_report_line_list.sort(key=lambda x: x.total_quantity)
    self.assertEqual(inventory_report_line_list[0].total_quantity, -201)
    self.assertEqual(inventory_report_line_list[0].total_asset_price, 0)
    self.assertEqual(inventory_report_line_list[1].total_quantity, -201)
    self.assertEqual(inventory_report_line_list[1].total_asset_price, 0)
    self.assertEqual(inventory_report_line_list[2].total_quantity, -200)
    self.assertEqual(inventory_report_line_list[2].total_asset_price, 0)
    self.assertEqual(inventory_report_line_list[3].total_quantity, -200)
    self.assertEqual(inventory_report_line_list[3].total_asset_price, 0)
    self.assertEqual(inventory_report_line_list[4].total_quantity, 45-14)
    self.assertAlmostEqual(inventory_report_line_list[4].total_asset_price, (45-14)*80*0.13)


    inventory_report = self.getInventoryReportModule().newContent(portal_type='Inventory Report')
    inventory_report.edit(
      destination_value = sequence.get('organisation_euro'),
      destination_section_value = sequence.get('organisation_euro'),
      valuation_method = 'Filo'
    )
    self.tic()
    inventory_report.InventoryReport_calculateProductStock(batch_mode=True)
    self.tic()
    inventory_report_line_list = inventory_report.contentValues(portal_type='Inventory Report Line')
    self.assertEqual(len(inventory_report_line_list), 5)
    inventory_report_line_list.sort(key=lambda x: x.total_quantity)
    self.assertEqual(inventory_report_line_list[0].total_quantity, -201)
    self.assertEqual(inventory_report_line_list[0].total_asset_price, 0)
    self.assertEqual(inventory_report_line_list[1].total_quantity, -201)
    self.assertEqual(inventory_report_line_list[1].total_asset_price, 0)
    self.assertEqual(inventory_report_line_list[2].total_quantity, -200)
    self.assertEqual(inventory_report_line_list[2].total_asset_price, 0)
    self.assertEqual(inventory_report_line_list[3].total_quantity, -200)
    self.assertEqual(inventory_report_line_list[3].total_asset_price, 0)
    self.assertEqual(inventory_report_line_list[4].total_quantity, 45-14)
    self.assertAlmostEqual(inventory_report_line_list[4].total_asset_price, (45-14)*50*0.13)

    inventory_report = self.getInventoryReportModule().newContent(portal_type='Inventory Report')
    inventory_report.edit(
      destination_value = sequence.get('organisation_euro'),
      destination_section_value = sequence.get('organisation_euro'),
      valuation_method = 'WeightedAverage'
    )
    self.tic()
    inventory_report.InventoryReport_calculateProductStock(batch_mode=True)
    self.tic()
    inventory_report_line_list = inventory_report.contentValues(portal_type='Inventory Report Line')
    self.assertEqual(len(inventory_report_line_list), 5)
    inventory_report_line_list.sort(key=lambda x: x.total_quantity)
    self.assertEqual(inventory_report_line_list[0].total_quantity, -201)
    self.assertEqual(inventory_report_line_list[0].total_asset_price, 0)
    self.assertEqual(inventory_report_line_list[1].total_quantity, -201)
    self.assertEqual(inventory_report_line_list[1].total_asset_price, 0)
    self.assertEqual(inventory_report_line_list[2].total_quantity, -200)
    self.assertEqual(inventory_report_line_list[2].total_asset_price, 0)
    self.assertEqual(inventory_report_line_list[3].total_quantity, -200)
    self.assertEqual(inventory_report_line_list[3].total_asset_price, 0)
    self.assertEqual(inventory_report_line_list[4].total_quantity, 45-14)
    #(45-14)*(80*80 + 50*50)/(80 + 50)*0.13
    self.assertAlmostEqual(inventory_report_line_list[4].total_asset_price, 275.9)


    inventory_report = self.getInventoryReportModule().newContent(portal_type='Inventory Report')
    inventory_report.edit(
      destination_value = sequence.get('organisation_euro'),
      destination_section_value = sequence.get('organisation_euro'),
      valuation_method = 'MonthlyWeightedAverage'
    )
    self.tic()
    inventory_report.InventoryReport_calculateProductStock(batch_mode=True)
    self.tic()
    inventory_report_line_list = inventory_report.contentValues(portal_type='Inventory Report Line')
    self.assertEqual(len(inventory_report_line_list), 5)
    inventory_report_line_list.sort(key=lambda x: x.total_quantity)
    self.assertEqual(inventory_report_line_list[0].total_quantity, -201)
    self.assertEqual(inventory_report_line_list[0].total_asset_price, 0)
    self.assertEqual(inventory_report_line_list[1].total_quantity, -201)
    self.assertEqual(inventory_report_line_list[1].total_asset_price, 0)
    self.assertEqual(inventory_report_line_list[2].total_quantity, -200)
    self.assertEqual(inventory_report_line_list[2].total_asset_price, 0)
    self.assertEqual(inventory_report_line_list[3].total_quantity, -200)
    self.assertEqual(inventory_report_line_list[3].total_asset_price, 0)
    self.assertEqual(inventory_report_line_list[4].total_quantity, 45-14)
    #(45-14)*(80*80 + 50*50)/(80 + 50)*0.13
    self.assertAlmostEqual(inventory_report_line_list[4].total_asset_price, 275.9)

    inventory_report = self.getInventoryReportModule().newContent(portal_type='Inventory Report')
    inventory_report.edit(
      destination_value = sequence.get('organisation_euro'),
      destination_section_value = sequence.get('organisation_euro'),
      at_date = DateTime('2018/06/11 04:00:00 GMT+0'),
      valuation_method = 'Fifo'
    )
    self.tic()
    inventory_report.InventoryReport_calculateProductStock(batch_mode=True)
    self.tic()
    inventory_report_line_list = inventory_report.contentValues(portal_type='Inventory Report Line')
    self.assertEqual(len(inventory_report_line_list), 3)
    inventory_report_line_list.sort(key=lambda x: x.total_quantity)
    self.assertEqual(inventory_report_line_list[0].total_quantity, -201)
    self.assertEqual(inventory_report_line_list[0].total_asset_price, 0)
    self.assertEqual(inventory_report_line_list[1].total_quantity, -200)
    self.assertEqual(inventory_report_line_list[1].total_asset_price, 0)
    self.assertEqual(inventory_report_line_list[2].total_quantity, 80+50-35)
    self.assertAlmostEqual(inventory_report_line_list[2].total_asset_price, (50-35)*50*0.13 + 80*80*0.13)

    inventory_report = self.getInventoryReportModule().newContent(portal_type='Inventory Report')
    inventory_report.edit(
      destination_value = sequence.get('organisation_euro'),
      destination_section_value = sequence.get('organisation_euro'),
      at_date = DateTime('2018/06/11 04:00:00 GMT+0'),
      valuation_method = 'Filo'
    )
    self.tic()
    inventory_report.InventoryReport_calculateProductStock(batch_mode=True)
    self.tic()
    inventory_report_line_list = inventory_report.contentValues(portal_type='Inventory Report Line')
    self.assertEqual(len(inventory_report_line_list), 3)
    inventory_report_line_list.sort(key=lambda x: x.total_quantity)
    self.assertEqual(inventory_report_line_list[0].total_quantity, -201)
    self.assertEqual(inventory_report_line_list[0].total_asset_price, 0)
    self.assertEqual(inventory_report_line_list[1].total_quantity, -200)
    self.assertEqual(inventory_report_line_list[1].total_asset_price, 0)
    self.assertEqual(inventory_report_line_list[2].total_quantity, 80+50-35)
    self.assertAlmostEqual(inventory_report_line_list[2].total_asset_price, 50*50*0.13 + (80-35)*80*0.13)

    inventory_report = self.getInventoryReportModule().newContent(portal_type='Inventory Report')
    inventory_report.edit(
      destination_value = sequence.get('organisation_euro'),
      destination_section_value = sequence.get('organisation_euro'),
      at_date = DateTime('2018/06/11 03:00:00 GMT+0'),
      valuation_method = 'Filo'
    )
    self.tic()
    inventory_report.InventoryReport_calculateProductStock(batch_mode=True)
    self.tic()
    inventory_report_line_list = inventory_report.contentValues(portal_type='Inventory Report Line')
    self.assertEqual(len(inventory_report_line_list), 1)
    inventory_report_line_list.sort(key=lambda x: x.total_quantity)
    self.assertEqual(inventory_report_line_list[0].total_quantity, 80+50-35)
    self.assertAlmostEqual(inventory_report_line_list[0].total_asset_price, 50*50*0.13 + (80-35)*80*0.13)


    inventory_report = self.getInventoryReportModule().newContent(portal_type='Inventory Report')
    inventory_report.edit(
      destination_value = sequence.get('organisation_dollar'),
      destination_section_value = sequence.get('organisation_dollar'),
      valuation_method = 'Fifo'
    )
    self.tic()
    inventory_report.InventoryReport_calculateProductStock(batch_mode=True)
    self.tic()
    inventory_report_line_list = inventory_report.contentValues(portal_type='Inventory Report Line')
    self.assertEqual(len(inventory_report_line_list), 5)
    inventory_report_line_list.sort(key=lambda x: x.total_quantity)
    self.assertEqual(inventory_report_line_list[0].total_quantity, -135)
    self.assertEqual(inventory_report_line_list[0].total_asset_price, 0)
    self.assertEqual(inventory_report_line_list[1].total_quantity, -134)
    self.assertEqual(inventory_report_line_list[1].total_asset_price, 0)
    self.assertEqual(inventory_report_line_list[2].total_quantity, 35+50)
    self.assertAlmostEqual(inventory_report_line_list[2].total_asset_price, 50*50*1.14 + 35*123*1.14)
    self.assertEqual(inventory_report_line_list[3].total_quantity, 200)
    self.assertAlmostEqual(inventory_report_line_list[3].total_asset_price, 50*200*0.14)
    self.assertEqual(inventory_report_line_list[4].total_quantity, 201)
    self.assertAlmostEqual(inventory_report_line_list[4].total_asset_price, 51*201*0.14)


  def test_01_workflowAndAccessPermission(self, run=run_all_test):
    """
    """
    if not run: return
    self.createUser('test_creator',
                    ['Auditor', 'Author'])

    user_id_list = ['test_creator', 'test_user', 'manager']
    for user in user_id_list:
      self.failUnlessUserCanAddDocument(user, self.getInventoryReportModule())

    self.login(user_id_list[0])
    inventory_report = self.getInventoryReportModule().newContent(portal_type='Inventory Report')

    self.login()
    for user in user_id_list:
      self.failUnlessUserCanAddDocument(user, inventory_report)

    inventory_report_line = inventory_report.newContent(portal_type='Inventory Report Line')
    self.assertEqual(inventory_report.getSimulationState(), 'draft')

    self.tic()
    for user in user_id_list:
      self.login(user)
      self.assertEqual(self.portal.portal_workflow.isTransitionPossible(inventory_report, 'calculate'), True)
      self.failUnlessUserCanModifyDocument(user, inventory_report)
      self.failUnlessUserCanModifyDocument(user, inventory_report_line)

    inventory_report.calculate()
    self.tic()
    self.assertEqual(inventory_report.getSimulationState(), 'calculating')
    for user in user_id_list:
      self.login(user)
      self.assertEqual(self.portal.portal_workflow.isTransitionPossible(inventory_report, 'record'), True)
      self.failUnlessUserCanModifyDocument(user, inventory_report)
      self.failUnlessUserCanModifyDocument(user, inventory_report_line)

    inventory_report.record()
    self.tic()
    self.assertEqual(inventory_report.getSimulationState(), 'recorded')

    for user in user_id_list:
      self.login(user)
      self.assertEqual(self.portal.portal_workflow.isTransitionPossible(inventory_report, 'calculate'), False)

    self.login()
    self.failIfUserCanPassWorkflowTransition(user_id_list[0], 'cancel_action', inventory_report)
    for user in user_id_list[1:]:
      self.failUnlessUserCanPassWorkflowTransition(user, 'cancel_action', inventory_report)


    for user in user_id_list[:-1]:
      self.failIfUserCanModifyDocument(user, inventory_report)
      self.failUnlessUserCanViewDocument(user, inventory_report)
      self.failIfUserCanModifyDocument(user, inventory_report_line)
      self.failUnlessUserCanViewDocument(user, inventory_report_line)

    self.failUnlessUserCanModifyDocument('manager', inventory_report)
    self.failUnlessUserCanModifyDocument('manager', inventory_report_line)

    inventory_report.cancel()
    self.tic()
    self.assertEqual(inventory_report.getSimulationState(), 'cancelled')
    for user in user_id_list[:-1]:
      self.failIfUserCanModifyDocument(user, inventory_report)
      self.failUnlessUserCanViewDocument(user, inventory_report)
      self.failIfUserCanModifyDocument(user, inventory_report_line)
      self.failUnlessUserCanViewDocument(user, inventory_report_line)

    self.failUnlessUserCanModifyDocument('manager', inventory_report)
    self.failUnlessUserCanModifyDocument('manager', inventory_report_line)

  def test_02_checkCalculateProduct(self, run=run_all_test):
    """
    2018/06/11 00:00:00 GMT+0
    organisation_rmb  --->  organisation_euro   sale packing list,quantity: 50 price: 50 rmb, product: notvariatedressource

    2018/06/11 02:00:00 GMT+0
    organisation_rmb  --->  organisation_euro   purchase packing list, quantity: 80, price: 80 rmb, product: notvariatedresource

    2018/06/11 03:00:00 GMT+0
    organisation_euro ---> organisation_dollar purchase packing list, quantity: 35, price: 123 euro, product: notvariatedreosurce

    2018/06/11 05:00:00 GMT+0
    organisation_euro ---> organisation_dollar sale packing list, quantity: 50, price: 50 euro, product: notvariatedresource

    2018/06/12 00:00:00 GMT+0
    organisation_euro warehouseA ---> organisation_euro warehouseB production packing list, quantity: 50, price: 50 euro, product: notvariatedresource

    2018/06/13 00:00:00 GMT+0
    organisation_euro organisation_euro ---> organisation_euro warehouseB internal packing list, quantity: 14, price: 16 euro, product: notvariatedresource

    2018/06/11 04:00:00 GMT+0
    organisation_euro ---> organisation_rmb sale packing list, quantity: 200, price: 50 euro, product: variatedresourceA Child/32
    organisation_euro ---> organisation_rmb sale packing list, quantity: 201, price: 51 euro, product: variatedresourceA Child/34

    2018/06/11 05:00:00 GMT+0
    organisation_rmb ---> organisation_dollar sale packing list, quantity: 200, price: 50 rmb, product: variatedresourceA child/32
    organisation_rmb ---> organisation_dollar sale packing list, quantity: 201, price: 51 rmb, product: variatedresourceA Child/34

    2018/07/11 03:00:00 GMT+0
    organisation_dollar ---> organisation_rmb purchase packing list, quantity: 134, price: 32 dollar, product: variatedresourceB child/32
    organisation_dollar ---> organisation_rmb purchase packing list, quantity: 135, price: 33 dollar, product: variatedresourceB child/34


    2018/08/01 04:00:00 GMT+0
    organisation_euro organisation_euro ---> organisation_euro warehouseB internal packing list, quantity: 200, price: 50 euro, product: variatedresourceA Child/32
    organisation_euro organisation_euro ---> organisation_euro warehouseB internal packing list, quantity: 201, price: 51 euro, product: variatedresourceA Child/32

    2018/08/02 04:00:00 GMT+0
    organisation_euro warehouseA ---> organisation_euro warehouseB production packing list, quantity: 200, price: 50 euro, product: variatedresourceA Child/32
    organisation_euro warehouseA ---> organisation_euro warehouseB production packing list, quantity: 201, price: 51 euro, product: variatedresourceA Child/32


    """
    if not run: return
    sequence_list = SequenceList()
    sequence_string = 'CreateNotVariatedResource \
                       stepCreateThreeCurrencys \
                       stepSetResourceUnit \
                       stepCreateThreeOrganisations \
                       stepCreateTwoWarehouse \
                       stepTic \
                       stepCreateSalesPackingListRMBToEURO \
                       stepDeliverPackingList \
                       stepTic \
                       stepCreateSalesPackingListEUROToUSD \
                       stepDeliverPackingList \
                       stepTic \
                       stepCreatePurchasePackingListFromRMBToEURO \
                       stepDeliverPackingList \
                       stepTic \
                       stepCreatePurchasePackingListFromEUROToUSD \
                       stepDeliverPackingList \
                       stepTic \
                       stepCreateProductionPackingListFromEUROWarehouseAToEuroWarehouseB \
                       stepDeliverPackingList \
                       stepTic \
                       stepCreateInternalPackingListFromEUROWarehouseEuroToEuroWarehouseB \
                       stepDeliverPackingList \
                       stepTic \
                       stepCreateVariatedResource \
                       stepSetResourceUnit \
                       stepTic \
                       stepCreateSalesPackingListEUROToRMB \
                       stepCreateVariatedSalesPackingListLine \
                       stepDeliverPackingList \
                       stepTic \
                       stepCreateSalesPackingListRMBToUSD \
                       stepCreateVariatedSalesPackingListLine \
                       stepDeliverPackingList \
                       stepTic \
                       stepCreateVariatedResource \
                       stepSetResourceUnit \
                       stepTic \
                       stepCreatePurchasePackingListFromUSDToRMB \
                       stepCreateVariatedPurchasePackingListLine \
                       stepDeliverPackingList \
                       stepTic \
                       stepCreateInternalPackingListFromEUROWarehouseEuroToEuroWarehouseB1 \
                       stepCreateVariatedInternalPackingListLine \
                       stepDeliverPackingList \
                       stepTic \
                       stepCreateProductionPackingListFromEUROWarehouseAToEuroWarehouseB1 \
                       stepCreateVariatedProductionPackingListLine \
                       stepDeliverPackingList \
                       stepTic \
                       stepTestCalculateProduct \
                      '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

def _test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestInventoryReportModule))
  return suite
