##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
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
"""
XXX This file is experimental for new simulation implementation, and
will replace DeliveryRule.
"""

import zope.interface
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5Type.Core.Predicate import Predicate
from Products.ERP5.mixin.rule import RuleMixin
from Products.ERP5.mixin.movement_collection_updater import \
     MovementCollectionUpdaterMixin
from Products.ERP5.mixin.movement_generator import MovementGeneratorMixin

class DeliverySimulationRule(RuleMixin, MovementCollectionUpdaterMixin, Predicate):
  """
  Delivery Rule object make sure an Delivery in the simulation
  is consistent with the real delivery

  WARNING: what to do with movement split ?
  """
  # CMF Type Definition
  meta_type = 'ERP5 Delivery Simulation Rule'
  portal_type = 'Delivery Simulation Rule'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative interfaces
  zope.interface.implements(interfaces.IRule,
                            interfaces.IDivergenceController,
                            interfaces.IMovementCollectionUpdater,)

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

  def _getMovementGenerator(self):
    """
    Return the movement generator to use in the expand process
    """
    return DeliveryRuleMovementGenerator()

  def _getMovementGeneratorContext(self, context):
    """
    Return the movement generator context to use for expand
    """
    return context

  def _getMovementGeneratorMovementList(self):
    """
    Return the movement lists to provide to the movement generator
    """
    return []

  def _isProfitAndLossMovement(self, movement):
    # For a kind of trade rule, a profit and loss movement lacks source
    # or destination.
    return (movement.getSource() is None or movement.getDestination() is None)

class DeliveryRuleMovementGenerator(MovementGeneratorMixin):
  def getGeneratedMovementList(self, context, movement_list=None,
                                rounding=False):
    """
    Input movement list comes from the parent
    """
    ret = []
    rule = context.getSpecialiseValue()
    for input_movement, business_path in self \
            ._getInputMovementAndPathTupleList(context):
      kw = self._getPropertyAndCategoryList(input_movement, business_path,
                                            rule)
      kw.update({'order':None,'delivery':None})
      simulation_movement = context.newContent(
        portal_type=RuleMixin.movement_type,
        temp_object=True,
        **kw)
      ret.append(simulation_movement)
    return ret

  def _getInputMovementList(self, context):
    return [context.getParentValue(),]
