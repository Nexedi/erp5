##############################################################################
#
# Copyright (c) 2015 Nexedi SA and Contributors. All Rights Reserved.
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
# Foundation, Inc., 51 Franklin Street - Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

from erp5.component.document.FirstCausalityMovementGroup import \
     FirstCausalityMovementGroup

class PreviousCausalityMovementGroup(FirstCausalityMovementGroup):
  """
  Group by previous causality of given type.

  This movement group will try to find a causality of given portal
  type by looking upper in the simulation tree. Merge will happen only
  if same causality of given type is the same.

  Sometimes, we can not find expected causality with given type because
  a movement has been added by hand into an intermediate delivery. In
  such case, we will look at causalities defined on deliveries

  For example, you might decide to merge in same invoice only
  movement from a particular Packing List, or only movement coming
  from a particular Order.
  """
  meta_type = 'ERP5 Previous Causality Movement Group'
  portal_type = 'Previous Causality Movement Group'

  def test(self, movement, property_dict, **kw):
    """Compare explanation to now if it is possible to update delivery"""
    explanation = property_dict.get('_previous_explanation','')
    if movement == movement.getDeliveryValue():
      # We are at delivery level, check if the explanation is part of the causality
      delivery = movement
      if explanation in delivery.getCausalityList():
        return True, {}
      else:
        return False, {}
    raise NotImplementedError("What should we do ?")

  def _testExplanation(self, explanation_value):
    """
    Check if explanation is valid

    We might later have other ways to test explanation, for example by a script
    """
    result = False
    causality_portal_type = self.getCausalityPortalType()
    if causality_portal_type is None or \
        explanation_value.getPortalType() == causality_portal_type:
      result = True
    return result

  def _searchUpperInTree(self, movement):
    explanation_value = None
    if movement.getParentValue() != movement.getRootAppliedRule() :
      # get the explanation of parent movement if we have not been
      # created by the root applied rule.
      movement = movement.getParentValue().getParentValue()
      intermediate_explanation_value = movement.getExplanationValue()
      if self._testExplanation(intermediate_explanation_value):
        explanation_value = intermediate_explanation_value
      if explanation_value is None:
        explanation_value = self._searchUpperInTree(movement)
    return explanation_value

  def _searchThroughDelivery(self, delivery):
    explanation_value = None
    if self._testExplanation(delivery):
      explanation_value = delivery
    else:
      for causality_value in delivery.getCausalityValueList():
        explanation_value = self._searchThroughDelivery(causality_value)
        if explanation_value:
          break
    return explanation_value

  def _getPropertyDict(self, movement, **kw):
    previous_explanation = self._searchUpperInTree(movement)
    if previous_explanation is None:
      movement = movement.getRootAppliedRule()
      previous_explanation = self._searchThroughDelivery(movement.getCausalityValue())
    property_dict = {}
    if previous_explanation is not None:
      property_dict["_previous_explanation"] = previous_explanation.getRelativeUrl()
    return property_dict
