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
from AccessControl.SecurityManagement import getSecurityManager
from zLOG import LOG
import transaction
import urllib

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
  Todo : 
  > Change name of all script, they are most of them never called on a SaleOrder
  > Test SaleOrder_getShoppingCartItemList With include_shipping=True
  > implement Person_getApplicableDiscountList (actually just return None)
  > implement Person_getApplicableTaxList (actually always return a tax of 20%)
  > Fix proxy for SaleOrder_confirmShopping, and anonym user cant call it !
  > SaleOrder_deleteShoppingCartItem doesnt use translation
  > SaleOrder_externalPaymentHandler is totally empty
  > SaleOrder_finalizeShopping doesnt check if the payment is successful or not
  > Fix proxy for SaleOrder_finalizeShopping anonym and normal user cant use it
  > SaleOrder_getAvailableShippingResourceList have hardcoded
  > SaleOrder_getSelectedShippingResource want a shipping_method but there is not
  > SaleOrder_getShoppingCartCustomer need to be refactor for fit clustering
  > SaleOrder_getShoppingCartDefaultCurrency should depend of site configuration
  > SaleOrder_isConsistent the usage must be more generic or rename it
  > SaleOrder_isShippingRequired this script just return 1 ...

  Not tested :
  Person_getApplicableDiscountList
  Person_getApplicableTaxList
  SaleOrder_getAvailableShippingResourceList
  SaleOrder_externalPaymentHandler
  SaleOrder_finalizeShopping
  SaleOrder_getSelectedShippingResource
  SaleOrder_isShippingRequired
  SaleOrder_paymentRedirect
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
  Person_editPersonalInformation (maybe useless to unittest)
  Resource_getShopUrl
  WebSection_getProductList
  """

  run_all_test = 1
  
  def getTitle(self):
    return "E-Commerce System"
  
  def afterSetUp(self):
    self.login()
    portal = self.getPortal()
    # create default currency (EUR)
    currency = portal.currency_module.newContent(portal_type='Currency', 
                                                 id='EUR')
    currency.setTitle('EUR')
    currency.setReference('EUR')
    currency.setBaseUnitQuantity(0.01)

    # create product, set price & currency
    product = portal.product_module.newContent(portal_type='Product', id='1')
    product.setSupplyLinePriceCurrency(currency.getRelativeUrl())
    product.setBasePrice(10.0)

    # create second product, set price & currency
    product = portal.product_module.newContent(portal_type='Product', id='2')
    product.setSupplyLinePriceCurrency(currency.getRelativeUrl())
    product.setBasePrice(20.0)
    # create shipping which is actually a product
    shipping = portal.product_module.newContent(portal_type='Product', 
                                                id='3')
    shipping.setSupplyLinePriceCurrency(currency.getRelativeUrl())
    shipping.setBasePrice(10.0)
    shipping.setProductLine('shipping')
    
    # validate default order rule
    default_order_rule = portal.portal_rules.default_order_rule
    if default_order_rule.getValidationState() != 'validated':
      portal.portal_rules.default_order_rule.validate()

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
    self.portal.portal_caches.clearAllCache()

  def createDefaultOrganisation(self):
    """
      Create Seller organisation
    """
    self.organisation_module = self.portal.getDefaultModule('Organisation')
    if 'seller' not in self.organisation_module.objectIds():
        self.nexedi = self.organisation_module.newContent(
        title="Seller",
        group='seller',
        role='internal',
        id='seller',
      )

  def createTestUser(self, first_name, last_name, reference, group,
                     destination_project=None, id=None):
    """
      Create a user with the given parameters
    """
    self.person_module = self.getPersonModule()
    person = self.person_module.newContent(
      first_name=first_name,
      last_name=last_name,
      reference=reference,
      password='secret',
      career_role='internal',
      id=id or reference,
    )

    # Set the assignment
    assignment = person.newContent(portal_type='Assignment')
    assignment.edit(function='', destination_value= getattr(self, 'seller', None),
                    start_date='1972-01-01', stop_date='2999-12-31',
                    group=group, destination_project=destination_project)
    assignment.open()
    transaction.commit()
    self.tic()

    #XXX: Security hack (lucas)
    self.portal.acl_users.zodb_roles.assignRoleToPrincipal('Manager', reference)

  def changeUser(self, name):
    user_folder = self.getPortal().acl_users
    user = user_folder.getUserById(name).__of__(user_folder)
    newSecurityManager(None, user)

  def login(self):
    uf = self.getPortal().acl_users
    uf._doAddUser('ivan', '', ['Manager'], [])
    uf._doAddUser('customer', '', ['Auditor', 'Author'], [])
    uf._doAddUser('ERP5TypeTestCase', '', ['Manager'], [])
    user = uf.getUserById('ivan').__of__(uf)
    newSecurityManager(None, user)

  def getBusinessTemplateList(self):
    """
      Return the list of required business templates.
    """
    return ('erp5_base', 'erp5_web', 
            'erp5_trade', 'erp5_pdm', 'erp5_commerce',)
            
  def getDefaultProduct(self, id='1'):
    """ 
      Get default product.
    """
    return self.getPortal().product_module[id]

  def initialiseSupplyLine(self):
    portal = self.getPortal()
    euro = portal.currency_module.newContent(portal_type='Currency',
                                                  id='euro',
                                                  reference='EUR')
    euro.setBaseUnitQuantity(1.00)
    euro.validate()
    
    category_list = []
    portal_categories = portal.portal_categories
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
        product = portal.product_module.newContent(portal_type="Product", 
                                                   title=title,
                                                   reference=reference)
        product_line = category.getRelativeUrl().replace('product_line/', '')
        product.setProductLine(product_line)
        product.setQuantityUnit('unit/piece')
        supply_line = product.newContent(id='default_supply_line',
                                         portal_type='Supply Line')
        supply_line.setBasePrice(10 * (i + 1))
        supply_line.setPricedQuantity(1)
        supply_line.setDefaultResourceValue(product)
        supply_line.setPriceCurrency('currency_module/EUR')
        product_list.append(product)
      
    for product in product_list:
      product.validate()
          
    ups = portal.product_module.newContent(portal_type='Product',
                                           title='UPS Shipping : 24h')
    ups.validate()
    ups.setQuantityUnit('unit/piece')
    supply_line = ups.setProductLine('shipping/UPS24h')
    supply_line = ups.newContent(id='default_supply_line',
                                 portal_type='Supply Line')
    supply_line.setBasePrice(10)
    supply_line.setPricedQuantity(1)
    supply_line.setDefaultResourceValue(product)
    supply_line.setPriceCurrency('currency_module/EUR')

  def createUser(self, name, role_list):
    user_folder = self.getPortal().acl_users
    user_folder._doAddUser(name, 'password', role_list, [])

  def changeUser(self, user_id):
    user_folder = self.getPortal().acl_users
    user = user_folder.getUserById(user_id).__of__(user_folder)
    newSecurityManager(None, user)

  def setupWebSite(self, **kw):
    """
      Setup Web Site
    """
    portal = self.getPortal()
    request = self.app.REQUEST
    
    # add supported languages for Localizer
    localizer = portal.Localizer
    for language in LANGUAGE_LIST:
      localizer.manage_addLanguage(language=language)
      
    # create website
    if hasattr(portal.web_site_module, 'web_site'):
      portal.web_site_module.manage_delObjects('web_site')
    web_site = portal.web_site_module.newContent(portal_type = 'Web Site', 
                                                id = 'web_site',
                                                **kw)
    transaction.commit()
    self.tic()

    web_site.WebSite_setupECommerceWebSite()
    self.initialiseSupplyLine()

    transaction.commit()
    self.tic()

    self.createDefaultOrganisation()
    self.createTestUser(first_name="Web",
                        last_name='master',
                        reference='webmaster',
                        group=None)

    return web_site
    
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
    self.assertEquals(SESSION_ID, portal.SaleOrder_getShoppingCartId())

    # add product to shopping cart
    self.assertTrue(portal.SaleOrder_isShoppingCartEmpty())
    portal.Resource_addToShoppingCart(default_product, 1)
    shoppping_cart_items =  portal.SaleOrder_getShoppingCartItemList()
    self.assertEquals(1, len(shoppping_cart_items))
    self.assertEquals(1, shoppping_cart_items[0].getQuantity())
    self.assertEquals(shoppping_cart_items[0].getResource(), \
                      default_product.getRelativeUrl())
    self.assertFalse(portal.SaleOrder_isShoppingCartEmpty())
    
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
       Test clear of shopping cart.
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

    another_product = self.getDefaultProduct(id = '2')
    portal.Resource_addToShoppingCart(default_product, quantity=1)
    portal.Resource_addToShoppingCart(another_product, quantity=1)
    self.tic()
    transaction.commit()
    
    shopping_cart = portal.SaleOrder_getShoppingCart(action='reset')
    self.assertEquals(0, len(portal.SaleOrder_getShoppingCartItemList()))


  def test_07_SessionIDGeneration(self, quiet=0, run=run_all_test):
    """
      Test the generation of session id
    """
    if not run:
      return
    if not quiet:
      message = '\nTest session id generation'
      ZopeTestCase._print(message)
      LOG('Testing... ', 0, message)
    import string

    id_string = self.getPortal().Base_generateSessionID()
    self.assertEquals(10, len(id_string))
    for caracter in id_string:
      self.assertTrue(caracter in string.letters)

    id_string = self.getPortal().Base_generateSessionID(max_long=20)
    self.assertEquals(20, len(id_string))

    # XXX : maybe it can be good to forbid this case
    id_string = self.getPortal().Base_generateSessionID(max_long=0)
    self.assertEquals(0, len(id_string))

  def test_08_getApplicableDiscountList(self, quiet=0, run=run_all_test):
    """
      Test the Person_getApplicableDiscountList script
    """
    if not run:
      return
    if not quiet:
      message = '\nTest the discount list'
      ZopeTestCase._print(message)
      LOG('Testing... ', 0, message)

    # XXX : actually the script is only in squeleton mode, only return None
    self.assertEquals(None, self.getPortal().Person_getApplicableDiscountList())

  def test_09_getApplicableTaxList(self, quiet=0, run=run_all_test):
    """
      Test the Person_getApplicableTaxList script
    """
    if not run:
      return
    if not quiet:
      message = '\nTest the applicable tax list'
      ZopeTestCase._print(message)
      LOG('Testing... ', 0, message)

    # XXX : actually the script is only in squeleton mode, only return a tax of 20%
    self.assertEquals({'VAT':20.0}, self.getPortal().Person_getApplicableTaxList())

  def test_10_confirmShopping(self, quiet=0, run=run_all_test):
    """
      Test the SaleOrder_confirmShopping script
    """
    if not run:
      return
    if not quiet:
      message = '\nTest the confirmation of shopping'
      ZopeTestCase._print(message)
      LOG('Testing... ', 0, message)
    portal = self.getPortal()
    request = self.app.REQUEST
    default_product = self.getDefaultProduct()
    request.set('session_id', SESSION_ID)

    portal.Resource_addToShoppingCart(default_product, quantity=1)
    self.tic()
    transaction.commit()

    # the confirmation should not be possible if the user is not logged
    self.logout()
    self.assertEquals(1, len(portal.SaleOrder_getShoppingCartItemList()))
    self.portal.SaleOrder_confirmShopping()
    self.assertTrue(urllib.quote("You need to create an account to " \
                                 "continue If you already have please login.") in 
                    request.RESPONSE.getHeader('location'))

    # but it should work if the user is authenticated
    self.changeUser('customer')
    self.portal.SaleOrder_confirmShopping()
    self.assertTrue(urllib.quote("SaleOrder_viewAsWebConfirm") in
                    request.RESPONSE.getHeader('location'))

  def test_11_deleteShoppingCartItem(self, quiet=0, run=run_all_test):
    """
      Test the SaleOrder_deleteShoppingCartItem script
    """
    if not run:
      return
    if not quiet:
      message = '\nTest the deletion of cart item'
      ZopeTestCase._print(message)
      LOG('Testing... ', 0, message)
    portal = self.getPortal()
    request = self.app.REQUEST
    default_product = self.getDefaultProduct()
    request.set('session_id', SESSION_ID)

    portal.Resource_addToShoppingCart(default_product, quantity=1)
    self.tic()
    transaction.commit()
    self.assertEquals(1, len(portal.SaleOrder_getShoppingCartItemList()))
    self.portal.SaleOrder_deleteShoppingCartItem()
    self.assertTrue(urllib.quote("Please select an item.") in 
                    request.RESPONSE.getHeader('location'))
    self.assertEquals(1, len(portal.SaleOrder_getShoppingCartItemList()))
    self.portal.SaleOrder_deleteShoppingCartItem(field_my_order_line_id=default_product.getId())
    self.assertTrue(urllib.quote("Successfully removed from shopping cart.") in
                    request.RESPONSE.getHeader('location'))
    self.assertEquals(0, len(portal.SaleOrder_getShoppingCartItemList()))

  def test_12_externalPaymentHandler(self, quiet=0, run=run_all_test):
    """
      Test the SaleOrder_externalPaymentHandler script
    """
    if not run:
      return
    if not quiet:
      message = '\nTest the External online payment system handler'
      ZopeTestCase._print(message)
      LOG('Testing... ', 0, message)
    portal = self.getPortal()
    request = self.app.REQUEST
    default_product = self.getDefaultProduct()
    request.set('session_id', SESSION_ID)

    # XXX : no test possible, script empty

  def test_13_finalizeShopping(self, quiet=0, run=run_all_test):
    """
      Test the SaleOrder_finalizeShopping script
    """
    if not run:
      return
    if not quiet:
      message = '\nTest the finalisation of the shopping procedure'
      ZopeTestCase._print(message)
      LOG('Testing... ', 0, message)

    self.createTestUser(first_name="Lucas",
                        last_name='Carvalho',
                        reference='lucas',
                        group=None)
    self.changeUser('lucas')
    portal = self.getPortal()
    request = self.app.REQUEST
    request.set('session_id', SESSION_ID)


    portal.Resource_addToShoppingCart(self.getDefaultProduct(), quantity=1)
    portal.Resource_addToShoppingCart(self.getDefaultProduct('2'), quantity=1)
    transaction.commit()
    self.tic()

    self.assertEquals(2, len(portal.SaleOrder_getShoppingCartItemList()))
    self.assertEquals(0, len(portal.sale_order_module.contentValues()))

    portal.SaleOrder_finalizeShopping()
    transaction.commit()
    self.tic()
    sale_order_object_list = portal.sale_order_module.contentValues()

    self.assertEquals(1, len(sale_order_object_list))
    self.assertEquals(2, len(sale_order_object_list[0].contentValues()))

    self.assertEquals(0, len(portal.SaleOrder_getShoppingCartItemList()))

    self.changeUser('ivan')
    
  def test_14_getAvailableShippingResourceList(self, quiet=0, run=run_all_test):
    """
      Test the SaleOrder_getAvailableShippingResourceList script
    """
    if not run:
      return
    if not quiet:
      message = '\nTest to get the available shipping resource list'
      ZopeTestCase._print(message)
      LOG('Testing... ', 0, message)

    portal = self.getPortal()
    request = self.app.REQUEST
    default_product = self.getDefaultProduct()
    request.set('session_id', SESSION_ID)

    shipping = portal.portal_categories.product_line.shipping.getRelativeUrl()
    portal.product_module.newContent(portal_type='Product',
                                     title='shipping',
                                     product_line=shipping)
    transaction.commit()
    self.tic()

    self.assertEquals(2,
                    len(portal.SaleOrder_getAvailableShippingResourceList()))
                                     

  def test_15_getFormatedData(self, quiet=0, run=run_all_test):
    """
      Test the datas formating scripts
    """
    if not run:
      return
    if not quiet:
      message = '\nTest to get the datas formating scripts'
      ZopeTestCase._print(message)
      LOG('Testing... ', 0, message)
    portal = self.getPortal()

    sale_order = portal.sale_order_module.newContent(portal_type="Sale Order",)
    sale_order_line = sale_order.newContent(portal_type="Sale Order Line",
                                            quantity="2",
                                            price="10")

    formated_date = sale_order.SaleOrder_getFormattedCreationDate()
    formated_price = sale_order.SaleOrder_getFormattedTotalPrice()
    self.assertEqual(sale_order.getCreationDate().strftime('%a, %b %Y %H:%M %p'), formated_date)
    self.assertEqual('%s %s' %('20.0', sale_order.getPriceCurrencyTitle()), formated_price)

  def test_16_getSelectedShippingResource(self, quiet=0, run=run_all_test):
    """
      Test the SaleOrder_getSelectedShippingResource script
    """
    if not run:
      return
    if not quiet:
      message = '\nTest to get selected shipping method from shopping cart'
      ZopeTestCase._print(message)
      LOG('Testing... ', 0, message)
    portal = self.getPortal()
    request = self.app.REQUEST
    request.set('session_id', SESSION_ID)
    default_product = self.getDefaultProduct()

    portal.Resource_addToShoppingCart(default_product, 1)
    shopping_cart = portal.SaleOrder_getShoppingCart()
    shipping_resource_list = portal.SaleOrder_getAvailableShippingResourceList()

    order_line = getattr(shopping_cart, 'shipping_method', None)
    if order_line is None:
      order_line = shopping_cart.newContent(id='shipping_method', portal_type='Sale Order Line')
    order_line.setResource(shipping_resource_list[0].getRelativeUrl())
    order_line.setQuantity(1)
    self.assertEquals(shipping_resource_list[0].getRelativeUrl(),
                      portal.SaleOrder_getSelectedShippingResource())

  def test_17_getShoppingCartDefaultCurrency(self, quiet=0, run=run_all_test):
    """
      Test the SaleOrder_getShoppingCartDefaultCurrency script
    """
    if not run:
      return
    if not quiet:
      message = '\nTest to get the default currency of a shopping cart'
      ZopeTestCase._print(message)
      LOG('Testing... ', 0, message)

    portal = self.getPortal()
    currency = portal.restrictedTraverse('currency_module/EUR')
    self.assertEquals(currency, portal.SaleOrder_getShoppingCartDefaultCurrency())

    
  def test_18_webSiteInitialisation(self, quiet=0, run=run_all_test):
    """
      Test the SaleOrder_getShoppingCartDefaultCurrency script
    """
    if not run:
      return
    if not quiet:
      message = '\nTest to get the default currency of a shopping cart'
      ZopeTestCase._print(message)
      LOG('Testing... ', 0, message)

    portal = self.getPortal()

  def test_19_simulatePaypalPayment(self, quiet=0, run=run_all_test):
    """
      Test all the scripts related to paypal
    """
    if not run:
      return
    if not quiet:
      message = '\nTest to simulate paypal payment.'
      ZopeTestCase._print(message)
      LOG('Testing... ', 0, message)

    portal = self.getPortal()

    # create new python script to replace the external method
    custom_skin = self.getPortal().portal_skins.custom
    method_id = 'ERP5Base_submitPaypalNVPRequest'
    if method_id in custom_skin.objectIds():
      custom_skin.manage_delObjects([method_id])
    custom_skin.manage_addProduct['PythonScripts']\
                   .manage_addPythonScript(id = method_id)
    script = custom_skin[method_id]
    script.ZPythonScript_edit('parameter_dict, nvp_url', SIMULATE_PAYPAL_SERVER)
    self.getPortal().changeSkin('View')
    
    #1 initialise a website
    web_site = self.setupWebSite()
    web_site.setProperty('ecommerce_paypal_username', 'user')
    web_site.setProperty('ecommerce_paypal_password', 'pass')
    web_site.setProperty('ecommerce_paypal_signature', 'signature')
   
    #2 login and activate a cart
    self.changeUser('webmaster')
    request = self.app.REQUEST
    request.set('session_id', SESSION_ID)

    #3 add a product in the cart
    default_product = self.getDefaultProduct()
    portal.Resource_addToShoppingCart(resource=default_product, quantity=1)
    transaction.commit()
    self.tic()
    
    #4 chose a shipping for the cart
    shopping_cart = portal.SaleOrder_getShoppingCart()
    shipping_resource_list = portal.SaleOrder_getAvailableShippingResourceList()
    order_line = getattr(shopping_cart, 'shipping_method', None)
    if order_line is None:
      order_line = shopping_cart.newContent(id='shipping_method',
                                            portal_type='Sale Order Line')
    order_line.setResource(shipping_resource_list[0].getRelativeUrl())
    order_line.setQuantity(1)
    self.assertEquals(shipping_resource_list[0].getRelativeUrl(),
                      portal.SaleOrder_getSelectedShippingResource())

    #5 : paypal step 1 : get a new token
    token = web_site.WebSite_getNewPaypalToken()    
    self.assertNotEquals(token, None)

    #6 : paypal step 2 : go to paypal and confirm this token
    # PayerID is normaly set in the request when paypal redirect to the instance
    request.set('PayerID', 'THEPAYERID')
    
    #7 : paypal step 3 : check if this token is confirmed by paypal
    error = web_site.WebSection_checkPaypalIdentification()
    self.assertEquals(error, None)
    self.assertTrue('/checkout' in request.RESPONSE.getHeader('location'))
    
    #8 : paypal step 4 : validate the payment
    self.assertEquals(1, len(portal.SaleOrder_getShoppingCartItemList()))
    self.assertEquals(0, len(portal.sale_order_module.contentValues()))
    
    web_site.WebSection_doPaypalPayment(token=token)
    transaction.commit()
    self.tic()
    
    #9 check if sale order created
    self.assertEquals(0, len(portal.SaleOrder_getShoppingCartItemList()))
    self.assertEquals(1, len(portal.sale_order_module.contentValues()))

    custom_skin.manage_delObjects([method_id])
    self.changeUser('ivan')
    
import unittest
def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestCommerce))
  return suite

