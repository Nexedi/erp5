# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008 Nexedi SA and Contributors. All Rights Reserved.
#                           Łukasz Nowak <luke@nexedi.com>
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

from erp5.component.document.CausalityMovementGroup import CausalityMovementGroup

class FirstCausalityMovementGroup(CausalityMovementGroup):
  """
  Returns first found causality, using delivery of parent movements
  Non modifiable version of DeliveryCausalityAssignmentMovementGroup
  """
  meta_type = 'ERP5 First Causality Movement Group'
  portal_type = 'First Causality Movement Group'

  def test(self, movement, property_dict, **kw):
    """Compare explanation to now if it is possible to update delivery"""
    explanation = property_dict.get('_explanation','')
    if movement == movement.getDeliveryValue():
      # XXX what is the expected behaviour of this movement group in
      # delivery level?
      if movement.getRelativeUrl() == explanation:
        return True, {}
      else:
        return False, {}
    else:
      simulation_movement = movement.getDeliveryRelatedValue()
      if simulation_movement is not None and \
         self._getExplanationRelativeUrl(simulation_movement) == explanation:
        return True, {}
      else:
        return False, {}

  def _getExplanationRelativeUrl(self, movement):
    """ Get the order value for a movement """
    applied_rule = movement.getParentValue()
    if applied_rule.isRootAppliedRule():
      return None
    parent_movement = applied_rule.getParentValue()
    # Go upper into the simulation tree in order to find a delivery link
    parent_delivery = parent_movement.getDeliveryValue()
    applied_rule = parent_movement.getParentValue()
    while parent_delivery is None and not applied_rule.isRootAppliedRule():
      parent_movement = applied_rule.getParentValue()
      parent_delivery = parent_movement.getDeliveryValue()
      applied_rule = parent_movement.getParentValue()
    delivery_movement = parent_delivery
    delivery_url = None
    if delivery_movement is not None:
      delivery = delivery_movement.getExplanationValue()
      if delivery is not None:
        delivery_url = delivery.getRelativeUrl()
    return delivery_url
