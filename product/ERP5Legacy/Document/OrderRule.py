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
from Products.ERP5Type import Permissions, PropertySheet, Constraint, interfaces
from Products.ERP5Legacy.Document.Rule import Rule
from Products.ERP5Legacy.Document.DeliveryRule import DeliveryRule
from zLOG import LOG, WARNING

class OrderRule(DeliveryRule):
  """
  Order Rule object make sure an Order in the simulation
  is consistent with the real order

  WARNING: what to do with movement split ?
  """
  # CMF Type Definition
  meta_type = 'ERP5 Order Rule'
  portal_type = 'Order Rule'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'isAccountable')
  def isAccountable(self, movement):
    """
    Tells whether generated movement needs to be accounted or not.

    Order movement are never accountable, so simulation movement for
    order movements should not be accountable either.
    """
    return 0

  # Simulation workflow
  security.declareProtected(Permissions.ModifyPortalContent, 'expand')
  def expand(self, applied_rule, force=0, **kw):
    """
      Expands the Order to a new simulation tree.
      expand is only allowed to modify a simulation movement if it doesn't
      have a delivery relation yet.

      If the movement is in ordered or planned state, has no delivered
      child, and is not in order, it can be deleted.
      Else, if the movement is in ordered or planned state, has no
      delivered child, and is in order, it can be modified.
      Else, it cannot be modified.
    """
    return Rule._expand(self, applied_rule, force=force, **kw)

  security.declareProtected(Permissions.AccessContentsInformation, 'isStable')
  def isStable(self, applied_rule):
    """
    Checks that the applied_rule is stable
    """
    LOG('OrderRule.isStable', WARNING, 'Not Implemented')
    return 1

  security.declareProtected(Permissions.AccessContentsInformation,
                            'isDivergent')
  def isDivergent(self, movement):
    """
    Checks that the movement is divergent
    """
    return Rule.isDivergent(self, movement)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getExpandablePropertyList')
  def getExpandablePropertyList(self, default=None):
    """
    Return a list of properties used in expand.
    """
    property_list = self._baseGetExpandablePropertyList()
    # For backward compatibility, we keep for some time the list
    # of hardcoded properties. Theses properties should now be
    # defined on the rule itself
    if len(property_list) == 0:
      LOG("Order Rule , getExpandablePropertyList", WARNING,
                 "Hardcoded properties set, please define your rule correctly")
      property_list = (
        'aggregate_list',
        'base_contribution_list',
        'description',
        'destination',
        'destination_account',
        'destination_function',
        'destination_section',
        'price',
        'price_currency',
        'quantity',
        'quantity_unit',
        'resource',
        'source',
        'source_account',
        'source_function',
        'source_section',
        'start_date',
        'stop_date',
        'variation_category_list',
        'variation_property_dict',
      )
    return property_list

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getMatchingPropertyList')
  def getMatchingPropertyList(self, default=None):
    """
    Return a list of properties used in expand.
    """
    property_list = self._baseGetMatchingPropertyList()
    # For backward compatibility, we keep for some time the list
    # of hardcoded properties. Theses properties should now be
    # defined on the rule itself
    if len(property_list) == 0:
      LOG("Order Rule , getMatchingPropertyList", WARNING,
          "Hardcoded properties set, please define your rule correctly")
      property_list=['order',]
    return property_list

  def _getInputMovementList(self, applied_rule):
    """Input movement list comes from order"""
    order = applied_rule.getDefaultCausalityValue()
    if order is not None:
      return order.getMovementList(
                     portal_type=order.getPortalOrderMovementTypeList())
    return []

  def _getExpandablePropertyUpdateDict(self, applied_rule, movement,
      business_path, current_property_dict):
    """Order rule specific update dictionary"""
    return {
      'order': movement.getRelativeUrl(),
    }
