##############################################################################
#
# Copyright (c) 2004 Nexedi SARL and Contributors. All Rights Reserved.
#          Sebastien Robin <seb@nexedi.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################



#
# Skeleton ZopeTestCase
#

from random import randint

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE'] = os.path.join(os.getcwd(), 'zLOG.log')
os.environ['EVENT_LOG_SEVERITY'] = '-300'

from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager, noSecurityManager
from DateTime import DateTime
from Acquisition import aq_base, aq_inner
from zLOG import LOG
from Products.ERP5Type.DateUtils import addToDate
from Products.ERP5Type.tests.Sequence import Sequence, SequenceList
import time
import os
from Products.ERP5Type import product_path
from DateTime import DateTime

class Test(ERP5TypeTestCase):
  """
  This is the list of test

  test setNextStartDate : 
  - every hour
  - at 6, 10, 15, 21 every day
  - every day at 10
  - every 3 days at 14 and 15 and 17
  - every monday and friday, at 6 and 15
  - every 1st and 15th every month, at 12 and 14
  - every 1st day of every 2 month, at 6
  """

  # Different variables used for this test
  run_all_test = 0
  source_company_id = 'Nexedi'
  destination_company_id = 'MyOrg'
  account1 = 'prestation_service'
  account2 = 'creance_client'
  account3 = 'tva_collectee_196'
  quantity1 = 3
  price1 = 72
  total_price1 = 216

  def getTitle(self):
    return "Invoices"

  def getBusinessTemplateList(self):
    """
    """
    return ('erp5_trade','erp5_accounting','erp5_pdm')

  def enableLightInstall(self):
    """
    You can override this. Return if we should do a light install (1) or not (0)
    """
    return 1

  def enableActivityTool(self):
    """
    You can override this. Return if we should create (1) or not (0) an activity tool
    """
    return 1

  def getSaleOrderModule(self):
    return getattr(self.getPortal(),'sale_order',None)

  def getSalePackingListModule(self):
    return getattr(self.getPortal(),'sale_packing_list',None)

  def getProductModule(self):
    return getattr(self.getPortal(),'product',None)

  def getAccountModule(self):
    return getattr(self.getPortal(),'account',None)

  def getAccountingModule(self):
    return getattr(self.getPortal(),'accounting',None)

  def login(self, quiet=0, run=run_all_test):
    uf = self.getPortal().acl_users
    uf._doAddUser('seb', '', ['Manager'], [])
    user = uf.getUserById('seb').__of__(uf)
    newSecurityManager(None, user)

  def afterSetUp(self, quiet=1, run=1):
    """
    """
    # Create categories
    self.category_tool = self.getCategoryTool()
    o = self.category_tool.region.newContent(portal_type='Category', id='europe')
    o = o.newContent(portal_type='Category', id='west')
    o.newContent(portal_type='Category', id='france')

    self.category_tool.pcg.newContent(portal_type='Category', id='1')

    o = self.category_tool.product_line.newContent(portal_type='Category', id='storever')
    o.newContent(portal_type='Category', id='notebook')
    # Create a product
    product_module = self.getProductModule()
    product = product_module.newContent(portal_type='Product',id='1', product_line='storever/notebook')
    product.setPricedQuantity(1.0)
    product.setBasePrice(self.price1)
    # Create a destination with region
    organisation_module = self.getOrganisationModule()
    organisation = organisation_module.newContent(portal_type='Organisation',id=self.destination_company_id)
    organisation.newContent(id='default_address', portal_type='Address', region='europe/west/france')
    organisation = organisation_module.newContent(portal_type='Organisation',id=self.source_company_id)
    # Create some accounts
    account_module = self.getAccountModule()
    account_module.newContent(portal_type='Account',id='prestation_service')
    account_module.newContent(portal_type='Account',id='creance_client')
    account_module.newContent(portal_type='Account',id='tva_collectee_196')
    account_module.newContent(portal_type='Account',id='dette_fournisseur')
    account_module.newContent(portal_type='Account',id='banques_etablissements_financiers')
    account_module.newContent(portal_type='Account',id='account1')
    account_module.newContent(portal_type='Account',id='account2')
    account_module.newContent(portal_type='Account',id='account3')
    account_module.newContent(portal_type='Account',id='account4')
    # Create some predicates
    self.invoice_transaction_rule = self.getPortal().portal_rules.default_invoice_transaction_rule
    self.invoice_transaction_rule.deleteContent(self.invoice_transaction_rule.contentIds()) # delete anything inside the rule first

    self.predicate_product1 = self.invoice_transaction_rule.newContent(id='product_1', title='product_1', portal_type='Predicate Group', string_index='product', int_index='1', membership_criterion_base_category_list=['product_line',], membership_criterion_category_list=['product_line/storever/notebook'], immediate_reindex=1)
    self.predicate_region1 = self.invoice_transaction_rule.newContent(id='region_1', title='region_1', portal_type='Predicate Group', string_index='region', int_index='1', membership_criterion_base_category_list=['region',], membership_criterion_category_list=['region/europe/west/france'], immediate_reindex=1)
    #self.invoice_transaction_rule.recursiveImmediateReindexObject()
    # Update the matrix
    self.invoice_transaction_rule.updateMatrix()
    # add some values to the transaction lines in the accounting rule cell
    cell_list = self.invoice_transaction_rule.contentValues(filter={'portal_type':'Accounting Rule Cell'})
    self.assertEqual(len(cell_list), 1) # Check that the rule is here
    self.product1_region1_cell = getattr(self.invoice_transaction_rule, 'vat_per_region_0_0', None)
    self.failUnless(self.product1_region1_cell != None)

    self.product1_region1_line1 = getattr(self.product1_region1_cell, 'income', None)
    self.failUnless(self.product1_region1_line1 != None)
    self.product1_region1_line1.edit(title='income', source='account/prestation_service', destination='account/account1', quantity=1)

    self.product1_region1_line2 = getattr(self.product1_region1_cell, 'receivable', None)
    self.failUnless(self.product1_region1_line2 != None)
    self.product1_region1_line2.edit(title='receivable', source='account/prestation_service', destination='account/account2', quantity=0.5)
    # flush activities
    #get_transaction().commit()
    #self.tic()

  def stepTic(self, **kw):
    self.tic()

  def stepFirstCheck(self,sequence=None, sequence_list=None,**kw):
    """
    Do some basics checking
    """
    # Check the default delivery rule
    portal_rules = self.getRuleTool()
    self.failUnless('default_order_rule' in portal_rules.objectIds())
    # Check defaults accounts
    account_module = self.getAccountModule()
    self.failUnless(self.account1 in account_module.objectIds())
    self.failUnless(self.account2 in account_module.objectIds())
    self.failUnless(self.account3 in account_module.objectIds())
    # Check product 
    product_module = self.getProductModule()
    product = product_module['1']
    sequence.edit(product=product)
    self.assertEquals(product.getBasePrice(),self.price1)

  def stepCreateSaleOrder(self,sequence=None, sequence_list=None,**kw):
    """
    """
    order_module = self.getSaleOrderModule()
    order = order_module.newContent(portal_type='Sale Order')
    order.setStartDate(DateTime('2004-11-20'))
    order.setStopDate(DateTime('2004-11-24'))
    destination_organisation = self.getOrganisationModule()[self.destination_company_id]
    order.setDestinationValue(destination_organisation)
    source_organisation = self.getOrganisationModule()[self.source_company_id]
    order.setSourceValue(source_organisation)
    line1 = order.newContent(portal_type='Sale Order Line',id='1')
    product = sequence.get('product')
    line1.setResourceValue(product)
    line1.setTargetQuantity(self.quantity1)
    line1.setPrice(self.price1)
    sequence.edit(order=order)
    self.assertEquals(line1.getTotalPrice(),self.total_price1)

  def stepCreateOrderRule(self,sequence=None, sequence_list=None,**kw):
    """
    """
    order = sequence.get('order')
    order._createOrderRule()

  def stepCreateDeliveryRule(self,sequence=None, sequence_list=None,**kw):
    """
    Only if we want a packing list with no order
    """
    packing_list = sequence.get('packing_list')
    packing_list._createDeliveryRule()

  def stepCheckOrderRule(self,sequence=None, sequence_list=None,**kw):
    order = sequence.get('order')
    simulation_tool = self.getSimulationTool()
    # Check that there is an applied rule for our packing list
    rule_list = [x for x in simulation_tool.objectValues() if x.getCausalityValue()==order]
    self.assertEquals(len(rule_list),1)
    order_rule = rule_list[0]
    sequence.edit(order_rule=order_rule)
    rule_line_list = order_rule.objectValues()
    order_line_list = order.objectValues()
    self.assertEquals(len(order_line_list,),len(rule_line_list))
    self.assertEquals(1,len(rule_line_list))
    rule_line = rule_line_list[0]
    sequence.edit(order_rule_line=rule_line)
    order_line = order_line_list[0]
    self.assertEquals(rule_line.getTargetQuantity(),self.quantity1)
    self.assertEquals(rule_line.getPrice(),self.price1)
    self.assertEquals(rule_line.getOrderValue(),order_line)
    self.assertEquals(rule_line.getStartDate(),order_line.getStartDate())
    self.assertEquals(rule_line.getStopDate(),order_line.getStopDate())
    self.assertEquals(rule_line.getPortalType(),'Simulation Movement')
    self.assertEquals(rule_line.getResourceValue(),order_line.getResourceValue())

  def stepCheckInvoicingRule(self,sequence=None, sequence_list=None,**kw):
    order_rule_line = sequence.get('order_rule_line')
    invoicing_rule_list = order_rule_line.objectValues()
    self.assertEquals(len(invoicing_rule_list),1)
    invoicing_rule = invoicing_rule_list[0]
    sequence.edit(invoicing_rule=invoicing_rule)
    self.assertEquals(invoicing_rule.getSpecialiseId(),'default_invoicing_rule')
    self.assertEquals(invoicing_rule.getPortalType(),'Applied Rule')
    rule_line_list = invoicing_rule.objectValues()
    self.assertEquals(len(rule_line_list),1)
    rule_line = rule_line_list[0]
    sequence.edit(invoicing_rule_line=rule_line)
    product = sequence.get('product')
    self.assertEquals(rule_line.getTargetQuantity(),self.quantity1)
    self.assertEquals(rule_line.getPrice(),self.price1)
    self.assertEquals(rule_line.getPortalType(),'Simulation Movement')
    self.assertEquals(rule_line.getResourceValue(), product)
    

  def stepCheckDeliveryRule(self,sequence=None, sequence_list=None,**kw):
    packing_list = sequence.get('packing_list')
    self.failUnless(packing_list is not None)
    simulation_tool = self.getSimulationTool()
    # Check that there is an applied rule for our packing list
    rule_list = [x for x in simulation_tool.objectValues() if x.getCausalityValue()==packing_list]
    self.assertEquals(len(rule_list),1)
    packing_list_rule = rule_list[0]
    sequence.edit(packing_list_rule=packing_list_rule)
    rule_line_list = packing_list_rule.objectValues()
    packing_list_line_list = packing_list.objectValues()
    self.assertEquals(len(packing_list_line_list,),len(rule_line_list))
    self.assertEquals(1,len(rule_line_list))
    rule_line = rule_line_list[0]
    packing_list_line = packing_list_line_list[0]
    self.assertEquals(rule_line.getQuantity(),self.quantity1)
    self.assertEquals(rule_line.getPrice(),self.price1)
    self.assertEquals(rule_line.getDeliveryValue(),packing_list_line)
    self.assertEquals(rule_line.getStartDate(),packing_list_line.getStartDate())
    self.assertEquals(rule_line.getStopDate(),packing_list_line.getStopDate())
    self.assertEquals(rule_line.getPortalType(),'Simulation Movement')

  def stepCheckInvoiceTransactionRule(self, sequence=None, sequence_list=None, **kw) :
    invoicing_rule_line = sequence.get('invoicing_rule_line')
    invoice_transaction_rule_list = invoicing_rule_line.objectValues()
    self.assertEquals(len(invoice_transaction_rule_list),1)
    invoice_transaction_rule = invoice_transaction_rule_list[0]
    sequence.edit(invoice_transaction_rule=invoice_transaction_rule)
    self.assertEquals(invoice_transaction_rule.getSpecialiseId(),'default_invoice_transaction_rule')
    self.assertEquals(invoice_transaction_rule.getPortalType(),'Applied Rule')
    rule_line_list = invoice_transaction_rule.objectValues()
    self.assertEquals(len(rule_line_list),3)
    for rule_line in rule_line_list :
      if rule_line.getId() == 'income' :
        self.assertEquals(rule_line.getSourceValue(), self.getAccountModule()['prestation_service'])
        self.assertEquals(rule_line.getDestinationValue(), self.getAccountModule()['account1'])
        self.assertEquals(rule_line.getPortalType(),'Simulation Movement')
        self.assertEquals(rule_line.getQuantity(), 3 * 72 * 1)
      elif rule_line.getId() == 'receivable' :
        self.assertEquals(rule_line.getSourceValue(), self.getAccountModule()['prestation_service'])
        self.assertEquals(rule_line.getDestinationValue(), self.getAccountModule()['account2'])
        self.assertEquals(rule_line.getPortalType(),'Simulation Movement')
        self.assertEquals(rule_line.getQuantity(), 3 * 72 * 0.5)
        sequence.edit(invoice_transaction_rule_line_revceivable=rule_line)
      elif rule_line.getId() == 'collected_vat' :
        self.assertEquals(rule_line.getSourceValue(), self.getAccountModule()['tva_collectee_196']) # this is defined in SaleInvoiceTransaction_init in ERP5 skins.
      else :
        raise self.failureException, 'Unknown movement : %s' % repr(rule_line)

  def stepCheckPaymentRule(self, sequence=None, sequence_list=None, **kw) :
    invoice_transaction_rule_line_revceivable = sequence.get('invoice_transaction_rule_line_revceivable')
    payment_rule_list = invoice_transaction_rule_line_revceivable.objectValues()
    self.assertEquals(len(payment_rule_list),1)
    payment_rule = payment_rule_list[0]
    sequence.edit(payment_rule=payment_rule)
    self.assertEquals(payment_rule.getSpecialiseId(),'default_payment_rule')
    self.assertEquals(payment_rule.getPortalType(),'Applied Rule')
    rule_line_list = payment_rule.objectValues()
    self.assertEquals(len(rule_line_list),2)
    for rule_line in rule_line_list :
      if rule_line.getId() == 'receivable' :
        self.assertEquals(rule_line.getPortalType(),'Simulation Movement')
        self.assertEquals(rule_line.getQuantity(), 0 - invoice_transaction_rule_line_revceivable.getQuantity())
        sequence.edit(payment_rule_line_receivable=rule_line)
      elif rule_line.getId() == 'bank' :
        self.assertEquals(rule_line.getPortalType(),'Simulation Movement')
        self.assertEquals(rule_line.getQuantity(), invoice_transaction_rule_line_revceivable.getQuantity())
        sequence.edit(payment_rule_line_bank=rule_line)
      else :
        raise self.failureException, 'Unknown movement : %s' % repr(rule_line)

  def stepBuildDeliveryList(self,sequence=None, sequence_list=None,**kw):
    """
    """
    order = sequence.get('order')

    # It should be in a script inside the workflow
    order.buildDeliveryList()

  def stepBuildInvoiceList(self,sequence=None, sequence_list=None,**kw):
    """
    """
    packing_list = sequence.get('packing_list')

    # It should be in a script inside the workflow
    packing_list.buildInvoiceList()

  def stepBuildInvoiceTransactionList(self, sequence=None, sequence_list=None, **kw) :
    invoice = sequence.get('invoice')

    # It should be in a script inside the workflow
    invoice.buildInvoiceTransactionList()

  def stepBuildPaymentTransactionList(self, sequence=None, sequence_list=None, **kw) :
    invoice = sequence.get('invoice')

    # It should be in a script inside the workflow
    invoice.buildPaymentTransactionList()

  def stepCheckPackingList(self,sequence=None, sequence_list=None,**kw):
    """
    """
    packing_list_module = self.getSalePackingListModule()
    order_rule = sequence.get('order_rule')
    order = sequence.get('order')
    sale_packing_list_list = []
    for o in packing_list_module.objectValues():
      if o.getCausalityValue() == order:
        sale_packing_list_list.append(o)
    self.assertEquals(len(sale_packing_list_list),1)
    sale_packing_list = sale_packing_list_list[0]
    sale_packing_list_line_list = sale_packing_list.objectValues()
    self.assertEquals(len(sale_packing_list_line_list),1)
    sale_packing_list_line = sale_packing_list_line_list[0]
    product = sequence.get('product')
    self.assertEquals(sale_packing_list_line.getResourceValue(),product)
    self.assertEquals(sale_packing_list_line.getPrice(),self.price1)
    LOG('sale_packing_list_line.showDict()',0,sale_packing_list_line.showDict())
    self.assertEquals(sale_packing_list_line.getQuantity(),self.quantity1)
    self.assertEquals(sale_packing_list_line.getTotalPrice(),self.total_price1)
    sequence.edit(packing_list=sale_packing_list)


  def stepCheckInvoice(self,sequence=None, sequence_list=None,**kw):
    """
    """
    accounting_module = self.getAccountingModule()
    #invoicing_rule = sequence.get('invoicing_rule')
    sale_invoice_transaction_list = accounting_module.objectValues()
    #for o in accounting_module.objectValues():
      #if invoicing_rule.getDeliveryValue() == o:
        #sale_invoice_transaction_list.append(o)
    self.assertEquals(len(sale_invoice_transaction_list),1)
    sale_invoice = sale_invoice_transaction_list[0]
    sequence.edit(invoice=sale_invoice)
    sale_invoice_line_list = sale_invoice.contentValues(filter={'portal_type':'Invoice Line'})
    LOG('IL', 0, repr([[i, i.getQuantity(), i.getPrice()] for i in sale_invoice_line_list]))
    self.assertEquals(len(sale_invoice_line_list),1)
    sale_invoice_line = sale_invoice_line_list[0]
    sequence.edit(invoice_line=sale_invoice_line)
    product = sequence.get('product')
    self.assertEquals(sale_invoice_line.getResourceValue(),product)
    self.assertEquals(sale_invoice_line.getPrice(),self.price1)
    self.assertEquals(sale_invoice_line.getQuantity(),self.quantity1)
    self.assertEquals(sale_invoice_line.getTotalPrice(),self.total_price1)
    LOG('ILR', 0, sale_invoice_line.getDeliveryRelatedValueList())


  def stepCheckInvoiceTransaction(self,sequence=None, sequence_list=None,**kw):
    """
    """
    accounting_module = self.getAccountingModule()
    sale_invoice_transaction_list = accounting_module.objectValues()
    self.assertEquals(len(sale_invoice_transaction_list),1)
    sale_invoice = sale_invoice_transaction_list[0]
    sale_invoice_line_list = sale_invoice.contentValues(filter={'portal_type':'Sale Invoice Transaction Line'})
    LOG('SITL', 0, repr([[i, i.getQuantity(), i.getPrice()] for i in sale_invoice_line_list]))
    self.assertEquals(len(sale_invoice_line_list),3)

    for transaction_line in sale_invoice_line_list :
      if transaction_line.getId() == 'income' :
        self.assertEquals(transaction_line.getSourceValue(), self.getAccountModule()['prestation_service'])
        self.assertEquals(transaction_line.getDestinationValue(), self.getAccountModule()['account1'])
        self.assertEquals(transaction_line.getQuantity(), 3 * 72 * 1)
      elif transaction_line.getId() == 'receivable' :
        self.assertEquals(transaction_line.getSourceValue(), self.getAccountModule()['prestation_service'])
        self.assertEquals(transaction_line.getDestinationValue(), self.getAccountModule()['account2'])
        self.assertEquals(transaction_line.getQuantity(), 3 * 72 * 0.5)
        sequence.edit(invoice_transaction_line_receivable=transaction_line)
      elif transaction_line.getId() == 'collected_vat' :
        self.assertEquals(transaction_line.getSourceValue(), self.getAccountModule()['tva_collectee_196']) # this is defined in SaleInvoiceTransaction_init in ERP5 skins.
      else :
        raise self.failureException

  def stepCheckPaymentTransaction(self, sequence=None, sequence_list=None, **kw) :
    """
    """
    accounting_module = self.getAccountingModule()
    payment_transaction_list = accounting_module.contentValues(filter={'portal_type':'Payment Transaction'})
    self.assertEquals(len(payment_transaction_list),1)
    payment_transaction = payment_transaction_list[0]
    payment_transaction_line_list = payment_transaction.objectValues()
    LOG('ATL', 0, repr([[i, i.getQuantity()] for i in payment_transaction_line_list]))
    self.assertEquals(len(payment_transaction_line_list),3)

    invoice_transaction_line_receivable = sequence.get('invoice_transaction_line_receivable')
    for transaction_line in payment_transaction_line_list :
      if transaction_line.getId() == 'receivable' :
        self.assertEquals(transaction_line.getSourceValue(), self.getAccountModule()['creance_client'])
        self.assertEquals(transaction_line.getQuantity(), 0 - invoice_transaction_line_receivable.getQuantity())
      elif transaction_line.getId() == 'bank' :
        self.assertEquals(transaction_line.getSourceValue(), self.getAccountModule()['banques_etablissements_financiers'])
        self.assertEquals(transaction_line.getQuantity(), invoice_transaction_line_receivable.getQuantity())
      elif transaction_line.getId() == 'payable' :
        self.assertEquals(transaction_line.getSourceValue(), self.getAccountModule()['dette_fournisseur']) # this is defined in SaleInvoiceTransaction_init in ERP5 skins.
      else :
        raise self.failureException


  def testInvoice(self, quiet=0,run=1):
    """
    We will play many sequences
    """
    sequence_list = SequenceList()
    # Simple sequence 
    # ... Fails
    sequence_string = 'FirstCheck CreateSaleOrder CreateOrderRule Tic' \
                    + ' CheckOrderRule BuildDeliveryList Tic' \
                    + ' CheckPackingList CheckInvoicingRule BuildInvoiceList Tic' \
                    + ' CheckInvoice CheckInvoiceTransactionRule BuildInvoiceTransactionList Tic ' \
                    + ' CheckInvoiceTransaction CheckPaymentRule BuildPaymentTransactionList Tic' \
                    + ' CheckPaymentTransaction'
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self)




if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(Test))
        return suite

