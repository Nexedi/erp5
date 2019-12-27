##############################################################################
#
# Copyright (c) 2008 Nexedi SA and Contributors. All Rights Reserved.
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
# Foundation, Inc., 51 Franklin Street - Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

from erp5.component.document.MovementGroup import MovementGroup

class RootAppliedRuleCausalityMovementGroup(MovementGroup):
  """
  The purpose of MovementGroup is to define how movements are grouped,
  and how values are updated from simulation movements.

  This movement group is used to group movements whose root apply rule
  has the same causality.
  """
  meta_type = 'ERP5 Root Applied Rule Causality Movement Group'
  portal_type = 'Root Applied Rule Causality Movement Group'

  def _getPropertyDict(self, movement, **kw):
    property_dict = {}
    root_causality_value = self._getRootCausalityValue(movement)
    property_dict['root_causality_value_list'] = [root_causality_value]
    return property_dict

  def test(self, movement, property_dict, **kw):
    # We can always update
    return True, property_dict

  def _getRootCausalityValue(self, movement):
    """ Get the causality value of the root applied rule for a movement """
    return movement.getRootAppliedRule().getCausalityValue()
