##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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

import string, re
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base

from Products.CMFCore.utils import getToolByName

from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5.VariationValue import VariationValue
from Products.ERP5.Document.Order import Order
from Products.ERP5.Document.Delivery import Delivery
from Products.ERP5.Document.OrderLine import OrderLine as ERP5OrderLine
from Products.ERP5.Document.Amount import Amount

from Products.MMMShop.ShopOrder import ShopOrder as MMMShopOrder
from Products.MMMShop.ShopOrder import OrderLine as MMMOrderLine
from Products.MMMShop.utils import getUniqueID

from Products.CMFCore.WorkflowCore import WorkflowMethod

from zLOG import LOG

match_path = re.compile('http.*//[^/]*/(.*)')

class OrderLine(MMMOrderLine, ERP5OrderLine):
    """
      An orderline describes 1 line of an order
    """
    meta_type = 'ERP5 Shop Order Line'
    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.View)

    # Declarative interfaces
    __implements__ = ( Interface.Variated, )

    security.declarePublic('getProduct')
    def getProduct(self):
        """
        Return the product object
        """
        try:
            portal = getToolByName(self, 'portal_url').getPortalObject()
            product_path = match_path.match(self.getProductUrl()).groups()[0]
            return portal.restrictedTraverse(product_path)
        except:
            return None

    security.declarePublic('getProductTitle')
    def getProductTitle(self):
        """
        Return the product object title
        """
        try:
            product = self.getProduct()
            return product.getTitle()
        except:
            return 'Unknown Product'

    security.declarePublic('getVariationValue')
    def getVariationValue(self):
        product = self.getProduct()
        return product.newVariationValue(context=self)


class ShopOrder(MMMShopOrder, Order):
    """
      Shop Order
    """
    meta_type = 'ERP5 Shop Order'
    portal_type = 'Shop Order'
    add_permission = Permissions.AddERP5Content
    isPortalContent = 1
    isRADContent = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.View)

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      , PropertySheet.Price
                      , PropertySheet.Task
                      , PropertySheet.ShopOrder
                      )

    # Default values
    _vat = 0.0

    # Factory Type Information
    factory_type_information = \
      {    'id'             : portal_type
         , 'meta_type'      : meta_type
         , 'description'    : """\
Un tissu est une resource variantable en couleur."""
         , 'icon'           : 'shop_product_icon.gif'
         , 'product'        : 'ERP5Shop'
         , 'factory'        : 'addShopOrder'
         , 'immediate_view' : 'shop_order_view'
         , 'allow_discussion'     : 1
         , 'allowed_content_types': ('File', 'Document', 'Image',
                                      )
         , 'filter_content_types' : 1
         , 'global_allow'   : 1
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'shop_order_view'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'list'
          , 'name'          : 'Object Contents'
          , 'category'      : 'object_action'
          , 'action'        : 'folder_contents'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'print'
          , 'name'          : 'Print'
          , 'category'      : 'object_print'
          , 'action'        : 'order_print'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'metadata'
          , 'name'          : 'Metadata'
          , 'category'      : 'object_view'
          , 'action'        : 'metadata_edit_form'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'translate'
          , 'name'          : 'Translate'
          , 'category'      : 'object_action'
          , 'action'        : 'translation_template_view'
          , 'permissions'   : (
              Permissions.TranslateContent, )
          }
        )
      }

    # Catalog related
    security.declareProtected( Permissions.View, 'Title')
    def Title(self):
        """
          Return a title
        """
        return 'Order %s' % self.id

    security.declareProtected(Permissions.View, 'Description')
    def Description(self):
        """
          Return a short description
        """
        return "%s\n%s" % (string.join(map(lambda x:str(x.getProductTitle()),
                                                self.listOrderLines()),'\n') ,
          string.join((self._name,
              self._organisation ,
              self._address ,
              self._zipcode ,
              self._city,
              self._country ,
              self._eu_vat )))

    security.declareProtected(Permissions.View, 'Description')
    def TranslatedTitle(self):
        """
          Return a translated title
        """
        return "%s %s" % (self.gettext('Order'), self.id)

    # Multiple Inheritance Resolving
    security.declareProtected(Permissions.ModifyPortalContent, 'edit')
    def edit(self, REQUEST=None, datadict=None, **kw):
      Delivery._edit(self, **kw)
      MMMShopOrder.edit(self, REQUEST=REQUEST, datadict=datadict)

    def _createOrderRule(self):
      # Do nothing
      return

    security.declareProtected(Permissions.ManageProperties, 'addProductToOrder')
    def addLineToOrder(self, title, description, price, quantity, producturl=None,
                                                                  variation_value=None):
      """
      Assigns a product and a quantity to the order
      """
      lineid = getUniqueID()
      line = OrderLine(lineid)
      self._setObject(lineid, line)
      lineobj = getattr(self, lineid)
      datadict = {      'title': title
                      , 'description': description
                      , 'price': price
                      , 'quantity': quantity
                      , 'product_url': producturl}
      lineobj.edit(datadict=datadict)
      if variation_value is not None: lineobj.setVariationValue(variation_value)
      return lineobj

    security.declarePublic('getOldTotalPrice')
    def getOldTotalPrice(self):
      """
      Get the total price for this order exc. VAT
      """
      all_price = self.send_fee
      for item in self.products:
        all_price = all_price + float(item.quantity) * item.price
      return all_price

    def hasEUTax(self):
      if self._country == 'France':
        return 1
      elif self.getEUVat() != '':
        return self._country != 'France'
      elif self._country in self.duty_free_countries:
        return 0
      return 1

    security.declarePublic('getTotalPriceVAT')
    def getTotalPriceVAT(self):
      """
      Get the total price for this order exc. VAT
      """
      return self.getTotalPrice() + self.getTax()

    def _online_payment(self):
      """
      This method is called by the bank
      to update order workflow
      """
      return 'toto'

    #security.declareProtected( Permissions.ModifyPortalContent, 'online_payment' )
    security.declarePublic( 'online_payment' )
    online_payment = WorkflowMethod(_online_payment,id='online_payment')

    # Overrriden methods
    security.declarePublic('listOrderLines')
    def listOrderLines(self):
        """
        List all products in this order
        """
        if hasattr(aq_base(self), 'products'):
          # Instance of previous MMMShop version
          products = self.listProducts()
          # Recreate order lines
          total_price = 0.0
          for item in products:
            product_url = item.getProduct()
            product = self.restrictedTraverse(product_url)
            variation_value=ComputerVariantValue(item.variant)
            total_price += product.getPrice(variation_value) * item.getQuantity()
            self.addLineToOrder('%s (%s)' % (product.getTitle() , variation_value.asString()),
                                product.getDescription(),
                                product.getPrice(variation_value),
                                item.getQuantity(),
                                producturl=product_url,
                                variation_value=variation_value)
          self._send_fee = self.send_fee
          total_price += self._send_fee
          self._total_price = self.total_price = total_price
          self._country = getattr(self, 'country', '')
          self._zipcode = getattr(self, 'zipcode', '')
          self._city = getattr(self, 'city', '')
          self._email = getattr(self, 'email', '')
          self._phone = getattr(self, 'phone', '')
          self._name = getattr(self, 'name', '')
          self._organisation = getattr(self, 'organisation', '')
          self._address = getattr(self, 'address', '')
          self._eu_vat = getattr(self, 'euvat', '')
          if self.hasEUTax():
            self._tax = self._total_price * 0.196
          del self.products
          LOG("Warning ERP5 Shop Order: old order converted",0,"Order %s" % str(self.id))
        # VariationValue(variant=item.variant)
        return self.objectValues(('MMM Shop Order Line', 'ERP5 Shop Order Line'))


# Compatibility dynamic patch
MMMShopOrder.hasEUTax = ShopOrder.hasEUTax
MMMShopOrder.listOrderLines = ShopOrder.listOrderLines
MMMShopOrder.addLineToOrder = ShopOrder.addLineToOrder

class ComputerVariantValue(VariationValue):
  def __init__(self, variant):
    self.variant = variant

  def setVariationValue(self, context):
    context.variant = self.variant

  def __cmp__(self, other):
    if not hasattr(other, 'variant'): return 1
    return cmp(list(self.variant), list(other.variant))

  def asString(self):
    result = ""
    for i in self.variant[0:4]:
      if i != '':
        result += "%s / " % i
    for i in self.variant[4]:
      if i != '':
        result += "%s / " % i
    for i in self.variant[5:]:
      if i != '':
        result += "%s / " % i
    return result
