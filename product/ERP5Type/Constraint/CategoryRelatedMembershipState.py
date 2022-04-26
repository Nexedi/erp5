# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Sebastien Robin <seb@nexedi.com>
#                    Courteaud Romain <romain@nexedi.com>
#                    Nicolas Delaby <nicolas@nexedi.com>
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

from Products.ERP5Type.Constraint.CategoryMembershipState \
          import CategoryMembershipState

class CategoryRelatedMembershipState(CategoryMembershipState):
  """
    This method checks if an object respects the arity from a category reverse
    membership point of view and is in a valid workflow state.

    For example we can check if every Order has at
    most one Order Applied Rule in expected simulation_states.
    Configuration example:
    { 'id'            : 'applied_rule',
      'description'   : 'There must at most one Applied Rule using this order',
      'type'          : 'CategoryRelatedMembershipArityState',
      'portal_type'   : ('Applied Rule', ),
      'base_category' : ('causality',)
      'simulation_state': ('planned', ),
      'message_different_state': 'Applied Rule must be planned',
      'condition'     : 'python: object.getPortalType() == 'Foo',
    },
  """

  def _checkConsistency(self, obj, fixit=0):
    """Check the object's consistency.
    """
    error_list = []
    # Retrieve values inside de PropertySheet (_constraints)
    base_category = self.constraint_definition['base_category']
    portal_type = self.constraint_definition['portal_type']
    related_membership_list = obj._getRelatedValueList(base_category,
                                       portal_type=portal_type)
    state_var_list = self.constraint_definition.copy()
    state_var_list.pop('portal_type')
    state_var_list.pop('base_category')

    for workflow_variable, valid_state_list in list(state_var_list.items()):
      for related_membership in related_membership_list:
        current_state = related_membership.getProperty(workflow_variable)
        if current_state not in valid_state_list:
          mapping = dict(workflow_variable=workflow_variable,
                         membership_url=related_membership.getRelativeUrl(),
                         current_state=current_state,
                         valid_state_list=str(valid_state_list),)
          message_id = 'message_different_state'

          # Add error
          error_list.append(self._generateError(obj,
                                  self._getMessage(message_id), mapping))

    return error_list

