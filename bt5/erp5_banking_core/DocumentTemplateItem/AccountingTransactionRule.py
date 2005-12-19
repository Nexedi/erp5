##############################################################################
#
# Copyright (c) 2002, 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#                    Romain Courteaud <romain@nexedi.com>
#                    Alexandre Boeglin <alex@nexedi.com>
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
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5.Document.Rule import Rule

from zLOG import LOG


class AccountingTransactionRule(Rule):
  """
    Accounting Transaction Rule object make sure an Accounting Transaction Line
      in the simulation is consistent with the real accounting transaction.

    WARNING: what to do with movement split ?
  """

  # CMF Type Definition
  meta_type = 'BAOBAB Accounting Transaction Rule'
  portal_type = 'Accounting Transaction Rule'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.View)

  # Default Properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    )

  def test(self, movement):
    """
      Tests if the rule (still) applies.
    """
    # An accounting transaction rule never applies since it is always
    #   explicitely instanciated.
    return 0

  # Simulation workflow
  security.declareProtected(Permissions.ModifyPortalContent, 'expand')
  def expand(self, applied_rule, force=0, **kw):
    """
      Expands the current movement downward:
        -> new status -> expanded

      An applied rule can be expanded only if its parent movement
        is expanded.
    """
    delivery_line_type = 'Simulation Movement'

    # Get the accounting transaction when we come from.
    my_accounting_transaction = applied_rule.getDefaultCausalityValue()

    # Only expand if my_accounting_transaction is not None and state is
    #   not 'confirmed'.
    if my_accounting_transaction is not None:
      # Only expand accounting transaction rule if accounting transaction
      #   not yet confirmed (This is consistent with the fact that once
      #   simulation is launched, we stick to it).
      if force or \
         (applied_rule.getLastExpandSimulationState() not in \
              applied_rule.getPortalReservedInventoryStateList() and \
         applied_rule.getLastExpandSimulationState() not in \
              applied_rule.getPortalCurrentInventoryStateList()):
        # First, check each contained movement and delete previous simulation movements
        for movement in applied_rule.contentValues(filter={'portal_type': \
                                  applied_rule.getPortalMovementTypeList()}):
            movement.flushActivity(invoke=0)
            applied_rule._delObject(movement.getId())

        # Copy each accounting movement (line or cell) from the accounting transaction
        for accounting_transaction_line_object in my_accounting_transaction.contentValues(filter={ \
                  'portal_type':applied_rule.Baobab_getAccountingMovementTypeList()}):
          LOG('AccountingTransactionRule.expand, examining:',0, \
                        accounting_transaction_line_object.getPhysicalPath())
          try:
            if accounting_transaction_line_object.hasCellContent():
              for c in accounting_transaction_line_object.getCellValueList():
                new_id = accounting_transaction_line_object.getId() + '_' + c.getId()
                LOG('Create Cell', 0, str(new_id))
                new_line = applied_rule.newContent(
                    type_name=delivery_line_type,
                    id=new_id,
                    order_value = c,
                    quantity = -c.getQuantity(),
                    deliverable = 1
                )
                LOG('AccountingTransactionRule.expand, object created:',0, \
                    new_line.getPhysicalPath())
            else:
              new_id = accounting_transaction_line_object.getId()
              LOG('Line', 0, str(new_id))
              if accounting_transaction_line_object.getVariationCategoryList() == []:
                new_line = applied_rule.newContent(
                    type_name=delivery_line_type,
                    id=new_id,
                    order_value = accounting_transaction_line_object,
                    quantity = -accounting_transaction_line_object.getQuantity(),
                    deliverable = 1
                )
                LOG('AccountingTransactionRule.expand, object created:',0, \
                    new_line.getPhysicalPath())
              else:
                raise 'Error', 'VariationCategoryList is defined on\
                      AccountingTransactionLine %s and no cell exists.' %\
                      accounting_transaction_line_object.getRelativeUrl()
          except AttributeError:
            LOG('ERP5: WARNING', 0, \
                'AttributeError during expand on accounting transaction line %s' \
                % accounting_transaction_line_object.absolute_url())

        # Now we can set the last expand simulation state
        # to the current state
        applied_rule.setLastExpandSimulationState( \
            my_accounting_transaction.getSimulationState())

    # Pass to base class
    Rule.expand(self, applied_rule, force=force, **kw)

  security.declareProtected(Permissions.ModifyPortalContent, 'solve')
  def solve(self, applied_rule, solution_list):
    """
      Solve inconsitency according to a certain number of solutions
      templates. This updates the

      -> new status -> solved

      This applies a solution to an applied rule. Once
      the solution is applied, the parent movement is checked.
      If it does not diverge, the rule is reexpanded. If not,
      diverge is called on the parent movement.
    """

  security.declareProtected(Permissions.ModifyPortalContent, 'diverge')
  def diverge(self, applied_rule):
    """
      -> new status -> diverged

      This basically sets the rule to "diverged"
      and blocks expansion process
    """

  # Solvers
  security.declareProtected(Permissions.View, 'isDivergent')
  def isDivergent(self, applied_rule):
    """
      Returns 1 if divergent rule
    """

  security.declareProtected(Permissions.View, 'getDivergenceList')
  def getDivergenceList(self, applied_rule):
    """
      Returns a list Divergence descriptors
    """

  security.declareProtected(Permissions.View, 'getSolverList')
  def getSolverList(self, applied_rule):
    """
      Returns a list Divergence solvers
    """

  # Deliverability / orderability
  def isOrderable(self, m):
    return 0

  def isDeliverable(self, m):
    if m.getSimulationState() in m.getPortalDraftOrderStateList():
      return 0
    return 1