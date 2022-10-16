# -*- coding: utf-8 -*-
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

import os
import string
import unittest
from six.moves.urllib.parse import quote
from unittest import skip

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import FileUpload

SESSION_ID = "12345678"
LANGUAGE_LIST = ('en', 'fr', 'de', 'bg',)
SIMULATE_PAYPAL_SERVER = """
# this script simulate the reponse of paypal
if not 'METHOD' in parameter_dict:
  return {'ACK':'Failure'}

# Step 1 : get a token
if parameter_dict['METHOD'] == 'SetExpressCheckout':
  return {'ACK':'Success',
          'TOKEN':'FOOTOKEN'}

# Step 2 : check if token is good
if parameter_dict['METHOD'] == 'GetExpressCheckoutDetails':
  return {'ACK':'Success',
          'PAYERID':'THEPAYERID'}

# Step 3 : pay
if parameter_dict['METHOD'] == 'DoExpressCheckoutPayment':
  return {'ACK':'Success',
          'PAYERID':'THEPAYERID'}
return {'ACK':'Failure'}
"""


class TestCommerce(ERP5TypeTestCase):
  """
  Todo:
  > Change name of all script, most of them should not be called on a
    SaleOrder.
  > Test SaleOrder_getShoppingCartItemList With include_shipping=True
  > implement Person_getApplicableDiscountList (actually just return None)
  > implement Person_getApplicableTaxList (actually always return a tax of 20%)
  > SaleOrder_externalPaymentHandler is totally empty
  > Fix proxy for SaleOrder_finalizeShopping anonym and normal user cant use it
  > SaleOrder_getAvailableShippingResourceList have hardcoded

  Not tested :
  Person_getApplicableDiscountList
  SaleOrder_externalPaymentHandler
  SaleOrder_isShippingRequired
  WebSection_checkPaypalIdentification
  WebSection_checkoutProcedure
  WebSection_doPaypalPayment
  WebSection_viewCurrentPersonAsWeb
  WebSite_doExpressCheckoutPayment
  WebSite_getExpressCheckoutDetails
  WebSite_getNewPaypalToken
  WebSite_getPaypalOrderParameterDict
  WebSite_getPaypalSecurityParameterDict
  WebSite_getPaypalUrl
  WebSite_setupECommerceWebSite
  Product_getRelatedDescription
  Person_editPersonalInformation
  """
  business_process = 'business_process_module/erp5_default_business_process'

  def getTitle(self):
    return "E-Commerce System"

  def getBusinessTemplateList(self):
    """
      Return the list of required business templates.
    """
    return ('erp5_core_proxy_field_legacy',
            'erp5_base',
            'erp5_web',
            'erp5_pdm',
            'erp5_simulation',
            'erp5_trade',
            'erp5_commerce',
            'erp5_configurator_standard_trade_template',
            'erp5_simulation_test')

  def afterSetUp(self):
    uf = self.getPortal().acl_users
    uf._doAddUser('ivan', '', ['Manager'], [])
    uf._doAddUser('customer', '', ['Auditor', 'Author'], [])

    self.loginByUserName('ivan')

    product_module = self.portal.product_module
    currency_module = self.portal.currency_module
    sale_order_module = self.portal.sale_order_module
    condition_module = self.portal.sale_trade_condition_module
    currency_module.manage_permission('Access contents information',
                                     roles=['Anonymous'], acquire=0)
    product_module.manage_permission('Access contents information',
                                     roles=['Anonymous'], acquire=0)
    sale_order_module.manage_permission('Access contents information',
                                     roles=['Anonymous'], acquire=0)

    # add quantity_unit/unit/piece
    if getattr(self.portal.portal_categories.quantity_unit, 'unit', None) is None:
      self.portal.portal_categories.quantity_unit.newContent(id='unit')
    if getattr(self.portal.portal_categories.quantity_unit.unit, 'piece', None) is None:
      self.portal.portal_categories.quantity_unit.unit.newContent(id='piece')

    # create default currency (EUR)
    currency = currency_module.newContent(portal_type='Currency',
                                          id='EUR')
    currency.setTitle('EUR')
    currency.setReference('EUR')
    currency.setShortTitle('€')
    currency.setBaseUnitQuantity(0.01)
    currency.validate()
    currency.publish()

    # create product, set price & currency
    product = product_module.newContent(portal_type='Product', id='1')
    product.setSupplyLinePriceCurrency(currency.getRelativeUrl())
    product.setBasePrice(10.0)
    product.validate()
    product.publish()

    # create second product, set price & currency
    product = product_module.newContent(portal_type='Product', id='2')
    product.setSupplyLinePriceCurrency(currency.getRelativeUrl())
    product.setBasePrice(20.0)
    product.validate()
    product.publish()

    # create shipping which is actually a product
    shipping = product_module.newContent(portal_type='Product',
                                         id='3')
    shipping.setSupplyLinePriceCurrency(currency.getRelativeUrl())
    shipping.setBasePrice(10.0)
    shipping.setProductLine('shipping')
    shipping.validate()
    shipping.publish()

    # add default trade condition
    condition = condition_module.newContent(id="default_trade_condition",
                                            portal_type="Sale Trade Condition",
                                            specialise=self.business_process)
    condition.validate()

    # validate default order rule
    rule = self.getRule(reference='default_order_rule')
    if rule.getValidationState() != 'validated':
      rule.validate()

    self.website = self.setupWebSite()
    self.website.setProperty('ecommerce_base_currency',
                                            currency.getRelativeUrl())

    self.app.REQUEST.set('session_id', SESSION_ID)
    self.loginByUserName('ivan')
    self.tic()

  def clearModule(self, module):
    module.manage_delObjects(list(module.objectIds()))
    self.tic()

  def beforeTearDown(self):
    self.clearModule(self.portal.web_site_module)
    self.clearModule(self.portal.product_module)
    self.clearModule(self.portal.sale_order_module)
    self.clearModule(self.portal.currency_module)
    self.clearModule(self.portal.sale_trade_condition_module)
    self.portal.portal_caches.clearAllCache()
    self.portal.portal_sessions.manage_delObjects([SESSION_ID])
    self.commit()

  def createDefaultOrganisation(self):
    """
      Create Seller organisation
    """
    self.organisation_module = self.portal.getDefaultModule('Organisation')
    if 'seller' not in self.organisation_module.objectIds():
      self.nexedi = self.organisation_module.newContent(title="Seller",
                                                          group='seller',
                                                          role='internal',
                                                          id='seller')

  def createTestUser(self, first_name, last_name, reference, group,
                     destination_project=None):
    """
      Create a user with the given parameters
    """
    self.person_module = self.getPersonModule()
    if hasattr(self.person_module, reference):
      return
    person = self.person_module.newContent(
      first_name=first_name,
      last_name=last_name,
      reference=reference,
      password='secret',
      career_role='internal',
      id=reference,
    )

    # Set the assignment
    assignment = person.newContent(portal_type='Assignment')
    assignment.edit(function='',
                    destination_value=getattr(self, 'seller', None),
                    start_date='1972-01-01', stop_date='2999-12-31',
                    group=group, destination_project=destination_project)
    assignment.open()
    person.newContent(portal_type='ERP5 Login', reference=reference).validate()
    self.tic()

    #XXX: Security hack (lucas)
    self.portal.acl_users.zodb_roles.assignRoleToPrincipal('Manager',
                                                           person.Person_getUserId())

  def getDefaultProduct(self, id='1'): # pylint: disable=redefined-builtin
    """
      Get default product.
    """
    return self.getPortal().product_module[id]

  def initialiseSupplyLine(self):
    category_list = []
    portal_categories = self.portal.portal_categories
    if hasattr(portal_categories.product_line, 'ldlc'):
      portal_categories.product_line.manage_delObjects(['ldlc'])
    ldlc = portal_categories.product_line.newContent(portal_type='Category',
                                                     id='ldlc',
                                                     title='LDLC')
    laptop = ldlc.newContent(portal_type='Category',
                             id='laptop',
                             title='Laptop')

    netbook = laptop.newContent(portal_type='Category',
                                id='netbook',
                                title='Netbook')

    lcd = ldlc.newContent(portal_type='Category',
                          id='lcd',
                          title='Lcd Screen')
    mp3_player = ldlc.newContent(portal_type='Category',
                                 id='mp3',
                                 title='Mp3 Player')
    category_list.append(laptop)
    category_list.append(netbook)
    category_list.append(lcd)
    category_list.append(mp3_player)

    product_list = []
    for category in category_list:
      for i in range(3):
        title = '%s %s' % (category.getTitle(), i)
        reference = '%s_%s' % (category.getId(), i)
        product = self. portal.product_module.newContent(portal_type="Product",
                                                         title=title,
                                                         reference=reference)
        product_line = category.getRelativeUrl().replace('product_line/', '')
        product.setProductLine(product_line)
        product.setQuantityUnit('unit/piece')
        supply_line = product.newContent(portal_type='Sale Supply Line')
        supply_line.setBasePrice(10 * (i + 1))
        supply_line.setPricedQuantity(1)
        supply_line.setDefaultResourceValue(product)
        supply_line.setPriceCurrency('currency_module/EUR')
        product_list.append(product)

    for product in product_list:
      product.validate()
      product.publish()

    ups = self.portal.product_module.newContent(portal_type='Product',
                                           title='UPS Shipping : 24h')
    ups.setQuantityUnit('unit/piece')
    supply_line = ups.setProductLine('shipping/UPS24h')
    supply_line = ups.newContent(portal_type='Sale Supply Line')
    supply_line.setBasePrice(10)
    supply_line.setPricedQuantity(1)
    supply_line.setDefaultResourceValue(product)
    supply_line.setPriceCurrency('currency_module/EUR')
    ups.validate()
    ups.publish()
    self.tic()

  def createUser(self, name, role_list): # pylint: disable=arguments-differ
    user_folder = self.portal.acl_users
    user_folder._doAddUser(name, 'password', role_list, [])

  def setupWebSite(self, **kw):
    """
      Setup Web Site
    """
    # add supported languages for Localizer
    localizer = self.portal.Localizer
    for language in LANGUAGE_LIST:
      localizer.manage_addLanguage(language=language)

    # create website
    website = getattr(self.portal.web_site_module, 'website', None)
    if website is None:
      website = self.portal.web_site_module.newContent(portal_type='Web Site',
                                                        id='website',
                                                        **kw)
      self.tic()

    website.WebSite_setupECommerceWebSite()
    for section in website.WebSite_getMainSectionList():
      # Default site template defines no predicate on web sections, which makes
      # sense for a template, but prevents this test from checking whether
      # website products are properly listed. To not encourage newcommers to
      # set this (performance-wise) dangerous flag but rather to define
      # predicate criterion on web sections, set this flag in tests.
      section.setEmptyCriterionValid(True)
    self.initialiseSupplyLine()
    self.tic()

    self.createDefaultOrganisation()
    self.createTestUser(first_name="Web",
                        last_name='master',
                        reference='webmaster',
                        group=None)

    return website

  def createShoppingCartWithProductListAndShipping(self):
    """
      This method must create a Shopping Cart and add
      some Products and select one Shipping.
    """
    default_product = self.getDefaultProduct()
    self.website.Resource_addToShoppingCart(resource=default_product,
                                             quantity=1)

    shopping_cart = self.portal.SaleOrder_getShoppingCart()
    shipping_list = self.portal.SaleOrder_getAvailableShippingResourceList()
    order_line = getattr(shopping_cart, 'shipping_method', None)
    if order_line is None:
      order_line = shopping_cart.newContent(id='shipping_method',
                                            portal_type='Sale Order Line')
    order_line.setResource(shipping_list[0].getRelativeUrl())
    order_line.setQuantity(1)
    self.tic()

  def doFakePayment(self):
    """Simulate a payment"""

    #Set the shopping cart payed
    self.website.SaleOrder_setShoppingCartBuyer()

  def test_01_AddResourceToShoppingCart(self):
    """
       Test adding an arbitrary resources to shopping cart.
    """
    default_product = self.getDefaultProduct()

    # set 'session_id' to simulate browser (cookie) environment
    self.app.REQUEST.set('session_id', SESSION_ID)
    self.assertEqual(SESSION_ID, self.website.SaleOrder_getShoppingCartId())

    # check if the shopping cart is empty
    self.assertTrue(self.website.SaleOrder_isShoppingCartEmpty())

    # add product to shopping cart
    self.website.Resource_addToShoppingCart(default_product, 1)

    shoppping_cart_item_list = self.website.SaleOrder_getShoppingCartItemList()
    self.assertEqual(1, len(shoppping_cart_item_list))
    self.assertEqual(1, shoppping_cart_item_list[0].getQuantity())
    self.assertEqual(shoppping_cart_item_list[0].getResource(), \
                                         default_product.getRelativeUrl())
    self.assertFalse(self.website.SaleOrder_isShoppingCartEmpty())

  def test_02_AddSameResourceToShoppingCart(self):
    """
       Test adding same resource to shopping cart.
    """
    default_product = self.getDefaultProduct()

    # add in two steps same product and check that we do not create
    # new Sale Order Line but just increase quantity on existing one
    self.website.Resource_addToShoppingCart(default_product, 1)
    self.website.Resource_addToShoppingCart(default_product, 1)

    shoppping_cart_item_list = self.website.SaleOrder_getShoppingCartItemList()

    self.assertEqual(1, len(shoppping_cart_item_list))
    self.assertEqual(2, shoppping_cart_item_list[0].getQuantity())
    self.assertEqual(shoppping_cart_item_list[0].getResource(), \
                                          default_product.getRelativeUrl())

  def test_03_AddDifferentResourceToShoppingCart(self):
    """
       Test adding different resource to shopping cart.
    """
    default_product = self.getDefaultProduct()
    another_product = self.getDefaultProduct(id='2')

    # add second diff product and check that we create new Sale Order Line
    self.website.Resource_addToShoppingCart(default_product, 1)
    self.website.Resource_addToShoppingCart(default_product, 1)
    self.website.Resource_addToShoppingCart(another_product, 1)
    shoppping_cart_item_list = self.website.SaleOrder_getShoppingCartItemList()
    self.assertEqual(2, len(shoppping_cart_item_list))
    self.assertEqual(2, shoppping_cart_item_list[0].getQuantity())
    self.assertEqual(1, shoppping_cart_item_list[1].getQuantity())
    self.assertEqual(shoppping_cart_item_list[0].getResource(), \
                                          default_product.getRelativeUrl())
    self.assertEqual(shoppping_cart_item_list[1].getResource(), \
                                          another_product.getRelativeUrl())

  def test_04_CalculateTotaShoppingCartPrice(self):
    """
       Test calculation shopping cart's total price.
    """
    default_product = self.getDefaultProduct()
    another_product = self.getDefaultProduct(id='2')
    self.website.Resource_addToShoppingCart(default_product, 1)
    self.website.Resource_addToShoppingCart(default_product, 1)
    self.website.Resource_addToShoppingCart(another_product, 1)

    self.assertEqual(40.0, \
         float(self.website.SaleOrder_getShoppingCartTotalPrice()))
    # include taxes (by default it's 20%)
    self.assertEqual(40.0 * 1.20, \
         float(self.website.SaleOrder_getShoppingCartTotalPrice(
                                                        include_shipping=True,
                                                        include_taxes=True)))
    # no shipping selected yet so price should be the same
    self.assertEqual(40.0, \
         float(self.website.SaleOrder_getShoppingCartTotalPrice(
                                         include_shipping=True)))

    # add shipping
    shipping = self.getDefaultProduct('3')
    self.portal.SaleOrder_editShoppingCart(
                        field_my_shipping_method=shipping.getRelativeUrl())

    # test price calculation only with shipping
    self.assertEqual(40.0 + 10.0, \
                float(self.website.SaleOrder_getShoppingCartTotalPrice(
                                                      include_shipping=True)))

    # test price calculation shipping and taxes
    self.assertEqual((40.0 + 10.0) * 1.20, \
                float(self.website.SaleOrder_getShoppingCartTotalPrice(
                                                      include_shipping=True,
                                                      include_taxes=True)))

  def test_05_TestUpdateShoppingCart(self):
    """
       Test update of shopping cart.
    """
    default_product = self.getDefaultProduct()
    another_product = self.getDefaultProduct(id='2')
    shipping = self.getDefaultProduct('3')

    self.website.Resource_addToShoppingCart(default_product, quantity=1)
    self.website.Resource_addToShoppingCart(another_product, quantity=1)

    shipping_url = shipping.getRelativeUrl()

    # increase shopping item number and set shipping
    self.portal.SaleOrder_editShoppingCart(field_my_buy_quantity=(2, 1,),
                                      field_my_shipping_method=shipping_url)

    # test price calculation without shipping and without taxes
    self.assertEqual((10.0 * 2 + 20.0 * 1) * 1.0, \
       float(self.website.SaleOrder_getShoppingCartTotalPrice(
                                                    include_shipping=False,
                                                    include_taxes=False)))

    # test price calculation with shipping and without taxes
    self.assertEqual((10.0 * 2 + 20.0 * 1 + 10.0) * 1.0, \
         float(self.website.SaleOrder_getShoppingCartTotalPrice(
                                                    include_shipping=True,
                                                    include_taxes=False)))
    # test price calculation with shipping and with taxes
    self.assertEqual((10.0 * 2 + 20.0 * 1 + 10.0) * 1.20, \
         float(self.website.SaleOrder_getShoppingCartTotalPrice(
                                                    include_shipping=True,
                                                    include_taxes=True)))

    # delete shopping item
    self.portal.SaleOrder_deleteShoppingCartItem('1')
    self.assertEqual(1, \
                      len(self.website.SaleOrder_getShoppingCartItemList()))

    self.portal.SaleOrder_deleteShoppingCartItem('2')
    self.assertEqual(0, \
                      len(self.website.SaleOrder_getShoppingCartItemList()))
    self.assertEqual(0.0, \
                   float(self.website.SaleOrder_getShoppingCartTotalPrice()))

  def test_06_TestClearShoppingCart(self):
    """
       Test clear of shopping cart.
    """
    self.createShoppingCartWithProductListAndShipping()
    self.tic()

    self.website.SaleOrder_getShoppingCart(action='reset')
    self.assertEqual(0, len(self.website.SaleOrder_getShoppingCartItemList()))

  def test_07_SessionIDGeneration(self):
    """
      Test the generation of session id.
    """
    id_string = self.getPortal().Base_generateSessionID()
    self.assertEqual(10, len(id_string))
    for caracter in id_string:
      self.assertIn(caracter, string.ascii_letters)

    id_string = self.getPortal().Base_generateSessionID(max_long=20)
    self.assertEqual(20, len(id_string))

    # XXX : maybe it can be good to forbid this case
    id_string = self.getPortal().Base_generateSessionID(max_long=0)
    self.assertEqual(0, len(id_string))

  def test_08_getApplicableTaxList(self):
    """
      Test the Person_getApplicableTaxList script
    """
    # XXX : actually the script is only in squeleton mode,
    # only return a tax of 20%
    self.assertEqual(
        {'VAT': {'translated_title': 'VAT', 'percent': 20.0}},
        self.getPortal().Person_getApplicableTaxList())

  def test_09_paymentRedirect(self):
    """
      Test the SaleOrder_paymentRedirect script
    """
    default_product = self.getDefaultProduct()
    self.website.Resource_addToShoppingCart(default_product, quantity=1)
    self.tic()

    # the confirmation should not be possible if the user is not logged
    self.logout()
    self.assertEqual(1, len(self.website.SaleOrder_getShoppingCartItemList()))
    self.website.SaleOrder_paymentRedirect()
    self.assertIn(quote("You need to create an account to " \
                              "continue. If you already have please login."),
                    self.app.REQUEST.RESPONSE.getHeader('location'))

    # but it should work if the user is authenticated
    self.loginByUserName('customer')
    self.portal.SaleOrder_paymentRedirect()
    self.assertIn(quote("SaleOrder_viewAsWeb"),
                    self.app.REQUEST.RESPONSE.getHeader('location'))

  def test_10_deleteShoppingCartItem(self):
    """
      Test the SaleOrder_deleteShoppingCartItem script
    """
    default_product = self.getDefaultProduct()
    self.website.Resource_addToShoppingCart(default_product, quantity=1)
    self.assertEqual(1, len(self.website.SaleOrder_getShoppingCartItemList()))

    # Trying to remove
    self.portal.SaleOrder_deleteShoppingCartItem()
    self.assertIn(quote("Please select an item."),
                               self.app.REQUEST.RESPONSE.getHeader('location'))

    # Check if the item still into the Shopping Cart
    self.assertEqual(1, len(self.website.SaleOrder_getShoppingCartItemList()))

    # Remove the product from the Shopping Cart
    product_id = default_product.getId()
    self.portal.SaleOrder_deleteShoppingCartItem(
                                          field_my_order_line_id=product_id)

    # Check if the Product have been removed sucessfully
    self.assertIn(
              quote("Successfully removed from shopping cart."),
                 self.app.REQUEST.RESPONSE.getHeader('location'))

    # Check if the Shopping Cart is empty
    self.assertEqual(0, len(self.website.SaleOrder_getShoppingCartItemList()))

  def test_11_finalizeShopping(self):
    """
      Test the SaleOrder_finalizeShopping script
    """
    self.loginByUserName('webmaster')
    self.website.Resource_addToShoppingCart(self.getDefaultProduct(),
                                           quantity=1)
    self.website.Resource_addToShoppingCart(self.getDefaultProduct('2'),
                                           quantity=1)
    self.tic()

    self.assertEqual(2, len(self.website.SaleOrder_getShoppingCartItemList()))
    self.assertEqual(0, len(self.portal.sale_order_module.contentValues()))

    #Simulate payment
    self.doFakePayment()

    self.website.SaleOrder_finalizeShopping()
    self.tic()

    sale_order_object_list = self.portal.sale_order_module.contentValues()
    self.assertEqual(1, len(sale_order_object_list))
    self.assertEqual(2, len(sale_order_object_list[0].contentValues()))
    self.assertEqual(0, len(self.website.SaleOrder_getShoppingCartItemList()))

  def test_12_getAvailableShippingResourceList(self):
    """
      Test the SaleOrder_getAvailableShippingResourceList script
    """
    product_line = self.portal.portal_categories.product_line
    shipping_url = product_line.shipping.getRelativeUrl()
    self.portal.product_module.newContent(portal_type='Product',
                                          title='shipping',
                                          product_line=shipping_url)
    self.tic()
    self.assertEqual(2,
               len(self.portal.SaleOrder_getAvailableShippingResourceList()))

  def test_13_getFormatedData(self):
    """
      Test the datas formating scripts
    """
    sale_order = self.portal.sale_order_module.newContent(
                                                portal_type="Sale Order")
    sale_order.newContent(portal_type="Sale Order Line",
                          quantity="2",
                          price="10")

    self.assertEqual(
          sale_order.getCreationDate().strftime('%a, %d %b %Y %H:%M %p'),
                    sale_order.SaleOrder_getFormattedCreationDate())
    self.assertEqual('%s %s' % ('20.0', sale_order.getPriceCurrencyTitle()),
                           sale_order.SaleOrder_getFormattedTotalPrice())

  def test_14_getSelectedShippingResource(self):
    """
      Test the SaleOrder_getSelectedShippingResource script
    """
    default_product = self.getDefaultProduct()
    self.website.Resource_addToShoppingCart(default_product, 1)
    shopping_cart = self.portal.SaleOrder_getShoppingCart()
    shipping_list = self.portal.SaleOrder_getAvailableShippingResourceList()

    order_line = getattr(shopping_cart, 'shipping_method', None)
    if order_line is None:
      order_line = shopping_cart.newContent(id='shipping_method',
                                            portal_type='Sale Order Line')

    order_line.setResource(shipping_list[0].getRelativeUrl())
    order_line.setQuantity(1)

    selected_resource = self.portal.SaleOrder_getSelectedShippingResource()
    self.assertEqual(shipping_list[0].getRelativeUrl(),
                      selected_resource.getRelativeUrl())

  def test_15_getShoppingCartDefaultCurrency(self):
    """
      Testing the scripts:
      - WebSite_getShoppingCartDefaultCurrency
      - WebSite_getShoppingCartDefaultCurrencyCode
      - WebSite_getShoppingCartDefaultCurrencySymbol
    """
    currency = self.portal.restrictedTraverse('currency_module/EUR')
    self.assertEqual(currency,
                      self.website.WebSite_getShoppingCartDefaultCurrency())

    self.assertEqual(currency.getReference(),
                   self.website.WebSite_getShoppingCartDefaultCurrencyCode())

    self.assertEqual(currency.getShortTitle(),
                 self.website.WebSite_getShoppingCartDefaultCurrencySymbol())

  def test_16_simulatePaypalPayment(self):
    """
      Test all the scripts related to paypal
    """
    # create new python script to replace the external method
    custom_skin = self.portal.portal_skins.custom
    method_id = 'WebSection_submitPaypalNVPRequest'
    if method_id in custom_skin.objectIds():
      custom_skin.manage_delObjects([method_id])
    custom_skin.manage_addProduct['PythonScripts']\
                   .manage_addPythonScript(id=method_id)

    script = custom_skin[method_id]
    script.ZPythonScript_edit('parameter_dict, nvp_url',
                                                  SIMULATE_PAYPAL_SERVER)

    self.portal.changeSkin('View')

    #1 initialise a website
    self.website.setProperty('ecommerce_paypal_username', 'user')
    self.website.setProperty('ecommerce_paypal_password', 'pass')
    self.website.setProperty('ecommerce_paypal_signature', 'signature')

    #2 login and activate a cart
    self.loginByUserName('webmaster')
    request = self.app.REQUEST
    request.set('session_id', SESSION_ID)

    #3 add a product in the cart
    self.createShoppingCartWithProductListAndShipping()

    #4 : paypal step 1 : get a new token
    token = self.website.cart.WebSection_getNewPaypalToken()
    self.assertNotEqual(token, None)

    #5 : paypal step 2 : go to paypal and confirm this token
    # PayerID is normaly set in the request when paypal
    # redirect to the instance
    request.set('PayerID', 'THEPAYERID')

    #6 : paypal step 3 : check if this token is confirmed by paypal
    error = self.website.WebSection_checkPaypalIdentification()
    self.assertEqual(error, None)
    url_location = request.RESPONSE.getHeader('location')
    self.assertIn('/checkout', url_location)

    #7 : paypal step 4 : validate the payment
    self.assertEqual(1,
                       len(self.website.SaleOrder_getShoppingCartItemList()))
    self.assertEqual(0, len(self.portal.sale_order_module.contentValues()))

    self.website.WebSection_doPaypalPayment(token=token)
    self.tic()

    #8 check if sale order created
    self.assertEqual(0, len(self.website.SaleOrder_getShoppingCartItemList()))
    self.assertEqual(1, len(self.portal.sale_order_module.contentValues()))

    custom_skin.manage_delObjects([method_id])

  def test_17_getProductListFromWebSection(self):
    """
      Test the  WebSection_getProductList script.
    """
    laptop_product = self.getDefaultProduct(id='1')
    laptop_product.setProductLine('ldlc/laptop')
    netbook_product = self.getDefaultProduct(id='2')
    netbook_product.setProductLine('ldlc/laptop')

    self.website.WebSection_generateSectionFromCategory(
                                              category='product_line/ldlc',
                                              section_id='product_section',
                                              depth=2)
    self.tic()

    self.assertEqual(14,
             len(self.website.product_section.WebSection_getProductList()))
    self.assertEqual(8,
         len(self.website.product_section.laptop.WebSection_getProductList()))

    netbook_section = self.website.product_section.laptop.netbook
    self.assertEqual(3, len(netbook_section.WebSection_getProductList()))

  def test_18_editShoppingCardWithABlankShippingMethod(self):
    """
      This test must make sure that you can edit the shopping cart selecting a
      blank shipping method and it will not break.
    """
    default_product = self.getDefaultProduct()
    self.website.Resource_addToShoppingCart(default_product, 1)

    shopping_cart = self.website.SaleOrder_getShoppingCart()
    self.assertFalse(hasattr(shopping_cart, 'shipping_method'))

    self.portal.SaleOrder_editShoppingCart(field_my_shipping_method='')
    self.portal.SaleOrder_editShoppingCart(field_my_shipping_method=None)

    # add shipping
    shipping = self.getDefaultProduct('3')
    self.portal.SaleOrder_editShoppingCart(
                          field_my_shipping_method=shipping.getRelativeUrl())

    self.assertTrue(hasattr(shopping_cart, 'shipping_method'))

  def test_19_editShoppingCardWithShippingMethodWithoutPrice(self):
    """
      This test must make sure that you can not edit the shopping cart
      selecting a shipping method without price.
    """
    default_product = self.getDefaultProduct(id='1')
    self.website.Resource_addToShoppingCart(default_product, 1)

    # add shipping
    shipping = self.getDefaultProduct('3')
    shipping.setBasePrice(None)
    self.website.SaleOrder_editShoppingCart(
                     field_my_shipping_method=shipping.getRelativeUrl())

    self.assertEqual(10.0, \
            float(self.website.SaleOrder_getShoppingCartTotalPrice(
                                                    include_shipping=True)))

  def test_20_getProductListFromWebSite(self):
    """
      Test the  WebSite_getProductList script.
    """
    self.assertEqual(5, len(self.website.WebSite_getProductList()))
    self.assertEqual(16,
               len(self.website.WebSite_getProductList(limit=1000)))

  def test_21_AddResourceToShoppingCartWithAnonymousUser(self):
    """
      Test adding an arbitrary resources to shopping cart with Anonymous user.
    """
    # anonymous user
    self.logout()
    self.createShoppingCartWithProductListAndShipping()
    shoppping_cart_item_list = self.website.SaleOrder_getShoppingCartItemList()
    self.assertEqual(1, len(shoppping_cart_item_list))

  @skip('WebSite_createWebSiteAccount is disabled by default.')
  def test_22_createShoppingCartWithAnonymousAndLogin(self):
    """
      Test adding an arbitrary resources to shopping cart with Anonymous user
      then create a new user, login and check if the Shopping Cart still the
      same.
    """
    # anonymous user
    self.logout()
    self.createShoppingCartWithProductListAndShipping()
    kw = dict(reference='toto',
              first_name='Toto',
              last_name='Test',
              default_email_text='test@test.com',
              password='secret',
              password_confirm='secret')
    for key, item in kw.items():
      self.app.REQUEST.set('field_your_%s' % key, item)
    self.website.WebSite_createWebSiteAccount('WebSite_viewRegistrationDialog')
    self.tic()

    self.loginByUserName('toto')
    self.portal.SaleOrder_paymentRedirect()
    self.assertIn(quote("SaleOrder_viewAsWeb"),
                    self.app.REQUEST.RESPONSE.getHeader('location'))

  def test_23_getShoppingCartCustomer(self):
    """
      It must test SaleOrder_getShoppingCartCustomer script
      for a given Authenticated Member it should return the person value.
    """
    self.logout()
    person_object = self.website.SaleOrder_getShoppingCartCustomer()
    self.assertEqual(person_object, None)

    self.loginByUserName('webmaster')
    person_object = self.website.SaleOrder_getShoppingCartCustomer()
    self.assertNotEqual(person_object, None)
    self.assertEqual(person_object.getReference(), 'webmaster')

  def test_24_getImageDataWithAnonymousUser(self):
    """
      Anonymous user must be able to get product image.
    """
    product = self.getDefaultProduct()
    import Products.ERP5.tests
    file_upload = FileUpload(
      os.path.join(os.path.dirname(Products.ERP5.tests.__file__),
                   'test_data', 'images', 'erp5_logo_small.png'))
    product.edit(default_image_file=file_upload)
    self.tic()

    self.logout()
    product = self.getDefaultProduct()
    self.assertNotIn(product.getDefaultImageValue().getData(), ('', None))

  def test_25_getSaleOrderModuleAbsoluteUrlWithAnonymousUser(self):
    """
      Anonymous User must have permission access Sale Order Module contents
      information.
    """
    self.logout()
    self.assertNotEqual(self.website.sale_order_module.absolute_url(), None)

  def test_26_getShoppingCartDefaultCurrencyWithAnonymousUser(self):
    """
      Anonymous User must have persmission to access Currency Module contents
      information and Published Currency objects.
      Testing the scripts:
      - WebSite_getShoppingCartDefaultCurrency
      - WebSite_getShoppingCartDefaultCurrencyCode
      - WebSite_getShoppingCartDefaultCurrencySymbol
    """
    self.logout()
    currency_url = self.website.getLayoutProperty('ecommerce_base_currency')
    currency_object = self.portal.restrictedTraverse(currency_url)
    self.assertEqual(currency_object,
                      self.website.WebSite_getShoppingCartDefaultCurrency())

    self.assertEqual(currency_object.getReference(),
                   self.website.WebSite_getShoppingCartDefaultCurrencyCode())

    self.assertEqual(currency_object.getShortTitle(),
                 self.website.WebSite_getShoppingCartDefaultCurrencySymbol())

  def test_27_ResourceGetShopUrl(self):
    """
      For a given Resource the Python Script (Resource_getShopUrl)
      should return the Shopping Url.
    """
    product = self.getDefaultProduct()
    self.assertEqual(product.Resource_getShopUrl(),
                 '%s/%s' % (product.absolute_url(), 'Resource_viewAsShop'))

  def test_28_finalizeShoppingWithComment(self):
    """
      Testing if the comment added during the checkout will be set on the sale
      order object generated.
    """
    self.loginByUserName('webmaster')
    comment = 'TESTING COMMENT'
    self.website.Resource_addToShoppingCart(self.getDefaultProduct(),
                                           quantity=1)

    self.website.SaleOrder_paymentRedirect(field_my_comment=comment)
    self.doFakePayment()
    self.website.SaleOrder_finalizeShopping()
    self.tic()

    sale_order_object_list = self.portal.sale_order_module.contentValues()
    self.assertEqual(comment, sale_order_object_list[0].getComment())


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestCommerce))
  return suite
