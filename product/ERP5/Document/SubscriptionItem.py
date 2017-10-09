# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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

import zope.interface
from AccessControl import ClassSecurityInfo

from Products.CMFCore.utils import getToolByName
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5.Document.Item import Item
from Products.ERP5.mixin.composition import CompositionMixin
from Products.ERP5.mixin.rule import MovementGeneratorMixin, SimulableMixin
from Products.ERP5.mixin.periodicity import PeriodicityMixin
from Products.ERP5Type.UnrestrictedMethod import UnrestrictedMethod
from Products.ERP5Type.Base import Base

from zLOG import LOG

class SubscriptionItem(Item, CompositionMixin, MovementGeneratorMixin,
                       SimulableMixin, PeriodicityMixin):
  """
    A SubscriptionItem is an Item which expands itself
    into simulation movements which represent the item future.
    Examples of subscription items (or subclasses) include:
    employee paysheet contracts, telecommunication subscriptions,
    banking service subscriptions, etc
  """
  meta_type = 'ERP5 Subscription Item'
  portal_type = 'Subscription Item'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Price
                    , PropertySheet.Item
                    , PropertySheet.Amount
                    , PropertySheet.Reference
                    , PropertySheet.Periodicity
                    )

  # Declarative interfaces
  zope.interface.implements(interfaces.IMovementGenerator,
                           )

  def _createRootAppliedRule(self):
    # only try to expand if we are not in draft state
    if self.getValidationState() in ('draft', ): # XXX-JPS harcoded
      return
    return super(SubscriptionItem, self)._createRootAppliedRule()

  def getSimulationMovementSimulationState(self, simulation_movement):
    """Returns the simulation state for this simulation movement.

    This generic implementation assumes that if there is one open order line
    which is validated or archived, the movements will be planned. This
    behaviour might have to be adapted in subclasses.
    """
    for path in self.getAggregateRelatedValueList(
        portal_type=self.getPortalObject().getPortalSupplyPathTypeList(),):
      if path.getValidationState() in ('validated', 'archived'):
        return 'planned'
    return 'draft'

  def isSimulated(self):
    """
      We are never simulated (unlike deliveries)
    """
    return False

  # IMovementGenerator interface implementation
  def _getUpdatePropertyDict(self, input_movement):
    # Default implementation bellow can be overriden by subclasses
    return {}

  def _getInputMovementList(self, movement_list=None, rounding=None):
    """
      Generate the list of input movements by looking at all
      open order lines relating to this subscription item.

      TODO: clever handling of quantity (based on the nature
      of resource, ie. float or unit)
    """
    from Products.ERP5Type.Document import newTempMovement
    result = []
    catalog_tool = getToolByName(self, 'portal_catalog')

    # Try to find the source open order
    for movement in catalog_tool(portal_type="Open Sale Order Line",
        default_aggregate_uid=self.getUid(),
        validation_state=('open', 'validated', 'archived'), # XXX-JPS hard coding
        sort_on=(('effective_date', 'descending'),
                # Do not return archived if effective dates are identical
                ('validation_state', 'descending')),
        limit=1 # Note Luke: Support the newest Open Order which defines
                # something for current subscription item
        ): # YXU-Why we have a list here?
        resource = movement.getResource()
        start_date = movement.getStartDate()
        stop_date = movement.getStopDate()
        if start_date is None or stop_date is None or start_date>=stop_date:
          # infinity nor time back machine does not exist
          continue
        source = movement.getSource()
        source_section = movement.getSourceSection()
        source_decision = movement.getSourceDecision()
        destination = movement.getDestination()
        destination_section = movement.getDestinationSection()
        destination_decision = movement.getDestinationDecision()
        quantity = movement.getQuantity()
        quantity_unit = movement.getQuantityUnit()
        price = movement.getPrice()
        price_currency = movement.getPriceCurrency()
        base_application_list = movement.getBaseApplicationList()
        base_contribution_list = movement.getBaseContributionList()
        use_list = movement.getUseList()

        specialise = movement.getSpecialise()
        current_date = start_date
        id_index = 0
        while current_date < stop_date:
          next_date = self.getNextPeriodicalDate(current_date)
          generated_movement = newTempMovement(self, 'subscription_%s' % id_index)
          generated_movement._edit(  aggregate_value=self,
                                     resource=resource,
                                     quantity=quantity,
                                     quantity_unit=quantity_unit,
                                     price=price,
                                     price_currency=price_currency,
                                     start_date=current_date,
                                     stop_date=next_date,
                                     source=source,
                                     source_section=source_section,
                                     source_decision=source_decision,
                                     destination=destination,
                                     destination_section=destination_section,
                                     destination_decision=destination_decision,
                                     specialise=specialise,
                                     base_application_list=base_application_list,
                                     base_contribution_list=base_contribution_list,
                                     use_list=use_list
                                    )
          result.append(generated_movement)
          current_date = next_date
          id_index += 1

    return result

  # XXX BELOW HACKS
  def getResource(self):
    open_order_line = self.getAggregateRelatedValue(portal_type='Open Sale Order Line')
    if open_order_line is None:
      return None
    return open_order_line.getResource()

  def getStartDate(self):
    open_order_line = self.getAggregateRelatedValue(portal_type='Open Sale Order Line')
    if open_order_line is None:
      return None
    return open_order_line.getStartDate()

  def getStopDate(self):
    open_order_line = self.getAggregateRelatedValue(portal_type='Open Sale Order Line')
    if open_order_line is None:
      return None
    return open_order_line.getStopDate()

  def getSource(self):
    open_order_line = self.getAggregateRelatedValue(portal_type='Open Sale Order Line')
    if open_order_line is None:
      return None
    return open_order_line.getSource()

  def getSourceSection(self):
    open_order_line = self.getAggregateRelatedValue(portal_type='Open Sale Order Line')
    if open_order_line is None:
      return None
    return open_order_line.getSourceSection()

  def getDestination(self):
    open_order_line = self.getAggregateRelatedValue(portal_type='Open Sale Order Line')
    if open_order_line is None:
      return None
    return open_order_line.getDestination()

  def getDestinationSection(self):
    open_order_line = self.getAggregateRelatedValue(portal_type='Open Sale Order Line')
    if open_order_line is None:
      return None
    return open_order_line.getDestinationSection()

  def getQuantity(self):
    open_order_line = self.getAggregateRelatedValue(portal_type='Open Sale Order Line')
    if open_order_line is None:
      return None
    return open_order_line.getQuantity()

  def getQuantityUnit(self, checked_permission=None):
    open_order_line = self.getAggregateRelatedValue(portal_type='Open Sale Order Line')
    if open_order_line is None:
      return None
    return open_order_line.getQuantityUnit(checked_permission=checked_permission)

  def getPrice(self):
    open_order_line = self.getAggregateRelatedValue(portal_type='Open Sale Order Line')
    if open_order_line is None:
      return None
    return open_order_line.getPrice()

  def getPriceCurrency(self):
    open_order_line = self.getAggregateRelatedValue(portal_type='Open Sale Order Line')
    if open_order_line is None:
      return None
    return open_order_line.getPriceCurrency()

  def getSpecialise(self):
    open_order_line = self.getAggregateRelatedValue(portal_type='Open Sale Order Line')
    if open_order_line is None:
      return None
    return open_order_line.getSpecialise()

  def getSpecialiseList(self):
    open_order_line = self.getAggregateRelatedValue(portal_type='Open Sale Order Line')
    if open_order_line is None:
      return []
    return open_order_line.getSpecialiseList()

  def getSpecialiseValue(self):
    open_order_line = self.getAggregateRelatedValue(portal_type='Open Sale Order Line')
    if open_order_line is None:
      return None
    return open_order_line.getSpecialiseValue()

  def getSpecialiseValueList(self):
    open_order_line = self.getAggregateRelatedValue(portal_type='Open Sale Order Line')
    if open_order_line is None:
      return []
    return open_order_line.getSpecialiseValueList()

  def _getCategoryMembershipList(self, category, spec=(), filter=None,
      portal_type=(), base=0, keep_default=1, checked_permission=None, **kw):
    if category == 'specialise':
      open_order_line = self.getAggregateRelatedValue(portal_type='Open Sale Order Line')
      return open_order_line._getCategoryMembershipList(category, spec=spec, filter=filter,
                             portal_type=portal_type, base=base, keep_default=keep_default,
                             checked_permission=checked_permission, **kw)
    return Base._getCategoryMembershipList(self, category, spec=spec, filter=filter,
                portal_type=portal_type, base=base, keep_default=keep_default,
                checked_permission=checked_permission, **kw)
