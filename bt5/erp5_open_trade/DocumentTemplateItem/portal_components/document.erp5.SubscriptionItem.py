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
from Products.ERP5Type import Permissions, PropertySheet
from erp5.component.document.Item import Item
from erp5.component.mixin.CompositionMixin import CompositionMixin
from erp5.component.mixin.SimulableMixin import SimulableMixin
from erp5.component.mixin.MovementGeneratorMixin import MovementGeneratorMixin
from Products.ERP5.mixin.periodicity import PeriodicityMixin
from Products.ERP5Type.Base import Base
from erp5.component.interface.IMovementGenerator import IMovementGenerator
from DateTime import DateTime

@zope.interface.implementer(IMovementGenerator,)
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

  def _getLatestOpenOrderPath(self):
    catalog_tool = getToolByName(self, 'portal_catalog')
    # Try to find the source open order
    line_list = catalog_tool(
      portal_type=["Open Sale Order Line", "Open Sale Order Cell"],
      aggregate__uid=self.getUid(),
      validation_state=('open', 'validated', 'archived'), # XXX-JPS hard coding
      sort_on=(('effective_date', 'descending'),
                # Do not return archived if effective dates are identical
                ('validation_state', 'descending')),
      limit=1 # Note Luke: Support the newest Open Order which defines
              # something for current subscription item
    )
    """
      if line.hasCellContent(base_id='path'):
        movement_list = line.getCellValueList(base_id='path')
      else:
        movement_list = [line]
    """
    if len(line_list) == 1:
      return line_list[0]
    return None

  def _getInputMovementList(self, movement_list=None, rounding=None):
    """
      Generate the list of input movements by looking at all
      open order lines relating to this subscription item.

      TODO: clever handling of quantity (based on the nature
      of resource, ie. float or unit)
    """
    result = []

    movement = self._getLatestOpenOrderPath()
    if movement is not None:
      resource = movement.getResource()
      start_date = movement.getStartDate()
      # if there is no stop_date, block the generation
      # to today
      stop_date = movement.getStopDate()
      if (start_date == stop_date) or (stop_date is None):
        # stop_date seems acquired from start_date
        stop_date = DateTime()
      if (start_date is None) or (stop_date < start_date):
        # infinity nor time back machine does not exist
        return result
      source = movement.getSource()
      source_section = movement.getSourceSection()
      source_project = movement.getSourceProject()
      source_decision = movement.getSourceDecision()
      source_payment = movement.getSourcePayment()
      destination = movement.getDestination()
      destination_section = movement.getDestinationSection()
      destination_project = movement.getDestinationProject()
      destination_decision = movement.getDestinationDecision()
      destination_payment = movement.getDestinationPayment()
      quantity = movement.getQuantity()
      quantity_unit = movement.getQuantityUnit()
      price = movement.getPrice()
      price_currency = movement.getPriceCurrency()
      # XXX no acquisition
      base_application_list = movement.getBaseApplicationList()
      base_contribution_list = movement.getBaseContributionList()
      # XXX no acquisition
      use_list = movement.getUseList()
      # XXX no acquisition
      aggregate_list = movement.getAggregateList()

      variation_category_list = movement.getVariationCategoryList()

      # XXX no acquisition
      specialise = movement.getSpecialise()
      current_date = start_date
      id_index = 0
      while current_date < stop_date:
        next_date = self.getNextPeriodicalDate(current_date)
        generated_movement = self.newContent(temp_object=True,
                                             portal_type='Movement',
                                             id='subscription_%s' % id_index)
        generated_movement._edit(  aggregate_list=aggregate_list,
                                   resource=resource,
                                   quantity=quantity,
                                   quantity_unit=quantity_unit,
                                   price=price,
                                   price_currency=price_currency,
                                   start_date=current_date,
                                   stop_date=next_date,
                                   source=source,
                                   source_section=source_section,
                                   source_project=source_project,
                                   source_decision=source_decision,
                                   source_payment=source_payment,
                                   destination=destination,
                                   destination_section=destination_section,
                                   destination_project=destination_project,
                                   destination_decision=destination_decision,
                                   destination_payment=destination_payment,
                                   specialise=specialise,
                                   base_application_list=base_application_list,
                                   base_contribution_list=base_contribution_list,
                                   use_list=use_list,
                                   variation_category_list=variation_category_list
                                  )
        result.append(generated_movement)
        current_date = next_date
        id_index += 1

    return result

  # XXX BELOW HACKS
  def getResource(self):
    open_order_line = self._getLatestOpenOrderPath()
    if open_order_line is None:
      return None
    return open_order_line.getResource()

  def getStartDate(self):
    open_order_line = self._getLatestOpenOrderPath()
    if open_order_line is None:
      return None
    return open_order_line.getStartDate()

  def getStopDate(self):
    open_order_line = self._getLatestOpenOrderPath()
    if open_order_line is None:
      return None
    return open_order_line.getStopDate()

  def getSource(self):
    open_order_line = self._getLatestOpenOrderPath()
    if open_order_line is None:
      return None
    return open_order_line.getSource()

  def getSourceSection(self):
    open_order_line = self._getLatestOpenOrderPath()
    if open_order_line is None:
      return None
    return open_order_line.getSourceSection()

  def getDestination(self):
    open_order_line = self._getLatestOpenOrderPath()
    if open_order_line is None:
      return None
    return open_order_line.getDestination()

  def getDestinationSection(self):
    open_order_line = self._getLatestOpenOrderPath()
    if open_order_line is None:
      return None
    return open_order_line.getDestinationSection()

  def getQuantity(self):
    open_order_line = self._getLatestOpenOrderPath()
    if open_order_line is None:
      return None
    return open_order_line.getQuantity()

  def getQuantityUnit(self, checked_permission=None):
    open_order_line = self._getLatestOpenOrderPath()
    if open_order_line is None:
      return None
    return open_order_line.getQuantityUnit(checked_permission=checked_permission)

  def getPrice(self, context=None):
    open_order_line = self._getLatestOpenOrderPath()
    if open_order_line is None:
      return None
    return open_order_line.getPrice()

  def getPriceCurrency(self):
    open_order_line = self._getLatestOpenOrderPath()
    if open_order_line is None:
      return None
    return open_order_line.getPriceCurrency()

  def getSpecialise(self):
    open_order_line = self._getLatestOpenOrderPath()
    if open_order_line is None:
      return None
    return open_order_line.getSpecialise()

  def getSpecialiseList(self):
    open_order_line = self._getLatestOpenOrderPath()
    if open_order_line is None:
      return []
    return open_order_line.getSpecialiseList()

  def getSpecialiseValue(self):
    open_order_line = self._getLatestOpenOrderPath()
    if open_order_line is None:
      return None
    return open_order_line.getSpecialiseValue()

  def getSpecialiseValueList(self):
    open_order_line = self._getLatestOpenOrderPath()
    if open_order_line is None:
      return []
    return open_order_line.getSpecialiseValueList()

  def _getCategoryMembershipList(
      self,
      category,
      spec=(),
      filter=None, #  pylint:disable=redefined-builtin
      portal_type=(),
      base=0,
      keep_default=1,
      checked_permission=None,
      **kw):
    if category == 'specialise':
      open_order_line = self._getLatestOpenOrderPath()
      if open_order_line is not None:
        return open_order_line._getCategoryMembershipList(category, spec=spec, filter=filter,
                               portal_type=portal_type, base=base, keep_default=keep_default,
                               checked_permission=checked_permission, **kw)
    return Base._getCategoryMembershipList(self, category, spec=spec, filter=filter,
                portal_type=portal_type, base=base, keep_default=keep_default,
                checked_permission=checked_permission, **kw)
