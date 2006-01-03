##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
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

from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5.Document.Rule import Rule
from Products.ERP5.Document.PredicateMatrix import PredicateMatrix

from zLOG import LOG, BLATHER, INFO, PROBLEM

class InvoiceTransactionRule(Rule, PredicateMatrix):
    """
      Invoice Transaction Rule object generates accounting movements
      for each invoice movement based on category membership and
      other predicated. Template accounting movements are stored
      in cells inside an instance of the InvoiceTransactionRule.

      WARNING: what to do with movement split ?
    """

    # CMF Type Definition
    meta_type = 'ERP5 Invoice Transaction Rule'
    portal_type = 'Invoice Transaction Rule'
    add_permission = Permissions.AddPortalContent
    isPortalContent = 1
    isRADContent = 1

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
        Tests if the rule (still) applies
      """
      # An invoice transaction rule applies when the movement's 
      # parent is an invoice rule
      parent = movement.getParentValue()
      parent_rule_value = parent.getSpecialiseValue()
      if parent_rule_value is None:
        return 0        
      if parent_rule_value.getPortalType() in (
                        'Invoicing Rule', 'Invoice Rule'):
        if self._getMatchingCell(movement) is not None:
          return 1
      return 0

    security.declareProtected(Permissions.ModifyPortalContent, 'expand')
    def expand(self, applied_rule, force=0, **kw):
      """ Expands the current movement downward.
      """
      invoice_transaction_line_type = 'Simulation Movement'
      
      # First, get the simulation movement we were expanded from
      my_invoice_line_simulation = applied_rule.getParentValue()
      
      # Next, we can try to expand the rule
      if force or \
         (applied_rule.getLastExpandSimulationState()\
            not in self.getPortalReservedInventoryStateList() and \
         applied_rule.getLastExpandSimulationState()\
            not in self.getPortalCurrentInventoryStateList()):

        # Find a matching cell
        my_cell = self._getMatchingCell(my_invoice_line_simulation)

        if my_cell is not None :
          my_cell_transaction_id_list = my_cell.contentIds()
        else :
          my_cell_transaction_id_list = []

        if my_cell is not None : # else, we do nothing
          # check each contained movement and delete
          # those that we don't need
          for movement in applied_rule.objectValues():
            if movement.getId() not in my_cell_transaction_id_list :
              applied_rule.deleteContent(movement.getId())
          
          # Add every movement from the Matrix to the Simulation
          for transaction_line in my_cell.objectValues() :
            if transaction_line.getId() in applied_rule.objectIds() :
              my_simulation_movement = applied_rule[transaction_line.getId()]
            else :
              my_simulation_movement = applied_rule.newContent(
                  id = transaction_line.getId()
                , portal_type=invoice_transaction_line_type)

            # get the resource (in that order):
            #  * resource from the invoice (using deliveryValue)
            #  * price_currency from the invoice
            #  * price_currency from the parents simulation movement's
            #  deliveryValue
            #  * price_currency from the top level simulation movement's
            # orderValue
            
            resource = None
            invoice_line = my_invoice_line_simulation.getDeliveryValue()
            if invoice_line is not None :
              invoice = invoice_line.getExplanationValue()
              if hasattr(invoice, 'getResource') and \
                    invoice.getResource() is not None :
                resource = invoice.getResource()
              elif hasattr(invoice, 'getPriceCurrency') and \
                    invoice.getPriceCurrency() is not None :
                resource = invoice.getPriceCurrency()
            if resource is None :
              # search the resource on parents simulation movement's deliveries
              simulation_movement = applied_rule.getParent()
              portal_simulation = self.getPortalObject().portal_simulation
              while resource is None and \
                          simulation_movement != portal_simulation :
                delivery = simulation_movement.getDeliveryValue()
                if hasattr(delivery, 'getPriceCurrency') and \
                      delivery.getPriceCurrency() is not None :
                  resource = delivery.getPriceCurrency()
                if simulation_movement.getParent().getParent() \
                                          == portal_simulation :
                  # we are on the first simulation movement, we'll try
                  # to get the resource from it's order price currency.
                  order = simulation_movement.getOrderValue()
                  if hasattr(order, 'getPriceCurrency') and \
                      order.getPriceCurrency() is not None :
                    resource = order.getPriceCurrency()
                simulation_movement = simulation_movement\
                                            .getParent().getParent()
                
            if resource is None :
              # last resort : get the resource from the rule
              resource = transaction_line.getResource() or my_cell.getResource()
              if resource in (None, '') :
                # XXX this happen in many order, so this log is probably useless
                LOG("InvoiceTransactionRule", PROBLEM,
                    "expanding %s: without resource" % applied_rule.getPath())
            my_simulation_movement._edit(
                  source = transaction_line.getSource()
                , destination = transaction_line.getDestination()
                , source_section = my_invoice_line_simulation.getSourceSection()
                , destination_section = my_invoice_line_simulation\
                                          .getDestinationSection()
                , resource = resource
                  # calculate (quantity * price) * cell_quantity
                , quantity = (my_invoice_line_simulation.getQuantity()
                              * my_invoice_line_simulation.getPrice())
                              * transaction_line.getQuantity()
                , start_date = my_invoice_line_simulation.getStartDate()
                , stop_date  = my_invoice_line_simulation.getStopDate()
                , force_update = 1
              )
      
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
      return 1

    def isDeliverable(self, m):
      if m.getSimulationState() in self.getPortalDraftOrderStateList():
        return 0
      return 1
    
