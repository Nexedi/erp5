##############################################################################
#
# Copyright (c) 2002, 2005 Nexedi SARL and Contributors. All Rights Reserved.
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

from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5.Document.Rule import Rule
from Products.ERP5.Document.DeliveryRule import DeliveryRule

class TaxRule(DeliveryRule):
  """
  """
  # CMF Type Definition
  meta_type = 'ERP5 Tax Rule'
  portal_type = 'Tax Rule'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)
  
  __implements__ = ( Interface.Predicate,
                     Interface.Rule )

  # Default Properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Task
                    )

  security.declareProtected(Permissions.ModifyPortalContent, 'expand')
  def expand(self, applied_rule, force=0, **kw):
    """ """ 
    movement_type = 'Simulation Movement'
    immutable_movement_list = []

    parent_simulation_movement = applied_rule.getParentValue()
    order_movement = parent_simulation_movement.getDefaultOrderValue()
    
    order_movement_dict = {}
    for s_m in applied_rule.objectValues():
      order_movement_dict.setdefault(s_m.getOrder(), []).append(s_m)

    order_movement_total_price = order_movement.getTotalPrice()
    parent_simulation_movement_total_price = \
                    parent_simulation_movement.getTotalPrice()

    # XXX round 
    if order_movement_total_price != 0 and \
        parent_simulation_movement_total_price != 0:
                      
      ratio = parent_simulation_movement_total_price / \
                           order_movement_total_price
      for tax_movement in order_movement\
                        .DeliveryMovement_getCorrespondingTaxLineList():
        existing_simulation_movement_list = order_movement_dict.get(
                                tax_movement.getRelativeUrl(), [])

        property_dict = dict()
        for prop in ('price', 'base_application_list',
                     'price_currency', 'payment_mode',
                     'base_contribution_list', 'resource'):
          property_dict[prop] = tax_movement.getProperty(prop)

        property_dict['quantity'] = tax_movement.getQuantity() * ratio

        if not existing_simulation_movement_list:
          applied_rule.newContent(
                portal_type=movement_type,
                order_value=tax_movement,
                order_ratio=1,
                delivery_ratio=1,
                deliverable=1,
                **property_dict )
        else:
          for existing_simulation_movement in \
                existing_simulation_movement_list:
            if existing_simulation_movement.getDelivery() is None:
              existing_simulation_movement.edit(**property_dict)

    # Pass to base class
    Rule.expand(self, applied_rule, force=force, **kw)

