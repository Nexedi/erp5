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

import string
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName, _getAuthenticatedUser

from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5.Document.OrderLine import OrderLine as ERP5OrderLine
from Products.ERP5.Document.Amount import Amount

from Products.MMMShop.ShoppingCart import ShoppingCart as MMMShoppingCart
from Products.MMMShop.ShoppingCart import CartObject as MMMCartObject
from Products.MMMShop import ShopPermissions
from Products.MMMShop.utils import getUniqueID

from Products.Base18.Base18 import Base18

import zLOG

class CartObject(MMMCartObject, ERP5OrderLine):

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.View)

    def getVariationValue(self):
        product = self.getProduct()
        return product.newVariationValue(context=self)

    security.declareProtected(Permissions.View, 'getExchangedPrice')
    def getExchangedPrice(self):
        product = self.getProduct()
        price = product.getExchangedPrice(context=self)
        return price

    _setVariationCategoryList = Amount._setVariationCategoryList


class ShoppingCart(MMMShoppingCart, Base18):

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.View)

    title = "Shopping Cart"

    security.declareProtected(Permissions.View, 'getTitle')
    def getTitle():
      return self.title

    security.declareProtected(ShopPermissions.CheckoutShoppingCart, 'addProductToCart')
    def addProductToCart( self, prod_path, prod_title, quantity, delivery_days,
                                mail_receive=None, variation_value=None):
        """
        Assigns a Product and a Quantity to the ShoppingCart
        """
        zLOG.LOG('Shopping Cart', zLOG.INFO, 'Called add to cart')
        for item in self.listProducts():
            zLOG.LOG('Item', zLOG.INFO, str(( item.getProductPath(),prod_path,
                                             variation_value.__dict__,
                                             item.getVariationValue().__dict__)))
            if item.getProductPath() == prod_path:
              zLOG.LOG('Item', 0, 'same path')
              if variation_value is None or item.getVariationValue() is None:
                item.edit(datadict = {'quantity': item.getQuantity() + int(quantity),})
                return
              elif variation_value == item.getVariationValue():
                item.edit(datadict = {'quantity': item.getQuantity() + int(quantity),})
                return

        prod_id = getUniqueID()
        prod = CartObject(prod_id)
        self._setObject(prod_id, prod)
        cartobj = getattr(self, prod_id)
        zLOG.LOG('Shopping Cart', zLOG.INFO, 'Receive by mail? %s' % str(mail_receive))
        datadict = {      'product_path': prod_path
                        , 'title': prod_title
                        , 'quantity': quantity
                        , 'delivery_days': delivery_days
                        , 'mail_receive': mail_receive}
        cartobj.edit(datadict=datadict)
        cartobj.setResource(prod_path)
        if variation_value is not None: cartobj.setVariationValue(variation_value)

    security.declareProtected(ShopPermissions.CheckoutShoppingCart, 'clearCart')
    def clearCart(self, REQUEST=None):
        """
        Empty the cart for all cart objects
        """
        for item in self.listProducts():
            itemid = item.id
            self.manage_delObjects(itemid)
        if REQUEST is not None:
            msg = 'Cart is empty'
            REQUEST.RESPONSE.redirect('%s/view?portal_status_message=%s' % (self.secure_absolute_url(),
                 msg.replace(' ', '+')))

    security.declareProtected(Permissions.ManageProperties, 'edit')
    def edit(self, REQUEST):
        """
        Edit the items in the cart (quantity)
        """
        req = REQUEST
        items = self.listProducts()
        for item in items:
            reqvar = "%s_quantity" % item.id
            if req.has_key(reqvar):
                data = {'quantity': req.get(reqvar)}
                item.edit(datadict=data)
        msg = 'Updated cart'
        req.RESPONSE.redirect("%s/view?portal_status_message=%s" % (self.secure_absolute_url(),
                      msg.replace(' ', '+')))

    security.declareProtected(ShopPermissions.CheckoutShoppingCart,'setPaymentData')
    def setPaymentData(self, REQUEST):
        """
        Save the entered personal data for the payment method
        """
        zLOG.LOG('Shopping cart - set payment', zLOG.INFO, 'setPaymentData called')
        req = REQUEST
        shopmanager = getToolByName(self, 'portal_shop_manager')
        paymentdata = self._paymentdata
        paymentid = req.get('paymentmethod_id', None)
        savedata = {}
        msg = 'Saved payment data'
        returnview = 'checkout'

        if paymentid is None:
            msg = 'No payment method selected'
            returnview = 'prepareOrder'
            zLOG.LOG('Shopping cart - set payment', zLOG.INFO, 'paymentid is None')
        else:
            zLOG.LOG('Shopping cart - set payment', zLOG.INFO, 'paymentid is NOT None')
            payment = shopmanager.getPaymentMethod(paymentid)
            paymentstructure = payment.getPaymentStructure()
            zLOG.LOG('Shopping cart - set payment', zLOG.INFO, 'Payment structure is:\n%s' %
                                  str(paymentstructure))
            propmsg = ''
            properror = 0
            for property in paymentstructure:
                propid = property['id']
                userdef = property['user_defined']
                validationinfo = property['validation_info']
                isRequired = property['isRequired']
                if isRequired and userdef and not validationinfo:
                    if not req.has_key(propid) or req[propid] == '':
                        if not propmsg:
                            propmsg = 'Missing input for %s' % property['title']
                        else:
                            propmsg = "%s, %s" % (propmsg, property['title'])
                        properror = 1
                if req.has_key(propid) and userdef and not validationinfo:
                    savedata[propid] = req.get(propid)
            if propmsg:
                msg = propmsg
            zLOG.LOG('Shopping cart - set payment', zLOG.INFO, 'Msg is: %s' % msg)
            if properror:
                returnview = 'prepareOrder'
            if shopmanager.isDeliveryNeeded():
                if req.has_key('delivery_fee'):
                    savedata['delivery_fee'] = req.get('delivery_fee')
                    delivery_error = 0
                else:
                    delivery_error = 1
                    msg = "%s. You have not selected any delivery method'" % msg
                if delivery_error:
                    returnview = 'prepareOrder'
            paymentdata[paymentid] = savedata
            self._paymentdata = paymentdata
            self._p_changed = 1
            self._last_used_payment = paymentid
        zLOG.LOG('Shopping cart - set payment', zLOG.INFO, 'Return view is %s and msg is %s' %
                  (returnview, msg))
        req.RESPONSE.redirect("%s/%s?payment_method=%s&portal_status_message=%s" %
              (self.secure_absolute_url(), returnview, paymentid, msg.replace(' ', '+')))

MMMShoppingCart.addProductToCart = ShoppingCart.addProductToCart
MMMShoppingCart.clearCart = ShoppingCart.clearCart
MMMShoppingCart.edit = ShoppingCart.edit
MMMShoppingCart.setPaymentData = ShoppingCart.setPaymentData
MMMShoppingCart.getTitle = ShoppingCart.getTitle
