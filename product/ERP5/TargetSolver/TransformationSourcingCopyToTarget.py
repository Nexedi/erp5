from __future__ import absolute_import
##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
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

from .CopyToTarget import CopyToTarget

class TransformationSourcingCopyToTarget(CopyToTarget):
  """
    Copy values simulation movement as target, and
    recursively solve the sourcing tree.
  """
  def _generateValueDeltaDict(self, simulation_movement):
    """
      Get interesting value
    """
    value_dict = CopyToTarget._generateValueDict(self, simulation_movement)
    value_dict.update({
      'aggregate_list':
        simulation_movement.getDeliveryValue().getAggregateList(),
    })
    return value_dict

  def _generateValueDict(self, simulation_movement, aggregate_list = None,
                         **value_delta_dict):
    """
      Generate values to save on movement.
    """
    value_dict = CopyToTarget._generateValueDict(self, simulation_movement,
                                                 **value_delta_dict)
    # Modify aggregate_list
    if aggregate_list is not None:
      value_dict['aggregate_list'] = aggregate_list
    return value_dict

  def _getParentParameters(self, simulation_movement,
                           **value_delta_dict):
    """
      Get parent movement, and its value delta dict.
    """
    applied_rule = simulation_movement.getParentValue()
    rule = applied_rule.getSpecialiseValue()
    if rule.getPortalType() != "Transformation Sourcing Rule":
      value_delta_dict.pop('aggregate_list', None)
    return CopyToTarget._getParentParameters(self, simulation_movement,
                                             **value_delta_dict)

