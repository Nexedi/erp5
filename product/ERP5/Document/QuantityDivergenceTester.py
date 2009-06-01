##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Rafael M. Monnerat <rafael@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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

from Products.ERP5Type.DivergenceMessage import DivergenceMessage
from Products.ERP5Type import Permissions, PropertySheet, Constraint, interfaces
from Products.ERP5.Document.PropertyDivergenceTester import \
                                              PropertyDivergenceTester

class QuantityDivergenceTester(PropertyDivergenceTester):
  """
  The purpose of this divergence tester is to check the
  consistency between delivery movement and simulation movement
  for the property quantity.
  """
  meta_type = 'ERP5 Quantity Divergence Tester'
  portal_type = 'Quantity Divergence Tester'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative interfaces
  __implements__ = ( interfaces.IDivergenceTester, )


  # Declarative properties
  property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      , PropertySheet.DivergenceTester
                      , PropertySheet.DecimalOption
                     )

  def explain(self, simulation_movement):
    """
    This method returns a list of messages that contains
    the divergence of the Delivery Line.
    """
    delivery = simulation_movement.getDeliveryValue()

    d_quantity = delivery.getQuantity()
    quantity = simulation_movement.getCorrectedQuantity()

    extra_parameters = dict()
    if abs(quantity - d_quantity) < 1:
     # if the difference between quantities are small, use repr to have more
     # precise float display in the divergence message.
     extra_parameters = dict(
         decision_title=repr(d_quantity),
         prevision_title=repr(quantity),)

    message = DivergenceMessage(object_relative_url= delivery.getRelativeUrl(),
                 divergence_scope='quantity',
                 simulation_movement = simulation_movement,
                 decision_value = d_quantity ,
                 prevision_value = quantity,
                 tested_property='quantity',
                 message='Quantity',
                 **extra_parameters
                 )


    if quantity is None:
      if d_quantity is None:
        return []
      return [message]
    if d_quantity is None:
      d_quantity = 0
    delivery_ratio = simulation_movement.getDeliveryRatio()
    # if the delivery_ratio is None, make sure that we are
    # divergent even if the delivery quantity is 0
    if delivery_ratio is not None:
      d_quantity *= delivery_ratio
      message.decision_value = d_quantity
      message.decision_title = repr(d_quantity)
      if delivery_ratio == 0 and quantity > 0:
        return [message]

    if not self.compare(d_quantity, quantity):
      return [message]
    return []

  def compare(self, x, y):
    if self.isDecimalAlignmentEnabled():
      from decimal import (Decimal, ROUND_DOWN, ROUND_UP, ROUND_CEILING,
                           ROUND_FLOOR, ROUND_HALF_DOWN, ROUND_HALF_EVEN,
                           ROUND_HALF_UP)
      # Python2.4 did not support ROUND_05UP yet.
      rounding_option_dict = {'ROUND_DOWN':ROUND_DOWN,
                              'ROUND_UP':ROUND_UP,
                              'ROUND_CEILING':ROUND_CEILING,
                              'ROUND_FLOOR':ROUND_FLOOR,
                              'ROUND_HALF_DOWN':ROUND_HALF_DOWN,
                              'ROUND_HALF_EVEN':ROUND_HALF_EVEN,
                              'ROUND_HALF_UP':ROUND_HALF_UP}
      rounding_option = rounding_option_dict.get(self.getDecimalRoundingOption(),
                                                 ROUND_DOWN)
      
      return (Decimal(str(x)).quantize(Decimal(self.getDecimalExponent()),
                                       rounding=rounding_option)
              ==
              Decimal(str(y)).quantize(Decimal(self.getDecimalExponent()),
                                       rounding=rounding_option))
    else:
      return x==y
