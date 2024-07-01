##############################################################################
#
# Copyright (c) 2002, 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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

from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.Utils import deprecated
from erp5.component.document.Delivery import Delivery

class Order(Delivery):
  # CMF Type Definition
  meta_type = 'ERP5 Order'
  portal_type = 'Order'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Default Properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Task
                    , PropertySheet.Arrow
                    , PropertySheet.Reference
                    , PropertySheet.TradeCondition
                    , PropertySheet.Comment
                    , PropertySheet.Order
                    )

  security.declareProtected(Permissions.AccessContentsInformation, \
                                                 'isAccountable')
  def isAccountable(self):
    """
    Returns 1 if this needs to be accounted
    Only account movements which are not associated to a delivery
    Whenever delivery is there, delivery has priority
    """
    return 0

  def getTotalPrice(self, **kw) :
    """Returns the total price for this Order.

    If base_contribution is passed, the trade model lines will be used to
    include movements that will be generated.
    """
    if kw.get('fast'):
      kw['only_accountable'] = False
    if kw.get('base_contribution') is None:
      kw.setdefault('portal_type', self.getPortalOrderMovementTypeList())
      return Delivery.getTotalPrice(self, **kw)
    else:
      # Find amounts from the result of getAggregatedAmountList.
      # Call getAggregatedAmountList and sum all the amounts which
      # base_contribution category is matched with.
      raise NotImplementedError
#      rounding = kw.get('rounding')
#      from Products.ERP5.PropertySheet.TradeModelLine import TARGET_LEVEL_MOVEMENT
#      trade_condition = self.getSpecialiseValue()
#      if trade_condition is None:
#        # We cannot find any amount so that the result is 0.
#        return 0
#      base_contribution = kw.get('base_contribution')
#      if isinstance(base_contribution, (tuple, list)):
#        base_contribution_list = base_contribution
#      else:
#        base_contribution_list = (base_contribution,)
#      base_contribution_value_list = []
#      portal_categories = self.portal_categories
#      for relative_url in base_contribution_list:
#        base_contribution_value = portal_categories.getCategoryValue(relative_url)
#        if base_contribution_value is not None:
#          base_contribution_value_list.append(base_contribution_value)
#      if not base_contribution_value_list:
#        # We cannot find any amount so that the result is 0.
#        return 0
#      current_aggregated_amount_list = trade_condition.getAggregatedAmountList(self, rounding=rounding, force_create_line=True)
#      trade_model_line = self.newContent(temp_object=True,
#          portal_type='Trade Model Line',
#          id='_temp_' + self.getId(), notify_workflow=False)
#      # prevent invoking interaction workflows.
#      trade_model_line.portal_type = ''
#      trade_model_line.edit(target_level=TARGET_LEVEL_MOVEMENT, price=1,
#                            efficiency=1, quantity=None,
#                            base_application_value_list=base_contribution_value_list)
#      aggregated_amount_list = trade_model_line._getAggregatedAmountList(
#          self,
#          movement_list=self.getMovementList(),
#          current_aggregated_amount_list=current_aggregated_amount_list,
#          rounding=rounding)
#      return aggregated_amount_list.getTotalPrice()

  def getTotalQuantity(self, **kw) :
    """Returns the total quantity for this Order. """
    if 'portal_type' not in kw:
      kw['portal_type'] = self.getPortalObject() \
        .getPortalOrderMovementTypeList()
    if kw.get('fast'):
      kw['only_accountable'] = False
    return Delivery.getTotalQuantity(self, **kw)

  @deprecated
  def applyToOrderRelatedMovement(self, method_id='expand', **kw):
    # WARNING: does not work if it was not catalogued immediately
    # 'order' category is deprecated. it is kept for compatibility.
    for m in self.getMovementList():
      for my_simulation_movement in m.getDeliveryRelatedValueList(
          portal_type='Simulation Movement') or \
          m.getOrderRelatedValueList(
          portal_type='Simulation Movement'):
        getattr(my_simulation_movement, method_id)(**kw)