##############################################################################
#
# Copyright (c) 2002, 2004 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#                    Romain Courteaud <romain@nexedi.com>
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

from Products.ERP5Type.Globals import InitializeClass, PersistentMapping
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base

from Products.ERP5Type import Permissions, PropertySheet, Constraint, interfaces
from Products.ERP5Type.Base import Base

from Products.ERP5.Document.DeliveryCell import DeliveryCell

from zLOG import LOG

class OrderCell(DeliveryCell):
    """
      A OrderCell allows to define specific quantities
      for each variation of a resource in a delivery line.
    """

    meta_type = 'ERP5 Order Cell'
    portal_type = 'Order Cell'
    isCell = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.CategoryCore
                      , PropertySheet.Arrow
                      , PropertySheet.Amount
                      , PropertySheet.Task
                      , PropertySheet.Movement
                      , PropertySheet.Price
                      , PropertySheet.Predicate
                      , PropertySheet.MappedValue
                      , PropertySheet.ItemAggregation
                      )

    def reindexObject(self, *k, **kw):
      """
      Reindex children and simulation
      """
      self.recursiveReindexObject(*k,**kw)

    security.declareProtected(Permissions.AccessContentsInformation,
        'isMovement')
    def isMovement(self):
      """
      should be considered as a movement if the parent does not have sub lines
      """
      return not self.getParentValue().hasLineContent()

    security.declareProtected(Permissions.AccessContentsInformation,
        'getTotalPrice')
    def getTotalPrice(self, default=0.0, *args, **kw):
      "only return a value if self is a movement"
      if not self.isMovement():
        return default
      return DeliveryCell.getTotalPrice(self, default=default, *args, **kw)

    security.declareProtected(Permissions.AccessContentsInformation,
        'getTotalQuantity')
    def getTotalQuantity(self, default=0.0, *args, **kw):
      "only return a value if self is a movement"
      if not self.isMovement():
        return default
      return DeliveryCell.getTotalQuantity(self, default=default, *args, **kw)

