# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
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

import zope.interface
from AccessControl import ClassSecurityInfo

from Products.ERP5Type.Core.Predicate import Predicate
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5.mixin.equivalence_tester import EquivalenceTesterMixin

class VariationEquivalenceTester(Predicate, EquivalenceTesterMixin):
  """
  The purpose of this divergence tester is to check the
  consistency between delivery movement and simulation movement
  for a specific property.
  """
  meta_type = 'ERP5 Dict Equivalence Tester'
  portal_type = 'Dict Equivalence Tester'
  add_permission = Permissions.AddPortalContent

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = (   PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      , PropertySheet.EquivalenceTester
                      , PropertySheet.SolverSelection
                     )

  # Declarative interfaces
  zope.interface.implements( interfaces.IEquivalenceTester, )

  def _compare(self, prevision_movement, decision_movement):
    """
    If prevision_movement and decision_movement don't match, it returns a
    list : (prevision_value, decision_value, message, mapping)
    """
    for tested_property in ('variation_category_list',
                            'variation_property_dict'):
      if getattr(decision_movement, 'isPropertyRecorded',
                 lambda x:False)(tested_property):
        decision_value = decision_movement.getRecordedProperty(tested_property)
      else:
        decision_value = decision_movement.getProperty(tested_property)
      prevision_value = prevision_movement.getProperty(tested_property)

      if isinstance(prevision_value, (list, tuple)):
        result = sorted(decision_value) == sorted(prevision_value)
      elif isinstance(prevision_value, dict):
        result = sorted(decision_value.items()) == \
                 sorted(prevision_value.items())
      else:
        # should not happen
        raise AttributeError, 'prevision and decision values of this divergence tester should be list, tuple or dict.'
      if not result:
        return (
          prevision_value, decision_value,
          'The value of ${property_name} is different between decision and prevision.',
          dict(property_name=tested_property))
    return None

  def generateHashKey(self, movement):
    """
    Returns a hash key which can be used to optimise the
    matching algorithm between movements. The purpose
    of this hash key is to reduce the size of lists of
    movements which need to be compared using the compare
    method (quadratic complexity).

    If decision_movement is a simulation movement, use
    the recorded properties instead of the native ones.
    """
    value_list = []
    for tested_property in ('variation_category_list',
                            'variation_property_dict'):
      if movement.isPropertyRecorded(tested_property):
        value_list.append(movement.getRecordedProperty(tested_property))
      else:
        value_list.append(movement.getProperty(tested_property))
    return 'variation/%r' % (value_list)

  def getUpdatablePropertyDict(self, prevision_movement, decision_movement):
    """
    Returns a list of properties to update on decision_movement
    prevision_movement so that next call to compare returns True.

    prevision_movement -- a simulation movement (prevision)

    decision_movement -- a delivery movement (decision)
    """
    property_dict = {}
    for tested_property in ('variation_category_list',
                            'variation_property_dict'):
      prevision_value = prevision_movement.getProperty(tested_property)
      property_dict[tested_property] = prevision_value
    return property_dict
