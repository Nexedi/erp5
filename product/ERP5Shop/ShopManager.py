##############################################################################
#    Copyright (C) 2001  MMmanager.org
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
##############################################################################
"""
"""

ADD_CONTENT_PERMISSION = 'Add portal content'

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass, package_home

from Products.MMMShop.ShopManager import ShopManager as MMMShopManager
from Products.MMMShop import ShopPermissions
from Products.MMMShop.MMMShopGlobals import order_meta_types

class ShopManager(MMMShopManager):

    """
        A ShopManager tool
    """

    id = 'portal_shop_manager'
    meta_type='ERP5 Shop Manager'
    security = ClassSecurityInfo()

    security.declarePublic('getMemberOrders')
    def getMemberOrders(self):
        """
        Returns a list containing all the logged-in members orders
        """
        orders = []
        cart = self.getMemberCart()
        if cart:
            orders = cart.objectValues(order_meta_types)
            orders += cart.aq_parent.objectValues(order_meta_types)
        return orders

InitializeClass(ShopManager)
