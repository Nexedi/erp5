##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                     Ivan Tyagov <ivan@nexedi.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import os, sys

from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from zLOG import LOG
import transaction

SESSION_ID = "12345678"

class TestCommerce(ERP5TypeTestCase):

  run_all_test = 1
  
  def getTitle(self):
    return "E-Commerce System"
  
  def afterSetUp(self):
    self.login()
    portal = self.getPortal()
    # create default currency (EUR)
    currency = portal.currency_module.newContent(portal_type = 'Currency', id = '1')
    currency.setTitle('EUR')
    currency.setReference('EUR')
    currency.setBaseUnitQuantity(0.01)
    # create product, set price & currency
    product = portal.product_module.newContent(portal_type = 'Product', id = '1')
    product.setSupplyLinePriceCurrency(currency.getRelativeUrl())
    product.setBasePrice(10.0)
    # create second product, set price & currency
    product = portal.product_module.newContent(portal_type = 'Product', id = '2')
    product.setSupplyLinePriceCurrency(currency.getRelativeUrl())
    product.setBasePrice(20.0)
    # create shipping which is actually a product
    shipping = portal.product_module.newContent(portal_type = 'Product', id = '3')
    shipping.setSupplyLinePriceCurrency(currency.getRelativeUrl())
    shipping.setBasePrice(10.0)
    shipping.setProductLine('shipping')
    transaction.commit()
    self.tic()

  def clearModule(self, module):
    module.manage_delObjects(list(module.objectIds()))
    transaction.commit()
    self.tic()

  def beforeTearDown(self):
    self.clearModule(self.portal.product_module)
    self.clearModule(self.portal.sale_order_module)
    self.clearModule(self.portal.currency_module)

  def login(self, quiet=0, run=run_all_test):
    uf = self.getPortal().acl_users
    uf._doAddUser('ivan', '', ['Manager'], [])
    uf._doAddUser('ERP5TypeTestCase', '', ['Manager'], [])
    user = uf.getUserById('ivan').__of__(uf)
    newSecurityManager(None, user)

  def getBusinessTemplateList(self):
    """
      Return the list of required business templates.
    """
    return ('erp5_base', 'erp5_web', 
            'erp5_trade', 'erp5_pdm', 'erp5_commerce',)
            
  def getDefaultProduct(self, id = '1'):
    """ 
      Get default product.
    """
    return self.getPortal().product_module[id]
    
  def test_01_AddResourceToShoppingCart(self, quiet=0, run=run_all_test):
    """ 
       Test adding an arbitrary resources to shopping cart.
    """
    if not run:
      return
    if not quiet:
      message = '\nCheck adding product to shopping cart'
      ZopeTestCase._print(message)
      LOG('Testing... ', 0, message)
    portal = self.getPortal()
    request = self.app.REQUEST
    default_product = self.getDefaultProduct()
    
    # set 'session_id' to simulate browser (cookie) environment 
    request.set('session_id', SESSION_ID)

    # add product to shopping cart
    portal.Resource_addToShoppingCart(default_product, 1)
    shoppping_cart_items =  portal.SaleOrder_getShoppingCartItemList()
    self.assertEquals(1, len(shoppping_cart_items))
    self.assertEquals(1, shoppping_cart_items[0].getQuantity())
    self.assertEquals(shoppping_cart_items[0].getResource(), \
                      default_product.getRelativeUrl())
    
  def test_02_AddSameResourceToShoppingCart(self, quiet=0, run=run_all_test):
    """ 
       Test adding same resource to shopping cart.
    """
    if not run:
      return
    if not quiet:
      message = '\nCheck adding same product to shopping cart'
      ZopeTestCase._print(message)
      LOG('Testing... ', 0, message)
    portal = self.getPortal()
    request = self.app.REQUEST
    default_product = self.getDefaultProduct()
    request.set('session_id', SESSION_ID)

    # add in two steps same product and check that we do not create
    # new Sale Order Line but just increase quantity on existing one
    portal.Resource_addToShoppingCart(default_product, 1)
    portal.Resource_addToShoppingCart(default_product, 1)
    shoppping_cart_items =  portal.SaleOrder_getShoppingCartItemList()
    self.assertEquals(1, len(shoppping_cart_items))
    self.assertEquals(2, shoppping_cart_items[0].getQuantity())
    self.assertEquals(shoppping_cart_items[0].getResource(), \
                      default_product.getRelativeUrl())

  def test_03_AddDifferentResourceToShoppingCart(self, quiet=0, run=run_all_test):
    """ 
       Test adding different resource to shopping cart.
    """
    if not run:
      return
    if not quiet:
      message = '\nCheck adding different product to shopping cart'
      ZopeTestCase._print(message)
      LOG('Testing... ', 0, message)
    portal = self.getPortal()
    request = self.app.REQUEST
    default_product = self.getDefaultProduct()
    another_product = self.getDefaultProduct(id = '2')
    request.set('session_id', SESSION_ID)
    
    # add second diff product and check that we create new Sale Order Line
    portal.Resource_addToShoppingCart(default_product, 1)
    portal.Resource_addToShoppingCart(default_product, 1)
    portal.Resource_addToShoppingCart(another_product, 1)
    shoppping_cart_items =  portal.SaleOrder_getShoppingCartItemList()
    self.assertEquals(2, len(shoppping_cart_items))
    self.assertEquals(2, shoppping_cart_items[0].getQuantity())
    self.assertEquals(1, shoppping_cart_items[1].getQuantity())
    self.assertEquals(shoppping_cart_items[0].getResource(), \
                      default_product.getRelativeUrl())
    self.assertEquals(shoppping_cart_items[1].getResource(), \
                      another_product.getRelativeUrl())
                      
                      
  def test_04_CalculateTotaShoppingCartPrice(self, quiet=0, run=run_all_test):
    """ 
       Test calculation shopping cart's total price.
    """
    if not run:
      return
    if not quiet:
      message = '\nTest calculation shopping cart total price'
      ZopeTestCase._print(message)
      LOG('Testing... ', 0, message)
    portal = self.getPortal()
    request = self.app.REQUEST
    default_product = self.getDefaultProduct()
    another_product = self.getDefaultProduct(id = '2')
    request.set('session_id', SESSION_ID)
    portal.Resource_addToShoppingCart(default_product, 1)
    portal.Resource_addToShoppingCart(default_product, 1)
    portal.Resource_addToShoppingCart(another_product, 1)

    shopping_cart = portal.SaleOrder_getShoppingCart()
    self.assertEquals(40.0, \
         float(shopping_cart.SaleOrder_getShoppingCartTotalPrice()))
    # include taxes (by default it's 20%)
    self.assertEquals(40.0*1.20, \
       float(shopping_cart.SaleOrder_getShoppingCartTotalPrice(include_shipping = True,
                                                                 include_taxes = True)))
    # no shipping selected yet so price should be the same
    self.assertEquals(40.0, \
       float(shopping_cart.SaleOrder_getShoppingCartTotalPrice(include_shipping = True)))
    # add shipping
    shipping = self.getDefaultProduct('3')
    portal.SaleOrder_editShoppingCart(field_my_shipping_method=shipping.getRelativeUrl())
    # test price calculation only with shipping
    self.assertEquals(40.0 + 10.0, \
       float(shopping_cart.SaleOrder_getShoppingCartTotalPrice(include_shipping = True)))
    # test price calculation shipping and taxes
    self.assertEquals((40.0 + 10.0)*1.20, \
         float(shopping_cart.SaleOrder_getShoppingCartTotalPrice(include_shipping = True,
                                                                 include_taxes = True)))
                                                                 
  def test_05_TestUpdateShoppingCart(self, quiet=0, run=run_all_test):
    """ 
       Test update of shopping cart.
    """
    if not run:
      return
    if not quiet:
      message = '\nTest update of shopping cart'
      ZopeTestCase._print(message)
      LOG('Testing... ', 0, message)
    portal = self.getPortal()
    request = self.app.REQUEST
    
    default_product = self.getDefaultProduct()
    another_product = self.getDefaultProduct(id = '2')
    shipping = self.getDefaultProduct('3')
    request.set('session_id', SESSION_ID)
    portal.Resource_addToShoppingCart(default_product, quantity=1)
    portal.Resource_addToShoppingCart(another_product, quantity=1)

    shopping_cart = portal.SaleOrder_getShoppingCart()
    portal.SaleOrder_editShoppingCart(field_my_shipping_method=shipping.getRelativeUrl())
    
    # increase shopping item number
    portal.SaleOrder_editShoppingCart((2, 1,))
    
    # test price calculation without shipping and without taxes
    self.assertEquals((10.0*2 + 20.0*1)*1.0, \
       float(shopping_cart.SaleOrder_getShoppingCartTotalPrice(include_shipping = False,
                                                               include_taxes = False)))
    # test price calculation with shipping and without taxes
    self.assertEquals((10.0*2  + 20.0*1 + 10.0)*1.0, \
         float(shopping_cart.SaleOrder_getShoppingCartTotalPrice(include_shipping = True,
                                                                 include_taxes = False)))
    # test price calculation with shipping and with taxes
    self.assertEquals((10.0*2 + 20.0*1 + 10.0)*1.20, \
         float(shopping_cart.SaleOrder_getShoppingCartTotalPrice(include_shipping = True,
                                                                 include_taxes = True)))
    
    # delete shopping item
    portal.SaleOrder_deleteShoppingCartItem('1')
    self.assertEquals(1, \
                      len(portal.SaleOrder_getShoppingCartItemList()))
                       
    portal.SaleOrder_deleteShoppingCartItem('2')
    self.assertEquals(0, \
                      len(portal.SaleOrder_getShoppingCartItemList()))
    self.assertEquals(0.0, \
                      float(shopping_cart.SaleOrder_getShoppingCartTotalPrice()))

  def test_06_TestClearShoppingCart(self, quiet=0, run=run_all_test):
    """ 
       Test update of shopping cart.
    """
    if not run:
      return
    if not quiet:
      message = '\nTest clear shopping cart'
      ZopeTestCase._print(message)
      LOG('Testing... ', 0, message)
    portal = self.getPortal()
    request = self.app.REQUEST
    default_product = self.getDefaultProduct()
    request.set('session_id', SESSION_ID)
    shopping_cart = portal.SaleOrder_getShoppingCart(action='reset')
    self.assertEquals(0, \
                      len(portal.SaleOrder_getShoppingCartItemList()))
    

import unittest
def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestCommerce))
  return suite

