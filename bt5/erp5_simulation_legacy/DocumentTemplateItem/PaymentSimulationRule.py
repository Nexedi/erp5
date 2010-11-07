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

from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions
from Products.ERP5Legacy.Document.Rule import Rule
from Products.ERP5.Document.PredicateMatrix import PredicateMatrix

class PaymentSimulationRule(Rule, PredicateMatrix):
  """
  Payment Simulation Rule generates payment simulation movements from
  accounting / invoice transaction simulation movements.
  """

  # CMF Type Definition
  meta_type = 'ERP5 Payment Simulation Rule'
  portal_type = 'Payment Simulation Rule'
  add_permission = Permissions.AddPortalContent

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  def _generatePrevisionList(self, applied_rule, **kw):
    """
    Generate a list of dictionaries, that contain calculated content of
    current Simulation Movements in applied rule.
    based on its context (parent movement, delivery, configuration ...)

    These previsions are returned as dictionaries.

    * source and destination (i.e. account) are provided by rule cells.
    * start_date, stop_date and quantity are calculated according to
      payment conditions.
    """
    # Find an input movement and using Payment Conditions.
    # XXX we also need to support local Payment Conditions, that are not
    # provided by BPM.
    movement_and_tuple_list = self._getInputMovementAndPathTupleList(
        applied_rule)
    input_movement = movement_and_tuple_list[0][0]

    payment_condition_list = []

    # try to find local payment conditions from the upper level delivery
    rule = applied_rule
    movement = input_movement
    delivery = movement.getDeliveryValue()
    while delivery is None and not(rule.isRootAppliedRule()):
      rule = movement.getParentValue()
      movement = rule.getParentValue()
      delivery = movement.getDeliveryValue()
    if delivery is not None:
      payment_condition_list = delivery.getPaymentConditionValueList()

    # try to find payment conditions in specialised trade conditions
    if len(payment_condition_list) == 0:
      specialise = input_movement.getSpecialiseValue()
      if specialise is None and delivery is not None:
        specialise = delivery.getSpecialiseValue()
      if specialise is not None:
        payment_condition_list = specialise.getPaymentConditionValueList()

    # try to use payment conditions in BPM configuration
    if len(payment_condition_list) == 0:
      payment_condition_list = [x[1] for x in movement_and_tuple_list if x[1] is not None]

    kw = self._getExpandablePropertyDict(applied_rule, input_movement, None)
    prevision_list = []

    # Find a matching cell
    cell = self._getMatchingCell(input_movement)

    if cell is not None : # else, we do nothing
      for payment_condition in payment_condition_list:
        # XXX
        if (payment_condition.getCalculationScript(input_movement) is not None
            or payment_condition.getEfficiency() != 1):
          raise NotImplementedError
        #amount, = payment_condition.getAggregatedAmountList((input_movement,))
        #start_date = amount.getStartDate()  # does it depend on any property
        #stop_date = amount.getStopDate()    # of payment_condition ?
        #quantity = amount.getQuantity()
        start_date = input_movement.getStartDate()
        stop_date = input_movement.getStopDate()
        quantity = input_movement.getTotalPrice() * payment_condition.getQuantity(1)
        payment_mode = payment_condition.getPaymentMode()

        # one for payable
        prevision_line = kw.copy()
        prevision_line.update(
          start_date=start_date,
          stop_date=stop_date,
          source=input_movement.getSource(),
          destination=input_movement.getDestination(),
          payment_mode=payment_mode,
          quantity=-quantity
          )
        prevision_list.append(prevision_line)
        # one for cash, bank etc.
        payment_rule_cell_line_list = cell.objectValues()
        assert len(payment_rule_cell_line_list) == 1
        payment_rule_cell_line = payment_rule_cell_line_list[0]
        prevision_line = kw.copy()
        prevision_line.update(
          start_date=start_date,
          stop_date=stop_date,
          source=payment_rule_cell_line.getSource(),
          destination=payment_rule_cell_line.getDestination(),
          payment_mode=payment_mode,
          quantity=quantity
          )
        prevision_list.append(prevision_line)
    return prevision_list

  security.declareProtected(Permissions.ModifyPortalContent, 'expand')
  def expand(self, applied_rule, **kw):
    """Expands the current movement downward.
    """
    return Rule._expand(self, applied_rule, **kw)

  # Matrix related
  security.declareProtected( Permissions.ModifyPortalContent,
                              'newCellContent' )
  def newCellContent(self, id, portal_type='Accounting Rule Cell', **kw):
    """Overriden to specify default portal type
    """
    return self.newContent(id=id, portal_type=portal_type, **kw)
