##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
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
from Products.ERP5Type import Permissions, PropertySheet, Constraint, interfaces
from Products.ERP5.Document.Rule import Rule
from Products.ERP5.Document.OrderRule import OrderRule
from Products.ERP5.Document.TransformationSourcingRule import\
                                            TransformationSourcingRuleMixin

from zLOG import LOG, WARNING

class ProductionOrderRule(OrderRule):
    """
      Prouction Order Rule object use a Supply Chain to expand a 
      Production Order.
    """

    # CMF Type Definition
    meta_type = 'ERP5 Production Order Rule'
    portal_type = 'Production Order Rule'

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    __implements = ( interfaces.IPredicate,
                     interfaces.IRule )

    # Simulation workflow
    security.declareProtected(Permissions.AccessContentsInformation,
                              '_getExpandablePropertyDict')
    def _getExpandablePropertyDict(self, applied_rule, movement, business_path=None,
                                   **kw):
      """
      Return a Dictionary with the Properties used to edit 
      the simulation movement.
      """
      property_dict = {}

      default_property_list = self.getExpandablePropertyList()
      # For backward compatibility, we keep for some time the list
      # of hardcoded properties. Theses properties should now be
      # defined on the rule itself
      if len(default_property_list) == 0:
        LOG("Production Order Rule , _getExpandablePropertyDict", WARNING,
                   "Hardcoded properties set, please define your rule correctly")
        default_property_list = (
          'aggregate_list',
          'destination', 
          'destination_section',
          'price', 
          'price_currency',
          'quantity', 
          'quantity_unit', 
          'resource', 
          'start_date', 
          'stop_date',
          'variation_category_list',
          'variation_property_dict', 
        )
    
      supply_chain = self.getSupplyChain(applied_rule)
      # We got a supply chain
      # Try to get the last SupplyLink
      last_link = supply_chain.getLastLink()
      # We got a valid industrial_phase
      # Now, we have to generate Simulation Movement, in order to
      # create a ProductionPackingList.
      destination_node = last_link.getDestinationValue()
      source = destination_node.getDestination()
      source_section = last_link.getDestinationSection()
      if source is not None:
        property_dict['source'] = source
      if source_section is not None:
        property_dict['source_section'] = source_section
    
      for prop in default_property_list:
        property_dict[prop] = movement.getProperty(prop)
    
      # rule specific
      property_dict.update(**self._getExpandablePropertyUpdateDict(applied_rule,
        movement, business_path, property_dict))

      return property_dict

from Products.ERP5Type.Utils import monkeyPatch
monkeyPatch(TransformationSourcingRuleMixin, ProductionOrderRule)
