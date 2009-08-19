##############################################################################
#
# Copyright (c) 2009 Nexedi KK, Nexedi SA and Contributors. All Rights Reserved.
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

from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5.Document.Rule import Rule
from Products.ERP5.Document.DeliveryRule import DeliveryRule
from zLOG import LOG, WARNING
from DateTime import DateTime

class OpenOrderRule(DeliveryRule):
  """
  Order Rule object make sure an Order in the simulation
  is consistent with the real order

  WARNING: what to do with movement split ?
  """
  # CMF Type Definition
  meta_type = 'ERP5 Open Order Rule'
  portal_type = 'Open Order Rule'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Simulation workflow
  security.declareProtected(Permissions.ModifyPortalContent, 'expand')
  def expand(self, applied_rule, force=0, **kw):
    """
      Expands the Order to a new simulation tree.
      expand is only allowed to modify a simulation movement if it doesn't
      have a delivery relation yet.

      If the movement is in ordered or planned state, has no delivered
      child, and is not in order, it can be deleted.
      Else, if the movement is in ordered or planned state, has no
      delivered child, and is in order, it can be modified.
      Else, it cannot be modified.
    """
    order = applied_rule.getDefaultCausalityValue()
    if getattr(order, 'expandOpenOrderRule', None) is not None:
      # Delegate implementation of expand to the SubscriptionItem or 
      # to the OpenOrder instance
      return order.expandOpenOrderRule(applied_rule, force=force, **kw)
    movement_type = 'Simulation Movement'    
    if order is not None:
      order_movement_list = order.getMovementList(
        portal_type=order.getPortalOrderMovementTypeList())

      for order_movement in order_movement_list:
        last_simulation_movement = self._getLastSimulationMovementValue(applied_rule, order_movement)
        if last_simulation_movement is not None:
          schedule_start_date = last_simulation_movement.getStartDate()
          schedule_list = self._getOrderDateScheduleTupleList(order_movement, schedule_start_date, **kw)
        else:
          # Because order's start_date might be matched with the periodicity.
          order_start_date = order.getStartDate()
          schedule_start_date = order_start_date-1
          schedule_list = [date_pair
                           for date_pair in self._getOrderDateScheduleTupleList(order_movement, schedule_start_date, **kw)
                           if date_pair[0]>=order_start_date]

        for start_date, stop_date in schedule_list:
          property_dict = {'start_date':start_date, 'stop_date':stop_date}
          property_dict = self._getExpandablePropertyDict(order_movement,
                                                          property_dict)
          simulation_movement = applied_rule.newContent(
            portal_type=movement_type,
            order_value=order_movement,
            order_ratio=1,
            delivery_ratio=1,
            deliverable=1,
            **property_dict
            )

      # Mark that expand finished.
      applied_rule.setLastExpandSimulationState(order.getSimulationState())
    # Pass to base class
    Rule.expand(self, applied_rule, force=force, **kw)

  security.declareProtected(Permissions.AccessContentsInformation, 'isStable')
  def isStable(self, applied_rule):
    """
    Checks that the applied_rule is stable
    """
    LOG('OrderRule.isStable', WARNING, 'Not Implemented')
    return 1

  security.declareProtected(Permissions.AccessContentsInformation,
                            'isDivergent')
  def isDivergent(self, movement):
    """
    Checks that the movement is divergent
    """
    return Rule.isDivergent(self, movement)

  def _getExpandablePropertyDict(self, order_movement, property_dict=None):
    property_list = (
      'title',
      'reference',
      'description',
      'int_index',
      'source',
      'source_section',
      'source_function',
      'source_trade_list',
      'destination',
      'destination_section',
      'destination_function',
      'resource',
      'variation_category_list',
      'variation_property_dict',
      'base_contribution_list',
      'aggregate_list',
      'price',
      'price_currency',
      'quantity',
      'quantity_unit',
      )
    if property_dict is None:
      property_dict = {}
    for property_name in property_list:
      if not property_name in property_dict:
        property_dict[property_name] = order_movement.getProperty(property_name)
    return property_dict

  def _getLastSimulationMovementValue(self, applied_rule, order_movement):
    result = applied_rule.searchFolder(order_uid=order_movement.getUid(),
                                       sort_on=[('movement.start_date','DESC')])
    if len(result)>0:
      return result[0].getObject()
    else:
      return None

  def _getOrderDateScheduleTupleList(self, order_movement, schedule_start_date,
                                     calculation_base_date=None, **kw):
    if calculation_base_date is None:
      # This is NOW
      calculation_base_date = DateTime()

    getPeriodicityLineValueList = order_movement._getTypeBasedMethod('getPeriodicityLineValueList')
    if getPeriodicityLineValueList is None:
      raise RuntimeError, "Cannot find getPeriodicityLineValueList script"
    schedule_stop_date = (calculation_base_date+
                          order_movement.getForecastingTermDayCount())
    if schedule_stop_date > order_movement.getStopDate():
      schedule_stop_date = order_movement.getStopDate()
    
    periodicity_line_list = getPeriodicityLineValueList(schedule_start_date,
                                                        schedule_stop_date)
    result = []
    for periodicity_line in periodicity_line_list:
      result.extend(periodicity_line.getDatePeriodList(schedule_start_date,
                                                       schedule_stop_date))
    return result
