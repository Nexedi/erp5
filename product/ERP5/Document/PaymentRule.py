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

from AccessControl import ClassSecurityInfo
from Acquisition import aq_base, aq_parent, aq_inner, aq_acquire
from Products.CMFCore.utils import getToolByName

from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5.Document.Rule import Rule

from zLOG import LOG

class PaymentRule(Rule):
    """
      Payment Rule generates payment simulation movement from invoice transaction simulation movements.
      This one is a very s(imple|tupid) one : if the parent movement is a 'receivable' one,
      we just create two submovements : 'receivable' (as credit)
      and 'bank' (as debit) with the same quantity as the parent.
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

    __implements__ = ( Interface.Predicate,
                       Interface.Rule )

    # Default Properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      , PropertySheet.Task
                      )

    def _test(self, movement):
      """
        Tests if the rule (still) applies
      """
      if 'receivable' in movement.getId() : ### TODO: expand 'payable' too
        parent = movement.getParentValue()
        parent_rule_value = parent.getSpecialiseValue()
        if parent_rule_value is None:
          return 0
        parent_rule_type = parent_rule_value.getPortalType()
        if parent_rule_type in ('Invoice Transaction Rule',
            'Invoice Rule'):
          if parent_rule_type == 'Invoice Rule':
            delivery_movement = movement.getDeliveryValue()
            if delivery_movement is not None:
              if delivery_movement.getPortalType() not in \
                  movement.getPortalAccountingMovementTypeList():
                return 0
          return 1
      return 0

    security.declareProtected(Permissions.ModifyPortalContent, 'expand')
    def expand(self, applied_rule, **kw):
      """
        Expands the current movement downward.

        -> new status -> expanded

        An applied rule can be expanded only if its parent movement
        is expanded.
      """
      payment_line_type = 'Simulation Movement'

      my_parent_movement = applied_rule.getParentValue()

      if my_parent_movement.getQuantity() is not None:
        bank_id = 'bank'
        if bank_id in applied_rule.objectIds():
          bank_movement = applied_rule[bank_id]
        else:
          bank_movement = applied_rule.newContent(
                portal_type=payment_line_type,
                id = bank_id)
        receivable_id = 'receivable'
        if receivable_id in applied_rule.objectIds():
          receivable_movement = applied_rule[receivable_id]
        else:
          receivable_movement = applied_rule.newContent(
                portal_type=payment_line_type,
                id = receivable_id)
        
        # TODO: specify this using a rule in portal_rules
        # TODO: generate many movement according to different trade conditions	
        bank_movement.edit(
          resource = my_parent_movement.getResource(),
          quantity = my_parent_movement.getQuantity(),
          source = 'account/banques_etablissements_financiers', # XXX Not Generic
          destination = 'account/banques_etablissements_financiers', # XXX Not Generic
          source_section = my_parent_movement.getSourceSection(),
          destination_section = my_parent_movement.getDestinationSection(),
        )
        receivable_movement.edit(
          resource = my_parent_movement.getResource(),
          quantity = - my_parent_movement.getQuantity(),
          source = 'account/creance_client', # XXX Not Generic
          destination = 'account/dette_fournisseur', # XXX Not Generic
          source_section = my_parent_movement.getSourceSection(),
          destination_section = my_parent_movement.getDestinationSection(),
        )
        
      Rule.expand(self, applied_rule, **kw)


    def isDeliverable(self, m):
      if m.getSimulationState() in self.getPortalDraftOrderStateList():
        return 0
      return 1
