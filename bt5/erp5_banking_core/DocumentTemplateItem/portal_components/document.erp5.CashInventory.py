##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Aurelien Calonne <aurel@nexedi.com>
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
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5.Document.Inventory import Inventory
from erp5.component.document.BankingOperation import BankingOperation


class CashInventory(Inventory, BankingOperation):
    """
      A Cash Inventory
    """
    # CMF Type Definition
    meta_type = 'ERP5Banking Cash Inventory'
    portal_type = 'Cash Inventory'

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    # Default Properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      , PropertySheet.Task
                      , PropertySheet.Arrow
                      , PropertySheet.Movement
                      , PropertySheet.Delivery
                      , PropertySheet.Path
                      , PropertySheet.FlowCapacity
                      )

    security.declarePublic('immediateReindexObject')
    def immediateReindexObject(self, **kw):
      """Call the Cash Inventory immediateReindexObject by
      setting another kind of temp delivery line.
      """
      def newTempCashDeliveryLine(self, inventory_id):
        return self.getPortalObject().portal_trash.newContent(
          portal_type='Cash Delivery Line',
          temp_object=True,
          id=inventory_id)
      return Inventory.immediateReindexObject(self,
                           temp_constructor=newTempCashDeliveryLine,**kw)

