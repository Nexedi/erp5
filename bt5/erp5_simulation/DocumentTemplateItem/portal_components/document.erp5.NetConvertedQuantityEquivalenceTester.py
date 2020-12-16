# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SARL and Contributors. All Rights Reserved.
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

from AccessControl import ClassSecurityInfo

from erp5.component.document.FloatEquivalenceTester import FloatEquivalenceTester
from Products.ERP5Type import Permissions

class NetConvertedQuantityEquivalenceTester(FloatEquivalenceTester):
  """
  The purpose of this divergence tester is to check the
  consistency between delivery movement and simulation movement
  for some specific properties.
  """
  meta_type = 'ERP5 Net Converted Quantity Equivalence Tester'
  portal_type = 'Net Converted Quantity Equivalence Tester'
  add_permission = Permissions.AddPortalContent

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  def _compare(self, prevision_movement, decision_movement):
    tested_property = self.getTestedProperty()
    if getattr(decision_movement, 'isPropertyRecorded',
               lambda x:False)(tested_property):
      decision_value = decision_movement.getRecordedProperty(tested_property) or 0.0
    else:
      decision_value = self._getTestedPropertyValue(decision_movement,
                                                    tested_property) or 0.0

    # XXX: QuantityDivergenceTester from Legacy Simulation: A delivery
    # quantity of 0 is an exceptional case that we cannot really handle with
    # the current approach of delivery ratio.
    if (decision_movement.getPortalType() != 'Simulation Movement' and
        decision_value == 0.0):
      prevision_value = sum([
        sm.getCorrectedQuantity()
        for sm in decision_movement.getDeliveryRelatedValueList(
            portal_type='Simulation Movement')])
    else:
      prevision_value = self._getTestedPropertyValue(prevision_movement,
                                                     tested_property) or 0.0

    return self._comparePrevisionDecisionValue(prevision_movement,
                                               prevision_value,
                                               decision_movement,
                                               decision_value)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getUpdatablePropertyDict')
  def getUpdatablePropertyDict(self, prevision_movement, decision_movement):
    """
    Returns a list of properties to update on decision_movement
    prevision_movement so that next call to compare returns True.

    prevision_movement -- a simulation movement (prevision)

    decision_movement -- a delivery movement (decision)
    """
    return {'quantity':prevision_movement.getNetConvertedQuantity(),
            'quantity_unit':prevision_movement.getQuantityUnit()}
