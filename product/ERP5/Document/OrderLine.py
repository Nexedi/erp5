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

from Globals import InitializeClass, PersistentMapping
from AccessControl import ClassSecurityInfo

from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5.Document.DeliveryLine import DeliveryLine
from Products.ERP5.Document.Movement import Movement

class OrderLine(DeliveryLine):
    """
      A order line defines quantity and price
    """

    meta_type = 'ERP5 Order Line'
    portal_type = 'Order Line'

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.View)

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.Amount
                      , PropertySheet.Task
                      , PropertySheet.DublinCore
                      , PropertySheet.Arrow
                      , PropertySheet.Movement
                      , PropertySheet.Price
                      , PropertySheet.VariationRange
                      )

    # Declarative interfaces
    __implements__ = ( Interface.Variated, )

    security.declarePrivate( '_edit' )
    def _edit(self, REQUEST=None, force_update = 0, **kw):
      DeliveryLine._edit(self, REQUEST=REQUEST, force_update = force_update, **kw)
      # We must expand our applied rule if needed
      self.updateAppliedRule() # Actually called on parent

#     security.declarePrivate('_checkConsistency')
#     def _checkConsistency(self, fixit=0, mapped_value_property_list = ('quantity', 'price')):
#       """
#         Check the constitency of transformation elements
#       """
#       return DeliveryLine._checkConsistency(self, fixit=fixit, mapped_value_property_list=mapped_value_property_list)
# 
    def applyToOrderLineRelatedMovement(self, portal_type='Simulation Movement', method_id = 'expand'):
      """
        Warning: does not work if it was not catalogued immediately
      """
      # Find related in simulation
      for my_simulation_movement in self.getOrderRelatedValueList(
                                              portal_type = 'Simulation Movement'):
        # And apply
        getattr(my_simulation_movement, method_id)()
      for c in self.contentValues(filter={'portal_type': 'Delivery Cell'}):
        for my_simulation_movement in c.getOrderRelatedValueList(
                                              portal_type = 'Simulation Movement'):
          # And apply
          getattr(my_simulation_movement, method_id)()

    def reindexObject(self, *k, **kw):
      """
        Reindex children and simulation
      """
      self.recursiveReindexObject()
      #self.activate().applyToOrderLineRelatedMovement(method_id = 'expand')
      # We do it at Order level through edit
      # This logic should actually be put in worklow

    # Simulation Consistency Check
    def getSimulationQuantity(self):
      """
          Computes the target quantities in the simulation
      """
      result = self.OrderLine_zGetRelatedQuantity(uid=self.getUid())
      if len(result) > 0:
        return result[0].quantity
      return None

