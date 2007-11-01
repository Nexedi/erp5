#############################################################################
#
# Copyright (c) 2004 Nexedi SARL and Contributors. All Rights Reserved.
#          Jerome Perrin <jerome@nexedi.com>
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

"""Tests some accounting functionality.

"""

import unittest
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import reindex
from Products.DCWorkflow.DCWorkflow import ValidationFailed
from AccessControl.SecurityManagement import newSecurityManager
from Products.ERP5Type.tests.Sequence import Sequence, SequenceList
from DateTime import DateTime

SOURCE = 'source'
DESTINATION = 'destination'
RUN_ALL_TESTS = 1
QUIET = 1

# Associate transaction portal type to the corresponding line portal type.
transaction_to_line_mapping = {
    'Accounting Transaction': 'Accounting Transaction Line',
    'Balance Transaction': 'Balance Transaction Line',
    'Purchase Invoice Transaction': 'Purchase Invoice Transaction Line',
    'Sale Invoice Transaction': 'Sale Invoice Transaction Line',
    'Payment Transaction': 'Accounting Transaction Line',
    'Closing Transaction': 'Closing Transaction Line',
  }


class AccountingTestCase(ERP5TypeTestCase):
  """A test case for all accounting tests.

  Like in erp5_accounting_ui_test, the testing environment is made of:

  Currencies:
    * EUR with precision 2
    * USD with precision 2
    * JPY with precision 0

  Regions:
    * region/europe/west/france
    
  Group:
    * group/demo_group
    * group/demo_group/sub1
    * group/demo_group/sub2
    * group/client
    * group/vendor'
    
  Payment Mode:
    * payment_mode/cash
    * payment_mode/check
  
  Organisations:
    * `self.section` an organisation in region europe/west/france
    using EUR as default currency, without any openned accounting period by
    default. This organisation is member of group/demo_group/sub1
    * self.client_1, self.client_2 & self.supplier, some other organisations
  
  Accounts:
      All accounts are associated to a virtual GAP category named "My Accounting
    Standards":
    * bank
    * collected_vat
    * equity
    * fixed_assets
    * goods_purchase
    * goods_sales
    * payable
    * receivable
    * refundable_vat
    * stocks
  
  Tests starts with a preference activated for self.my_organisation, logged in
  as a user with Assignee, Assignor and Author role.

  All documents created appart from this configuration will be deleted in
  teardown. So users of this test case are encouraged to create new documents
  rather than modifying default documents. 
  """
  
  username = 'username'

  @reindex
  def _makeOne(self, portal_type='Accounting Transaction', lines=None,
               simulation_state='draft', **kw):
    """Creates an accounting transaction, and edit it with kw.
    
    The default settings is for self.section.
    You can pass a list of mapping as lines, then lines will be created
    using this information.
    """
    created_by_builder = kw.pop('created_by_builder', lines is not None)
    kw.setdefault('start_date', DateTime())
    kw.setdefault('resource', 'currency_module/euro')
    if portal_type in ('Purchase Invoice Transaction',
                       'Balance Transaction'):
      if 'destination_section' not in kw:
        kw.setdefault('destination_section_value', self.section)
    else:
      if 'source_section' not in kw:
        kw.setdefault('source_section_value', self.section)
    tr = self.accounting_module.newContent(portal_type=portal_type,
                         created_by_builder=created_by_builder, **kw)
    if lines:
      for line in lines:
        line.setdefault('portal_type', transaction_to_line_mapping[portal_type])
        tr.newContent(**line)
    if simulation_state == 'planned':
      tr.plan()
    elif simulation_state == 'confirmed':
      tr.confirm()
    elif simulation_state in ('stopped', 'delivered'):
      tr.stop()
      if simulation_state == 'delivered':
        tr.deliver()
    return tr


  def login(self):
    """login with Assignee, Assignor & Author roles."""
    uf = self.getPortal().acl_users
    uf._doAddUser(self.username, '', ['Assignee', 'Assignor', 'Author'], [])
    user = uf.getUserById(self.username).__of__(uf)
    newSecurityManager(None, user)


  def setUp(self):
    """Setup the fixture.
    """
    ERP5TypeTestCase.setUp(self)
    self.portal = self.getPortal()
    self.account_module = self.portal.account_module
    self.accounting_module = self.portal.accounting_module
    self.organisation_module = self.portal.organisation_module
    self.person_module = self.portal.person_module
    self.currency_module = self.portal.currency_module
    self.section = self.organisation_module.my_organisation
    
    # make sure documents are validated
    for module in (self.account_module, self.organisation_module,
                   self.person_module):
      for doc in module.objectValues():
        doc.validate()

    # and the preference enabled
    pref = self.portal.portal_preferences.accounting_zuite_preference
    pref.manage_addLocalRoles(self.username, ('Auditor', ))
    # Make sure _aq_dynamic is called before calling the workflow method
    # otherwise .enable might not been wrapped yet. This happen in --load
    pref._aq_dynamic('hack')
    pref.enable()
    
    # and all this available to catalog
    get_transaction().commit()
    self.tic()


  def tearDown(self):
    """Remove all documents, except the default ones.
    """
    get_transaction().abort()
    self.accounting_module.manage_delObjects(
                      list(self.accounting_module.objectIds()))
    self.organisation_module.manage_delObjects([x for x in 
          self.accounting_module.objectIds() if x not in ('my_organisation',
            'client_1', 'client_2', 'supplier')])
    self.organisation_module.my_organisation.manage_delObjects([x.getId()
        for x in self.organisation_module.my_organisation.objectValues(
                   portal_type=('Accounting Period', 'Bank Account'))])
    self.person_module.manage_delObjects([x for x in 
          self.person_module.objectIds() if x not in ('john_smith',)])
    self.account_module.manage_delObjects([x for x in 
          self.account_module.objectIds() if x not in ('bank', 'collected_vat',
            'equity', 'fixed_assets', 'goods_purchase', 'goods_sales',
            'payable', 'receivable', 'refundable_vat', 'stocks',)])
    self.portal.portal_preferences.manage_delObjects([x for x in
          self.portal.portal_preferences.objectIds() if x not in
          ('accounting_zuite_preference', 'default_site_preference')])
    self.portal.portal_simulation.manage_delObjects(list(
          self.portal.portal_simulation.objectIds()))
    get_transaction().commit()
    self.tic()
    ERP5TypeTestCase.tearDown(self)


  def getBusinessTemplateList(self):
    """Returns list of BT to be installed."""
    return ('erp5_base', 'erp5_pdm', 'erp5_trade', 'erp5_accounting',
            'erp5_accounting_ui_test')


class TestTransactionValidation(AccountingTestCase):
  """Test validations of accounting transactions.

  In this test suite, the section have a closed accounting period for 2006, and
  an open one for 2007.
  """
  def afterSetUp(self):
    self.organisation_module = self.portal.organisation_module
    self.section = self.organisation_module.my_organisation

    if 'accounting_period_2006' not in self.section.objectIds():
      accounting_period_2006 = self.section.newContent(
                                  id='accounting_period_2006',
                                  portal_type='Accounting Period',
                                  start_date=DateTime('2006/01/01'),
                                  stop_date=DateTime('2006/12/31'))
      accounting_period_2006.start()
      accounting_period_2006.stop()
      accounting_period_2007 = self.section.newContent(
                                  id='accounting_period_2007',
                                  portal_type='Accounting Period',
                                  start_date=DateTime('2007/01/01'),
                                  stop_date=DateTime('2007/12/31'))
      accounting_period_2007.start()
      get_transaction().commit()
      self.tic()

  def test_SaleInvoiceTransactionValidationDate(self):
    # Accounting Period Date matters for Sale Invoice Transaction
    transaction = self._makeOne(
               portal_type='Sale Invoice Transaction',
               start_date=DateTime('2006/03/03'),
               destination_section_value=self.organisation_module.supplier,
               lines=(dict(source_value=self.account_module.goods_purchase,
                           source_debit=500),
                      dict(source_value=self.account_module.receivable,
                           source_credit=500)))
    # validation is refused, because period is closed
    self.assertRaises(ValidationFailed,
        self.portal.portal_workflow.doActionFor,
        transaction, 'stop_action')
    # in 2007, it's OK
    transaction.setStartDate(DateTime("2007/03/03"))
    self.portal.portal_workflow.doActionFor(transaction, 'stop_action')
  
  def test_PurchaseInvoiceTransactionValidationDate(self):
    # Accounting Period Date matters for Purchase Invoice Transaction
    transaction = self._makeOne(
               portal_type='Purchase Invoice Transaction',
               stop_date=DateTime('2006/03/03'),
               source_section_value=self.organisation_module.supplier,
               lines=(dict(destination_value=self.account_module.goods_purchase,
                           destination_debit=500),
                      dict(destination_value=self.account_module.receivable,
                           destination_credit=500)))
    # validation is refused, because period is closed
    self.assertRaises(ValidationFailed,
        self.portal.portal_workflow.doActionFor,
        transaction, 'stop_action')
    # in 2007, it's OK
    transaction.setStopDate(DateTime("2007/03/03"))
    self.portal.portal_workflow.doActionFor(transaction, 'stop_action')

  def test_PaymentTransactionValidationDate(self):
    # Accounting Period Date matters for Payment Transaction
    transaction = self._makeOne(
               portal_type='Payment Transaction',
               start_date=DateTime('2006/03/03'),
               destination_section_value=self.organisation_module.supplier,
               payment_module='default',
               lines=(dict(source_value=self.account_module.goods_purchase,
                           source_debit=500),
                      dict(source_value=self.account_module.receivable,
                           source_credit=500)))
    # validation is refused, because period is closed
    self.assertRaises(ValidationFailed,
        self.portal.portal_workflow.doActionFor,
        transaction, 'stop_action')
    # in 2007, it's OK
    transaction.setStartDate(DateTime("2007/03/03"))
    self.portal.portal_workflow.doActionFor(transaction, 'stop_action')

  def test_DestinationPaymentTransactionValidationDate(self):
    # Accounting Period Date matters for Payment Transaction
    transaction = self._makeOne(
               portal_type='Payment Transaction',
               stop_date=DateTime('2006/03/03'),
               source_section_value=self.organisation_module.supplier,
               destination_section_value=self.section, 
               payment_module='default',
               lines=(dict(destination_value=self.account_module.goods_purchase,
                           destination_debit=500),
                      dict(destination_value=self.account_module.receivable,
                           destination_credit=500)))
    # validation is refused, because period is closed
    self.assertRaises(ValidationFailed,
        self.portal.portal_workflow.doActionFor,
        transaction, 'stop_action')
    # in 2007, it's OK
    transaction.setStopDate(DateTime("2007/03/03"))
    self.portal.portal_workflow.doActionFor(transaction, 'stop_action')

  def test_AccountingTransactionValidationStartDate(self):
    # Check we can/cannot validate at date boundaries of the period
    transaction = self._makeOne(
               portal_type='Accounting Transaction',
               start_date=DateTime('2006/12/31'),
               destination_section_value=self.organisation_module.supplier,
               payment_module='default',
               lines=(dict(source_value=self.account_module.goods_purchase,
                           source_debit=500),
                      dict(source_value=self.account_module.receivable,
                           source_credit=500)))
    # validation is refused, because period is closed
    self.assertRaises(ValidationFailed,
        self.portal.portal_workflow.doActionFor,
        transaction, 'stop_action')
    transaction.setStartDate(DateTime("2007/01/01"))
    self.portal.portal_workflow.doActionFor(transaction, 'stop_action')



class TestClosingPeriod(AccountingTestCase):
  """Various tests for closing the period.
  """
  def beforeTearDown(self):
    get_transaction().abort()
    # we manually remove the content of stock table, because unindexObject
    # might not work correctly on Balance Transaction, and we don't want
    # leave something in stock table that will change the next test.
    self.portal.erp5_sql_connection.manage_test('truncate stock')
    get_transaction().commit()

  def test_createBalanceOnNode(self):
    period = self.section.newContent(portal_type='Accounting Period')
    period.setStartDate(DateTime(2006, 1, 1))
    period.setStopDate(DateTime(2006, 12, 31))

    transaction1 = self._makeOne(
        start_date=DateTime(2006, 1, 1),
        portal_type='Accounting Transaction',
        simulation_state='delivered',
        lines=(dict(source_value=self.account_module.equity,
                    source_debit=500),
               dict(source_value=self.account_module.stocks,
                    source_credit=500)))

    transaction2 = self._makeOne(
        start_date=DateTime(2006, 1, 2),
        portal_type='Accounting Transaction',
        simulation_state='delivered',
        lines=(dict(source_value=self.account_module.stocks,
                    source_debit=100),
               dict(source_value=self.account_module.goods_purchase,
                    source_credit=100)))

    period.AccountingPeriod_createBalanceTransaction(
                               profit_and_loss_account=None)
    accounting_transaction_list = self.accounting_module.contentValues()
    self.assertEquals(3, len(accounting_transaction_list))
    balance_transaction_list = self.accounting_module.contentValues(
                              portal_type='Balance Transaction')
    self.assertEquals(1, len(balance_transaction_list))
    balance_transaction = balance_transaction_list[0]

    # this should create a balance with 3 lines,
    #   equity = 500 D
    #   stocks =     400 C
    #   pl     =     100 C 
    self.assertEquals(self.section,
                      balance_transaction.getDestinationSectionValue())
    self.assertEquals(None,
                      balance_transaction.getSourceSection())
    self.assertEquals([period], balance_transaction.getCausalityValueList())
    self.assertEquals(DateTime(2007, 1, 1),
                      balance_transaction.getStartDate())
    self.assertEquals('currency_module/euro',
                      balance_transaction.getResource())
    self.assertEquals('delivered', balance_transaction.getSimulationState())
    movement_list = balance_transaction.getMovementList()
    self.assertEquals(3, len(movement_list))

    equity_movement_list = [m for m in movement_list
          if m.getDestinationValue() == self.account_module.equity]
    self.assertEquals(1, len(equity_movement_list))
    equity_movement = equity_movement_list[0]
    self.assertEquals([], equity_movement.getValueList('resource'))
    self.assertEquals([], equity_movement.getValueList('destination_section'))
    self.assertEquals(None, equity_movement.getSource())
    self.assertEquals(None, equity_movement.getSourceSection())
    self.assertEquals(None, equity_movement.getDestinationTotalAssetPrice())
    self.assertEquals(None, equity_movement.getSourceTotalAssetPrice())
    self.assertEquals(500., equity_movement.getDestinationDebit())

    stock_movement_list = [m for m in movement_list
          if m.getDestinationValue() == self.account_module.stocks]
    self.assertEquals(1, len(stock_movement_list))
    stock_movement = stock_movement_list[0]
    self.assertEquals([], stock_movement.getValueList('resource'))
    self.assertEquals([], stock_movement.getValueList('destination_section'))
    self.assertEquals(None, stock_movement.getSource())
    self.assertEquals(None, stock_movement.getSourceSection())
    self.assertEquals(None, stock_movement.getDestinationTotalAssetPrice())
    self.assertEquals(None, stock_movement.getSourceTotalAssetPrice())
    self.assertEquals(400., stock_movement.getDestinationCredit())

    pl_movement_list = [m for m in movement_list
                        if m.getDestinationValue() is None]
    self.assertEquals(1, len(pl_movement_list))
    pl_movement = pl_movement_list[0]
    self.assertEquals([], pl_movement.getValueList('resource'))
    self.assertEquals([], pl_movement.getValueList('destination_section'))
    self.assertEquals(None, pl_movement.getSource())
    self.assertEquals(None, pl_movement.getSourceSection())
    self.assertEquals(None, pl_movement.getDestinationTotalAssetPrice())
    self.assertEquals(None, pl_movement.getSourceTotalAssetPrice())
    self.assertEquals(100., pl_movement.getDestinationCredit())


  def test_createBalanceOnMirrorSection(self):
    organisation_module = self.organisation_module
    period = self.section.newContent(portal_type='Accounting Period')
    period.setStartDate(DateTime(2006, 1, 1))
    period.setStopDate(DateTime(2006, 12, 31))

    transaction1 = self._makeOne(
        start_date=DateTime(2006, 1, 1),
        destination_section_value=organisation_module.client_1,
        portal_type='Sale Invoice Transaction',
        simulation_state='delivered',
        lines=(dict(source_value=self.account_module.goods_sales,
                    source_debit=100),
               dict(source_value=self.account_module.receivable,
                    source_credit=100)))

    transaction2 = self._makeOne(
        start_date=DateTime(2006, 1, 2),
        destination_section_value=organisation_module.client_2,
        portal_type='Sale Invoice Transaction',
        simulation_state='delivered',
        lines=(dict(source_value=self.account_module.goods_sales,
                    source_debit=200),
               dict(source_value=self.account_module.receivable,
                    source_credit=200)))

    period.AccountingPeriod_createBalanceTransaction(
                             profit_and_loss_account=None)
    accounting_transaction_list = self.accounting_module.contentValues()
    self.assertEquals(3, len(accounting_transaction_list))
    balance_transaction_list = self.accounting_module.contentValues(
                              portal_type='Balance Transaction')
    self.assertEquals(1, len(balance_transaction_list))
    balance_transaction = balance_transaction_list[0]

    # this should create a balance with 3 lines,
    #   pl                 = 300 D
    #   receivable/client1 =     200 C
    #   receivable/client2 =     100 C
    self.assertEquals(self.section,
                      balance_transaction.getDestinationSectionValue())
    self.assertEquals(None, balance_transaction.getSourceSection())
    self.assertEquals(DateTime(2007, 1, 1),
                      balance_transaction.getStartDate())
    self.assertEquals('currency_module/euro',
                      balance_transaction.getResource())
    self.assertEquals('delivered', balance_transaction.getSimulationState())
    movement_list = balance_transaction.getMovementList()
    self.assertEquals(3, len(movement_list))

    client1_movement_list = [m for m in movement_list
     if m.getSourceSectionValue() == organisation_module.client_1]
    self.assertEquals(1, len(client1_movement_list))
    client1_movement = client1_movement_list[0]
    self.assertEquals([], client1_movement.getValueList('resource'))
    self.assertEquals([], client1_movement.getValueList('destination_section'))
    self.assertEquals(None, client1_movement.getSource())
    self.assertEquals(self.account_module.receivable,
                      client1_movement.getDestinationValue())
    self.assertEquals(organisation_module.client_1,
                      client1_movement.getSourceSectionValue())
    self.assertEquals(None, client1_movement.getDestinationTotalAssetPrice())
    self.assertEquals(None, client1_movement.getSourceTotalAssetPrice())
    self.assertEquals(100., client1_movement.getDestinationCredit())

    client2_movement_list = [m for m in movement_list
     if m.getSourceSectionValue() == organisation_module.client_2]
    self.assertEquals(1, len(client2_movement_list))
    client2_movement = client2_movement_list[0]
    self.assertEquals([], client2_movement.getValueList('resource'))
    self.assertEquals([], client2_movement.getValueList('destination_section'))
    self.assertEquals(None, client2_movement.getSource())
    self.assertEquals(self.account_module.receivable,
                      client2_movement.getDestinationValue())
    self.assertEquals(organisation_module.client_2,
                      client2_movement.getSourceSectionValue())
    self.assertEquals(None, client2_movement.getDestinationTotalAssetPrice())
    self.assertEquals(None, client2_movement.getSourceTotalAssetPrice())
    self.assertEquals(200., client2_movement.getDestinationCredit())

    pl_movement_list = [m for m in movement_list
                         if m.getDestination() is None]
    self.assertEquals(1, len(pl_movement_list))
    pl_movement = pl_movement_list[0]
    self.assertEquals([], pl_movement.getValueList('resource'))
    self.assertEquals(None, pl_movement.getSource())
    self.assertEquals(None,
                      pl_movement.getDestinationValue())
    self.assertEquals(None,
                      pl_movement.getSourceSection())
    self.assertEquals(None, pl_movement.getDestinationTotalAssetPrice())
    self.assertEquals(None, pl_movement.getSourceTotalAssetPrice())
    self.assertEquals(300., pl_movement.getDestinationDebit())


  def test_createBalanceOnPayment(self):
    organisation_module = self.organisation_module
    period = self.section.newContent(portal_type='Accounting Period')
    period.setStartDate(DateTime(2006, 1, 1))
    period.setStopDate(DateTime(2006, 12, 31))

    bank1 = self.section.newContent(
                    id='bank1', reference='bank1',
                    portal_type='Bank Account')
    bank2 = self.section.newContent(
                    id='bank2', reference='bank2',
                    portal_type='Bank Account')

    transaction1 = self._makeOne(
        start_date=DateTime(2006, 1, 1),
        destination_section_value=organisation_module.client_1,
        source_payment_value=bank1,
        title='bank 1',
        portal_type='Payment Transaction',
        simulation_state='delivered',
        lines=(dict(source_value=self.account_module.receivable,
                    source_debit=100),
               dict(source_value=self.account_module.bank,
                    source_credit=100)))
    
    # we are destination on this one
    transaction2 = self._makeOne(
        stop_date=DateTime(2006, 1, 2),
        destination_section_value=self.section,
        destination_payment_value=bank2,
        source_section_value=organisation_module.client_2,
        title='bank 2',
        portal_type='Payment Transaction',
        simulation_state='delivered',
        lines=(dict(destination_value=self.account_module.bank,
                    destination_debit=200),
               dict(destination_value=self.account_module.goods_purchase,
                    destination_credit=200)))

    period.AccountingPeriod_createBalanceTransaction(
                             profit_and_loss_account=None)
    accounting_transaction_list = self.accounting_module.contentValues()
    self.assertEquals(3, len(accounting_transaction_list))
    balance_transaction_list = self.accounting_module.contentValues(
                              portal_type='Balance Transaction')
    self.assertEquals(1, len(balance_transaction_list))
    balance_transaction = balance_transaction_list[0]

    # this should create a balance with 4 lines,
    #   receivable/client_1 = 100 D
    #   bank/bank1          =     100 C
    #   bank/bank2          = 200 D
    #   pl                  =     200 C

    self.assertEquals(self.section,
                      balance_transaction.getDestinationSectionValue())
    self.assertEquals(None,
                      balance_transaction.getSourceSection())
    self.assertEquals([period], balance_transaction.getCausalityValueList())
    self.assertEquals(DateTime(2007, 1, 1),
                      balance_transaction.getStartDate())
    self.assertEquals('currency_module/euro',
                      balance_transaction.getResource())
    self.assertEquals('delivered', balance_transaction.getSimulationState())
    movement_list = balance_transaction.getMovementList()
    self.assertEquals(4, len(movement_list))
    
    receivable_movement_list = [m for m in movement_list
        if m.getDestinationValue() == self.account_module.receivable]
    self.assertEquals(1, len(receivable_movement_list))
    receivable_movement = receivable_movement_list[0]
    self.assertEquals([], receivable_movement.getValueList('resource'))
    self.assertEquals(None, receivable_movement.getSource())
    self.assertEquals(self.account_module.receivable,
                      receivable_movement.getDestinationValue())
    self.assertEquals(self.organisation_module.client_1,
                      receivable_movement.getSourceSectionValue())
    self.assertEquals(None, receivable_movement.getDestinationTotalAssetPrice())
    self.assertEquals(None, receivable_movement.getSourceTotalAssetPrice())
    self.assertEquals(100., receivable_movement.getDestinationDebit())

    bank1_movement_list = [m for m in movement_list
                       if m.getDestinationPaymentValue() == bank1]
    self.assertEquals(1, len(bank1_movement_list))
    bank1_movement = bank1_movement_list[0]
    self.assertEquals([], bank1_movement.getValueList('resource'))
    self.assertEquals(None, bank1_movement.getSource())
    self.assertEquals(self.account_module.bank,
                      bank1_movement.getDestinationValue())
    self.assertEquals(bank1,
                      bank1_movement.getDestinationPaymentValue())
    self.assertEquals(None,
                      bank1_movement.getSourceSectionValue())
    self.assertEquals(None, bank1_movement.getDestinationTotalAssetPrice())
    self.assertEquals(None, bank1_movement.getSourceTotalAssetPrice())
    self.assertEquals(100., bank1_movement.getDestinationCredit())

    bank2_movement_list = [m for m in movement_list
                         if m.getDestinationPaymentValue() == bank2]
    self.assertEquals(1, len(bank2_movement_list))
    bank2_movement = bank2_movement_list[0]
    self.assertEquals([], bank2_movement.getValueList('resource'))
    self.assertEquals(None, bank2_movement.getSource())
    self.assertEquals(self.account_module.bank,
                      bank2_movement.getDestinationValue())
    self.assertEquals(bank2,
                      bank2_movement.getDestinationPaymentValue())
    self.assertEquals(None,
                      bank2_movement.getSourceSectionValue())
    self.assertEquals(None, bank2_movement.getDestinationTotalAssetPrice())
    self.assertEquals(None, bank2_movement.getSourceTotalAssetPrice())
    self.assertEquals(200., bank2_movement.getDestinationDebit())

    pl_movement_list = [m for m in movement_list
                         if m.getDestination() is None]
    self.assertEquals(1, len(pl_movement_list))
    pl_movement = pl_movement_list[0]
    self.assertEquals([], pl_movement.getValueList('resource'))
    self.assertEquals(None, pl_movement.getSource())
    self.assertEquals(None, pl_movement.getDestination())
    self.assertEquals(None, pl_movement.getDestinationPaymentValue())
    self.assertEquals(None, pl_movement.getSourceSectionValue())
    self.assertEquals(None, pl_movement.getDestinationTotalAssetPrice())
    self.assertEquals(None, pl_movement.getSourceTotalAssetPrice())
    self.assertEquals(200., pl_movement.getDestinationCredit())


  def test_createBalanceOnMirrorSectionMultiCurrency(self):
    organisation_module = self.organisation_module
    period = self.section.newContent(portal_type='Accounting Period')
    period.setStartDate(DateTime(2006, 1, 1))
    period.setStopDate(DateTime(2006, 12, 31))

    transaction1 = self._makeOne(
        start_date=DateTime(2006, 1, 1),
        title='Yen',
        resource='currency_module/yen',
        destination_section_value=organisation_module.client_1,
        portal_type='Sale Invoice Transaction',
        simulation_state='delivered',
        lines=(dict(source_value=self.account_module.goods_sales,
                    source_asset_debit=1.1,
                    source_debit=100),
               dict(source_value=self.account_module.receivable,
                    source_asset_credit=1.1,
                    source_credit=100)))

    transaction2 = self._makeOne(
        start_date=DateTime(2006, 1, 2),
        title='Dollar',
        resource='currency_module/usd',
        destination_section_value=organisation_module.client_2,
        portal_type='Sale Invoice Transaction',
        simulation_state='delivered',
        lines=(dict(source_value=self.account_module.goods_sales,
                    source_asset_debit=2.2,
                    source_debit=200),
               dict(source_value=self.account_module.receivable,
                    source_asset_credit=2.2,
                    source_credit=200)))

    period.AccountingPeriod_createBalanceTransaction(
                              profit_and_loss_account=None)
    accounting_transaction_list = self.accounting_module.contentValues()
    self.assertEquals(3, len(accounting_transaction_list))
    balance_transaction_list = self.accounting_module.contentValues(
                              portal_type='Balance Transaction')
    self.assertEquals(1, len(balance_transaction_list))
    balance_transaction = balance_transaction_list[0]

    self.assertEquals(self.section,
                      balance_transaction.getDestinationSectionValue())
    self.assertEquals(None, balance_transaction.getSourceSection())
    self.assertEquals(DateTime(2007, 1, 1),
                      balance_transaction.getStartDate())
    self.assertEquals('currency_module/euro',
                      balance_transaction.getResource())

    # this should create a balance with 3 lines,
    #   pl                 = 3.3 D     ( resource acquired )
    #   receivable/client1 =     1.1 C ( resource yen ) qty=100
    #   receivable/client2 =     2.2 C ( resource usd ) qyt=200
    
    accounting_currency_precision = \
        self.portal.currency_module.euro.getQuantityPrecision()
    self.assertEquals(accounting_currency_precision, 2)

    movement_list = balance_transaction.getMovementList()
    self.assertEquals(3, len(movement_list))
    client1_movement_list = [m for m in movement_list
     if m.getSourceSectionValue() == organisation_module.client_1]
    self.assertEquals(1, len(client1_movement_list))
    client1_movement = client1_movement_list[0]
    self.assertEquals('currency_module/yen',
                      client1_movement.getResource())
    self.assertEquals([], client1_movement.getValueList('destination_section'))
    self.assertEquals(None, client1_movement.getSource())
    self.assertEquals(self.account_module.receivable,
                      client1_movement.getDestinationValue())
    self.assertEquals(organisation_module.client_1,
                      client1_movement.getSourceSectionValue())
    self.assertAlmostEquals(1.1,
          client1_movement.getDestinationInventoriatedTotalAssetCredit(),
          accounting_currency_precision)
    self.assertEquals(None, client1_movement.getSourceTotalAssetPrice())
    self.assertEquals(100, client1_movement.getDestinationCredit())

    client2_movement_list = [m for m in movement_list
     if m.getSourceSectionValue() == organisation_module.client_2]
    self.assertEquals(1, len(client2_movement_list))
    client2_movement = client2_movement_list[0]
    self.assertEquals('currency_module/usd',
                      client2_movement.getResource())
    self.assertEquals([], client2_movement.getValueList('destination_section'))
    self.assertEquals(None, client2_movement.getSource())
    self.assertEquals(self.account_module.receivable,
                      client2_movement.getDestinationValue())
    self.assertEquals(organisation_module.client_2,
                      client2_movement.getSourceSectionValue())
    self.assertAlmostEquals(2.2,
        client2_movement.getDestinationInventoriatedTotalAssetCredit(),
        accounting_currency_precision)
    self.assertEquals(None, client2_movement.getSourceTotalAssetPrice())
    self.assertEquals(200., client2_movement.getDestinationCredit())

    pl_movement_list = [m for m in movement_list
                         if m.getDestination() is None]
    self.assertEquals(1, len(pl_movement_list))
    pl_movement = pl_movement_list[0]
    self.assertEquals([], pl_movement.getValueList('resource'))
    self.assertEquals(None, pl_movement.getSource())
    self.assertEquals(None,
                      pl_movement.getDestinationValue())
    self.assertEquals(None,
                      pl_movement.getSourceSection())
    self.assertEquals(None, pl_movement.getDestinationTotalAssetPrice())
    self.assertEquals(None, pl_movement.getSourceTotalAssetPrice())
    self.assertAlmostEquals(3.3,
                  pl_movement.getDestinationDebit(),
                  accounting_currency_precision)


  def test_AccountingPeriodWorkflow(self):
    """Tests that accounting_period_workflow creates a balance transaction.
    """
    # open a period for our section
    period = self.section.newContent(portal_type='Accounting Period')
    period.setStartDate(DateTime(2006, 1, 1))
    period.setStopDate(DateTime(2006, 12, 31))
    self.assertEquals('draft', period.getSimulationState())
    self.portal.portal_workflow.doActionFor(period, 'start_action')
    self.assertEquals('started', period.getSimulationState())

    # create a simple transaction in the period
    transaction = self._makeOne(
        start_date=DateTime(2006, 6, 30),
        portal_type='Sale Invoice Transaction',
        destination_section_value=self.organisation_module.client_1,
        simulation_state='delivered',
        lines=(dict(source_value=self.account_module.receivable,
                    source_credit=100),
               dict(source_value=self.account_module.goods_purchase,
                    source_debit=100)))
    self.assertEquals(1, len(self.accounting_module))

    # close the period
    self.portal.portal_workflow.doActionFor(period, 'stop_action')
    self.assertEquals('stopped', period.getSimulationState())
    # reopen it, then close it got real
    self.portal.portal_workflow.doActionFor(period, 'restart_action')
    self.assertEquals('started', period.getSimulationState())
    self.portal.portal_workflow.doActionFor(period, 'stop_action')
    self.assertEquals('stopped', period.getSimulationState())
    
    pl_account = self.portal.account_module.newContent(
                    portal_type='Account',
                    account_type='equity',
                    gap='my_country/my_accounting_standards/1',
                    title='Profit & Loss')
    pl_account.validate()
    self.portal.portal_workflow.doActionFor(
            period, 'deliver_action',
            profit_and_loss_account=pl_account.getRelativeUrl())

    get_transaction().commit()
    self.tic()
    self.assertEquals('delivered', period.getSimulationState())
    
    # this created a balance transaction
    balance_transaction_list = self.accounting_module.contentValues(
                                  portal_type='Balance Transaction')
    self.assertEquals(1, len(balance_transaction_list))
    balance_transaction = balance_transaction_list[0]

    # and this transaction must use the account we used in the workflow action.
    self.assertEquals(1, len([m for m in
                              balance_transaction.getMovementList()
                              if m.getDestinationValue() == pl_account]))


  def test_SecondAccountingPeriod(self):
    """Tests having two accounting periods.
    """
    period1 = self.section.newContent(portal_type='Accounting Period')
    period1.setStartDate(DateTime(2006, 1, 1))
    period1.setStopDate(DateTime(2006, 12, 31))
    period1.start()
    
    transaction1 = self._makeOne(
        start_date=DateTime(2006, 1, 2),
        portal_type='Purchase Invoice Transaction',
        source_section_value=self.organisation_module.client_1,
        simulation_state='delivered',
        lines=(dict(destination_value=self.account_module.goods_purchase,
                    destination_debit=100),
               dict(destination_value=self.account_module.payable,
                    destination_credit=100)))
    period1.stop()
    # deliver the period1 using workflow, so that we have 
    pl_account = self.portal.account_module.newContent(
                    portal_type='Account',
                    account_type='equity',
                    gap='my_country/my_accounting_standards/1',
                    title='Profit & Loss')
    pl_account.validate()
    self.portal.portal_workflow.doActionFor(
            period1, 'deliver_action',
            profit_and_loss_account=pl_account.getRelativeUrl())
    
    balance_transaction_list = self.accounting_module.contentValues(
                                  portal_type='Balance Transaction')
    self.assertEquals(1, len(balance_transaction_list))
    balance_transaction1 = balance_transaction_list[0]
    
    period2 = self.section.newContent(portal_type='Accounting Period')
    period2.setStartDate(DateTime(2007, 1, 1))
    period2.setStopDate(DateTime(2007, 12, 31))
    period2.start()

    transaction2 = self._makeOne(
        start_date=DateTime(2007, 1, 2),
        portal_type='Accounting Transaction',
        simulation_state='delivered',
        lines=(dict(source_value=self.account_module.equity,
                    source_debit=100),
               dict(source_value=pl_account,
                    source_credit=100)))
    transaction3 = self._makeOne(
        start_date=DateTime(2007, 1, 3),
        portal_type='Purchase Invoice Transaction',
        source_section_value=self.organisation_module.client_1,
        simulation_state='delivered',
        lines=(dict(destination_value=self.account_module.goods_purchase,
                    destination_debit=300),
               dict(destination_value=self.account_module.payable,
                    destination_credit=300)))

    period2.AccountingPeriod_createBalanceTransaction(
                profit_and_loss_account=pl_account.getRelativeUrl())
    balance_transaction_list = [tr for tr in 
                          self.accounting_module.contentValues(
                              portal_type='Balance Transaction')
                          if tr != balance_transaction1]
    self.assertEquals(1, len(balance_transaction_list))
    balance_transaction2 = balance_transaction_list[0]
    
    self.assertEquals(DateTime(2008, 1, 1),
                      balance_transaction2.getStartDate())
    # this should create a balance with 3 lines,
    #   equity          = 100 D
    #   payable/client1 =       100 + 300 C
    #   pl              = 300 D    
    movement_list = balance_transaction2.getMovementList()
    self.assertEquals(3, len(movement_list))

    equity_movement_list = [m for m in movement_list
          if m.getDestinationValue() == self.account_module.equity]
    self.assertEquals(1, len(equity_movement_list))
    equity_movement = equity_movement_list[0]
    self.assertEquals(100., equity_movement.getDestinationDebit())
    
    payable_movement_list = [m for m in movement_list
          if m.getDestinationValue() == self.account_module.payable]
    self.assertEquals(1, len(payable_movement_list))
    payable_movement = payable_movement_list[0]
    self.assertEquals(400., payable_movement.getDestinationCredit())
    
    pl_movement_list = [m for m in movement_list
          if m.getDestinationValue() == pl_account]
    self.assertEquals(1, len(pl_movement_list))
    pl_movement = pl_movement_list[0]
    self.assertEquals(300., pl_movement.getDestinationDebit())


  def test_ProfitAndLossUsedInPeriod(self):
    """When the profit and loss account has a non zero balance at the end of
    the period, AccountingPeriod_createBalanceTransaction script should add
    this balance and the new calculated profit and loss to have only one line.
    """
    period = self.section.newContent(portal_type='Accounting Period')
    period.setStartDate(DateTime(2006, 1, 1))
    period.setStopDate(DateTime(2006, 12, 31))
    pl_account = self.portal.account_module.newContent(
                    portal_type='Account',
                    account_type='equity',
                    gap='my_country/my_accounting_standards/1',
                    title='Profit & Loss')
    pl_account.validate()

    transaction1 = self._makeOne(
        start_date=DateTime(2006, 1, 1),
        portal_type='Accounting Transaction',
        simulation_state='delivered',
        lines=(dict(source_value=self.account_module.goods_purchase,
                    source_debit=400),
               dict(source_value=pl_account,
                    source_debit=100),
               dict(source_value=self.account_module.stocks,
                    source_credit=500)))

    period.AccountingPeriod_createBalanceTransaction(
                  profit_and_loss_account=pl_account.getRelativeUrl())
    
    balance_transaction_list = self.accounting_module.contentValues(
                              portal_type='Balance Transaction')
    self.assertEquals(1, len(balance_transaction_list))
    balance_transaction = balance_transaction_list[0]
    balance_transaction.alternateReindexObject()
    movement_list = balance_transaction.getMovementList()
    self.assertEquals(2, len(movement_list))

    pl_movement_list = [m for m in movement_list
                      if m.getDestinationValue() == pl_account]
    self.assertEquals(1, len(pl_movement_list))
    self.assertEquals(500, pl_movement_list[0].getDestinationDebit())
    
    stock_movement_list = [m for m in movement_list
          if m.getDestinationValue() == self.account_module.stocks]
    self.assertEquals(1, len(stock_movement_list))
    self.assertEquals(500, stock_movement_list[0].getDestinationCredit())
    

  def test_InventoryIndexingNodeAndMirrorSection(self):
    # Balance Transactions are indexed as Inventories.
    transaction1 = self._makeOne(
        start_date=DateTime(2006, 1, 1),
        portal_type='Sale Invoice Transaction',
        destination_section_value=self.organisation_module.client_1,
        simulation_state='delivered',
        lines=(dict(source_value=self.account_module.receivable,
                    source_debit=100),
               dict(source_value=self.account_module.goods_sales,
                    source_credit=100)))

    balance = self.accounting_module.newContent(
                          portal_type='Balance Transaction',
                          destination_section_value=self.section,
                          start_date=DateTime(2006, 12, 31),
                          resource_value=self.currency_module.euro,)
    balance.newContent(
                portal_type='Balance Transaction Line',
                destination_value=self.account_module.receivable,
                source_section_value=self.organisation_module.client_1,
                destination_debit=100,)
    balance.newContent(
                portal_type='Balance Transaction Line',
                destination_value=self.account_module.stocks,
                destination_credit=100,)
    balance.stop()
    balance.deliver()
    balance.immediateReindexObject()

    # now check inventory
    stool = self.getSimulationTool()
    # the account 'receivable' has a balance of 100
    node_uid = self.account_module.receivable.getUid()
    self.assertEquals(100, stool.getInventory(
                              section_uid=self.section.getUid(),
                              node_uid=node_uid))
    self.assertEquals(100, stool.getInventory(
                    section_uid=self.section.getUid(),
                    mirror_section_uid=self.organisation_module.client_1.getUid(),
                    node_uid=node_uid))
    self.assertEquals(100, stool.getInventoryAssetPrice(
                    section_uid=self.section.getUid(),
                    node_uid=node_uid))
    # and only one movement is returned by getMovementHistoryList
    self.assertEquals(1, len(stool.getMovementHistoryList(
                    section_uid=self.section.getUid(),
                    node_uid=node_uid)))
    
    # the account 'goods_sales' has a balance of -100
    node_uid = self.account_module.goods_sales.getUid()
    self.assertEquals(-100, stool.getInventory(
                              section_uid=self.section.getUid(),
                              node_uid=node_uid))

    # the account 'stocks' has a balance of -100
    node_uid = self.account_module.stocks.getUid()
    self.assertEquals(-100, stool.getInventory(
                              section_uid=self.section.getUid(),
                              node_uid=node_uid))


  def test_InventoryIndexingNodeDiffOnNode(self):
    # Balance Transactions are indexed as Inventories.
    transaction1 = self._makeOne(
        start_date=DateTime(2006, 1, 1),
        portal_type='Accounting Transaction',
        simulation_state='delivered',
        lines=(dict(source_value=self.account_module.receivable,
                    source_debit=100),
               dict(source_value=self.account_module.stocks,
                    source_credit=100)))

    balance = self.accounting_module.newContent(
                          portal_type='Balance Transaction',
                          destination_section_value=self.section,
                          start_date=DateTime(2006, 12, 31),
                          resource_value=self.currency_module.euro,)
    balance.newContent(
                portal_type='Balance Transaction Line',
                destination_value=self.account_module.receivable,
                destination_debit=150,)
    balance.newContent(
                portal_type='Balance Transaction Line',
                destination_value=self.account_module.stocks,
                destination_credit=90,)
    balance.stop()
    get_transaction().commit()
    self.tic()
    
    stool = self.portal.portal_simulation
    # the account 'receivable' has a balance of 150
    node_uid = self.account_module.receivable.getUid()
    self.assertEquals(150, stool.getInventory(
                              section_uid=self.section.getUid(),
                              node_uid=node_uid))
    # movement history list shows 2 movements, the initial with qty 100, and
    # the balance with quantity 50

    # the account 'stocks' has a balance of -100
    node_uid = self.account_module.stocks.getUid()
    self.assertEquals(-90, stool.getInventory(
                              section_uid=self.section.getUid(),
                              node_uid=node_uid))
    

  def test_BalanceTransactionLineBrainGetObject(self):
    # Balance Transaction Line can be retrieved using Brain.getObject
    balance = self.accounting_module.newContent(
                          portal_type='Balance Transaction',
                          destination_section_value=self.section,
                          start_date=DateTime(2006, 12, 31),
                          resource_value=self.currency_module.euro,)
    balance_line = balance.newContent(
                portal_type='Balance Transaction Line',
                destination_value=self.account_module.receivable,
                destination_debit=100,)
    balance_line2 = balance.newContent(
                portal_type='Balance Transaction Line',
                destination_value=self.account_module.payable,
                destination_credit=100,)
    balance.stop()
    get_transaction().commit()
    self.tic()
    
    stool = self.portal.portal_simulation
    # the account 'receivable' has a balance of 100
    node_uid = self.account_module.receivable.getUid()
    self.assertEquals(100, stool.getInventory(
                              section_uid=self.section.getUid(),
                              node_uid=node_uid))
    # there is one line in getMovementHistoryList:
    mvt_history_list = stool.getMovementHistoryList(
                              section_uid=self.section.getUid(),
                              node_uid=node_uid)
    self.assertEquals(1, len(mvt_history_list))
    self.assertEquals(mvt_history_list[0].getObject(),
                      balance_line)

    # There is also one line on payable account
    node_uid = self.account_module.payable.getUid()
    mvt_history_list = stool.getMovementHistoryList(
                              section_uid=self.section.getUid(),
                              node_uid=node_uid)
    self.assertEquals(1, len(mvt_history_list))
    self.assertEquals(mvt_history_list[0].getObject(),
                      balance_line2)


  def test_BalanceTransactionDate(self):
    # check that dates are correctly used for Balance Transaction indexing
    organisation_module = self.organisation_module

    transaction1 = self._makeOne(
        start_date=DateTime(2006, 12, 31),
        destination_section_value=organisation_module.client_1,
        portal_type='Sale Invoice Transaction',
        simulation_state='delivered',
        lines=(dict(source_value=self.account_module.goods_sales,
                    source_debit=100),
               dict(source_value=self.account_module.receivable,
                    source_credit=100)))

    balance = self.accounting_module.newContent(
                          portal_type='Balance Transaction',
                          destination_section_value=self.section,
                          start_date=DateTime(2007, 1, 1),
                          resource_value=self.currency_module.euro,)
    balance_line = balance.newContent(
                portal_type='Balance Transaction Line',
                destination_value=self.account_module.equity,
                destination_debit=100,)
    balance_line = balance.newContent(
                portal_type='Balance Transaction Line',
                source_section_value=organisation_module.client_1,
                destination_value=self.account_module.receivable,
                destination_credit=100,)
    balance.stop()
    balance.deliver()
    get_transaction().commit()
    self.tic()

    stool = self.portal.portal_simulation
    # the account 'receivable' has a balance of -100
    node_uid = self.account_module.receivable.getUid()
    self.assertEquals(-100, stool.getInventory(
                              section_uid=self.section.getUid(),
                              node_uid=node_uid))
    self.assertEquals(1, len(stool.getMovementHistoryList(
                              section_uid=self.section.getUid(),
                              node_uid=node_uid)))

    # this is a transaction with the same date as the balance transaction, but
    # this transaction should not be taken into account when we reindex the
    # Balance Transaction.
    transaction2 = self._makeOne(
        start_date=DateTime(2007, 1, 1),
        destination_section_value=organisation_module.client_1,
        portal_type='Sale Invoice Transaction',
        simulation_state='delivered',
        lines=(dict(source_value=self.account_module.goods_sales,
                    source_debit=50),
               dict(source_value=self.account_module.receivable,
                    source_credit=50)))
    get_transaction().commit()
    self.tic()
    # let's try to reindex and check if values are still OK
    balance.reindexObject()
    get_transaction().commit()
    self.tic()
    
    self.assertEquals(-150, stool.getInventory(
                              section_uid=self.section.getUid(),
                              node_uid=node_uid))
    self.assertEquals(2, len(stool.getMovementHistoryList(
                              section_uid=self.section.getUid(),
                              node_uid=node_uid)))


  def test_BalanceTransactionDateInInventoryAPI(self):
    # check that dates are correctly used for Balance Transaction when making
    # reports using inventory API
    balance = self.accounting_module.newContent(
                          portal_type='Balance Transaction',
                          destination_section_value=self.section,
                          start_date=DateTime(2006, 12, 31),
                          resource_value=self.currency_module.euro,)
    balance_line = balance.newContent(
                portal_type='Balance Transaction Line',
                destination_value=self.account_module.receivable,
                destination_debit=100,)
    balance.stop()
    get_transaction().commit()
    self.tic()
    
    stool = self.portal.portal_simulation
    # the account 'receivable' has a balance of 100 after 2006/12/31
    node_uid = self.account_module.receivable.getUid()
    self.assertEquals(100, stool.getInventory(
                              at_date=DateTime(2006, 12, 31),
                              section_uid=self.section.getUid(),
                              node_uid=node_uid))
    self.assertEquals(1, len(stool.getMovementHistoryList(
                              at_date=DateTime(2006, 12, 31),
                              section_uid=self.section.getUid(),
                              node_uid=node_uid)))
    # and 0 before
    self.assertEquals(0, stool.getInventory(
                              at_date=DateTime(2005, 12, 31),
                              section_uid=self.section.getUid(),
                              node_uid=node_uid))
    self.assertEquals(0, len(stool.getMovementHistoryList(
                              at_date=DateTime(2005, 12, 31),
                              section_uid=self.section.getUid(),
                              node_uid=node_uid)))


  def test_BalanceTransactionLineInventoryAPIParentPortalType(self):
    # related keys like parent_portal_type= can be used in inventory API to get
    # balance transaction lines
    balance = self.accounting_module.newContent(
                          portal_type='Balance Transaction',
                          destination_section_value=self.section,
                          start_date=DateTime(2006, 12, 31),
                          resource_value=self.currency_module.euro,)
    balance_line = balance.newContent(
                portal_type='Balance Transaction Line',
                destination_value=self.account_module.receivable,
                destination_debit=100,)
    balance.stop()
    get_transaction().commit()
    self.tic()
    
    stool = self.portal.portal_simulation
    # the account 'receivable' has a balance of 100
    node_uid = self.account_module.receivable.getUid()
    self.assertEquals(100, stool.getInventory(
                              parent_portal_type='Balance Transaction',
                              section_uid=self.section.getUid(),
                              node_uid=node_uid))
    # there is one line in getMovementHistoryList:
    mvt_history_list = stool.getMovementHistoryList(
                              parent_portal_type='Balance Transaction',
                              section_uid=self.section.getUid(),
                              node_uid=node_uid)
    self.assertEquals(1, len(mvt_history_list))

  # TODO : test deletion ?

class TestAccounting(ERP5TypeTestCase):
  """The first test for Accounting
  """
  def getAccountingModule(self):
    return getattr(self.getPortal(), 'accounting_module',
           getattr(self.getPortal(), 'accounting', None))
  
  def getAccountModule(self) :
    return getattr(self.getPortal(), 'account_module',
           getattr(self.getPortal(), 'account', None))
  
  # XXX
  def playSequence(self, sequence_string, quiet=1) :
    sequence_list = SequenceList()
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)
  
  account_portal_type           = 'Account'
  accounting_period_portal_type = 'Accounting Period'
  accounting_transaction_portal_type = 'Accounting Transaction'
  accounting_transaction_line_portal_type = 'Accounting Transaction Line'
  currency_portal_type          = 'Currency'
  organisation_portal_type      = 'Organisation'
  sale_invoice_portal_type      = 'Sale Invoice Transaction'
  sale_invoice_line_portal_type = 'Sale Invoice Line' 
  sale_invoice_transaction_line_portal_type = 'Sale Invoice Transaction Line'
  sale_invoice_cell_portal_type = 'Invoice Cell'
  purchase_invoice_portal_type      = 'Purchase Invoice Transaction'
  purchase_invoice_line_portal_type = 'Purchase Invoice Line' 
  purchase_invoice_transaction_line_portal_type = \
                'Purchase Invoice Transaction Line'
  purchase_invoice_cell_portal_type = 'Invoice Cell'

  start_date = DateTime(2004, 01, 01)
  stop_date  = DateTime(2004, 12, 31)

  default_region = 'europe/west/france'

  def getTitle(self):
    return "Accounting"
  
  def afterSetUp(self):
    """Prepare the test."""
    self.portal = self.getPortal()
    self.workflow_tool = self.portal.portal_workflow
    self.organisation_module = self.portal.organisation_module
    self.account_module = self.portal.account_module
    self.accounting_module = self.portal.accounting_module
    self.createCategories()
    self.createCurrencies()
    self.createEntities()
    self.createAccounts()

    # setup preference for the vendor group
    self.pref = self.portal.portal_preferences.newContent(
         portal_type='Preference', preferred_section_category='group/vendor',
         preferred_accounting_transaction_section_category='group/vendor',
         priority=3 )
    self.workflow_tool.doActionFor(self.pref, 'enable_action')

    self.login()

  def beforeTearDown(self):
    """Cleanup for next test.
    All tests uses the same accounts and same entities, so we just cleanup
    accounting module and simulation. """
    get_transaction().abort()
    for folder in (self.accounting_module, self.portal.portal_simulation):
      folder.manage_delObjects([i for i in folder.objectIds()])
    get_transaction().commit()
    self.tic()

  def login(self) :
    """sets the security manager"""
    uf = self.getPortal().acl_users
    uf._doAddUser('alex', '', ['Member', 'Assignee', 'Assignor',
                               'Auditor', 'Author', 'Manager'], [])
    user = uf.getUserById('alex').__of__(uf)
    newSecurityManager(None, user)
  
  def createCategories(self):
    """Create the categories for our test. """
    # create categories
    for cat_string in self.getNeededCategoryList():
      base_cat = cat_string.split("/")[0]
      path = self.getPortal().portal_categories[base_cat]
      for cat in cat_string.split("/")[1:]:
        if not cat in path.objectIds():
          path = path.newContent(
            portal_type='Category',
            id=cat,
            immediate_reindex=1)
        else:
          path = path[cat]
          
    # check categories have been created
    for cat_string in self.getNeededCategoryList() :
      self.assertNotEquals(None,
                self.getCategoryTool().restrictedTraverse(cat_string),
                cat_string)
                
  def getNeededCategoryList(self):
    """Returns a list of categories that should be created."""
    return ('group/client', 'group/vendor/sub1', 'group/vendor/sub2',
            'payment_mode/check', 'region/%s' % self.default_region, )
  
  def getBusinessTemplateList(self):
    """Returns list of BT to be installed."""
    return ('erp5_base', 'erp5_pdm', 'erp5_trade', 'erp5_accounting', )

  def stepTic(self, **kw):
    """Flush activity queue. """
    self.tic()
  
  def createEntities(self):
    """Create entities. """
    self.client = self.getOrganisationModule().newContent(
        title = 'Client',
        portal_type = self.organisation_portal_type,
        group = "client",
        price_currency = "currency_module/USD")
    self.vendor = self.getOrganisationModule().newContent(
        title = 'Vendor',
        portal_type = self.organisation_portal_type,
        group = "vendor/sub1",
        price_currency = "currency_module/EUR")
    self.other_vendor = self.getOrganisationModule().newContent(
        title = 'Other Vendor',
        portal_type = self.organisation_portal_type,
        group = "vendor/sub2",
        price_currency = "currency_module/EUR")
    # validate entities
    for entity in (self.client, self.vendor, self.other_vendor):
      entity.setRegion(self.default_region)
      self.getWorkflowTool().doActionFor(entity, 'validate_action')
    get_transaction().commit()
    self.tic()
    
  def stepCreateEntities(self, sequence, **kw) :
    """Create entities. """
    # TODO: remove this method
    sequence.edit( client=self.client,
                   vendor=self.vendor,
                   other_vendor=self.other_vendor,
                   organisation=self.vendor )
  
  def stepCreateAccountingPeriod(self, sequence, **kw):
    """Creates an Accounting Period for the Organisation."""
    organisation = sequence.get('organisation')
    start_date = self.start_date
    stop_date = self.stop_date
    accounting_period = organisation.newContent(
      portal_type = self.accounting_period_portal_type,
      start_date = start_date, stop_date = stop_date )
    sequence.edit( accounting_period = accounting_period,
                   valid_date_list = [ start_date, start_date+1, stop_date],
                   invalid_date_list = [start_date-1, stop_date+1] )
    
  def stepUseValidDates(self, sequence, **kw):
    """Puts some valid dates in sequence."""
    sequence.edit(date_list = sequence.get('valid_date_list'))
    
  def stepUseInvalidDates(self, sequence, **kw):
    """Puts some invalid dates in sequence."""
    sequence.edit(date_list = sequence.get('invalid_date_list'))
  
  def stepOpenAccountingPeriod(self, sequence, **kw):
    """Opens the Accounting Period."""
    accounting_period = sequence.get('accounting_period')
    self.getPortal().portal_workflow.doActionFor(
                        accounting_period,
                        'start_action' )
    self.assertEquals(accounting_period.getSimulationState(),
                      'started')
                      
  def stepConfirmAccountingPeriod(self, sequence, **kw):
    """Confirm the Accounting Period."""
    accounting_period = sequence.get('accounting_period')
    self.getPortal().portal_workflow.doActionFor(
                        accounting_period,
                        'stop_action' )
    self.assertEquals(accounting_period.getSimulationState(),
                      'stopped')

  def stepCheckAccountingPeriodRefusesClosing(self, sequence, **kw):
    """Checks the Accounting Period refuses closing."""
    accounting_period = sequence.get('accounting_period')
    self.assertRaises(ValidationFailed,
          self.getPortal().portal_workflow.doActionFor,
          accounting_period, 'stop_action' )

  def stepDeliverAccountingPeriod(self, sequence, **kw):
    """Deliver the Accounting Period."""
    accounting_period = sequence.get('accounting_period')
    # take any account for profit and loss account, here we don't care
    profit_and_loss_account = self.portal.account_module.contentValues()[0]
    self.getPortal().portal_workflow.doActionFor(
           accounting_period, 'deliver_action',
           profit_and_loss_account=profit_and_loss_account.getRelativeUrl())
    self.assertEquals(accounting_period.getSimulationState(),
                      'delivered')
    
  def stepCheckAccountingPeriodDelivered(self, sequence, **kw):
    """Check the Accounting Period is delivered."""
    accounting_period = sequence.get('accounting_period')
    self.assertEquals(accounting_period.getSimulationState(),
                      'delivered')
    
  def createCurrencies(self):
    """Create some currencies.
    This script will reuse existing currencies, because we want currency ids to
    be stable, as we use them as categories.
    """
    currency_module = self.getCurrencyModule()
    if not hasattr(currency_module, 'EUR'):
      self.EUR = currency_module.newContent(
          portal_type = self.currency_portal_type,
          reference = "EUR", id = "EUR" )
      self.USD = currency_module.newContent(
          portal_type = self.currency_portal_type,
          reference = "USD", id = "USD" )
      self.YEN = currency_module.newContent(
          portal_type = self.currency_portal_type,
          reference = "YEN", id = "YEN" )
      get_transaction().commit()
      self.tic()
    else:
      self.EUR = currency_module.EUR
      self.USD = currency_module.USD
      self.YEN = currency_module.YEN

  def stepCreateCurrencies(self, sequence, **kw) :
    """Create some currencies. """
    # TODO: remove
    sequence.edit(EUR=self.EUR, USD=self.USD, YEN=self.YEN)
  
  def createAccounts(self):
    """Create some accounts.
    """
    receivable = self.receivable_account = self.getAccountModule().newContent(
          title = 'receivable',
          portal_type = self.account_portal_type,
          account_type = 'asset/receivable' )
    payable = self.payable_account = self.getAccountModule().newContent(
          title = 'payable',
          portal_type = self.account_portal_type,
          account_type = 'liability/payable' )
    expense = self.expense_account = self.getAccountModule().newContent(
          title = 'expense',
          portal_type = self.account_portal_type,
          account_type = 'expense' )
    income = self.income_account = self.getAccountModule().newContent(
          title = 'income',
          portal_type = self.account_portal_type,
          account_type = 'income' )
    collected_vat = self.collected_vat_account = self\
                                        .getAccountModule().newContent(
          title = 'collected_vat',
          portal_type = self.account_portal_type,
          account_type = 'liability/payable/collected_vat' )
    refundable_vat = self.refundable_vat_account = self\
                                        .getAccountModule().newContent(
          title = 'refundable_vat',
          portal_type = self.account_portal_type,
          account_type = 'asset/receivable/refundable_vat' )
    bank = self.bank_account = self.getAccountModule().newContent(
          title = 'bank',
          portal_type = self.account_portal_type,
          account_type = 'asset/cash/bank')
    
    # set mirror accounts.
    receivable.setDestinationValue(payable)
    payable.setDestinationValue(receivable)
    expense.setDestinationValue(income)
    income.setDestinationValue(expense)
    collected_vat.setDestinationValue(refundable_vat)
    refundable_vat.setDestinationValue(collected_vat)
    bank.setDestinationValue(bank)
    
    self.account_list = [ receivable,
                          payable,
                          expense,
                          income,
                          collected_vat,
                          refundable_vat,
                          bank ]

    for account in self.account_list :
      account.validate()
      self.failUnless('Site Error' not in account.view())
      self.assertEquals(account.getValidationState(), 'validated')
    get_transaction().commit()
    self.tic()

  def stepCreateAccounts(self, sequence, **kw) :
    """Create necessary accounts. """
    # XXX remove me !  
    sequence.edit( receivable_account=self.receivable_account,
                   payable_account=self.payable_account,
                   expense_account=self.expense_account,
                   income_account=self.income_account,
                   collected_vat_account=self.collected_vat_account,
                   refundable_vat_account=self.refundable_vat_account,
                   bank_account=self.bank_account,
                   account_list=self.account_list )
  
    
  def getInvoicePropertyList(self):
    """Returns the list of properties for invoices, stored as 
      a list of dictionnaries. """
    # source currency is EUR
    # destination currency is USD
    return [
      # in currency of destination, converted for source
      { 'income' : -200,             'source_converted_income' : -180,
        'collected_vat' : -40,       'source_converted_collected_vat' : -36,
        'receivable' : 240,          'source_converted_receivable' : 216,
        'currency' : 'currency_module/USD' },
      
      # in currency of source, converted for destination
      { 'income' : -100,        'destination_converted_expense' : -200,
        'collected_vat' : 10,   'destination_converted_refundable_vat' : 100,
        'receivable' : 90,      'destination_converted_payable' : 100,
        'currency' : 'currency_module/EUR' },
      
      { 'income' : -100,        'destination_converted_expense' : -200,
        'collected_vat' : 10,   'destination_converted_refundable_vat' : 100,
        'receivable' : 90,      'destination_converted_payable' : 100,
        'currency' : 'currency_module/EUR' },
      
      # in an external currency, converted for both source and dest.
      { 'income' : -300,
                    'source_converted_income' : -200,
                    'destination_converted_expense' : -400,
        'collected_vat' : 40,
                    'source_converted_collected_vat' : 36,
                    'destination_converted_refundable_vat' : 50,
        'receivable' : 260,
                    'source_converted_receivable' : 164,
                    'destination_converted_payable': 350,
        'currency' : 'currency_module/YEN' },
      
      # currency of source, not converted for destination -> 0
      { 'income' : -100,
        'collected_vat' : -20,
        'receivable' : 120,
        'currency' : 'currency_module/EUR' },
      
    ]
  
  def stepCreateInvoices(self, sequence, **kw) :
    """Create invoices with properties from getInvoicePropertyList. """
    invoice_prop_list = self.getInvoicePropertyList()
    invoice_list = []
    date_list = sequence.get('date_list')
    if not date_list : date_list = [ DateTime(2004, 12, 31) ]
    i = 0
    for invoice_prop in invoice_prop_list :
      i += 1
      date = date_list[i % len(date_list)]
      invoice = self.getAccountingModule().newContent(
          portal_type = self.sale_invoice_portal_type,
          source_section_value = sequence.get('vendor'),
          source_value = sequence.get('vendor'),
          destination_section_value = sequence.get('client'),
          destination_value = sequence.get('client'),
          resource = invoice_prop['currency'],
          start_date = date, stop_date = date,
          created_by_builder = 0,
      )
      
      for line_type in ['income', 'receivable', 'collected_vat'] :
        source_account = sequence.get('%s_account' % line_type)
        line = invoice.newContent(
          portal_type = self.sale_invoice_transaction_line_portal_type,
          quantity = invoice_prop[line_type],
          source_value = source_account
        )
        source_converted = invoice_prop.get(
                          'source_converted_%s' % line_type, None)
        if source_converted is not None :
          line.setSourceTotalAssetPrice(source_converted)
        
        destination_account = source_account.getDestinationValue(
                                                portal_type = 'Account' )
        destination_converted = invoice_prop.get(
                          'destination_converted_%s' %
                          destination_account.getAccountTypeId(), None)
        if destination_converted is not None :
          line.setDestinationTotalAssetPrice(destination_converted)
 
      invoice_list.append(invoice)
    sequence.edit( invoice_list = invoice_list )
  
  def stepCreateOtherSectionInvoices(self, sequence, **kw):
    """Create invoice for other sections."""
    other_source = self.getOrganisationModule().newContent(
                      portal_type = 'Organisation' )
    other_destination = self.getOrganisationModule().newContent(
                      portal_type = 'Organisation' )
    invoice = self.getAccountingModule().newContent(
        portal_type = self.sale_invoice_portal_type,
        source_section_value = other_source,
        source_value = other_source,
        destination_section_value = other_destination,
        destination_value = other_destination,
        resource_value = sequence.get('EUR'),
        start_date = self.start_date,
        stop_date = self.start_date,
        created_by_builder = 0,
    )
    
    line = invoice.newContent(
        portal_type = self.sale_invoice_transaction_line_portal_type,
        quantity = 100, source_value = sequence.get('account_list')[0])
    line = invoice.newContent(
        portal_type = self.sale_invoice_transaction_line_portal_type,
        quantity = -100, source_value = sequence.get('account_list')[1])
    sequence.edit(invoice_list = [invoice])
  
  def stepStopInvoices(self, sequence, **kw) :
    """Validates invoices."""
    invoice_list = sequence.get('invoice_list')
    for invoice in invoice_list:
      self.getPortal().portal_workflow.doActionFor(
          invoice, 'stop_action')
  
  def stepCheckStopInvoicesRefused(self, sequence, **kw) :
    """Checks that invoices cannot be validated."""
    invoice_list = sequence.get('invoice_list')
    for invoice in invoice_list:
      self.assertRaises(ValidationFailed,
          self.getPortal().portal_workflow.doActionFor,
          invoice, 'stop_action')

  def stepCheckInvoicesAreDraft(self, sequence, **kw) :
    """Checks invoices are in draft state."""
    invoice_list = sequence.get('invoice_list')
    for invoice in invoice_list:
      self.assertEquals(invoice.getSimulationState(), 'draft')

  def stepCheckInvoicesAreStopped(self, sequence, **kw) :
    """Checks invoices are in stopped state."""
    invoice_list = sequence.get('invoice_list')
    for invoice in invoice_list:
      self.assertEquals(invoice.getSimulationState(), 'stopped')
      
  def checkAccountBalanceInCurrency(self, section, currency,
                                          sequence, **kw) :
    """ Checks accounts balances in a given currency."""
    invoice_list = sequence.get('invoice_list')
    for account_type in [ 'income', 'receivable', 'collected_vat',
                          'expense', 'payable', 'refundable_vat' ] :
      account = sequence.get('%s_account' % account_type)
      calculated_balance = 0
      for invoice in invoice_list :
        for line in invoice.getMovementList():
          # source
          if line.getSourceValue() == account and\
             line.getResourceValue() == currency and\
             section == line.getSourceSectionValue() :
            calculated_balance += (
                    line.getSourceDebit() - line.getSourceCredit())
          # dest.
          elif line.getDestinationValue() == account and\
            line.getResourceValue() == currency and\
            section == line.getDestinationSectionValue() :
            calculated_balance += (
                    line.getDestinationDebit() - line.getDestinationCredit())
      
      self.assertEquals(calculated_balance,
          self.getPortal().portal_simulation.getInventory(
            node_uid = account.getUid(),
            section_uid = section.getUid(),
            resource_uid = currency.getUid(),
          ))
  
  def stepCheckAccountBalanceLocalCurrency(self, sequence, **kw) :
    """ Checks accounts balances in the organisation default currency."""
    for section in (sequence.get('vendor'), sequence.get('client')) :
      currency = section.getPriceCurrencyValue()
      self.checkAccountBalanceInCurrency(section, currency, sequence)
  
  def stepCheckAccountBalanceExternalCurrency(self, sequence, **kw) :
    """ Checks accounts balances in external currencies ."""
    for section in (sequence.get('vendor'), sequence.get('client')) :
      for currency in (sequence.get('USD'), sequence.get('YEN')) :
        self.checkAccountBalanceInCurrency(section, currency, sequence)
    
  def checkAccountBalanceInConvertedCurrency(self, section, sequence, **kw) :
    """ Checks accounts balances converted in section default currency."""
    invoice_list = sequence.get('invoice_list')
    for account_type in [ 'income', 'receivable', 'collected_vat',
                          'expense', 'payable', 'refundable_vat' ] :
      account = sequence.get('%s_account' % account_type)
      calculated_balance = 0
      for invoice in invoice_list :
        for line in invoice.getMovementList() :
          if line.getSourceValue() == account and \
             section == line.getSourceSectionValue() :
            calculated_balance += line.getSourceInventoriatedTotalAssetPrice()
          elif line.getDestinationValue() == account and\
               section == line.getDestinationSectionValue() :
            calculated_balance += \
                             line.getDestinationInventoriatedTotalAssetPrice()
      self.assertEquals(calculated_balance,
          self.getPortal().portal_simulation.getInventoryAssetPrice(
            node_uid = account.getUid(),
            section_uid = section.getUid(),
          ))
  
  def stepCheckAccountBalanceConvertedCurrency(self, sequence, **kw):
    """Checks accounts balances converted in the organisation default
    currency."""
    for section in (sequence.get('vendor'), sequence.get('client')) :
      self.checkAccountBalanceInConvertedCurrency(section, sequence)
  
  def stepCheckAcquisition(self, sequence, **kw):
    """Checks acquisition and portal types configuration. """
    resource_value = sequence.get('EUR')
    source_section_title = "Source Section Title"
    destination_section_title = "Destination Section Title"
    source_section_value = self.getOrganisationModule().newContent(
        portal_type = self.organisation_portal_type,
        title = source_section_title,
        group = "group/client",
        price_currency = "currency_module/USD")
    destination_section_value = self.getOrganisationModule().newContent(
        portal_type = self.organisation_portal_type,
        title = destination_section_title,
        group = "group/vendor",
        price_currency = "currency_module/EUR")
    
    portal = self.getPortal()
    accounting_module = portal.accounting_module
    self.failUnless('Site Error' not in accounting_module.view())
    self.assertNotEquals(
          len(portal.getPortalAccountingMovementTypeList()), 0)
    self.assertNotEquals(
          len(portal.getPortalAccountingTransactionTypeList()), 0)
    for accounting_portal_type in portal\
                    .getPortalAccountingTransactionTypeList():
      accounting_transaction = accounting_module.newContent(
            portal_type = accounting_portal_type,
            source_section_value = source_section_value,
            destination_section_value = destination_section_value,
            resource_value = resource_value )
      self.failUnless('Site Error' not in accounting_transaction.view())
      self.assertEquals( accounting_transaction.getSourceSectionValue(),
                         source_section_value )
      self.assertEquals( accounting_transaction.getDestinationSectionValue(),
                         destination_section_value )
      self.assertEquals( accounting_transaction.getResourceValue(),
                         resource_value )
      self.assertNotEquals(
              len(accounting_transaction.allowedContentTypes()), 0)
      tested_line_portal_type = 0
      for line_portal_type in portal.getPortalAccountingMovementTypeList():
        allowed_content_types = [x.id for x in
                            accounting_transaction.allowedContentTypes()]
        if line_portal_type in allowed_content_types :
          line = accounting_transaction.newContent(
            portal_type = line_portal_type, )
          self.failUnless('Site Error' not in line.view())
          # section and resource is acquired from parent transaction.
          self.assertEquals( line.getDestinationSectionValue(),
                             destination_section_value )
          self.assertEquals( line.getDestinationSectionTitle(),
                             destination_section_title )
          self.assertEquals( line.getSourceSectionValue(),
                             source_section_value )
          self.assertEquals( line.getSourceSectionTitle(),
                             source_section_title )
          self.assertEquals( line.getResourceValue(),
                             resource_value )
          tested_line_portal_type = 1
      self.assert_(tested_line_portal_type, ("No lines tested ... " +
                          "getPortalAccountingMovementTypeList = %s " +
                          "<%s>.allowedContentTypes = %s") %
                          (portal.getPortalAccountingMovementTypeList(),
                            accounting_transaction.getPortalType(),
                            allowed_content_types ))
  
  def createAccountingTransaction(self,
                        portal_type=accounting_transaction_portal_type,
                        line_portal_type=accounting_transaction_line_portal_type,
                        quantity=100, reindex=1, check_consistency=1, **kw):
    """Creates an accounting transaction.
    By default, this transaction contains 2 lines, income and receivable.
      quantity          - The quantity property on created lines.
      reindex           - The transaction will be reindexed.
      check_consistency - a consistency check will be performed on the
                          transaction.
    """
    kw.setdefault('resource_value', self.EUR)
    kw.setdefault('source_section_value', self.vendor)
    kw.setdefault('destination_section_value', self.client)
    if 'start_date' not in kw:
      start_date = DateTime(2000, 01, 01)
      # get a valid date for source section
      for openned_source_section_period in\
        kw['source_section_value'].searchFolder(
              portal_type=self.accounting_period_portal_type,
              simulation_state='planned' ):
        start_date = openned_source_section_period.getStartDate() + 1
      kw['start_date'] = start_date

    if 'stop_date' not in kw:
      # get a valid date for destination section
      stop_date = DateTime(2000, 02, 02)
      for openned_destination_section_period in\
        kw['destination_section_value'].searchFolder(
              portal_type=self.accounting_period_portal_type,
              simulation_state='planned' ):
        stop_date = openned_destination_section_period.getStartDate() + 1
      kw['stop_date'] = stop_date

    # create the transaction.
    transaction = self.getAccountingModule().newContent(
      portal_type=portal_type,
      start_date=kw['start_date'],
      stop_date=kw['stop_date'],
      resource_value=kw['resource_value'],
      source_section_value=kw['source_section_value'],
      destination_section_value=kw['destination_section_value'],
      created_by_builder = 1 # prevent the init script from
                             # creating lines.
    )
    income = transaction.newContent(
                  id='income',
                  portal_type=line_portal_type,
                  quantity=-quantity,
                  source_value=kw.get('income_account', self.income_account),
                  destination_value=kw.get('expense_account',
                                              self.expense_account), )
    self.failUnless(income.getSource() != None)
    self.failUnless(income.getDestination() != None)
    
    receivable = transaction.newContent(
                  id='receivable',
                  portal_type=line_portal_type,
                  quantity=quantity,
                  source_value=kw.get('receivable_account',
                                          self.receivable_account),
                  destination_value=kw.get('payable_account',
                                            self.payable_account), )
    self.failUnless(receivable.getSource() != None)
    self.failUnless(receivable.getDestination() != None)
    if reindex:
      get_transaction().commit()
      self.tic()
    if check_consistency:
      self.failUnless(len(transaction.checkConsistency()) == 0,
         "Check consistency failed : %s" % transaction.checkConsistency())
    return transaction

  def test_createAccountingTransaction(self):
    """Make sure acounting transactions created by createAccountingTransaction
    method are valid.
    """
    transaction = self.createAccountingTransaction()
    self.assertEquals(self.vendor, transaction.getSourceSectionValue())
    self.assertEquals(self.client, transaction.getDestinationSectionValue())
    self.assertEquals(self.EUR, transaction.getResourceValue())
    self.failUnless(transaction.AccountingTransaction_isSourceView())
    
    self.workflow_tool.doActionFor(transaction, 'stop_action')
    self.assertEquals('stopped', transaction.getSimulationState())
    self.assertEquals([] , transaction.checkConsistency())

  def stepCreateValidAccountingTransaction(self, sequence,
                                          sequence_list=None, **kw) :
    """Creates a valid accounting transaction and put it in
    the sequence as `transaction` key. """
    transaction = self.createAccountingTransaction(
                            resource_value=sequence.get('EUR'),
                            source_section_value=sequence.get('vendor'),
                            destination_section_value=sequence.get('client'),
                            income_account=sequence.get('income_account'),
                            expense_account=sequence.get('expense_account'),
                            receivable_account=sequence.get('receivable_account'),
                            payable_account=sequence.get('payable_account'), )
    sequence.edit(
      transaction = transaction,
      income = transaction.income,
      receivable = transaction.receivable
    )
    
  def stepValidateNoDate(self, sequence, sequence_list=None, **kw) :
    """When no date is defined, validation should be impossible.
    
    Actually, we could say that if we have source_section, we need start_date,
    and if we have destination section, we need stop_date only, but we decided
    to update a date (of start_date / stop_date) using the other one if one is
    missing. (ie. stop_date defaults automatically to start_date if not set and
    start_date is set to stop_date in the workflow script if not set.
    """
    transaction = sequence.get('transaction')
    old_stop_date = transaction.getStopDate()
    old_start_date = transaction.getStartDate()
    transaction.setStopDate(None)
    if transaction.getStopDate() != None :
      transaction.setStartDate(None)
      transaction.setStopDate(None)
    self.assertRaises(ValidationFailed,
        self.getWorkflowTool().doActionFor,
        transaction,
        'stop_action')
    transaction.setStartDate(old_start_date)
    transaction.setStopDate(old_stop_date)
    self.getWorkflowTool().doActionFor(transaction, 'stop_action')
    self.assertEquals(transaction.getSimulationState(), 'stopped')
  
  def stepValidateNoSection(self, sequence, sequence_list=None, **kw) :
    """Check validation behaviour related to section & mirror_section.
    When no source section is defined, we are in one of the following
    cases : 
      o if we use payable or receivable account, the validation should
        be refused.
      o if we do not use any payable or receivable accounts and we have
      a destination section, validation should be ok.
    """
    transaction = sequence.get('transaction')
    old_source_section = transaction.getSourceSection()
    old_destination_section = transaction.getDestinationSection()
    # default transaction uses payable accounts, so validating without
    # source section is refused.
    transaction.setSourceSection(None)
    self.assertRaises(ValidationFailed,
        self.getWorkflowTool().doActionFor,
        transaction,
        'stop_action')
    # ... as well as validation without destination section
    transaction.setSourceSection(old_source_section)
    transaction.setDestinationSection(None)
    self.assertRaises(ValidationFailed,
        self.getWorkflowTool().doActionFor,
        transaction,
        'stop_action')
    # mirror section can be set only on the line
    for line in transaction.getMovementList() :
      if line.getSourceValue().isMemberOf(
              'account_type/asset/receivable') or \
         line.getSourceValue().isMemberOf(
              'account_type/liability/payable') :
        line.setDestinationSection(old_destination_section)
    try:
      self.getWorkflowTool().doActionFor(transaction, 'stop_action')
      self.assertEquals(transaction.getSimulationState(), 'stopped')
    except ValidationFailed, err :
      self.assert_(0, "Validation failed : %s" % err.msg)
    
    # if we do not use any payable / receivable account, then we can
    # validate the transaction without setting the mirror section.
    for side in (SOURCE, ): # DESTINATION) :
      # TODO: for now, we only test for source, as it makes no sense to use for
      # destination section only. We could theoritically support it.

      # get a new valid transaction
      transaction = self.createAccountingTransaction()
      expense_account = sequence.get('expense_account')
      for line in transaction.getMovementList() :
        line.edit( source_value = expense_account,
                   destination_value = expense_account )
      if side == SOURCE :
        transaction.setDestinationSection(None)
      else :
        transaction.setSourceSection(None)
      try:
        self.getWorkflowTool().doActionFor(transaction, 'stop_action')
        self.assertEquals(transaction.getSimulationState(), 'stopped')
      except ValidationFailed, err :
        self.assert_(0, "Validation failed : %s" % err.msg)
        
  def stepValidateNoCurrency(self, sequence, sequence_list=None, **kw) :
    """Check validation behaviour related to currency.
    """
    transaction = sequence.get('transaction')
    old_resource = transaction.getResource()
    transaction.setResource(None)
    self.assertRaises(ValidationFailed,
        self.getWorkflowTool().doActionFor,
        transaction,
        'stop_action')
    # setting a dummy relationship is not enough, resource must be a
    # currency
    transaction.setResource(transaction.getDestinationSection())
    self.assertRaises(ValidationFailed,
        self.getWorkflowTool().doActionFor,
        transaction,
        'stop_action')
    
  def stepValidateClosedAccount(self, sequence, sequence_list=None, **kw) :
    """Check validation behaviour related to closed accounts.
    If an account is blocked, then it's impossible to validate a
    transaction related to this account.
    """
    transaction = sequence.get('transaction')
    account = transaction.getMovementList()[0].getSourceValue()
    self.getWorkflowTool().doActionFor(account, 'invalidate_action')
    self.assertEquals(account.getValidationState(), 'invalidated')
    self.assertRaises(ValidationFailed,
        self.getWorkflowTool().doActionFor,
        transaction,
        'stop_action')
    # reopen the account for other tests
    account.validate()
    self.assertEquals(account.getValidationState(), 'validated')
    
  def stepValidateNoAccounts(self, sequence, sequence_list=None, **kw) :
    """Simple check that the validation is refused when we do not have
    accounts correctly defined on lines.
    """
    transaction = sequence.get('transaction')
    # no account at all is refused
    for line in transaction.getMovementList():
      line.setSource(None)
      line.setDestination(None)
    self.assertRaises(ValidationFailed,
        self.getWorkflowTool().doActionFor,
        transaction,
        'stop_action')
    
    # only one line without account and with a quantity is also refused
    transaction = self.createAccountingTransaction()
    transaction.getMovementList()[0].setSource(None)
    transaction.getMovementList()[0].setDestination(None)
    self.assertRaises(ValidationFailed,
        self.getWorkflowTool().doActionFor,
        transaction,
        'stop_action')
    
    # but if we have a line with 0 quantity on both sides, we can
    # validate the transaction and delete this line.
    transaction = self.createAccountingTransaction()
    line_count = len(transaction.getMovementList())
    transaction.newContent(
        portal_type = self.accounting_transaction_line_portal_type)
    self.getWorkflowTool().doActionFor(transaction, 'stop_action')
    self.assertEquals(transaction.getSimulationState(), 'stopped')
    self.assertEquals(line_count, len(transaction.getMovementList()))
    
    # 0 quantity, but a destination asset price => do not delete the
    # line
    transaction = self.createAccountingTransaction()
    new_line = transaction.newContent(
        portal_type = self.accounting_transaction_line_portal_type)
    self.assertEquals(len(transaction.getMovementList()), 3)
    line_list = transaction.getMovementList()
    line_list[0].setDestinationTotalAssetPrice(100)
    line_list[0]._setCategoryMembership(
          'destination', sequence.get('expense_account').getRelativeUrl())
    line_list[1].setDestinationTotalAssetPrice(- 50)
    line_list[1]._setCategoryMembership(
          'destination', sequence.get('expense_account').getRelativeUrl())
    line_list[2].setDestinationTotalAssetPrice(- 50)
    line_list[2]._setCategoryMembership(
          'destination', sequence.get('expense_account').getRelativeUrl())
    try:
      self.getWorkflowTool().doActionFor(transaction, 'stop_action')
      self.assertEquals(transaction.getSimulationState(), 'stopped')
    except ValidationFailed, err :
      self.assert_(0, "Validation failed : %s" % err.msg)
  
  def stepValidateNotBalanced(self, sequence, sequence_list=None, **kw) :
    """Check validation behaviour when transaction is not balanced.
    """
    transaction = sequence.get('transaction')
    transaction.getMovementList()[0].setQuantity(4325)
    self.assertRaises(ValidationFailed,
        self.getWorkflowTool().doActionFor,
        transaction,
        'stop_action')
    
    # asset price have priority (ie. if asset price is not balanced,
    # refuses validation even if quantity is balanced)
    transaction = self.createAccountingTransaction()
    line_list = transaction.getMovementList()
    line_list[0].setDestinationTotalAssetPrice(10)
    line_list[1].setDestinationTotalAssetPrice(100)
    self.assertRaises(ValidationFailed,
        self.getWorkflowTool().doActionFor,
        transaction,
        'stop_action')
    
    transaction = self.createAccountingTransaction()
    line_list = transaction.getMovementList()
    line_list[0].setSourceTotalAssetPrice(10)
    line_list[1].setSourceTotalAssetPrice(100)
    self.assertRaises(ValidationFailed,
        self.getWorkflowTool().doActionFor,
        transaction,
        'stop_action')
    
    # only asset price needs to be balanced
    transaction = self.createAccountingTransaction()
    line_list = transaction.getMovementList()
    line_list[0].setSourceTotalAssetPrice(100)
    line_list[0].setDestinationTotalAssetPrice(100)
    line_list[0].setQuantity(432432)
    line_list[1].setSourceTotalAssetPrice(-100)
    line_list[1].setDestinationTotalAssetPrice(-100)
    line_list[1].setQuantity(32546787)
    try:
      self.getWorkflowTool().doActionFor(transaction, 'stop_action')
      self.assertEquals(transaction.getSimulationState(), 'stopped')
    except ValidationFailed, err :
      self.assert_(0, "Validation failed : %s" % err.msg)
  
  def stepValidateNoPayment(self, sequence, sequence_list=None, **kw) :
    """Check validation behaviour related to payment & mirror_payment.
    If we use an account of type asset/cash/bank, we must use set a Bank
    Account as source_payment or destination_payment.
    This this source/destination payment must be a portal type from the
    `payment node` portal type group. It can be defined on transaction
    or line.
    """
    def useBankAccount(transaction):
      """Modify the transaction, so that a line will use an account member of
      account_type/cash/bank , which requires to use a payment category.
      """
      # get the default and replace income account by bank
      income_account_found = 0
      for line in transaction.getMovementList() :
        source_account = line.getSourceValue()
        if source_account.isMemberOf('account_type/income') :
          income_account_found = 1
          line.edit( source_value = sequence.get('bank_account'),
                     destination_value = sequence.get('bank_account') )
      self.failUnless(income_account_found)
    # XXX
    transaction = sequence.get('transaction')
    useBankAccount(transaction)
    self.assertRaises(ValidationFailed,
        self.getWorkflowTool().doActionFor,
        transaction,
        'stop_action')
    
    source_section_value = transaction.getSourceSectionValue()
    destination_section_value = transaction.getDestinationSectionValue()
    for ptype in self.getPortal().getPortalPaymentNodeTypeList() :
      source_payment_value = source_section_value.newContent(
                                  portal_type = ptype, )
      destination_payment_value = destination_section_value.newContent(
                                  portal_type = ptype, )
      transaction = self.createAccountingTransaction(
                      destination_section_value=self.other_vendor)
      useBankAccount(transaction)

      # payment node have to be set on both sides if both sides are member of
      # the same group.
      transaction.setSourcePaymentValue(source_payment_value)
      transaction.setDestinationPaymentValue(None)
      self.assertRaises(ValidationFailed,
          self.getWorkflowTool().doActionFor,
          transaction,
          'stop_action')
      transaction.setSourcePaymentValue(None)
      transaction.setDestinationPaymentValue(destination_payment_value)
      self.assertRaises(ValidationFailed,
          self.getWorkflowTool().doActionFor,
          transaction,
          'stop_action')
      transaction.setSourcePaymentValue(source_payment_value)
      transaction.setDestinationPaymentValue(destination_payment_value)
      try:
        self.getWorkflowTool().doActionFor(transaction, 'stop_action')
        self.assertEquals(transaction.getSimulationState(), 'stopped')
      except ValidationFailed, err :
        self.fail("Validation failed : %s" % err.msg)

      # if we are not interested in the accounting for the third party, no need
      # to have a destination_payment
      transaction = self.createAccountingTransaction()
      useBankAccount(transaction)
      # only set payment for source
      transaction.setSourcePaymentValue(source_payment_value)
      transaction.setDestinationPaymentValue(None)
      # then we should be able to validate.
      try:
        self.getWorkflowTool().doActionFor(transaction, 'stop_action')
        self.assertEquals(transaction.getSimulationState(), 'stopped')
      except ValidationFailed, err:
        self.fail("Validation failed : %s" % err.msg)
    
  def stepValidateRemoveEmptyLines(self, sequence, sequence_list=None, **kw):
    """Check validating a transaction remove empty lines. """
    transaction = sequence.get('transaction')
    lines_count = len(transaction.getMovementList())
    empty_lines_count = 0
    for line in transaction.getMovementList():
      if line.getSourceTotalAssetPrice() ==  \
         line.getDestinationTotalAssetPrice() == 0:
        empty_lines_count += 1
    if empty_lines_count == 0:
      transaction.newContent(
            portal_type=self.accounting_transaction_line_portal_type)
    
    self.getWorkflowTool().doActionFor(transaction, 'stop_action')
    self.assertEquals(len(transaction.getMovementList()),
                      lines_count - empty_lines_count)
    
    # we don't remove empty lines if there is only empty lines
    transaction = self.getAccountingModule().newContent(
                      portal_type=self.accounting_transaction_portal_type,
                      created_by_builder=1)
    for i in range(3):
      transaction.newContent(
            portal_type=self.accounting_transaction_line_portal_type)
    lines_count = len(transaction.getMovementList())
    transaction.AccountingTransaction_deleteEmptyLines(redirect=0)
    self.assertEquals(len(transaction.getMovementList()), lines_count)
    
  ############################################################################
  ## Test Methods ############################################################
  ############################################################################
  
  def test_MultiCurrencyInvoice(self, quiet=QUIET, run=RUN_ALL_TESTS):
    """Basic test for multi currency accounting"""
    if not run : return
    self.playSequence("""
      stepCreateCurrencies
      stepCreateEntities
      stepCreateAccounts
      stepCreateInvoices
      stepTic
      stepCheckAccountBalanceLocalCurrency
      stepCheckAccountBalanceExternalCurrency
      stepCheckAccountBalanceConvertedCurrency
    """, quiet=quiet)

  def test_AccountingPeriodRefusesWrongDateTransactionValidation(
        self, quiet=QUIET, run=RUN_ALL_TESTS):
    """Accounting Periods prevents transactions from being validated when there
    is no oppened accounting period"""
    if not run : return
    self.playSequence("""
      stepCreateCurrencies
      stepCreateEntities
      stepCreateAccounts
      stepCreateAccountingPeriod
      stepOpenAccountingPeriod
      stepTic
      stepUseInvalidDates
      stepCreateInvoices
      stepCheckStopInvoicesRefused
      stepTic
      stepCheckInvoicesAreDraft
    """, quiet=quiet)

  def test_AccountingPeriodNotStoppedTransactions(self, quiet=QUIET,
                                                  run=RUN_ALL_TESTS):
    """Accounting Periods refuse to close when some transactions are
      not stopped"""
    if not run : return
    self.playSequence("""
      stepCreateCurrencies
      stepCreateEntities
      stepCreateAccounts
      stepCreateAccountingPeriod
      stepOpenAccountingPeriod
      stepTic
      stepCreateInvoices
      stepTic
      stepCheckAccountingPeriodRefusesClosing
      stepTic
      stepCheckInvoicesAreDraft
    """, quiet=quiet)

  def test_AccountingPeriodOtherSections(self, quiet=QUIET,
                                                  run=RUN_ALL_TESTS):
    """Accounting Periods does not change other section transactions."""
    if not run : return
    self.playSequence("""
      stepCreateCurrencies
      stepCreateEntities
      stepCreateAccounts
      stepCreateAccountingPeriod
      stepOpenAccountingPeriod
      stepTic
      stepCreateOtherSectionInvoices
      stepTic
      stepConfirmAccountingPeriod
      stepTic
      stepDeliverAccountingPeriod
      stepTic
      stepCheckAccountingPeriodDelivered
      stepCheckInvoicesAreDraft
    """, quiet=quiet)

  def test_Acquisition(self, quiet=QUIET, run=RUN_ALL_TESTS):
    """Tests acquisition, categories and portal types are well
    configured. """
    if not run : return
    self.playSequence("""
      stepCreateCurrencies
      stepCheckAcquisition
      """, quiet=quiet)

  def test_AccountingTransactionValidationDate(self, quiet=QUIET,
                                            run=RUN_ALL_TESTS):
    """Transaction validation and dates"""
    if not run : return
    self.playSequence("""
      stepCreateEntities
      stepCreateCurrencies
      stepCreateAccounts
      stepCreateValidAccountingTransaction
      stepValidateNoDate""", quiet=quiet)


  def test_AccountingTransactionValidationSection(self, quiet=QUIET,
                                             run=RUN_ALL_TESTS):
    """Transaction validation and section"""
    if not run : return
    self.playSequence("""
      stepCreateEntities
      stepCreateCurrencies
      stepCreateAccounts
      stepCreateValidAccountingTransaction
      stepValidateNoSection""", quiet=quiet)

  def test_AccountingTransactionValidationCurrency(self, quiet=QUIET,
                                           run=RUN_ALL_TESTS):
    """Transaction validation and currency"""
    if not run : return
    self.playSequence("""
      stepCreateEntities
      stepCreateCurrencies
      stepCreateAccounts
      stepCreateValidAccountingTransaction
      stepValidateNoCurrency""", quiet=quiet)

  def test_AccountingTransactionValidationAccounts(self, quiet=QUIET,
                                           run=RUN_ALL_TESTS):
    """Transaction validation and accounts"""
    if not run : return
    self.playSequence("""
      stepCreateEntities
      stepCreateCurrencies
      stepCreateAccounts
      stepCreateValidAccountingTransaction
      stepValidateClosedAccount
      stepCreateValidAccountingTransaction
      stepValidateNoAccounts""", quiet=quiet)

  def test_AccountingTransactionValidationBalanced(self, quiet=QUIET,
                                              run=RUN_ALL_TESTS):
    """Transaction validation and balance"""
    if not run : return
    self.playSequence("""
      stepCreateEntities
      stepCreateCurrencies
      stepCreateAccounts
      stepCreateValidAccountingTransaction
      stepValidateNotBalanced""", quiet=quiet)

  def test_AccountingTransactionValidationPayment(self, quiet=QUIET,
                                             run=RUN_ALL_TESTS):
    """Transaction validation and payment"""
    if not run : return
    self.playSequence("""
      stepCreateEntities
      stepCreateCurrencies
      stepCreateAccounts
      stepCreateValidAccountingTransaction
      stepValidateNoPayment
    """, quiet=quiet)

  def test_AccountingTransactionValidationRemoveEmptyLines(self, quiet=QUIET,
                                             run=RUN_ALL_TESTS):
    """Transaction validation removes empty lines"""
    if not run : return
    self.playSequence("""
      stepCreateEntities
      stepCreateCurrencies
      stepCreateAccounts
      stepCreateValidAccountingTransaction
      stepValidateRemoveEmptyLines
    """, quiet=quiet)

  def test_AccountingTransactionValidationRefusedWithCategoriesAsSections(self,
                                        quiet=QUIET, run=RUN_ALL_TESTS):
    """Validating a transaction with categories as sections is refused.
    See http://wiki.erp5.org/Discussion/AccountingProblems """
    category = self.vendor.getGroupValue()
    self.assertNotEquals(category, None)
    transaction = self.createAccountingTransaction(
                                    source_section_value=category)
    self.assertRaises(ValidationFailed, self.getWorkflowTool().doActionFor,
                      transaction, 'stop_action')
    transaction = self.createAccountingTransaction(
                                    destination_section_value=category)
    self.assertRaises(ValidationFailed, self.getWorkflowTool().doActionFor,
                      transaction, 'stop_action')

  def test_Account_isCreditAccount(self):
    """Tests the 'credit_account' property on account, which was named
    is_credit_account, which generated isIsCreditAccount accessor"""
    account = self.getAccountModule().newContent(portal_type='Account')
    # simulate an old object
    account.is_credit_account = True
    self.failUnless(account.isCreditAccount())
    self.failUnless(account.getProperty('credit_account'))
    
    account.setCreditAccount(False)
    self.failIf(account.isCreditAccount())

  # tests for Invoice_createRelatedPaymentTransaction
  def _checkRelatedSalePayment(self, invoice, payment, payment_node, quantity):
    """Check payment of a Sale Invoice.
    """
    eq = self.assertEquals
    eq('Payment Transaction', payment.getPortalTypeName())
    eq([invoice], payment.getCausalityValueList())
    eq(invoice.getSourceSection(), payment.getSourceSection())
    eq(invoice.getDestinationSection(), payment.getDestinationSection())
    eq(payment_node, payment.getSourcePaymentValue())
    eq(self.getCategoryTool().payment_mode.check,
       payment.getPaymentModeValue())
    # test lines
    eq(2, len(payment.getMovementList()))
    for line in payment.getMovementList():
      if line.getId() == 'bank':
        eq(quantity, line.getSourceCredit())
        eq(self.bank_account, line.getSourceValue())
      else:
        eq(quantity, line.getSourceDebit())
        eq(self.receivable_account, line.getSourceValue())
    # this transaction can be validated
    eq([], payment.checkConsistency())
    self.workflow_tool.doActionFor(payment, 'stop_action')
    eq('stopped', payment.getSimulationState())

  def test_Invoice_createRelatedPaymentTransactionSimple(self):
    """Simple case of creating a related payment transaction.
    """
    payment_node = self.vendor.newContent(portal_type='Bank Account')
    invoice = self.createAccountingTransaction()
    payment = invoice.Invoice_createRelatedPaymentTransaction(
                                  node=self.bank_account.getRelativeUrl(),
                                  payment=payment_node.getRelativeUrl(),
                                  payment_mode='check',
                                  batch_mode=1)
    self._checkRelatedSalePayment(invoice, payment, payment_node, 100)

  def test_Invoice_createRelatedPaymentTransactionGroupedLines(self):
    """Simple creating a related payment transaction when grouping reference of
    some lines is already set.
    """
    payment_node = self.vendor.newContent(portal_type='Bank Account')
    invoice = self.createAccountingTransaction()
    invoice.receivable.setSourceCredit(60)
    invoice.newContent(id='receivable_groupped',
                       source_credit=40,
                       source_value=self.receivable_account)
    invoice.receivable_groupped.setGroupingReference('A')
    
    payment = invoice.Invoice_createRelatedPaymentTransaction(
                                  node=self.bank_account.getRelativeUrl(),
                                  payment=payment_node.getRelativeUrl(),
                                  payment_mode='check',
                                  batch_mode=1)
    self._checkRelatedSalePayment(invoice, payment, payment_node, 60)
  
  def test_Invoice_createRelatedPaymentTransactionDifferentSection(self):
    """Simple creating a related payment transaction when we have two line for
    2 different destination sections.
    """
    payment_node = self.vendor.newContent(portal_type='Bank Account')
    invoice = self.createAccountingTransaction()
    invoice.receivable.setSourceCredit(60)
    invoice.newContent(id='receivable_other_third_party',
                       destination_section_value=self.other_vendor,
                       source_credit=40,
                       source_value=self.receivable_account)
    
    payment = invoice.Invoice_createRelatedPaymentTransaction(
                                  node=self.bank_account.getRelativeUrl(),
                                  payment=payment_node.getRelativeUrl(),
                                  payment_mode='check',
                                  batch_mode=1)
    self._checkRelatedSalePayment(invoice, payment, payment_node, 60)
 
  def test_Invoice_createRelatedPaymentTransactionRelatedInvoice(self):
    """Simple creating a related payment transaction when we have related
    transactions.
    """
    payment_node = self.vendor.newContent(portal_type='Bank Account')
    invoice = self.createAccountingTransaction()
    accounting_transaction = self.createAccountingTransaction()
    accounting_transaction.receivable.setSourceDebit(20)
    accounting_transaction.income.setSourceCredit(20)
    accounting_transaction.setCausalityValue(invoice)
    self.portal.portal_workflow.doActionFor(accounting_transaction,
                                           'stop_action')
    self.assertEquals('stopped', accounting_transaction.getSimulationState())
    get_transaction().commit()
    self.tic()
    
    payment = invoice.Invoice_createRelatedPaymentTransaction(
                                  node=self.bank_account.getRelativeUrl(),
                                  payment=payment_node.getRelativeUrl(),
                                  payment_mode='check',
                                  batch_mode=1)
    self._checkRelatedSalePayment(invoice, payment, payment_node, 80)
    
  def test_Invoice_createRelatedPaymentTransactionRelatedInvoiceDifferentSide(self):
    """Simple creating a related payment transaction when we have related
    transactions with different side
    """
    payment_node = self.vendor.newContent(portal_type='Bank Account')
    invoice = self.createAccountingTransaction()
    accounting_transaction = self.createAccountingTransaction()
    accounting_transaction.edit(
            source_section=accounting_transaction.getDestinationSection(),
            destination_section=accounting_transaction.getSourceSection())
    accounting_transaction.receivable.edit(
          source=accounting_transaction.receivable.getDestination(),
          destination=accounting_transaction.receivable.getSource(),
          destination_debit=20)
    accounting_transaction.income.edit(
          source=accounting_transaction.income.getDestination(),
          destination=accounting_transaction.income.getSource(),
          destination_credit=20)
    accounting_transaction.setCausalityValue(invoice)
    self.portal.portal_workflow.doActionFor(accounting_transaction,
                                            'stop_action')
    self.assertEquals('stopped', accounting_transaction.getSimulationState())
    get_transaction().commit()
    self.tic()

    payment = invoice.Invoice_createRelatedPaymentTransaction(
                                  node=self.bank_account.getRelativeUrl(),
                                  payment=payment_node.getRelativeUrl(),
                                  payment_mode='check',
                                  batch_mode=1)
    self._checkRelatedSalePayment(invoice, payment, payment_node, 80)
 
  def test_Invoice_createRelatedPaymentTransactionRelatedInvoiceDraft(self):
    """Simple creating a related payment transaction when we have related
    transactions in draft/cancelled state (they are ignored)
    """
    payment_node = self.vendor.newContent(portal_type='Bank Account')
    invoice = self.createAccountingTransaction()
    accounting_transaction = self.createAccountingTransaction()
    accounting_transaction.setCausalityValue(invoice)
    other_accounting_transaction = self.createAccountingTransaction()
    other_accounting_transaction.setCausalityValue(invoice)
    other_accounting_transaction.cancel()
    get_transaction().commit()
    self.tic()

    payment = invoice.Invoice_createRelatedPaymentTransaction(
                                  node=self.bank_account.getRelativeUrl(),
                                  payment=payment_node.getRelativeUrl(),
                                  payment_mode='check',
                                  batch_mode=1)
    self._checkRelatedSalePayment(invoice, payment, payment_node, 100)

  def test_SourceDestinationReference(self):
    """Check that source reference and destination reference are filled
    automatically.
    """
    # clear all existing ids in portal ids
    if hasattr(self.portal.portal_ids, 'dict_ids'):
      self.portal.portal_ids.dict_ids.clear()
    accounting_transaction = self.createAccountingTransaction()
    self.portal.portal_workflow.doActionFor(
          accounting_transaction, 'stop_action')
    self.assertEquals('1', accounting_transaction.getSourceReference())
    self.assertEquals('1', accounting_transaction.getDestinationReference())

    other_transaction = self.createAccountingTransaction()
    other_transaction.setDestinationSectionValue(self.other_vendor)
    self.portal.portal_workflow.doActionFor(other_transaction, 'stop_action')
    self.assertEquals('2', other_transaction.getSourceReference())
    self.assertEquals('1', other_transaction.getDestinationReference())


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestAccounting))
  suite.addTest(unittest.makeSuite(TestClosingPeriod))
  suite.addTest(unittest.makeSuite(TestTransactionValidation))
  return suite

