# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2014 Nexedi SA and Contributors. All Rights Reserved.
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

import zope.interface
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5.mixin.rule import RuleMixin
from Products.ERP5.mixin.movement_generator import MovementGeneratorMixin
from Products.ERP5.mixin.movement_collection_updater import \
     MovementCollectionUpdaterMixin

class TransformationSourcingSimulationRule(RuleMixin, MovementCollectionUpdaterMixin):
  """
    Transformation Sourcing Rule makes sure
    items required in a Transformation are sourced.
  """
  # CMF Type Definition
  meta_type = 'ERP5 Transformation Sourcing Simulation Rule'
  portal_type = 'Transformation Sourcing Simulation Rule'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Default Properties
  property_sheets = (
    PropertySheet.Base,
    PropertySheet.XMLObject,
    PropertySheet.CategoryCore,
    PropertySheet.DublinCore,
    PropertySheet.Task,
    PropertySheet.Predicate,
    PropertySheet.Reference,
    PropertySheet.Version,
    PropertySheet.Rule
    )

  def _getMovementGenerator(self, context):
    """
    Return the movement generator to use in the expand process
    """
    return TransformationSourcingRuleMovementGenerator(applied_rule=context, rule=self)

class TransformationSourcingRuleMovementGenerator(MovementGeneratorMixin):

  def _getUpdatePropertyDict(self, input_movement):
    return {}

  def _getInputMovementList(self, movement_list=None, rounding=None):
    parent_movement = self._applied_rule.getParentValue()
    phase_dict = parent_movement.asComposedDocument() \
                                .getPreviousTradePhaseDict()
    movement = aq_base(parent_movement).__of__(self._applied_rule)
    movement = movement.asContext(quantity=-movement.getQuantity())
    movement._setReference(None)
    movement._setTradePhaseList(phase_dict[parent_movement.getTradePhase()])
    if parent_movement.getReference().startswith('cr/'):
      # For partially produced resources, automatically guess source from other
      # movements of the transformation. This avoids duplicate information
      # on Trade Model Paths.
      # 'here/getSource' condition can be used to match such movements.
      # The opposite condition can be used to match raw materials.
      reference = 'pr' + parent_movement.getIndustrialPhase()[11:]
      for pr in parent_movement.getParentValue().objectValues():
        if pr.getReference() == reference:
          movement._setSource(pr.getDestination())
          movement._setSourceSection(pr.getDestinationSection())
          break
    return movement,
