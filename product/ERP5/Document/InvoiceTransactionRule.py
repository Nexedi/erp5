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
from Products.ERP5Type.XMLMatrix import XMLMatrix
from Products.CMFCore.utils import getToolByName
from UserDict import UserDict

from zLOG import LOG

class InvoiceTransactionRule(Rule, XMLMatrix):
    """
      Invoice Transaction Rule object make sure an Invoice in the similation
      is consistent with the real invoice

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
      # An invoice transaction rule applies when the movement's parent is an invoice rule
      parent = movement.getParent()
      parent_rule_id = parent.getSpecialiseId()
      if ('default_invoice_rule' in parent_rule_id) \
        or ('default_invoicing_rule' in parent_rule_id) :
        return 1
      return 0

    # Simulation workflow
    security.declareProtected(Permissions.ModifyPortalContent, 'expand')
    def expand(self, applied_rule, force=0, **kw):
      """
        Expands the current movement downward.

        -> new status -> expanded

        An applied rule can be expanded only if its parent movement
        is expanded.
      """

      invoice_transaction_line_type = 'Simulation Movement'

      # First, we need the region
      my_order = applied_rule.getRootAppliedRule().getCausalityValue()
      
      my_destination = my_order.getDestinationValue() # maybe DestinationSection instead of Destination
      my_destination_address = my_destination.get('default_address')
      if my_destination_address is None :
        my_destination_region = None
        LOG('InvoiceTransactionRule.expand :', 0, 'Problem : destination_region is None')
      else :
        my_destination_region = my_destination_address.getRegionValue()
      #LOG('InvoiceTransactionRule.expand :', 0, repr(( 'region', my_order, my_destination, my_destination_address, my_destination_region, )))
      # Then, the product line
      my_invoice_line_simulation = applied_rule.getParent()
      my_resource = my_invoice_line_simulation.getResourceValue()
      if my_resource is None :
        my_product_line = None
        LOG('InvoiceTransactionRule.expand :', 0, 'Problem : product_line is None')
      else :
        my_product_line = my_resource.getProductLineValue()
      #LOG('InvoiceTransactionRule.expand :', 0, repr(( 'product_line', my_invoice_line_simulation, my_resource, my_product_line, )))
      # Finally, the InvoiceTransactionRule Matrix
      my_invoice_transaction_rule = applied_rule.getSpecialiseValue()

      # Next, we can try to expand the rule
      if force or \
         (applied_rule.getLastExpandSimulationState() not in self.getPortalReservedInventoryStateList() and \
         applied_rule.getLastExpandSimulationState() not in self.getPortalCurrentInventoryStateList()):

        # get the corresponding Cell
        new_kw = (('product_line', my_product_line), ('region', my_destination_region))
        my_cell = my_invoice_transaction_rule.getCellByPredicate(*new_kw) #XXX WARNING ! : my_cell can be None
        #LOG('InvoiceTransactionRule.expand :', 0, repr(( 'cell', my_cell, my_invoice_transaction_rule.contentValues(), len(my_invoice_transaction_rule.searchFolder()), )))

        if my_cell is not None :
          my_cell_transaction_id_list = map(lambda x : x.getId(), my_cell.contentValues())
        else :
          my_cell_transaction_id_list = []

        if my_cell is not None : # else, we do nothing
          # check each contained movement and delete
          # those that we don't need
          for movement in applied_rule.objectValues():
            if movement.getId() not in my_cell_transaction_id_list :
              movement.flushActivity(invoke=0)
              applied_rule.deleteContent(movement.getId())

          # Add every movement from the Matrix to the Simulation
          for transaction_line in my_cell.objectValues() :
            if transaction_line.getId() in applied_rule.objectIds() :
              simulation_movement = applied_rule[transaction_line.getId()]
            else :
              simulation_movement = applied_rule.newContent(id=transaction_line.getId()
                  , portal_type=invoice_transaction_line_type)
            #LOG('InvoiceTransactionRule.expand :', 0, repr(( 'movement', simulation_movement, transaction_line.getSource(), transaction_line.getDestination(), (my_invoice_line_simulation.getQuantity() * my_invoice_line_simulation.getPrice()) * transaction_line.getQuantity() )))
            simulation_movement._edit(source = transaction_line.getSource()
                , destination = transaction_line.getDestination()
                , quantity = (my_invoice_line_simulation.getQuantity() * my_invoice_line_simulation.getPrice())
                  * transaction_line.getQuantity()
                  # calculate (quantity * price) * cell_quantity
                , force_update = 1
              )

        # Now we can set the last expand simulation state to the current state
        #XXX Note : this is wrong, as there isn't always a sale invoice when we expand this rule.
        #applied_rule.setLastExpandSimulationState(my_invoice.getSimulationState())

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

    # Matrix related
    security.declareProtected( Permissions.ModifyPortalContent, 'newCellContent' )
    def newCellContent(self, id):
      """
          This method can be overriden
      """
      self.invokeFactory(type_name='Accounting Rule Cell',id=id)
      new_cell = self.get(id)
      return new_cell

    security.declareProtected(Permissions.ModifyPortalContent, 'updateMatrix')
    def updateMatrix(self) :
      """
      Makes sure that the cells are consistent with the predicates.
      """
      base_id = 'vat_per_region'
      kwd = {'base_id': base_id}
      new_range = self.InvoiceTransactionRule_asCellRange() # This is a site dependent script
      #LOG('InvoiceTransactionRule.updateMatrix :', 0, repr(( new_range, self.contentIds(), [x for x in self.searchFolder()], )))

      self._setCellRange(*new_range, **kwd)
      cell_range_key_list = self.getCellRangeKeyList(base_id = base_id)
      if cell_range_key_list <> [[None, None]] :
        for k in cell_range_key_list :
          c = self.newCell(*k, **kwd)
          c.edit( mapped_value_property_list = ( 'title',),
                  predicate_operator = 'SUPERSET_OF',
                  predicate_category_list = filter(lambda k_item: k_item is not None, k),
                  title = 'Transaction %s' % repr(map(lambda k_item : self.restrictedTraverse(k_item).getTitle(), k)),
                  force_update = 1
                )
      else :
        # If only one cell, delete it
        cell_range_id_list = self.getCellRangeIdList(base_id = base_id)
        for k in cell_range_id_list :
          if self.get(k) is not None :
            self[k].flushActivity(invoke=0)
            self[k].immediateReindexObject()
            self._delObject(k)

    security.declareProtected(Permissions.View, 'getCellByPredicate')
    def getCellByPredicate(self, *kw) :
      """
      Returns the cell that match the *kw predicate.

      *kw is a list of couple (base_category_title, category) we want to test against the predicates
      """
      base_id = 'vat_per_region'
      kwd = {'base_id': base_id}

      predicate_list = self.InvoiceTransactionRule_asCellRange() # This is a site dependent script
      portal_url = getToolByName(self, 'portal_url')

      class Dummy(UserDict) :
        def isMemberOf(self, category) :
          if category in self.data.values() :
            return 1
          return 0
        def getProperty(self, key) :
          return self.data.get(key)

      my_dummy = Dummy()
      for (k,v) in kw :
        if hasattr(v, 'getCategoryRelativeUrl') :
          my_dummy[k]=v.getCategoryRelativeUrl(base=1)
        else :
          my_dummy[k]=v

      selected_predicate_list = []
      # predicate_list is a list of list of predicate, each dimension is one sublist
      for predicate_dimension_item_list in predicate_list :
        for predicate in predicate_dimension_item_list :
          # test predicate against *kw and append to selected_predicate_list if they match
          predicate = portal_url.restrictedTraverse(predicate)
          if predicate.test(my_dummy) :
            selected_predicate_list.append(predicate.getRelativeUrl())
            break # we only want to add one predicate per dimension to the list
          # LOG('cellByPredicate', 0, repr(( 'after', predicate, selected_predicate_list )))
        # LOG('cellByPredicate', 0, repr(( 'after loop', predicate_dimension_item_list, selected_predicate_list )))
      return self.getCell(*selected_predicate_list, **kwd)

