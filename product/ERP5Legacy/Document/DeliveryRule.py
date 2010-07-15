##############################################################################
#
# Copyright (c) 2002 - 2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#                    Romain Courteaud <romain@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
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
from Products.ERP5Type import Permissions
from Products.ERP5Legacy.Document.Rule import Rule
from zLOG import LOG, WARNING

class DeliveryRule(Rule):
  """
    Delivery Rule object make sure orphaned movements in a Delivery
    (ie. movements which have no explanation in terms of order)
    are part of the simulation process
  """

  # CMF Type Definition
  meta_type = 'ERP5 Delivery Rule'
  portal_type = 'Delivery Rule'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Simulation workflow
  security.declareProtected(Permissions.ModifyPortalContent, 'expand')
  def expand(self, applied_rule, delivery_movement_type_list=None, **kw):
    """
    Expands the additional Delivery movements to a new simulation tree.
    Expand is only allowed to create or modify simulation movements for
    delivery lines which are not already linked to another simulation
    movement.

    If the movement is not in current state, has no delivered child, and not
    in delivery movements, it can be deleted.
    Else if the movement is not in current state, it can be modified.
    Else, it cannot be modified.
    """
    return Rule._expand(self, applied_rule, **kw)

  security.declareProtected(Permissions.ModifyPortalContent, 'solve')
  def solve(self, applied_rule, solution_list):
    """
      Solve inconsistency according to a certain number of solutions
      templates. This updates the

      -> new status -> solved

      This applies a solution to an applied rule. Once
      the solution is applied, the parent movement is checked.
      If it does not diverge, the rule is reexpanded. If not,
      diverge is called on the parent movement.
    """

  security.declareProtected(Permissions.ModifyPortalContent, 'diverge')
  def diverge(self, applied_rule):
    """
      -> new status -> diverged

      This basically sets the rule to "diverged"
      and blocks expansion process
    """

  # Solvers
  security.declareProtected(Permissions.AccessContentsInformation, 'isStable')
  def isStable(self, applied_rule):
    """
    Checks that the applied_rule is stable
    """
    return 0

  # Deliverability / orderability
  def isOrderable(self, movement):
    return 1

  def isDeliverable(self, movement):
    if movement.getSimulationState() in movement.getPortalDraftOrderStateList():
      return 0
    return 1

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
      LOG("Delivery Rule , getExpandablePropertyList", WARNING,
                 "Hardcoded properties set, please define your rule correctly")
      property_list = (
        'aggregate_list',
        'base_application_list',
        'base_contribution_list',
        'description',
        'destination',
        'destination_account',
        'destination_administration',
        'destination_decision',
        'destination_function',
        'destination_payment',
        'destination_project',
        'destination_section',
        'price',
        'price_currency',
        'quantity',
        'quantity_unit',
        'resource',
        'source',
        'source_account',
        'source_administration',
        'source_decision',
        'source_function',
        'source_payment',
        'source_project',
        'source_section',
        'start_date',
        'stop_date',
        'variation_category_list',
        'variation_property_dict',
      )
    return property_list

  def _getExpandablePropertyUpdateDict(self, applied_rule, movement,
      business_path, current_property_dict):
    """Delivery specific update dict"""
    # 'order' category is deprecated. it is kept for compatibility.
    return {
      'order': movement.getRelativeUrl(),
      'delivery': movement.getRelativeUrl(),
    }

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
      LOG("Delivery Rule , getMatchingPropertyList", WARNING,
          "Hardcoded properties set, please define your rule correctly")
      property_list=['delivery',]
    return property_list
