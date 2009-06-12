##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Sebastien Robin <seb@nexedi.com>
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
from Acquisition import aq_base, aq_parent, aq_inner, aq_acquire
from Products.CMFCore.utils import getToolByName

from Products.ERP5Type import Permissions, PropertySheet, Constraint, interfaces
from Products.ERP5.Document.Rule import Rule

from zLOG import LOG, INFO

class PaymentRule(Rule):
    """Payment Rule generates payment simulation movement from invoice
    transaction simulation movements.
    """

    # CMF Type Definition
    meta_type = 'ERP5 Payment Rule'
    portal_type = 'Payment Rule'
    add_permission = Permissions.AddPortalContent
    isPortalContent = 1
    isRADContent = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    zope.interface.implements( interfaces.IPredicate,
                       interfaces.IRule )

    # Default Properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      , PropertySheet.Task
                      )

    receivable_account_type_list = ('asset/receivable', )
    payable_account_type_list = ('liability/payable', )


    def _getPaymentConditionList(self, movement):
      """Returns payment conditions for this movement.
      """
      while 1:
        delivery_movement = movement.getDeliveryValue()
        if delivery_movement is not None:
          explanation = delivery_movement.getExplanationValue()
          payment_condition_list = explanation.contentValues(
                 filter=dict(portal_type='Payment Condition'))
          if payment_condition_list:
            return payment_condition_list

        order_movement = movement.getOrderValue()
        if order_movement is not None:
          explanation = order_movement.getExplanationValue()
          payment_condition_list = explanation.contentValues(
                 filter=dict(portal_type='Payment Condition'))
          if payment_condition_list:
            return payment_condition_list

        movement = movement.getParentValue().getParentValue()
        if movement.getPortalType() != 'Simulation Movement':
          LOG('ERP5', INFO, "PaymentRule couldn't find payment condition")
          return []
     
    def _createMovementsForPaymentCondition(self,
          applied_rule, payment_condition):
      """Create simulation movements for this payment condition.
      """
      simulation_movement = applied_rule.getParentValue()
      date = payment_condition.TradeCondition_getDueDate()
      
      if payment_condition.getQuantity():
        quantity = payment_condition.getQuantity()
      else:
        ratio = payment_condition.getEfficiency(1)
        quantity = simulation_movement.getQuantity() * ratio

      edit_dict = dict(
            causality_value=payment_condition,
            payment_mode=payment_condition.getPaymentMode(),
            source=simulation_movement.getSource(),
            source_section=simulation_movement.getSourceSection(),
            source_payment=payment_condition.getSourcePayment() or
                              simulation_movement.getSourcePayment(),
            destination=simulation_movement.getDestination(),
            destination_section=simulation_movement.getDestinationSection(),
            destination_payment=payment_condition.getDestinationPayment() or
                              simulation_movement.getDestinationPayment(),
            resource=simulation_movement.getResource(),
            start_date=date,
            price=1,
            quantity= - quantity,)
      
      applied_rule.newContent( **edit_dict )

      edit_dict['source'] = self.getSourcePayment()
      edit_dict['destination'] = self.getDestinationPayment()
      edit_dict['quantity'] = - edit_dict['quantity']
      applied_rule.newContent( **edit_dict )
      
      
    security.declareProtected(Permissions.ModifyPortalContent, 'expand')
    def expand(self, applied_rule, **kw):
      """Expands the current movement downward.
      """
      payment_line_type = 'Simulation Movement'

      my_parent_movement = applied_rule.getParentValue()
      # generate for source
      bank_account = self.getDestinationPaymentValue(
                             portal_type='Account')
      assert bank_account is not None

      for payment_condition in self._getPaymentConditionList(
                                            my_parent_movement):
        payment_condition_url = payment_condition.getRelativeUrl()
        # look for a movement for this payment condition:
        corresponding_movement_list = []
        for simulation_movement in applied_rule.contentValues():
          if simulation_movement.getCausality() == payment_condition_url:
            corresponding_movement_list.append(simulation_movement)
        if not corresponding_movement_list:
          self._createMovementsForPaymentCondition(applied_rule,
                                                   payment_condition)
        else:
          # TODO: update corresponding_movement_list
          pass
      
      #Rule.expand(self, applied_rule, **kw)

    def test(self, context, tested_base_category_list=None):
      """Test if this rule apply.
      """

      # XXX for now disable this rule
      return False

      if context.getParentValue()\
          .getSpecialiseValue().getPortalType() == 'Payment Rule':
        return False

      for account in ( context.getSourceValue(portal_type='Account'),
          context.getDestinationValue(portal_type='Account')):
        if account is not None:
          account_type = account.getAccountType()
          if account_type in self.receivable_account_type_list or \
              account_type in self.payable_account_type_list:
            return True

      return False

