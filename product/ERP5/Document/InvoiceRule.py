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

from zLOG import LOG

class InvoiceRule(Rule):
    """
      Invoice Rule object make sure an Invoice in the similation
      is consistent with the real invoice

      WARNING: what to do with movement split ?
    """

    # CMF Type Definition
    meta_type = 'ERP5 Invoice Rule'
    portal_type = 'Invoice Rule'
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
      # An invoice rule never applies since it is always explicitely instanciated
      # This will change in the near future : invoice will be generated following a delivery
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
      invoice_line_type = 'Simulation Movement'

      # Get the invoice where we come from
      my_invoice = applied_rule.getDefaultCausalityValue()

      # Only expand if my_invoice is not None and state is not 'confirmed'
      if my_invoice is not None:
        # Only expand invoice rule if invoice not yet confirmed (This is consistent
        # with the fact that once simulation is launched, we stick to it)
        if force or \
           (applied_rule.getLastExpandSimulationState() not in applied_rule.getPortalReservedInventoryStateList() and \
           applied_rule.getLastExpandSimulationState() not in applied_rule.getPortalCurrentInventoryStateList()):
          # First, check each contained movement and make
          # a list of invoice_line ids which do not need to be copied
          # eventually delete movement which do not exist anylonger
          existing_uid_list = []
          for movement in applied_rule.contentValues(filter={'portal_type':applied_rule.getPortalMovementTypeList()}):
            invoice_element = movement.getDeliveryValue(portal_type=applied_rule.getPortalInvoiceMovementTypeList())
            if invoice_element is None:
              # Does not exist any longer
              movement.flushActivity(invoke=0)
              applied_rule._delObject(movement.getId())  # XXXX Make sur this is not deleted if already in delivery
            else:
              if getattr(invoice_element, 'isCell', 0):
                # It is a Cell
                existing_uid_list += [invoice_element.getUid()]
              elif invoice_element.hasCellContent():
                # Do not keep head of cells
                invoice_element.flushActivity(invoke=0)
                applied_rule._delObject(movement.getId())  # XXXX Make sur this is not deleted if already in delivery
              else:
                # It is a Line
                existing_uid_list += [invoice_element.getUid()]

          # Copy each movement (line or cell) from the invoice
          for invoice_line_object in my_invoice.contentValues(filter={'portal_type':applied_rule.getPortalInvoiceMovementTypeList()}):
            try:
              if invoice_line_object.hasCellContent():
                for c in invoice_line_object.getCellValueList():
                  #LOG('Cell  in', 0, '%s %s' % (c.getUid(), existing_uid_list))
                  if c.getUid() not in existing_uid_list:
                    new_id = invoice_line_object.getId() + '_' + c.getId()
                    #LOG('Create Cell', 0, str(new_id))
                    my_invoice.portal_types.constructContent(type_name=invoice_line_type,
                        container=applied_rule,
                        id=new_id,
                        delivery_value = c,
                        deliverable = 1
                    )
                    #LOG('After Create Cell', 0, str(new_id))
              else:
                if invoice_line_object.getUid() not in existing_uid_list:
                  new_id = invoice_line_object.getId()
                  #LOG('Line', 0, str(new_id))
                  my_invoice.portal_types.constructContent(type_name=invoice_line_type,
                      container=applied_rule,
                      id=new_id,
                      delivery_value = invoice_line_object,
                      deliverable = 1,
                  )
                  #LOG('After Create Cell', 0, str(new_id))
                  # Source, Destination, Quantity, Date, etc. are
                  # acquired from the invoice and need not to be copied.
            except AttributeError:
              LOG('ERP5: WARNING', 0, 'AttributeError during expand on invoice line %s'
                                                      % invoice_line_object.absolute_url())

          # Now we can set the last expand simulation state to the current state
          applied_rule.setLastExpandSimulationState(my_invoice.getSimulationState())

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
      if m.getSimulationState() in draft_order_state:
        return 0
      return 1

    def collectSimulationMovements(self, applied_rule):
      LOG("invoiceRule", 0, "collected")

      # get every movement we want to group
      movement_list = []
      for simulation_movement in applied_rule.contentValues() :
        for rule in simulation_movement() :
          for sub_simulation_movement in rule.contentValues() :
            movement_list += [sub_simulation_movement ]

      # group movements
      root_group = self.portal_simulation.collectMovement(movement_list=movement_list, class_list=[CategoryMovementGroup])

      invoice = applied_rule.getCausalityValue()
      existing_transaction_line_id_list = invoice.contentIds()
      # sum quantities and add lines to invoice
      for group in root_group.group_list :
        orig_group_id = group.movement_list[0].getId()
        quantity = 0
        for movement in group.movement_list :
          quantity += movement.getQuantity()
        # Guess an unused name for the new movement
        if orig_group_id in existing_transaction_line_id_list :
          n = 1
          while '%s_%s' % (orig_group_id, n) in existing_transaction_line_id_list :
            n += 1
          group_id = '%s_%s' % (orig_group_id, n)
        else :
          group_id = orig_group_id
        existing_transaction_line_id_list.append(group_id)

        # add sum of movements to invoice
        invoice.newContent(portal_type = 'Accounting Transaction Line'
          , id = group_id
          , source = group.movement_list[0].getSource()
          , destination = group.movement_list[0].getDestination()
          , quantity = quantity
          )

      return
