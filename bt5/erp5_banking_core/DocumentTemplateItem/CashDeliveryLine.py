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

from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5.Document.DeliveryLine import DeliveryLine

in_portal_type_list = ('Cash Exchange Line In', 'Cash To Currency Sale Line In','Cash To Currency Purchase Line In', 'Cash Incident Line In')
out_portal_type_list = ('Cash Exchange Line Out', 'Cash To Currency Sale Line Out','Cash To Currency Purchase Line Out','Cash Incident Line Out')


class CashDeliveryLine(DeliveryLine):
    """
      A Cash DeliveryLine object allows to implement lines in
      Cash Deliveries (packing list, Check payment, Cash Movement, etc.)

      It may include a price (for insurance, for customs, for invoices,
      for orders)
    """

    meta_type = 'BAOBAB Cash Delivery Line'
    portal_type = 'Cash Delivery Line'
    add_permission = Permissions.AddPortalContent
    isPortalContent = 1
    isRADContent = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.View)

    # Declarative interfaces
    __implements__ = ( Interface.Variated, )

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.Amount
                      , PropertySheet.Task
                      , PropertySheet.Arrow
                      , PropertySheet.Movement
                      , PropertySheet.Price
                      , PropertySheet.VariationRange
                      , PropertySheet.ItemAggregation
                      , PropertySheet.CashDeliveryLine
                      )

    security.declareProtected(Permissions.View, 'getBaobabSourceSectionUid')
    def getBaobabSourceSectionUid(self):
        """
            Returns a calculated source section
        """
        LOG("KevClasses>> Cash Delivery Line >>> getBaobabSourceSectionUid ",0,repr(self))
        return self.getSourceSectionUid()

    security.declareProtected(Permissions.View, 'getBaobabDestinationSectionUid')
    def getBaobabDestinationSectionUid(self):
        """
            Returns a calculated destination section
        """
        LOG("KevClasses>> Cash Delivery Line >>> getBaobabDestinationSectionUid ",0,repr(self))
        return self.getDestinationSectionUid()

    security.declareProtected(Permissions.View, 'getBaobabSource')
    def getBaobabSource(self):
        """
            Returns a calculated source
        """
        LOG("KevClasses>> Cash Delivery Line >>> getBaobabSource ",0,repr(self))
        if self.portal_type in out_portal_type_list:
          return self.portal_categories.resolveCategory(self.getSource()).unrestrictedTraverse('sortante').getRelativeUrl()
        elif self.portal_type in in_portal_type_list:
          return None
        return self.getSource()

    security.declareProtected(Permissions.View, 'getBaobabSourceUid')
    def getBaobabSourceUid(self):
        """
            Returns a calculated source
        """
        LOG("KevClasses>> Cash Delivery Line  >>> getBaobabSourceUid ",0,repr(self))
        if self.portal_type in out_portal_type_list:
          return self.portal_categories.resolveCategory(self.getSource()).unrestrictedTraverse('sortante').getUid()
        elif self.portal_type in in_portal_type_list:
          return None
        return self.getSourceUid()

    security.declareProtected(Permissions.View, 'getBaobabDestinationUid')
    def getBaobabDestinationUid(self):
        """
            Returns a calculated destination
        """
        LOG("KevClasses>> Cash Delivery Line >>> getBaobabDestinationUid ",0,repr(self))
        if self.portal_type in in_portal_type_list:
          return self.portal_categories.resolveCategory(self.getSource()).unrestrictedTraverse('entrante').getUid()
        elif self.portal_type in out_portal_type_list :
          return None
        return self.getDestinationUid()

