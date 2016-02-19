##############################################################################
#
# Copyright (c) 2002-2016 Nexedi SA and Contributors. All Rights Reserved.
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
import transaction

class PandasInventoryTest(ERP5TypeTestCase):
  """
  A test case to ensure the Pandas-based Inventory API works as expected.
  """

  def getBusinessTemplateList(self):
    """
    Tuple of Business Templates we need to install
    """
    return ('erp5_wendelin',)

  def afterSetUp(self):
    """
    This is ran before anything, used to set the environment
    """
    self.supplier = self.createSupplier()
    self.client = self.createClient()
    self.sale_order = self.createSaleOrder(self.supplier, self.client)
    transaction.commit()

    self.tic()
    self.assertNoPendingMessage()
  
  def createSupplier(self):
    organisation_module = self.portal.getDefaultModule(portal_type='Organisation')
    organisation = organisation_module.newContent(
      title='My Supplier',
      
    )
    organisation.validate()
    return organisation
    
  def createClient(self):
    organisation_module = self.portal.getDefaultModule(portal_type='Organisation')
    organisation = organisation_module.newContent(
      title='My Client',
    )
    organisation.validate()
    return organisation
    
  def createSaleOrder(self, supplier, client):
    sale_order_module = self.portal.getDefaultModule(portal_type='Sale Order')
    product_module = self.portal.getDefaultModule(portal_type='Product')
    sale_trade_condition_module = self.portal.getDefaultModule(portal_type='Sale Trade Condition')
    currency_module = self.portal.getDefaultModule(portal_type='Currency')
    
    currency = currency_module.searchFolder(title='Euro')[0].getObject()
    specialise = sale_trade_condition_module.searchFolder(title='General Sale Trade Condition')[0].getObject()
    
    sale_order = sale_order_module.newContent(
      source_section_value=supplier,
      source_value=supplier,
      destination_section_value=client,
      destination_value=client,
      price_currency=currency.getRelativeUrl(),
      start_date='01/01/2015'
    )
    
    sale_order.setSpecialiseValue(specialise, portal_type="Sale Trade Condition")
    
    product = product_module.newContent(
      title='My product',
      quantity_unit='unit/piece'
    )
    
    sale_order.newContent(
      portal_type='Sale Order Line',
      quantity=1,
      price=10.0,
      resource_value=product
    )
    
    self.portal.portal_workflow.doActionFor(
      sale_order,
      'plan_action',
      wf_id='order_workflow'
    )
    
    self.portal.portal_workflow.doActionFor(
      sale_order,
      'confirm_action',
      wf_id='order_workflow'
    )

    return sale_order
    
  def test_01_fillBigArrayTest(self):
    resource_uid = self.sale_order['1'].getResourceUid()
    data = self.portal.portal_skins.erp5_wendelin_inventory.Base_zGetStockByResource(resource_uid=resource_uid)
    self.portal.portal_skins.erp5_wendelin_inventory.Base_convertResultsToBigArray(
      data,
      reference='TestingFillBigArray'
    )
    transaction.commit()
    self.tic()
    
    data_array = self.portal.portal_catalog(portal_type='Data Array', reference='TestingFillBigArray')[0].getObject()
    self.assertEquals(len(data_array.getArray()), 8)

  def test_02_extendBigArrayTest(self):
    resource_uid = self.sale_order['1'].getResourceUid()
    data = self.portal.portal_skins.erp5_wendelin_inventory.Base_zGetStockByResource(resource_uid=resource_uid)
    self.portal.portal_skins.erp5_wendelin_inventory.Base_convertResultsToBigArray(
      data,
      reference='TestingExtendBigArray'
    )
    transaction.commit()
    self.tic()
    
    data_array = self.portal.portal_catalog(portal_type='Data Array', reference='TestingExtendBigArray')[0].getObject()
    current_size = len(data_array)
    
    self.portal.portal_skins.erp5_wendelin_inventory.Base_extendBigArray(
        data_array.getArray(), 
        data_array.getArray()
    )
    
    self.assertTrue(len(data_array) == 2*current_size)
    
    first_half = data_array.getArray()[0:7]
    second_half = data_array.getArray()[8:15]
    
    result = all([x[0] == x[1] for x in zip(first_half, second_half)])
    self.assertTrue(result)
    
  def test_03_importCategoryInformationTest(self):
    resource_uid = self.sale_order['1'].getResourceUid()
    data = self.portal.portal_skins.erp5_wendelin_inventory.Base_zGetStockByResource(resource_uid=resource_uid)
    self.portal.portal_skins.erp5_wendelin_inventory.Base_convertResultsToBigArray(
      data,
      reference='TestingImportCategoryInformation'
    )
    transaction.commit()
    self.tic()
    
    array = self.portal.portal_skins.erp5_wendelin_inventory.Base_fillPandasInventoryCategoryList(
        'TestingImportCategoryInformation',
        verbose=False, 
        duplicate_category=False
    )
    
    transaction.commit()
    self.tic()
    
    resource_category_array = array[:][['resource_category']]
    self.assertTrue(all([item != '' for item in resource_category_array]))
    
  def test_04_getMovementHistoryListTest(self):
    resource_uid = self.sale_order['1'].getResourceUid()
    data = self.portal.portal_skins.erp5_wendelin_inventory.Base_zGetStockByResource(resource_uid=resource_uid)
    self.portal.portal_skins.erp5_wendelin_inventory.Base_convertResultsToBigArray(
      data,
      reference='TestingGetMovementHistoryList'
    )
    transaction.commit()
    self.tic()
    
    result = self.portal.portal_catalog(portal_type='Data Array', reference='TestingGetMovementHistoryList')
    self.assertTrue(len(result) != 0)
    
    df = self.portal.portal_skins.erp5_wendelin_inventory.Base_filterInventoryDataFrame(
      is_accountable=True,
      resource_uid=resource_uid,
      data_array_reference='TestingGetMovementHistoryList'
    )
    
    self.assertTrue(all(df['is_accountable'] == True))
    self.assertTrue(all(df['resource_uid'] == resource_uid))
    
    