##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solane <jp@nexedi.com>
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

try:
    from Interface import Interface
except ImportError:
    # for Zope versions before 2.6.0
    from Interface import Base as Interface

class ShopOrder(Interface):
    """
        Common Interface for all ERP5 ShopProduct objects
        This is where we define the common interface between MMMShop and ERP5
    """

    def edit(self):
        """
            Change the product parameters (price, options, etc.)
        """
        pass

    def addLineToOrder(self, title, description, price, quantity, producturl=None):
        """
        Assigns a product and a quantity to the order
        """
        pass

    def delOrderLine(self, id):
        """
        Delete a product from the order
        """
        pass


    def listOrderLines(self):
        """
        List all products in this order
        """
        pass



