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
from Products.CMFCore.utils import getToolByName
from Products.ERP5.Document.AccountingTransaction import AccountingTransaction
from zLOG import LOG

class Invoice(AccountingTransaction):
    # CMF Type Definition
    meta_type = 'ERP5 Invoice'
    portal_type = 'Invoice'
    add_permission = Permissions.AddPortalContent
    isPortalContent = 1
    isRADContent = 1

    # Global variables
    _transaction_line_portal_type = 'Sale Invoice Transaction Line'
    
    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.View)

    # Default Properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      , PropertySheet.Delivery
                      , PropertySheet.Task
                      , PropertySheet.Arrow
                      , PropertySheet.Movement
                      , PropertySheet.Amount
                      , PropertySheet.Reference
                      , PropertySheet.PaymentCondition
                      , PropertySheet.ValueAddedTax
                      , PropertySheet.EcoTax
                      , PropertySheet.CopyrightTax
                      , PropertySheet.Folder
                      )

    security.declareProtected(Permissions.AccessContentsInformation, 'getTotalPrice')
    def getTotalPrice(self):
      """
        Returns the total price for this invoice
      """
      aggregate = self.Invoice_zGetTotal()[0]
      return aggregate.total_price

    security.declareProtected(Permissions.AccessContentsInformation, 'getTotalQuantity')
    def getTotalQuantity(self):
      """
        Returns the total quantity for this invoice
      """
      aggregate = self.Invoice_zGetTotal()[0]
      return aggregate.total_quantity

    security.declareProtected(Permissions.AccessContentsInformation, 'getTotalNetPrice')
    def getTotalNetPrice(self):
      """
        Returns the total net price for this invoice
      """
      return self.Invoice_zGetTotalNetPrice()

    security.declareProtected(Permissions.ModifyPortalContent, 'buildInvoiceTransactionList')
    def buildInvoiceTransactionList(self):
      """
        Retrieve all invoices transaction lines into the simulation
      """
      reindexable_movement_list = []

      parent_simulation_line_list = []
      # Browse invoice lines
      for o in self.getMovementList(portal_type = self.getPortalInvoiceMovementTypeList()) :
        parent_simulation_line_list += [x for x in o.getDeliveryRelatedValueList() \
                                        if x.getPortalType()=='Simulation Movement']
      invoice_transaction_rule_list = []
      simulation_line_list = []
      for o in parent_simulation_line_list:
        for rule in o.objectValues():
          invoice_transaction_rule_list.append(rule)
          simulation_line_list += rule.objectValues()
      #LOG('buildInvoiceTransactionList simulation_line_list',0,simulation_line_list)
      from Products.ERP5.MovementGroup import CategoryMovementGroup
      class_list = [CategoryMovementGroup, ]
      root_group = self.portal_simulation.collectMovement(simulation_line_list,class_list=class_list)

      if root_group is not None:
        #LOG('buildInvoiceTransactionList root_group.group_list',0,root_group.group_list)
        # First delete existing accounting lines
        self.deleteContent(self.contentIds(
            filter={'portal_type':self.getPortalDeliveryMovementTypeList()}))
        # we don't want to overwrite the Invoice Lines
        existing_invoice_line_id_list = self.contentIds()
        for category_group in root_group.group_list:
          #LOG('buildInvoiceTransactionList category_group.group_list',0,category_group.group_list)
          #LOG('buildInvoiceTransactionList category_group.movement_list',0,category_group.movement_list)
          # sum quantities and add lines to invoice
          quantity = 0.0
          orig_group_id = None
          reference_movement = None
          for movement in category_group.movement_list :
            quantity += movement.getQuantity()
            # Guess an unused name for the new movement
            if orig_group_id is None:
              orig_group_id = movement.getId()
              reference_movement = movement
          #LOG('buildInvoiceTransactionList orig_group_id',0,orig_group_id)
          #LOG('buildInvoiceTransactionList existing_invoice_line_id_list',0,existing_invoice_line_id_list)
          if orig_group_id in existing_invoice_line_id_list :
            n = 1
            while '%s_%s' % (orig_group_id, n) in existing_invoice_line_id_list :
              n += 1
            group_id = '%s_%s' % (orig_group_id, n)            
          else :
            group_id = orig_group_id          
          existing_invoice_line_id_list.append(group_id)
            
          # add sum of movements to invoice
          #LOG('buildInvoiceTransactionList group_id',0,group_id)          
          #LOG('buildInvoiceTransactionList reference_movement',0,str(reference_movement.getRelativeUrl()))
          #LOG('buildInvoiceTransactionList reference_movement',0,str(reference_movement.showDict()))
          #LOG('buildInvoiceTransactionList reference_movement',0,str(reference_movement.getSource()))
          #LOG('buildInvoiceTransactionList reference_movement',0,str(reference_movement.getDestination()))
          sale_invoice_transaction_line_item = getattr(self, group_id, None)          
          if sale_invoice_transaction_line_item is None :
            sale_invoice_transaction_line_item = self.newContent(
                portal_type = self._transaction_line_portal_type
              , id = group_id
              , source = reference_movement.getSource()
              , destination = reference_movement.getDestination()
              , quantity = quantity
            )
            if self.getDestinationSection() != reference_movement.getDestinationSection():
              sale_invoice_transaction_line_item._setDestinationSection(reference_movement.getDestinationSection())
            if self.getSourceSection() != reference_movement.getSourceSection():
              sale_invoice_transaction_line_item._setSourceSection(reference_movement.getSourceSection())
            #LOG('buildInvoiceTransactionList sale_invoice_transaction_line',0,str(sale_invoice_transaction_line_item.showDict())) 
          else :
            sale_invoice_transaction_line_item.edit(
                source = reference_movement.getSource()
              , destination = reference_movement.getDestination()
              , quantity = quantity
              , force_update = 1
            )
            if self.getDestinationSection() != reference_movement.getDestinationSection():
              sale_invoice_transaction_line_item._setDestinationSection(reference_movement.getDestinationSection())
            if self.getSourceSection() != reference_movement.getSourceSection():
              sale_invoice_transaction_line_item._setSourceSection(reference_movement.getSourceSection())

          # What do we really need to update in the simulation movement ?
          for movement in category_group.movement_list :
            if movement.getPortalType() == 'Simulation Movement' :
              movement._setDeliveryValue(sale_invoice_transaction_line_item)
              reindexable_movement_list.append(movement)

      # we now reindex the movements we modified
      for movement in reindexable_movement_list :
        movement.immediateReindexObject()
      return [self]

    security.declareProtected(Permissions.ModifyPortalContent, 'buildPaymentTransactionList')
    def buildPaymentTransactionList(self):
      """
        Retrieve all payments transaction lines into the simulation

        For this rule, we don't want to group anything : legally, we need to have every payment matching the quantity of a sale invoice.

        Warning : this code is not good, it is too simple, but is here to fulfill a very specific need at the moment.
      """
      reindexable_movement_list = []
      payment_transaction_list = []

      parent_simulation_line_list = []
      for o in self.contentValues(filter={'portal_type':'Sale Invoice Transaction Line'}) :
        parent_simulation_line_list += [x for x in o.getDeliveryRelatedValueList() \
                                        if x.getPortalType()=='Simulation Movement']
      payment_transaction_rule_list = []
      simulation_line_list = []
      for o in parent_simulation_line_list:
        for rule in o.objectValues():
          payment_transaction_rule_list.append(rule)
          simulation_line_list += rule.objectValues()
      #LOG('buildPaymentTransactionList simulation_line_list',0,simulation_line_list)

      # create payment transaction
      accounting_module = self.accounting
      payment_type = 'Payment Transaction'
      payment_id = str(accounting_module.generateNewId())
      payment_transaction = accounting_module.newContent(portal_type = payment_type
          , id = payment_id
          , reference = self.getReference()
          , resource = self.getResource()
          , start_date = self.getStartDate()
          , source_payment = self.getSourcePayment()
          , source_section = self.getSourceSection()
          , destination_payment = self.getDestinationPayment()
          , destination_section = self.getDestinationSection()
          )
      #LOG('buildPaymentTransactionList payment_transaction', 0, repr(( payment_transaction.showDict() )))

      # fill quantity in lines
      for movement in simulation_line_list :
      
          quantity = movement.getQuantity()
          movement_id = movement.getId()

          payment_transaction_line = getattr(payment_transaction, movement_id, None)
          if payment_transaction_line is None :
            payment_transaction.newContent(
                portal_type = 'Accounting Transaction Line'
              , id = movement_id
            )
            previous_quantity = 0.0
          else :
            previous_quantity = payment_transaction_line.getQuantity()
          if previous_quantity is not None:
            quantity = quantity + previous_quantity
          payment_transaction_line.edit(
              quantity = quantity
            , source = movement.getSource()
            , destination = movement.getDestination()
            , force_update = 1
            )

          #LOG('buildPaymentTransactionList movement', 0, repr(( movement.showDict() )))              
          #LOG('buildPaymentTransactionList payment_transaction_line', 0, repr(( payment_transaction_line.showDict() )))              
              
          # What do we really need to update in the simulation movement ?
          if movement.getPortalType() == 'Simulation Movement' :
            movement._setDeliveryValue(payment_transaction_line)
            reindexable_movement_list.append(movement)

      # we now reindex the movements we modified
      for movement in reindexable_movement_list :
        movement.immediateReindexObject()
      return [self]
