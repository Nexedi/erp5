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
import os

from DateTime import DateTime
from Products.CMFCore.utils import _checkPermission

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import reindex
from Products.DCWorkflow.DCWorkflow import ValidationFailed
from AccessControl.SecurityManagement import newSecurityManager
from Products.ERP5Type.tests.Sequence import SequenceList
from Products.ERP5Form.PreferenceTool import Priority

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
  }


class AccountingTestCase(ERP5TypeTestCase):
  """A test case for all accounting tests.

  Like in erp5_accounting_ui_test, the testing environment is made of:

  Currencies:
    * currency_module/euro (EUR) with precision 2
    * currency_module/usd (USD) with precision 2
    * currency_module/yen (JPY) with precision 0

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
    * `self.section` an organisation using EUR as default currency, without any
    openned accounting period by default. This organisation is member of
    group/demo_group/sub1
    * `self.main_section` an using EUR as default currency, without any
    openned accounting period by default. This organisation is member of
    group/demo_group. Both self.main_section and self.section are in the same
    company from accounting point of view.
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
  business_process = 'business_process_module/erp5_default_business_process'

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
    if 'resource_value' not in kw:
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
    if self.business_process and not tr.getSpecialise():
      tr._setSpecialise(self.business_process)
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

  def createUserAndlogin(self, name=username):
    """login with Assignee, Assignor & Author roles."""
    uf = self.getPortal().acl_users
    uf._doAddUser(self.username, '', ['Assignee', 'Assignor', 'Author'], [])
    user = uf.getUserById(self.username).__of__(uf)
    newSecurityManager(None, user)

  def afterSetUp(self):
    self.account_module = self.portal.account_module
    self.accounting_module = self.portal.accounting_module
    self.organisation_module = self.portal.organisation_module
    self.person_module = self.portal.person_module
    self.currency_module = self.portal.currency_module
    self.section = getattr(self.organisation_module, 'my_organisation', None)
    self.main_section = getattr(self.organisation_module, 'main_organisation', None)

    # make sure documents are validated
    for module in (self.account_module, self.organisation_module,
                   self.person_module):
      for doc in module.objectValues():
        if doc.getValidationState() != 'validated':
          doc.validate()

    # and the preference enabled
    pref = self.portal.portal_preferences._getOb(
                  'accounting_zuite_preference', None)
    if pref is not None:
      pref.manage_addLocalRoles(self.username, ('Auditor', ))
      if pref.getPreferenceState() != 'enabled':
        pref.enable()

    self.validateRules()

    self.createUserAndlogin(self.username)

    # and all this available to catalog
    self.tic()

  def beforeTearDown(self):
    """Remove all documents, except the default ones.
    """
    self.abort()
    self.login()
    self.accounting_module.manage_delObjects(
                      list(self.accounting_module.objectIds()))
    organisation_list = ('my_organisation', 'main_organisation',
                         'client_1', 'client_2', 'supplier')
    self.organisation_module.manage_delObjects([x for x in
          self.accounting_module.objectIds() if x not in organisation_list])
    for organisation_id in organisation_list:
      organisation = self.organisation_module._getOb(organisation_id, None)
      if organisation is not None:
        organisation.manage_delObjects([x.getId() for x in
                organisation.objectValues(
                  portal_type=('Accounting Period', 'Bank Account'))])
    self.person_module.manage_delObjects([x for x in
          self.person_module.objectIds() if x not in ('john_smith',)])
    self.account_module.manage_delObjects([x for x in
          self.account_module.objectIds() if x not in ('bank', 'collected_vat',
            'equity', 'fixed_assets', 'goods_purchase', 'goods_sales',
            'payable', 'receivable', 'refundable_vat', 'stocks',)])
    self.portal.portal_preferences.manage_delObjects([x.getId() for x in
          self.portal.portal_preferences.objectValues()
          if x.getId() not in ('accounting_zuite_preference', 'default_site_preference')
          and x.getPriority() != Priority.SITE])
    self.portal.portal_simulation.manage_delObjects(list(
          self.portal.portal_simulation.objectIds()))
    self.tic()

  def getBusinessTemplateList(self):
    """Returns list of BT to be installed."""
    # note that this test case does *not* install erp5_invoicing, even if it's
    # a dependancy of erp5_accounting_ui_test, because it's used to test
    # standalone accounting and only installs erp5_accounting_ui_test to have
    # some default content created.
    return ('erp5_core_proxy_field_legacy',
            'erp5_base', 'erp5_pdm', 'erp5_simulation', 'erp5_trade',
            'erp5_accounting', 'erp5_project', 'erp5_accounting_ui_test',
            'erp5_ods_style',
            'erp5_configurator_standard_trade_template',
            'erp5_configurator_standard_accounting_template',
            'erp5_configurator_standard_invoicing_template',
            'erp5_simulation_test')


class TestAccounts(AccountingTestCase):
  """Tests Accounts.
  """
  def test_AccountValidation(self):
    # Accounts need an account_type category to be valid
    account = self.portal.account_module.newContent(portal_type='Account')
    self.assertEqual(1, len(account.checkConsistency()))
    account.setAccountType('equity')
    self.assertEqual(0, len(account.checkConsistency()))

  def test_AccountWorkflow(self):
    account = self.portal.account_module.newContent(portal_type='Account')
    self.assertEqual('draft', account.getValidationState())
    doActionFor = self.portal.portal_workflow.doActionFor
    self.assertRaises(ValidationFailed, doActionFor, account,
                          'validate_action')
    account.setAccountType('equity')
    account.setGap('my_country/my_accounting_standards/1')
    doActionFor(account, 'validate_action')
    self.assertEqual('validated', account.getValidationState())

  def test_isCreditAccount(self):
    """Tests the 'credit_account' property on account, which was named
    is_credit_account, which generated isIsCreditAccount accessor"""
    account = self.portal.account_module.newContent(portal_type='Account')
    # simulate an old object
    account.is_credit_account = True
    self.assertTrue(account.isCreditAccount())
    self.assertTrue(account.getProperty('credit_account'))

    account.setCreditAccount(False)
    self.assertFalse(account.isCreditAccount())


class TestTransactionValidation(AccountingTestCase):
  """Test validations of accounting transactions.

  In this test suite, the main section have a closed accounting period for
  2006, and an open one for 2007.
  """
  def afterSetUp(self):
    super(TestTransactionValidation, self).afterSetUp()
    self.organisation_module = self.portal.organisation_module
    self.main_section = self.organisation_module.main_organisation

    if 'accounting_period_2006' not in self.main_section.objectIds():
      accounting_period_2006 = self.main_section.newContent(
                                  id='accounting_period_2006',
                                  portal_type='Accounting Period',
                                  start_date=DateTime('2006/01/01'),
                                  stop_date=DateTime('2006/12/31'))
      accounting_period_2006.start()
      self.portal.portal_workflow.doActionFor(accounting_period_2006,
          'stop_action',
          profit_and_loss_account=self.portal.account_module.contentValues()[0].getRelativeUrl())
      accounting_period_2007 = self.main_section.newContent(
                                  id='accounting_period_2007',
                                  portal_type='Accounting Period',
                                  start_date=DateTime('2007/01/01'),
                                  stop_date=DateTime('2007/12/31'))
      accounting_period_2007.start()
      self.tic()

  def test_SaleInvoiceTransactionValidationDate(self):
    # Accounting Period Date matters for Sale Invoice Transaction
    accounting_transaction = self._makeOne(
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
        accounting_transaction, 'stop_action')
    # in 2007, it's OK
    accounting_transaction.setStartDate(DateTime("2007/03/03"))
    self.portal.portal_workflow.doActionFor(accounting_transaction, 'stop_action')

  def test_PurchaseInvoiceTransactionValidationDate(self):
    # Accounting Period Date matters for Purchase Invoice Transaction
    accounting_transaction = self._makeOne(
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
        accounting_transaction, 'stop_action')
    # in 2007, it's OK
    accounting_transaction.setStopDate(DateTime("2007/03/03"))
    self.portal.portal_workflow.doActionFor(accounting_transaction, 'stop_action')

  def test_PaymentTransactionValidationDate(self):
    # Accounting Period Date matters for Payment Transaction
    accounting_transaction = self._makeOne(
               portal_type='Payment Transaction',
               start_date=DateTime('2006/03/03'),
               destination_section_value=self.organisation_module.supplier,
               payment_mode='default',
               lines=(dict(source_value=self.account_module.goods_purchase,
                           source_debit=500),
                      dict(source_value=self.account_module.receivable,
                           source_credit=500)))
    # validation is refused, because period is closed
    self.assertRaises(ValidationFailed,
        self.portal.portal_workflow.doActionFor,
        accounting_transaction, 'stop_action')
    # in 2007, it's OK
    accounting_transaction.setStartDate(DateTime("2007/03/03"))
    self.portal.portal_workflow.doActionFor(accounting_transaction, 'stop_action')

  def test_DestinationPaymentTransactionValidationDate(self):
    # Accounting Period Date matters for Payment Transaction
    accounting_transaction = self._makeOne(
               portal_type='Payment Transaction',
               stop_date=DateTime('2006/03/03'),
               source_section_value=self.organisation_module.supplier,
               destination_section_value=self.section,
               payment_mode='default',
               lines=(dict(destination_value=self.account_module.goods_purchase,
                           destination_debit=500),
                      dict(destination_value=self.account_module.receivable,
                           destination_credit=500)))
    # validation is refused, because period is closed
    self.assertRaises(ValidationFailed,
        self.portal.portal_workflow.doActionFor,
        accounting_transaction, 'stop_action')
    # in 2007, it's OK
    accounting_transaction.setStopDate(DateTime("2007/03/03"))
    self.portal.portal_workflow.doActionFor(accounting_transaction, 'stop_action')

  def test_UnusedSectionTransactionValidationDate(self):
    # If a section doesn't have any accounts on its side, we don't check the
    # accounting period dates
    accounting_transaction = self._makeOne(
               portal_type='Accounting Transaction',
               start_date=DateTime('2006/03/03'),
               source_section_value=self.organisation_module.supplier,
               destination_section_value=self.section,
               payment_mode='default',
               lines=(dict(source_value=self.account_module.goods_purchase,
                           destination_value=self.account_module.goods_purchase,
                           source_debit=500),
                      dict(source_value=self.account_module.receivable,
                           destination_value=self.account_module.receivable,
                           source_credit=500)))

    # 2006 is closed for destination_section
    self.assertRaises(ValidationFailed,
        self.portal.portal_workflow.doActionFor,
        accounting_transaction, 'stop_action')
    # If we don't have accounts on destination side, validating transaction is
    # not refused
    for line in accounting_transaction.getMovementList():
      line.setDestination(None)
    self.portal.portal_workflow.doActionFor(accounting_transaction, 'stop_action')

  def test_AccountingTransactionValidationStartDate(self):
    # Check we can/cannot validate at date boundaries of the period
    accounting_transaction = self._makeOne(
               portal_type='Accounting Transaction',
               start_date=DateTime('2006/12/31'),
               destination_section_value=self.organisation_module.supplier,
               payment_mode='default',
               lines=(dict(source_value=self.account_module.goods_purchase,
                           source_debit=500),
                      dict(source_value=self.account_module.receivable,
                           source_credit=500)))
    # validation is refused, because period is closed
    self.assertRaises(ValidationFailed,
        self.portal.portal_workflow.doActionFor,
        accounting_transaction, 'stop_action')
    accounting_transaction.setStartDate(DateTime("2007/01/01"))
    self.portal.portal_workflow.doActionFor(accounting_transaction, 'stop_action')

  def test_AccountingTransactionValidationBeforePeriod(self):
    # Check we cannot validate before the period
    accounting_transaction = self._makeOne(
               portal_type='Accounting Transaction',
               start_date=DateTime('2003/12/31'),
               destination_section_value=self.organisation_module.supplier,
               payment_mode='default',
               lines=(dict(source_value=self.account_module.goods_purchase,
                           source_debit=500),
                      dict(source_value=self.account_module.receivable,
                           source_credit=500)))
    # validation is refused, because there are no open period for 2008
    self.assertRaises(ValidationFailed,
        self.portal.portal_workflow.doActionFor,
        accounting_transaction, 'stop_action')

  def test_AccountingTransactionValidationAfterPeriod(self):
    # Check we cannot validate after the period
    accounting_transaction = self._makeOne(
               portal_type='Accounting Transaction',
               start_date=DateTime('2008/12/31'),
               destination_section_value=self.organisation_module.supplier,
               payment_mode='default',
               lines=(dict(source_value=self.account_module.goods_purchase,
                           source_debit=500),
                      dict(source_value=self.account_module.receivable,
                           source_credit=500)))
    # validation is refused, because there are no open period for 2008
    self.assertRaises(ValidationFailed,
        self.portal.portal_workflow.doActionFor,
        accounting_transaction, 'stop_action')

  def test_AccountingTransactionValidationRecursivePeriod(self):
    # Check we can/cannot validate when secondary period exists

    accounting_period_2007 = self.main_section.accounting_period_2007
    accounting_period_2007_1 = accounting_period_2007.newContent(
                                portal_type='Accounting Period',
                                start_date=DateTime('2007/01/01'),
                                stop_date=DateTime('2007/01/31'),)
    accounting_period_2007_1.start()
    accounting_period_2007_1.stop()

    accounting_period_2007_2 = accounting_period_2007.newContent(
                                portal_type='Accounting Period',
                                start_date=DateTime('2007/02/01'),
                                stop_date=DateTime('2007/02/28'),)
    accounting_period_2007_2.start()

    accounting_transaction = self._makeOne(
               portal_type='Accounting Transaction',
               start_date=DateTime('2007/01/02'),
               source_section_value=self.main_section,
               destination_section_value=self.organisation_module.supplier,
               payment_mode='default',
               lines=(dict(source_value=self.account_module.goods_purchase,
                           source_debit=500),
                      dict(source_value=self.account_module.receivable,
                           source_credit=500)))
    # validation is refused, because there are no open period for 2007-01
    self.assertRaises(ValidationFailed,
        self.portal.portal_workflow.doActionFor,
        accounting_transaction, 'stop_action')
    # in 2007-02, it's OK
    accounting_transaction.setStartDate(DateTime("2007/02/02"))
    self.portal.portal_workflow.doActionFor(accounting_transaction, 'stop_action')


  def test_PaymentTransactionWithEmployee(self):
    # we have to set bank account if we use an asset/cash/bank account, but not
    # for our employees
    accounting_transaction = self._makeOne(
               portal_type='Accounting Transaction',
               start_date=DateTime('2007/01/02'),
               destination_section_value=self.person_module.john_smith,
               payment_mode='default',
               lines=(dict(source_value=self.account_module.bank,
                           destination_value=self.account_module.bank,
                           source_debit=500),
                      dict(source_value=self.account_module.receivable,
                           destination_value=self.account_module.receivable,
                           source_credit=500)))
    # refused because no bank account
    self.assertRaises(ValidationFailed,
        self.portal.portal_workflow.doActionFor,
        accounting_transaction, 'stop_action')
    # with bank account, it's OK
    bank_account = self.section.newContent(portal_type='Bank Account')
    accounting_transaction.setSourcePaymentValue(bank_account)
    self.portal.portal_workflow.doActionFor(accounting_transaction, 'stop_action')

  def test_PaymentTransactionValidationCheckBankAccountPriceCurrency(self):
    # we have to declare a transaction with price_currency different from the
    # bank account
    bank_account = self.section.newContent(portal_type='Bank Account',
        price_currency_value=self.currency_module.euro)
    accounting_transaction = self._makeOne(
               portal_type='Payment Transaction',
               start_date=DateTime('2007/01/02'),
               destination_section_value=self.person_module.john_smith,
               payment_mode='default',
               resource_value=self.currency_module.usd,
               source_payment_value=bank_account,
               lines=(dict(source_value=self.account_module.bank,
                           destination_value=self.account_module.bank,
                           source_debit=500),
                      dict(source_value=self.account_module.receivable,
                           destination_value=self.account_module.receivable,
                           source_credit=500)))
    # refused because bank account currency different from transaction resource
    self.assertRaises(ValidationFailed,
        self.portal.portal_workflow.doActionFor,
        accounting_transaction, 'stop_action')
    # with same currency in bank account and transaction, it's OK
    accounting_transaction.setResourceValue(self.currency_module.euro)
    self.portal.portal_workflow.doActionFor(accounting_transaction, 'stop_action')

  def test_NonBalancedAccountingTransaction(self):
    # Accounting Transactions have to be balanced to be validated
    accounting_transaction = self._makeOne(
               portal_type='Accounting Transaction',
               start_date=DateTime('2007/01/02'),
               destination_section_value=self.organisation_module.client_1,
               resource='currency_module/yen',
               lines=(dict(source_value=self.account_module.payable,
                           source_asset_debit=39,
                           source_debit=500),
                      dict(source_value=self.account_module.receivable,
                           source_asset_credit=38.99,
                           source_credit=500)))
    # refused because not balanced
    self.assertRaises(ValidationFailed,
        self.portal.portal_workflow.doActionFor,
        accounting_transaction, 'stop_action')
    for line in accounting_transaction.getMovementList():
      if line.getSourceId() == 'payable':
        line.setSourceAssetDebit(38.99)
    self.portal.portal_workflow.doActionFor(accounting_transaction, 'stop_action')

  def test_NonBalancedDestinationAccountingTransaction(self):
    # Accounting Transactions have to be balanced to be validated,
    # also for destination
    accounting_transaction = self._makeOne(
               portal_type='Accounting Transaction',
               start_date=DateTime('2007/01/02'),
               destination_section_value=self.organisation_module.client_1,
               resource='currency_module/yen',
               lines=(dict(source_value=self.account_module.payable,
                           destination_value=self.account_module.receivable,
                           destination_asset_debit=39,
                           source_debit=500),
                      dict(source_value=self.account_module.receivable,
                           destination_value=self.account_module.payable,
                           destination_asset_credit=38.99,
                           source_credit=500)))
    # refused because not balanced
    self.assertRaises(ValidationFailed,
        self.portal.portal_workflow.doActionFor,
        accounting_transaction, 'stop_action')
    for line in accounting_transaction.getMovementList():
      if line.getDestinationId() == 'receivable':
        line.setDestinationAssetDebit(38.99)
    self.portal.portal_workflow.doActionFor(accounting_transaction, 'stop_action')

  def test_NonBalancedDestinationAccountingTransactionNoAccount(self):
    # Accounting Transactions have to be balanced to be validated,
    # also for destination
    accounting_transaction = self._makeOne(
               portal_type='Accounting Transaction',
               start_date=DateTime('2007/01/02'),
               destination_section_value=self.organisation_module.client_1,
               resource='currency_module/yen',
               lines=(dict(source_value=self.account_module.payable,
                           destination_asset_debit=39,
                           source_debit=500),
                      dict(source_value=self.account_module.receivable,
                           destination_value=self.account_module.receivable,
                           destination_asset_credit=38.99,
                           source_credit=500)))
    # This is not balanced but there are no accounts on destination
    self.assertRaises(ValidationFailed,
        self.portal.portal_workflow.doActionFor,
        accounting_transaction, 'stop_action')
    for line in accounting_transaction.getMovementList():
      if line.getDestinationId() == 'receivable':
        line.setDestination(None)
    # but if there are no accounts defined it's not a problem
    self.portal.portal_workflow.doActionFor(accounting_transaction, 'stop_action')

  def test_NonBalancedAccountingTransactionSectionOnLines(self):
    accounting_transaction = self._makeOne(
               portal_type='Accounting Transaction',
               start_date=DateTime('2007/01/02'),
               resource='currency_module/yen',
               lines=(dict(source_value=self.account_module.goods_sales,
                           destination_value=self.account_module.goods_purchase,
                           destination_section_value=self.organisation_module.client_1,
                           source_debit=500),
                      dict(source_value=self.account_module.goods_purchase,
                           source_credit=500)))

    # This is not balanced for client 1
    self.assertRaises(ValidationFailed,
        self.portal.portal_workflow.doActionFor,
        accounting_transaction, 'stop_action')

    for line in accounting_transaction.getMovementList():
      line.setDestinationSection(None)
    self.assertEqual([], accounting_transaction.checkConsistency())
    self.portal.portal_workflow.doActionFor(accounting_transaction, 'stop_action')

  def test_NonBalancedAccountingTransactionDifferentSectionOnLines(self):
    accounting_transaction = self._makeOne(
               portal_type='Accounting Transaction',
               start_date=DateTime('2007/01/02'),
               resource='currency_module/yen',
               lines=(dict(source_value=self.account_module.goods_sales,
                           destination_value=self.account_module.goods_purchase,
                           destination_section_value=self.organisation_module.client_1,
                           source_debit=500),
                      dict(source_value=self.account_module.goods_purchase,
                           destination_value=self.account_module.goods_sales,
                           destination_section_value=self.organisation_module.client_2,
                           source_credit=500)))

    # This is not balanced for client 1 and client 2, but if you look globally,
    # it looks balanced.
    self.assertRaises(ValidationFailed,
        self.portal.portal_workflow.doActionFor,
        accounting_transaction, 'stop_action')
    self.assertEqual(1, len(accounting_transaction.checkConsistency()),
                         accounting_transaction.checkConsistency())

    for line in accounting_transaction.getMovementList():
      line.setDestinationSectionValue(
          self.organisation_module.client_2)

    self.assertEqual([], accounting_transaction.checkConsistency())
    self.portal.portal_workflow.doActionFor(accounting_transaction, 'stop_action')

  def test_NonBalancedAccountingTransactionSectionPersonOnLines(self):
    accounting_transaction = self._makeOne(
               portal_type='Accounting Transaction',
               start_date=DateTime('2007/01/02'),
               resource='currency_module/yen',
               lines=(dict(source_value=self.account_module.goods_purchase,
                           destination_value=self.account_module.goods_purchase,
                           destination_section_value=self.person_module.john_smith,
                           source_debit=500),
                      dict(source_value=self.account_module.goods_purchase,
                           source_credit=500)))

    # This is not balanced for john smith, but as he is a person, it's not a
    # problem
    self.assertEqual([], accounting_transaction.checkConsistency())
    self.portal.portal_workflow.doActionFor(accounting_transaction, 'stop_action')

  def test_AccountingTransactionValidationRefusedWithCategoriesAsSections(self):
    # Validating a transaction with categories as sections is refused.
    # See http://wiki.erp5.org/Discussion/AccountingProblems
    category = self.section.getGroupValue()
    self.assertNotEquals(category, None)
    accounting_transaction = self._makeOne(
               portal_type='Accounting Transaction',
               start_date=DateTime('2007/01/02'),
               source_section_value=category,
               destination_section_value=self.organisation_module.client_1,
               resource='currency_module/yen',
               lines=(dict(source_value=self.account_module.payable,
                           source_debit=500),
                      dict(source_value=self.account_module.receivable,
                           source_credit=500)))

    self.assertRaises(ValidationFailed,
        self.portal.portal_workflow.doActionFor,
        accounting_transaction, 'stop_action')
    accounting_transaction.setSourceSectionValue(self.section)
    accounting_transaction.setDestinationSectionValue(category)
    self.assertRaises(ValidationFailed,
        self.portal.portal_workflow.doActionFor,
        accounting_transaction, 'stop_action')

    accounting_transaction.setDestinationSectionValue(self.organisation_module.client_1)
    self.portal.portal_workflow.doActionFor(accounting_transaction, 'stop_action')

  def test_AccountingWorkflow(self):
    accounting_transaction = self._makeOne(
               portal_type='Accounting Transaction',
               start_date=DateTime('2007/01/02'),
               destination_section_value=self.organisation_module.client_1,
               lines=(dict(source_value=self.account_module.payable,
                           destination_value=self.account_module.receivable,
                           source_debit=500),
                      dict(source_value=self.account_module.receivable,
                           destination_value=self.account_module.payable,
                           source_credit=500)))

    doActionFor = self.portal.portal_workflow.doActionFor
    self.assertEqual('draft', accounting_transaction.getSimulationState())
    self.assertTrue(_checkPermission('Modify portal content',
      accounting_transaction))

    doActionFor(accounting_transaction, 'plan_action')
    self.assertEqual('planned', accounting_transaction.getSimulationState())
    self.assertTrue(_checkPermission('Modify portal content',
      accounting_transaction))

    doActionFor(accounting_transaction, 'confirm_action')
    self.assertEqual('confirmed', accounting_transaction.getSimulationState())
    self.assertTrue(_checkPermission('Modify portal content',
      accounting_transaction))

    doActionFor(accounting_transaction, 'start_action')
    self.assertEqual('started', accounting_transaction.getSimulationState())
    self.assertTrue(_checkPermission('Modify portal content',
      accounting_transaction))

    doActionFor(accounting_transaction, 'stop_action')
    self.assertEqual('stopped', accounting_transaction.getSimulationState())
    self.assertFalse(_checkPermission('Modify portal content',
      accounting_transaction))

    doActionFor(accounting_transaction, 'restart_action')
    self.assertEqual('started', accounting_transaction.getSimulationState())
    self.assertTrue(_checkPermission('Modify portal content',
      accounting_transaction))

    doActionFor(accounting_transaction, 'stop_action')
    self.assertEqual('stopped', accounting_transaction.getSimulationState())
    self.assertFalse(_checkPermission('Modify portal content',
      accounting_transaction))

    doActionFor(accounting_transaction, 'deliver_action')
    self.assertEqual('delivered', accounting_transaction.getSimulationState())
    self.assertFalse(_checkPermission('Modify portal content',
      accounting_transaction))

  def test_UneededSourceAssetPrice(self):
    # It is refunsed to validate an accounting transaction if lines have an
    # asset price but the resource is the same as the accounting resource
    accounting_transaction = self._makeOne(
               portal_type='Accounting Transaction',
               start_date=DateTime('2007/01/02'),
               destination_section_value=self.organisation_module.client_1,
               lines=(dict(source_value=self.account_module.payable,
                           source_debit=500,
                           source_asset_debit=600),
                      dict(source_value=self.account_module.receivable,
                           source_credit=500,
                           source_asset_credit=600)))

    section = accounting_transaction.getSourceSectionValue()
    self.assertEqual(section.getPriceCurrency(),
                      accounting_transaction.getResource())

    # validation is refused
    doActionFor = self.portal.portal_workflow.doActionFor
    self.assertRaises(ValidationFailed, doActionFor, accounting_transaction,
                      'stop_action')
    # and the source conversion tab is visible
    self.assertTrue(
        accounting_transaction.AccountingTransaction_isSourceCurrencyConvertible())

    # if asset price is set to the same value as quantity, validation is
    # allowed
    for line in accounting_transaction.getMovementList():
      if line.getSourceValue() == self.account_module.payable:
        line.setSourceAssetDebit(line.getSourceDebit())
      elif line.getSourceValue() == self.account_module.receivable:
        line.setSourceAssetCredit(line.getSourceCredit())
      else:
        self.fail('wrong line ?')
    doActionFor(accounting_transaction, 'stop_action')
    self.assertEqual('stopped', accounting_transaction.getSimulationState())


  def test_UneededDestinationAssetPrice(self):
    # It is refunsed to validate an accounting transaction if lines have an
    # asset price but the resource is the same as the accounting resource
    accounting_transaction = self._makeOne(
               portal_type='Purchase Invoice Transaction',
               stop_date=DateTime('2007/01/02'),
               source_section_value=self.organisation_module.client_1,
               lines=(dict(destination_value=self.account_module.payable,
                           destination_debit=500,
                           destination_asset_debit=600),
                      dict(destination_value=self.account_module.receivable,
                           destination_credit=500,
                           destination_asset_credit=600)))

    section = accounting_transaction.getDestinationSectionValue()
    self.assertEqual(section.getPriceCurrency(),
                      accounting_transaction.getResource())

    # validation is refused
    doActionFor = self.portal.portal_workflow.doActionFor
    self.assertRaises(ValidationFailed, doActionFor, accounting_transaction,
                      'stop_action')
    # and the destination conversion tab is visible
    self.assertTrue(
        accounting_transaction.AccountingTransaction_isDestinationCurrencyConvertible())

    # if asset price is set to the same value as quantity, validation is
    # allowed
    for line in accounting_transaction.getMovementList():
      if line.getDestinationValue() == self.account_module.payable:
        line.setDestinationAssetDebit(line.getDestinationDebit())
      elif line.getDestinationValue() == self.account_module.receivable:
        line.setDestinationAssetCredit(line.getDestinationCredit())
      else:
        self.fail('wrong line ?')

    doActionFor(accounting_transaction, 'stop_action')
    self.assertEqual('stopped', accounting_transaction.getSimulationState())

  def test_CancellationAmount(self):
    accounting_transaction = self._makeOne(
               portal_type='Accounting Transaction',
               start_date=DateTime('2007/01/02'),
               destination_section_value=self.organisation_module.client_1,
               lines=(dict(source_value=self.account_module.payable,
                           source_debit=500),
                      dict(source_value=self.account_module.receivable,
                           source_debit=-500,
                           cancellation_amount=True
                           )))

    self.assertEqual([], accounting_transaction.checkConsistency())
    self.portal.portal_workflow.doActionFor(accounting_transaction,
                                            'stop_action')


class TestClosingPeriod(AccountingTestCase):
  """Various tests for closing the period.
  """
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
    self.assertEqual(3, len(accounting_transaction_list))
    balance_transaction_list = self.accounting_module.contentValues(
                              portal_type='Balance Transaction')
    self.assertEqual(1, len(balance_transaction_list))
    balance_transaction = balance_transaction_list[0]

    # this should create a balance with 3 lines,
    #   equity = 500 D
    #   stocks =     400 C
    #   pl     =     100 C
    self.assertEqual(self.section,
                      balance_transaction.getDestinationSectionValue())
    self.assertEqual(None,
                      balance_transaction.getSourceSection())
    self.assertEqual([period], balance_transaction.getCausalityValueList())
    self.assertEqual(DateTime(2007, 1, 1),
                      balance_transaction.getStartDate())
    self.assertEqual('currency_module/euro',
                      balance_transaction.getResource())
    self.assertEqual('delivered', balance_transaction.getSimulationState())
    movement_list = balance_transaction.getMovementList()
    self.assertEqual(3, len(movement_list))

    equity_movement_list = [m for m in movement_list
          if m.getDestinationValue() == self.account_module.equity]
    self.assertEqual(1, len(equity_movement_list))
    equity_movement = equity_movement_list[0]
    self.assertEqual([], equity_movement.getValueList('resource'))
    self.assertEqual([], equity_movement.getValueList('destination_section'))
    self.assertEqual(None, equity_movement.getSource())
    self.assertEqual(None, equity_movement.getSourceSection())
    self.assertEqual(None, equity_movement.getDestinationTotalAssetPrice())
    self.assertEqual(None, equity_movement.getSourceTotalAssetPrice())
    self.assertEqual(500., equity_movement.getDestinationDebit())

    stock_movement_list = [m for m in movement_list
          if m.getDestinationValue() == self.account_module.stocks]
    self.assertEqual(1, len(stock_movement_list))
    stock_movement = stock_movement_list[0]
    self.assertEqual([], stock_movement.getValueList('resource'))
    self.assertEqual([], stock_movement.getValueList('destination_section'))
    self.assertEqual(None, stock_movement.getSource())
    self.assertEqual(None, stock_movement.getSourceSection())
    self.assertEqual(None, stock_movement.getDestinationTotalAssetPrice())
    self.assertEqual(None, stock_movement.getSourceTotalAssetPrice())
    self.assertEqual(400., stock_movement.getDestinationCredit())

    pl_movement_list = [m for m in movement_list
                        if m.getDestinationValue() is None]
    self.assertEqual(1, len(pl_movement_list))
    pl_movement = pl_movement_list[0]
    self.assertEqual([], pl_movement.getValueList('resource'))
    self.assertEqual([], pl_movement.getValueList('destination_section'))
    self.assertEqual(None, pl_movement.getSource())
    self.assertEqual(None, pl_movement.getSourceSection())
    self.assertEqual(None, pl_movement.getDestinationTotalAssetPrice())
    self.assertEqual(None, pl_movement.getSourceTotalAssetPrice())
    self.assertEqual(100., pl_movement.getDestinationCredit())


  def test_createBalanceOnMirrorSection(self):
    organisation_module = self.organisation_module
    period = self.section.newContent(portal_type='Accounting Period')
    period.setStartDate(DateTime(2006, 1, 1))
    period.setStopDate(DateTime(2006, 12, 31))
    pl = self.portal.account_module.newContent(
              portal_type='Account',
              account_type='equity')

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
                             profit_and_loss_account=pl.getRelativeUrl())
    accounting_transaction_list = self.accounting_module.contentValues()
    self.assertEqual(3, len(accounting_transaction_list))
    balance_transaction_list = self.accounting_module.contentValues(
                              portal_type='Balance Transaction')
    self.assertEqual(1, len(balance_transaction_list))
    balance_transaction = balance_transaction_list[0]

    # this should create a balance with 3 lines,
    #   pl                 = 300 D
    #   receivable/client1 =     200 C
    #   receivable/client2 =     100 C
    self.assertEqual(self.section,
                      balance_transaction.getDestinationSectionValue())
    self.assertEqual(None, balance_transaction.getSourceSection())
    self.assertEqual(DateTime(2007, 1, 1),
                      balance_transaction.getStartDate())
    self.assertEqual('currency_module/euro',
                      balance_transaction.getResource())
    self.assertEqual('delivered', balance_transaction.getSimulationState())
    movement_list = balance_transaction.getMovementList()
    self.assertEqual(3, len(movement_list))

    client1_movement_list = [m for m in movement_list
     if m.getSourceSectionValue() == organisation_module.client_1]
    self.assertEqual(1, len(client1_movement_list))
    client1_movement = client1_movement_list[0]
    self.assertEqual([], client1_movement.getValueList('resource'))
    self.assertEqual([], client1_movement.getValueList('destination_section'))
    self.assertEqual(None, client1_movement.getSource())
    self.assertEqual(self.account_module.receivable,
                      client1_movement.getDestinationValue())
    self.assertEqual(organisation_module.client_1,
                      client1_movement.getSourceSectionValue())
    self.assertEqual(None, client1_movement.getDestinationTotalAssetPrice())
    self.assertEqual(None, client1_movement.getSourceTotalAssetPrice())
    self.assertEqual(100., client1_movement.getDestinationCredit())

    client2_movement_list = [m for m in movement_list
     if m.getSourceSectionValue() == organisation_module.client_2]
    self.assertEqual(1, len(client2_movement_list))
    client2_movement = client2_movement_list[0]
    self.assertEqual([], client2_movement.getValueList('resource'))
    self.assertEqual([], client2_movement.getValueList('destination_section'))
    self.assertEqual(None, client2_movement.getSource())
    self.assertEqual(self.account_module.receivable,
                      client2_movement.getDestinationValue())
    self.assertEqual(organisation_module.client_2,
                      client2_movement.getSourceSectionValue())
    self.assertEqual(None, client2_movement.getDestinationTotalAssetPrice())
    self.assertEqual(None, client2_movement.getSourceTotalAssetPrice())
    self.assertEqual(200., client2_movement.getDestinationCredit())

    pl_movement_list = [m for m in movement_list
                        if m.getDestinationValue() == pl]
    self.assertEqual(1, len(pl_movement_list))
    pl_movement = pl_movement_list[0]
    self.assertEqual([], pl_movement.getValueList('resource'))
    self.assertEqual(None, pl_movement.getSource())
    self.assertEqual(pl,
                      pl_movement.getDestinationValue())
    self.assertEqual(None,
                      pl_movement.getSourceSection())
    self.assertEqual(None, pl_movement.getDestinationTotalAssetPrice())
    self.assertEqual(None, pl_movement.getSourceTotalAssetPrice())
    self.assertEqual(300., pl_movement.getDestinationDebit())
    self.tic()

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
    self.assertEqual(3, len(accounting_transaction_list))
    balance_transaction_list = self.accounting_module.contentValues(
                              portal_type='Balance Transaction')
    self.assertEqual(1, len(balance_transaction_list))
    balance_transaction = balance_transaction_list[0]

    # this should create a balance with 4 lines,
    #   receivable/client_1 = 100 D
    #   bank/bank1          =     100 C
    #   bank/bank2          = 200 D
    #   pl                  =     200 C

    self.assertEqual(self.section,
                      balance_transaction.getDestinationSectionValue())
    self.assertEqual(None,
                      balance_transaction.getSourceSection())
    self.assertEqual([period], balance_transaction.getCausalityValueList())
    self.assertEqual(DateTime(2007, 1, 1),
                      balance_transaction.getStartDate())
    self.assertEqual('currency_module/euro',
                      balance_transaction.getResource())
    self.assertEqual('delivered', balance_transaction.getSimulationState())
    movement_list = balance_transaction.getMovementList()
    self.assertEqual(4, len(movement_list))

    receivable_movement_list = [m for m in movement_list
        if m.getDestinationValue() == self.account_module.receivable]
    self.assertEqual(1, len(receivable_movement_list))
    receivable_movement = receivable_movement_list[0]
    self.assertEqual([], receivable_movement.getValueList('resource'))
    self.assertEqual(None, receivable_movement.getSource())
    self.assertEqual(self.account_module.receivable,
                      receivable_movement.getDestinationValue())
    self.assertEqual(self.organisation_module.client_1,
                      receivable_movement.getSourceSectionValue())
    self.assertEqual(None, receivable_movement.getDestinationTotalAssetPrice())
    self.assertEqual(None, receivable_movement.getSourceTotalAssetPrice())
    self.assertEqual(100., receivable_movement.getDestinationDebit())

    bank1_movement_list = [m for m in movement_list
                       if m.getDestinationPaymentValue() == bank1]
    self.assertEqual(1, len(bank1_movement_list))
    bank1_movement = bank1_movement_list[0]
    self.assertEqual([], bank1_movement.getValueList('resource'))
    self.assertEqual(None, bank1_movement.getSource())
    self.assertEqual(self.account_module.bank,
                      bank1_movement.getDestinationValue())
    self.assertEqual(bank1,
                      bank1_movement.getDestinationPaymentValue())
    self.assertEqual(None,
                      bank1_movement.getSourceSectionValue())
    self.assertEqual(None, bank1_movement.getDestinationTotalAssetPrice())
    self.assertEqual(None, bank1_movement.getSourceTotalAssetPrice())
    self.assertEqual(100., bank1_movement.getDestinationCredit())

    bank2_movement_list = [m for m in movement_list
                         if m.getDestinationPaymentValue() == bank2]
    self.assertEqual(1, len(bank2_movement_list))
    bank2_movement = bank2_movement_list[0]
    self.assertEqual([], bank2_movement.getValueList('resource'))
    self.assertEqual(None, bank2_movement.getSource())
    self.assertEqual(self.account_module.bank,
                      bank2_movement.getDestinationValue())
    self.assertEqual(bank2,
                      bank2_movement.getDestinationPaymentValue())
    self.assertEqual(None,
                      bank2_movement.getSourceSectionValue())
    self.assertEqual(None, bank2_movement.getDestinationTotalAssetPrice())
    self.assertEqual(None, bank2_movement.getSourceTotalAssetPrice())
    self.assertEqual(200., bank2_movement.getDestinationDebit())

    pl_movement_list = [m for m in movement_list
                         if m.getDestination() is None]
    self.assertEqual(1, len(pl_movement_list))
    pl_movement = pl_movement_list[0]
    self.assertEqual([], pl_movement.getValueList('resource'))
    self.assertEqual(None, pl_movement.getSource())
    self.assertEqual(None, pl_movement.getDestination())
    self.assertEqual(None, pl_movement.getDestinationPaymentValue())
    self.assertEqual(None, pl_movement.getSourceSectionValue())
    self.assertEqual(None, pl_movement.getDestinationTotalAssetPrice())
    self.assertEqual(None, pl_movement.getSourceTotalAssetPrice())
    self.assertEqual(200., pl_movement.getDestinationCredit())


  def test_createBalanceOnMirrorSectionMultiCurrency(self):
    pl = self.portal.account_module.newContent(
              portal_type='Account',
              account_type='equity')
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
                      profit_and_loss_account=pl.getRelativeUrl())
    accounting_transaction_list = self.accounting_module.contentValues()
    self.assertEqual(3, len(accounting_transaction_list))
    balance_transaction_list = self.accounting_module.contentValues(
                              portal_type='Balance Transaction')
    self.assertEqual(1, len(balance_transaction_list))
    balance_transaction = balance_transaction_list[0]

    self.assertEqual(self.section,
                      balance_transaction.getDestinationSectionValue())
    self.assertEqual(None, balance_transaction.getSourceSection())
    self.assertEqual(DateTime(2007, 1, 1),
                      balance_transaction.getStartDate())
    self.assertEqual('currency_module/euro',
                      balance_transaction.getResource())

    # this should create a balance with 3 lines,
    #   pl                 = 3.3 D     ( resource acquired )
    #   receivable/client1 =     1.1 C ( resource yen ) qty=100
    #   receivable/client2 =     2.2 C ( resource usd ) qyt=200

    accounting_currency_precision = \
        self.portal.currency_module.euro.getQuantityPrecision()
    self.assertEqual(accounting_currency_precision, 2)

    movement_list = balance_transaction.getMovementList()
    self.assertEqual(3, len(movement_list))
    client1_movement_list = [m for m in movement_list
     if m.getSourceSectionValue() == organisation_module.client_1]
    self.assertEqual(1, len(client1_movement_list))
    client1_movement = client1_movement_list[0]
    self.assertEqual('currency_module/yen',
                      client1_movement.getResource())
    self.assertEqual([], client1_movement.getValueList('destination_section'))
    self.assertEqual(None, client1_movement.getSource())
    self.assertEqual(self.account_module.receivable,
                      client1_movement.getDestinationValue())
    self.assertEqual(organisation_module.client_1,
                      client1_movement.getSourceSectionValue())
    self.assertAlmostEquals(1.1,
          client1_movement.getDestinationInventoriatedTotalAssetCredit(),
          accounting_currency_precision)
    self.assertEqual(None, client1_movement.getSourceTotalAssetPrice())
    self.assertEqual(100, client1_movement.getDestinationCredit())

    client2_movement_list = [m for m in movement_list
     if m.getSourceSectionValue() == organisation_module.client_2]
    self.assertEqual(1, len(client2_movement_list))
    client2_movement = client2_movement_list[0]
    self.assertEqual('currency_module/usd',
                      client2_movement.getResource())
    self.assertEqual([], client2_movement.getValueList('destination_section'))
    self.assertEqual(None, client2_movement.getSource())
    self.assertEqual(self.account_module.receivable,
                      client2_movement.getDestinationValue())
    self.assertEqual(organisation_module.client_2,
                      client2_movement.getSourceSectionValue())
    self.assertAlmostEquals(2.2,
        client2_movement.getDestinationInventoriatedTotalAssetCredit(),
        accounting_currency_precision)
    self.assertEqual(None, client2_movement.getSourceTotalAssetPrice())
    self.assertEqual(200., client2_movement.getDestinationCredit())

    pl_movement_list = [m for m in movement_list
                         if m.getDestinationValue() == pl]
    self.assertEqual(1, len(pl_movement_list))
    pl_movement = pl_movement_list[0]
    self.assertEqual([], pl_movement.getValueList('resource'))
    self.assertEqual(None, pl_movement.getSource())
    self.assertEqual(pl,
                      pl_movement.getDestinationValue())
    self.assertEqual(None,
                      pl_movement.getSourceSection())
    self.assertEqual(None, pl_movement.getDestinationTotalAssetPrice())
    self.assertEqual(None, pl_movement.getSourceTotalAssetPrice())
    self.assertAlmostEquals(3.3,
                  pl_movement.getDestinationDebit(),
                  accounting_currency_precision)

    self.tic()

    # now check content of stock table
    q = self.portal.erp5_sql_connection.manage_test
    # 3 lines, one with quantity 3.3, 2 with quantity 0
    self.assertEqual(1, q(
      "SELECT count(*) FROM stock WHERE portal_type="
      "'Balance Transaction Line'")[0][0])
    self.assertAlmostEquals(3.3, q(
      "SELECT total_price FROM stock WHERE portal_type="
      "'Balance Transaction Line'")[0][0],
      accounting_currency_precision)
    self.assertAlmostEquals(3.3, q(
      "SELECT quantity FROM stock WHERE portal_type="
      "'Balance Transaction Line'")[0][0],
      accounting_currency_precision)
    self.assertEqual(self.portal.currency_module.euro.getUid(), q(
      "SELECT resource_uid FROM stock WHERE portal_type="
      "'Balance Transaction Line'")[0][0])
    self.assertEqual(self.section.getUid(), q(
      "SELECT section_uid FROM stock WHERE portal_type="
      "'Balance Transaction Line'")[0][0])
    self.assertEqual(None, q(
      "SELECT mirror_section_uid FROM stock WHERE portal_type="
      "'Balance Transaction Line'")[0][0])
    self.assertEqual(pl.getUid(), q(
      "SELECT node_uid FROM stock WHERE portal_type="
      "'Balance Transaction Line'")[0][0])
    self.assertEqual(None, q(
      "SELECT mirror_node_uid FROM stock WHERE portal_type="
      "'Balance Transaction Line'")[0][0])
    self.assertEqual(DateTime(2007, 1, 1), q(
      "SELECT date FROM stock WHERE portal_type="
      "'Balance Transaction Line'")[0][0])

    # we can reindex again
    balance_transaction.reindexObject()
    self.tic()


  def test_createBalanceOnMirrorSectionMultiCurrencySameMirrorSection(self):
    pl = self.portal.account_module.newContent(
              portal_type='Account',
              account_type='equity')
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
        destination_section_value=organisation_module.client_1,
        portal_type='Sale Invoice Transaction',
        simulation_state='delivered',
        lines=(dict(source_value=self.account_module.goods_sales,
                    source_asset_debit=2.2,
                    source_debit=200),
               dict(source_value=self.account_module.receivable,
                    source_asset_credit=2.2,
                    source_credit=200)))
    self.tic()

    period.AccountingPeriod_createBalanceTransaction(
                          profit_and_loss_account=pl.getRelativeUrl())
    accounting_transaction_list = self.accounting_module.contentValues()
    self.assertEqual(3, len(accounting_transaction_list))
    balance_transaction_list = self.accounting_module.contentValues(
                              portal_type='Balance Transaction')
    self.assertEqual(1, len(balance_transaction_list))
    balance_transaction = balance_transaction_list[0]

    self.assertEqual(self.section,
                      balance_transaction.getDestinationSectionValue())
    self.assertEqual(None, balance_transaction.getSourceSection())
    self.assertEqual(DateTime(2007, 1, 1),
                      balance_transaction.getStartDate())
    self.assertEqual('currency_module/euro',
                      balance_transaction.getResource())

    # this should create a balance with 3 lines,
    #   pl                 = 3.3 D     ( resource acquired )
    #   receivable/client1 =     1.1 C ( resource yen ) qty=100
    #   receivable/client1 =     2.2 C ( resource usd ) qyt=200

    accounting_currency_precision = \
        self.portal.currency_module.euro.getQuantityPrecision()
    self.assertEqual(accounting_currency_precision, 2)

    movement_list = balance_transaction.getMovementList()
    self.assertEqual(3, len(movement_list))
    client1_movement_list = [m for m in movement_list
     if m.getSourceSectionValue() == organisation_module.client_1]
    self.assertEqual(2, len(client1_movement_list))
    yen_movement = [x for x in client1_movement_list if
                    x.getResource() == 'currency_module/yen'][0]
    self.assertEqual([], yen_movement.getValueList('destination_section'))
    self.assertEqual(None, yen_movement.getSource())
    self.assertEqual(self.account_module.receivable,
                      yen_movement.getDestinationValue())
    self.assertEqual(organisation_module.client_1,
                      yen_movement.getSourceSectionValue())
    self.assertAlmostEquals(1.1,
          yen_movement.getDestinationInventoriatedTotalAssetCredit(),
          accounting_currency_precision)
    self.assertEqual(None, yen_movement.getSourceTotalAssetPrice())
    self.assertEqual(100, yen_movement.getDestinationCredit())

    dollar_movement = [x for x in client1_movement_list if
                    x.getResource() == 'currency_module/usd'][0]
    self.assertEqual([], dollar_movement.getValueList('destination_section'))
    self.assertEqual(None, dollar_movement.getSource())
    self.assertEqual(self.account_module.receivable,
                      dollar_movement.getDestinationValue())
    self.assertEqual(organisation_module.client_1,
                      dollar_movement.getSourceSectionValue())
    self.assertAlmostEquals(2.2,
          dollar_movement.getDestinationInventoriatedTotalAssetCredit(),
          accounting_currency_precision)
    self.assertEqual(None, dollar_movement.getSourceTotalAssetPrice())
    self.assertEqual(200, dollar_movement.getDestinationCredit())

    self.tic()

    # now check content of stock table
    q = self.portal.erp5_sql_connection.manage_test
    self.assertEqual(1, q(
      "SELECT count(*) FROM stock WHERE portal_type="
      "'Balance Transaction Line'")[0][0])
    self.assertAlmostEquals(3.3, q(
      "SELECT total_price FROM stock WHERE portal_type="
      "'Balance Transaction Line'")[0][0],
      accounting_currency_precision)
    self.assertAlmostEquals(3.3, q(
      "SELECT quantity FROM stock WHERE portal_type="
      "'Balance Transaction Line'")[0][0],
      accounting_currency_precision)
    self.assertEqual(self.portal.currency_module.euro.getUid(), q(
      "SELECT resource_uid FROM stock WHERE portal_type="
      "'Balance Transaction Line'")[0][0])
    self.assertEqual(self.section.getUid(), q(
      "SELECT section_uid FROM stock WHERE portal_type="
      "'Balance Transaction Line'")[0][0])
    self.assertEqual(None, q(
      "SELECT mirror_section_uid FROM stock WHERE portal_type="
      "'Balance Transaction Line'")[0][0])
    self.assertEqual(pl.getUid(), q(
      "SELECT node_uid FROM stock WHERE portal_type="
      "'Balance Transaction Line'")[0][0])
    self.assertEqual(None, q(
      "SELECT mirror_node_uid FROM stock WHERE portal_type="
      "'Balance Transaction Line'")[0][0])
    self.assertEqual(DateTime(2007, 1, 1), q(
      "SELECT date FROM stock WHERE portal_type="
      "'Balance Transaction Line'")[0][0])

    # we can reindex again
    balance_transaction.reindexObject()
    self.tic()


  def test_AccountingPeriodWorkflow(self):
    """Tests that accounting_period_workflow creates a balance transaction.
    """
    # open a period for our section
    period = self.section.newContent(portal_type='Accounting Period')
    period.setStartDate(DateTime(2006, 1, 1))
    period.setStopDate(DateTime(2006, 12, 31))
    self.assertEqual('draft', period.getSimulationState())
    self.portal.portal_workflow.doActionFor(period, 'start_action')
    self.assertEqual('started', period.getSimulationState())

    # create a simple transaction in the period
    accounting_transaction = self._makeOne(
        start_date=DateTime(2006, 6, 30),
        portal_type='Sale Invoice Transaction',
        destination_section_value=self.organisation_module.client_1,
        simulation_state='delivered',
        lines=(dict(source_value=self.account_module.receivable,
                    source_credit=100),
               dict(source_value=self.account_module.goods_purchase,
                    source_debit=100)))
    self.assertEqual(1, len(self.accounting_module))

    pl_account = self.portal.account_module.newContent(
                    portal_type='Account',
                    account_type='equity',
                    gap='my_country/my_accounting_standards/1',
                    title='Profit & Loss')
    pl_account.validate()

    # close the period
    self.portal.portal_workflow.doActionFor(period, 'stop_action',
            profit_and_loss_account=pl_account.getRelativeUrl())
    self.assertEqual('stopped', period.getSimulationState())
    self.tic()
    # reopen it, then close it got real
    self.portal.portal_workflow.doActionFor(period, 'restart_action')
    self.assertEqual('started', period.getSimulationState())
    self.tic()
    self.portal.portal_workflow.doActionFor(period, 'stop_action',
            profit_and_loss_account=pl_account.getRelativeUrl())
    self.assertEqual('stopped', period.getSimulationState())
    self.tic()

    self.portal.portal_workflow.doActionFor(period, 'deliver_action',)

    self.tic()
    self.assertEqual('delivered', period.getSimulationState())

    # this created a balance transaction
    balance_transaction_list = self.accounting_module.contentValues(
                                  portal_type='Balance Transaction')
    self.assertEqual(1, len(balance_transaction_list))
    balance_transaction = balance_transaction_list[0]

    # and this transaction must use the account we used in the workflow action.
    self.assertEqual(1, len([m for m in
                              balance_transaction.getMovementList()
                              if m.getDestinationValue() == pl_account]))

  def test_MultipleSection(self):
    period = self.main_section.newContent(portal_type='Accounting Period')
    period.setStartDate(DateTime(2006, 1, 1))
    period.setStopDate(DateTime(2006, 12, 31))
    period.start()

    transaction_main = self._makeOne(
        start_date=DateTime(2006, 1, 2),
        portal_type='Purchase Invoice Transaction',
        destination_section_value=self.main_section,
        source_section_value=self.organisation_module.client_1,
        simulation_state='delivered',
        lines=(dict(destination_value=self.account_module.goods_purchase,
                    destination_debit=30),
               dict(destination_value=self.account_module.payable,
                    destination_credit=30)))

    transaction_section = self._makeOne(
        start_date=DateTime(2006, 1, 2),
        portal_type='Purchase Invoice Transaction',
        destination_section_value=self.section,
        source_section_value=self.organisation_module.client_1,
        simulation_state='stopped',
        lines=(dict(destination_value=self.account_module.goods_purchase,
                    destination_debit=20),
               dict(destination_value=self.account_module.payable,
                    destination_credit=20)))

    # transaction_section is just stopped, so stopping the period is refused.
    self.assertRaises(ValidationFailed,
                      self.portal.portal_workflow.doActionFor,
                      period,
                      'stop_action')

    transaction_section.deliver()
    self.tic()

    pl = self.portal.account_module.newContent(
              portal_type='Account',
              account_type='equity')
    self.portal.portal_workflow.doActionFor(period, 'stop_action',
              profit_and_loss_account=pl.getRelativeUrl())


    self.tic()

    created_balance_transaction_list = self.portal.accounting_module.contentValues(
                                    portal_type='Balance Transaction')
    self.assertEqual(2, len(created_balance_transaction_list))

    main_section_balance_transaction = [bt for bt in
        created_balance_transaction_list if bt.getDestinationSectionValue() ==
        self.main_section][0]
    self.assertEqual(2, len(main_section_balance_transaction.getMovementList()))
    self.assertEqual([], main_section_balance_transaction.checkConsistency())

    section_balance_transaction = [bt for bt in
        created_balance_transaction_list if bt.getDestinationSectionValue() ==
        self.section][0]
    self.assertEqual(2, len(section_balance_transaction.getMovementList()))
    self.assertEqual([], section_balance_transaction.checkConsistency())

    self.tic()
    # we can reindex again
    main_section_balance_transaction.reindexObject()
    section_balance_transaction.reindexObject()
    self.tic()

  def test_MultipleSectionIndependant(self):
    stool = self.portal.portal_simulation
    period_main_section = self.main_section.newContent(portal_type='Accounting Period')
    period_main_section.setStartDate(DateTime(2006, 1, 1))
    period_main_section.setStopDate(DateTime(2006, 12, 31))
    period_main_section.start()

    period_section = self.section.newContent(portal_type='Accounting Period')
    period_section.setStartDate(DateTime(2006, 1, 1))
    period_section.setStopDate(DateTime(2006, 12, 31))
    period_section.start()

    transaction_main = self._makeOne(
        start_date=DateTime(2006, 1, 2),
        portal_type='Purchase Invoice Transaction',
        destination_section_value=self.main_section,
        source_section_value=self.organisation_module.client_1,
        simulation_state='delivered',
        lines=(dict(destination_value=self.account_module.goods_purchase,
                    destination_debit=30),
               dict(destination_value=self.account_module.payable,
                    destination_credit=30)))

    transaction_section = self._makeOne(
        start_date=DateTime(2006, 1, 2),
        portal_type='Purchase Invoice Transaction',
        destination_section_value=self.section,
        source_section_value=self.organisation_module.client_1,
        simulation_state='stopped',
        lines=(dict(destination_value=self.account_module.goods_purchase,
                    destination_debit=20),
               dict(destination_value=self.account_module.payable,
                    destination_credit=20)))

    transaction_section.deliver()
    self.tic()

    pl = self.portal.account_module.newContent(
              portal_type='Account',
              account_type='equity')
    self.portal.portal_workflow.doActionFor(period_main_section, 'stop_action',
              profit_and_loss_account=pl.getRelativeUrl())

    self.tic()

    created_balance_transaction_list = self.portal.accounting_module.contentValues(
                                    portal_type='Balance Transaction')
    self.assertEqual(1, len(created_balance_transaction_list))

    self.assertEqual(30, stool.getInventory(
                              section_uid=self.main_section.getUid(),
                              node_uid=pl.getUid()))
    self.assertEqual(-30, stool.getInventory(
                              section_uid=self.main_section.getUid(),
                              node_uid=self.portal.account_module.payable.getUid()))

    # Section is not impacted at the moment
    self.assertEqual(0, stool.getInventory(
                              section_uid=self.section.getUid(),
                              node_uid=pl.getUid()))
    self.assertEqual(-20, stool.getInventory(
                              section_uid=self.section.getUid(),
                              node_uid=self.portal.account_module.payable.getUid()))

    # Close section's period
    self.portal.portal_workflow.doActionFor(period_section, 'stop_action',
              profit_and_loss_account=pl.getRelativeUrl())

    self.tic()

    created_balance_transaction_list = self.portal.accounting_module.contentValues(
                                    portal_type='Balance Transaction')
    self.assertEqual(2, len(created_balance_transaction_list))

    # section is now impacted
    self.assertEqual(20, stool.getInventory(
                              section_uid=self.section.getUid(),
                              node_uid=pl.getUid()))
    self.assertEqual(-20, stool.getInventory(
                              section_uid=self.section.getUid(),
                              node_uid=self.portal.account_module.payable.getUid()))

    self.assertEqual(30, stool.getInventory(
                              section_uid=self.main_section.getUid(),
                              node_uid=pl.getUid()))
    self.assertEqual(-30, stool.getInventory(
                              section_uid=self.main_section.getUid(),
                              node_uid=self.portal.account_module.payable.getUid()))

  def test_MultipleSectionEmpty(self):
    period = self.main_section.newContent(portal_type='Accounting Period')
    period.setStartDate(DateTime(2006, 1, 1))
    period.setStopDate(DateTime(2006, 12, 31))
    period.start()

    transaction_main = self._makeOne(
        start_date=DateTime(2006, 1, 2),
        portal_type='Purchase Invoice Transaction',
        destination_section_value=self.main_section,
        source_section_value=self.organisation_module.client_1,
        simulation_state='delivered',
        lines=(dict(destination_value=self.account_module.goods_purchase,
                    destination_debit=30),
               dict(destination_value=self.account_module.payable,
                    destination_credit=30)))

    pl = self.portal.account_module.newContent(
              portal_type='Account',
              account_type='equity')
    self.portal.portal_workflow.doActionFor(period, 'stop_action',
              profit_and_loss_account=pl.getRelativeUrl())

    self.tic()

    created_balance_transaction_list = self.portal.accounting_module.contentValues(
                                    portal_type='Balance Transaction')
    self.assertEqual(1, len(created_balance_transaction_list))
    # no balance transaction has been created for section

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
    pl_account = self.portal.account_module.newContent(
                    portal_type='Account',
                    account_type='equity',
                    gap='my_country/my_accounting_standards/1',
                    title='Profit & Loss')
    pl_account.validate()
    self.portal.portal_workflow.doActionFor(
            period1, 'stop_action',
            profit_and_loss_account=pl_account.getRelativeUrl())
    self.tic()

    balance_transaction_list = self.accounting_module.contentValues(
                                  portal_type='Balance Transaction')
    self.assertEqual(1, len(balance_transaction_list))
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
    self.assertEqual(1, len(balance_transaction_list))
    balance_transaction2 = balance_transaction_list[0]

    self.assertEqual(DateTime(2008, 1, 1),
                      balance_transaction2.getStartDate())
    # this should create a balance with 3 lines,
    #   equity          = 100 D
    #   payable/client1 =       100 + 300 C
    #   pl              = 300 D
    movement_list = balance_transaction2.getMovementList()
    self.assertEqual(3, len(movement_list))

    equity_movement_list = [m for m in movement_list
          if m.getDestinationValue() == self.account_module.equity]
    self.assertEqual(1, len(equity_movement_list))
    equity_movement = equity_movement_list[0]
    self.assertEqual(100., equity_movement.getDestinationDebit())

    payable_movement_list = [m for m in movement_list
          if m.getDestinationValue() == self.account_module.payable]
    self.assertEqual(1, len(payable_movement_list))
    payable_movement = payable_movement_list[0]
    self.assertEqual(400., payable_movement.getDestinationCredit())

    pl_movement_list = [m for m in movement_list
          if m.getDestinationValue() == pl_account]
    self.assertEqual(1, len(pl_movement_list))
    pl_movement = pl_movement_list[0]
    self.assertEqual(300., pl_movement.getDestinationDebit())


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
    self.assertEqual(1, len(balance_transaction_list))
    balance_transaction = balance_transaction_list[0]
    balance_transaction.alternateReindexObject()
    movement_list = balance_transaction.getMovementList()
    self.assertEqual(2, len(movement_list))

    pl_movement_list = [m for m in movement_list
                      if m.getDestinationValue() == pl_account]
    self.assertEqual(1, len(pl_movement_list))
    self.assertEqual(500, pl_movement_list[0].getDestinationDebit())

    stock_movement_list = [m for m in movement_list
          if m.getDestinationValue() == self.account_module.stocks]
    self.assertEqual(1, len(stock_movement_list))
    self.assertEqual(500, stock_movement_list[0].getDestinationCredit())

    self.tic()
    balance_transaction.reindexObject()
    self.tic()

  def test_BalanceTransactionWhenProfitAndLossBalanceIsZero(self):
    # The case of a balance transaction after all accounts have a 0 balance.
    period1 = self.section.newContent(portal_type='Accounting Period')
    period1.setStartDate(DateTime(2006, 1, 1))
    period1.setStopDate(DateTime(2006, 12, 31))
    period2 = self.section.newContent(portal_type='Accounting Period')
    period2.setStartDate(DateTime(2007, 1, 1))
    period2.setStopDate(DateTime(2007, 12, 31))
    pl = self.portal.account_module.newContent(
              portal_type='Account',
              account_type='equity')

    transaction1 = self._makeOne(
        start_date=DateTime(2006, 1, 1),
        portal_type='Sale Invoice Transaction',
        destination_section_value=self.organisation_module.client_1,
        simulation_state='delivered',
        lines=(dict(source_value=self.account_module.receivable,
                    source_debit=100),
               dict(source_value=self.account_module.goods_sales,
                    source_credit=100)))
    self.tic()

    period1.AccountingPeriod_createBalanceTransaction(
                             profit_and_loss_account=pl.getRelativeUrl())
    year_1_accounting_transaction_list = self.accounting_module.contentValues()
    self.assertEqual(2, len(year_1_accounting_transaction_list))
    self.tic()

    transaction2 = self._makeOne(
        start_date=DateTime(2007, 1, 1),
        portal_type='Sale Invoice Transaction',
        destination_section_value=self.organisation_module.client_1,
        simulation_state='delivered',
        lines=(dict(source_value=self.account_module.receivable,
                    source_debit=-100),
               dict(source_value=self.account_module.goods_sales,
                    source_credit=-100)))
    self.tic()

    period2.AccountingPeriod_createBalanceTransaction(
                             profit_and_loss_account=pl.getRelativeUrl())
    accounting_transaction_list = self.accounting_module.contentValues()
    self.assertEqual(4, len(accounting_transaction_list))
    self.tic()

    balance_transaction, = [t for t in accounting_transaction_list if t not in
        year_1_accounting_transaction_list and t != transaction2]
    # Maybe we want to add line for each account in that case ?
    line, = balance_transaction.contentValues()

    self.assertEquals(line.getDestinationValue(), pl)
    self.assertEquals(line.getQuantity(), 0)
    self.assertEquals(line.getDestinationTotalAssetPrice(), None)


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
    self.tic()

    # now check inventory
    stool = self.getSimulationTool()
    # the account 'receivable' has a balance of 100
    node_uid = self.account_module.receivable.getUid()
    self.assertEqual(100, stool.getInventory(
                              section_uid=self.section.getUid(),
                              node_uid=node_uid))
    self.assertEqual(100, stool.getInventory(
                    section_uid=self.section.getUid(),
                    mirror_section_uid=self.organisation_module.client_1.getUid(),
                    node_uid=node_uid))
    self.assertEqual(100, stool.getInventoryAssetPrice(
                    section_uid=self.section.getUid(),
                    node_uid=node_uid))
    # and only one movement is returned by getMovementHistoryList
    movement_history_list = stool.getMovementHistoryList(
                    section_uid=self.section.getUid(),
                    node_uid=node_uid)
    self.assertEqual(1, len(movement_history_list))
    self.assertEqual([100], [x.total_price  for x in movement_history_list])

    # the account 'goods_sales' has a balance of -100
    node_uid = self.account_module.goods_sales.getUid()
    self.assertEqual(-100, stool.getInventory(
                              section_uid=self.section.getUid(),
                              node_uid=node_uid))

    # the account 'stocks' has a balance of -100
    node_uid = self.account_module.stocks.getUid()
    self.assertEqual(-100, stool.getInventory(
                              section_uid=self.section.getUid(),
                              node_uid=node_uid))

    # we can reindex again
    balance.reindexObject()
    self.tic()
    # the account 'receivable' still has a balance of 100
    node_uid = self.account_module.receivable.getUid()
    self.assertEqual(100, stool.getInventory(
                              section_uid=self.section.getUid(),
                              node_uid=node_uid))

    # Now check that even if we change the old movement and we
    # reindex the balance, the stock will still be the same
    getInventoryList = self.portal.portal_simulation.getInventoryList
    def getInventoryQuantityList():
      quantity_list = [x.inventory for x in getInventoryList(
         section_uid=self.section.getUid(),
         node_uid=node_uid)]
      quantity_list.sort()
      return quantity_list
    # 100 for the transaction, 0 for the balance
    # because in the balance we put exactly what we have in stock
    self.assertEqual(getInventoryQuantityList(),
                      [100])
    def setQuantityOnTransaction1(quantity):
      for line in transaction1.objectValues():
        if line.getSourceDebit():
          line.setSourceDebit(quantity)
        if line.getSourceCredit():
          line.setSourceCredit(quantity)
      self.tic()
      balance.reindexObject()
      self.tic()
    setQuantityOnTransaction1(99)
    # 99 for the transaction, 1 for the balance
    # because in the balance we have 100, which is 1 more
    # than actual stock of 99
    self.assertEqual(getInventoryQuantityList(),
                      [1, 99])
    setQuantityOnTransaction1(100)
    # Then finally we check that we have again same thing
    # as initial conditions
    self.assertEqual(getInventoryQuantityList(),
                      [100])

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
    self.tic()

    stool = self.portal.portal_simulation
    # the account 'receivable' has a balance of 150
    node_uid = self.account_module.receivable.getUid()
    self.assertEqual(150, stool.getInventory(
                              section_uid=self.section.getUid(),
                              node_uid=node_uid))
    # movement history list shows 2 movements, the initial with qty 100, and
    # the balance with quantity 50

    # the account 'stocks' has a balance of -100
    node_uid = self.account_module.stocks.getUid()
    self.assertEqual(-90, stool.getInventory(
                              section_uid=self.section.getUid(),
                              node_uid=node_uid))
    # we can reindex again
    balance.reindexObject()
    self.tic()

  def test_IndexingBalanceTransactionLinesWithSameNodes(self):
    # Indexes balance transaction without any previous inventory.
    # This make sure that indexing two balance transaction lines with same
    # categories does not try to insert duplicate keys in category table.
    balance = self.accounting_module.newContent(
                          portal_type='Balance Transaction',
                          destination_section_value=self.section,
                          start_date=DateTime(2006, 12, 31),
                          resource_value=self.currency_module.euro,)
    balance.newContent(
                portal_type='Balance Transaction Line',
                source_section_value=self.organisation_module.client_1,
                destination_value=self.account_module.receivable,
                destination_debit=150,)
    balance.newContent(
                portal_type='Balance Transaction Line',
                source_section_value=self.organisation_module.client_2,
                destination_value=self.account_module.receivable,
                destination_debit=30,)

    balance.stop()
    self.tic()

    stool = self.portal.portal_simulation
    # the account 'receivable' has a balance of 150 + 30
    node_uid = self.account_module.receivable.getUid()
    self.assertEqual(180, stool.getInventory(
                              section_uid=self.section.getUid(),
                              node_uid=node_uid))
    self.assertEqual(150, stool.getInventory(
                              section_uid=self.section.getUid(),
                              mirror_section_uid=self.organisation_module\
                                                    .client_1.getUid(),
                              node_uid=node_uid))
    self.assertEqual(30, stool.getInventory(
                              section_uid=self.section.getUid(),
                              mirror_section_uid=self.organisation_module\
                                                    .client_2.getUid(),
                              node_uid=node_uid))
    # we can reindex again
    balance.reindexObject()
    self.tic()

  def test_BalanceTransactionLineBrainGetObject(self):
    # Balance Transaction Line can be retrieved using Brain.getObject
    existing_transaction = self._makeOne(
               start_date=DateTime(2006, 1, 31),
               portal_type='Sale Invoice Transaction',
               simulation_state='delivered',
               lines=(dict(source_value=self.account_module.receivable,
                           source_debit=30),
                      dict(source_value=self.account_module.goods_sales,
                           source_credit=30)))

    balance = self.accounting_module.newContent(
                          portal_type='Balance Transaction',
                          id='different_from_line',
                          destination_section_value=self.section,
                          start_date=DateTime(2006, 12, 31),
                          resource_value=self.currency_module.euro,)
    # this line already exists in stock table, only the difference will be
    # indexed
    balance_line = balance.newContent(
                portal_type='Balance Transaction Line',
                destination_value=self.account_module.receivable,
                destination_debit=100,)
    # this line does not already exist
    balance_line2 = balance.newContent(
                portal_type='Balance Transaction Line',
                destination_value=self.account_module.payable,
                destination_credit=100,)
    balance.stop()
    self.tic()

    stool = self.portal.portal_simulation
    # the account 'receivable' has a balance of 100
    node_uid = self.account_module.receivable.getUid()
    self.assertEqual(100, stool.getInventory(
                              section_uid=self.section.getUid(),
                              node_uid=node_uid))
    # there is one line in getMovementHistoryList:
    mvt_history_list = stool.getMovementHistoryList(
                              section_uid=self.section.getUid(),
                              node_uid=node_uid,
                              sort_on=(('date', 'ASC'), ))
    self.assertEqual(2, len(mvt_history_list))
    self.assertEqual(mvt_history_list[1].getObject(),
                      balance_line)
    self.assertEqual([30, 70], [b.total_price for b in mvt_history_list])

    # There is also one line on payable account
    node_uid = self.account_module.payable.getUid()
    mvt_history_list = stool.getMovementHistoryList(
                              section_uid=self.section.getUid(),
                              node_uid=node_uid)
    self.assertEqual(1, len(mvt_history_list))
    self.assertEqual(mvt_history_list[0].getObject(),
                      balance_line2)

    # we can reindex again
    balance.reindexObject()
    self.tic()

  def test_BalanceTransactionLineBrainGetObjectDifferentThirdParties(self):
    # Balance Transaction Line can be retrieved using Brain.getObject, when
    # the balance is for different third parties
    existing_transaction = self._makeOne(
               start_date=DateTime(2006, 1, 30),
               portal_type='Sale Invoice Transaction',
               simulation_state='delivered',
               destination_section_value=self.organisation_module.client_1,
               lines=(dict(source_value=self.account_module.receivable,
                           source_debit=30),
                      dict(source_value=self.account_module.goods_sales,
                           source_credit=30)))
    another_existing_transaction = self._makeOne(
               start_date=DateTime(2006, 1, 31),
               portal_type='Sale Invoice Transaction',
               simulation_state='delivered',
               destination_section_value=self.organisation_module.client_2,
               lines=(dict(source_value=self.account_module.receivable,
                           source_debit=40),
                      dict(source_value=self.account_module.goods_sales,
                           source_credit=40)))

    balance = self.accounting_module.newContent(
                          portal_type='Balance Transaction',
                          id='different_from_line',
                          destination_section_value=self.section,
                          start_date=DateTime(2006, 12, 31),
                          resource_value=self.currency_module.euro,)

    balance_line = balance.newContent(
                portal_type='Balance Transaction Line',
                destination_value=self.account_module.receivable,
                source_section_value=self.organisation_module.client_2,
                destination_debit=100,)
    balance_line2 = balance.newContent(
                portal_type='Balance Transaction Line',
                destination_value=self.account_module.payable,
                destination_credit=100,)
    balance.stop()
    self.tic()

    stool = self.portal.portal_simulation
    # the account 'receivable' has a balance of 100 + 30
    node_uid = self.account_module.receivable.getUid()
    self.assertEqual(130, stool.getInventory(
                              section_uid=self.section.getUid(),
                              node_uid=node_uid,))
    # there is one line in getMovementHistoryList:
    mvt_history_list = stool.getMovementHistoryList(
                              section_uid=self.section.getUid(),
                              node_uid=node_uid,
                              sort_on=(('date', 'ASC'), ))
    self.assertEqual(3, len(mvt_history_list))
    self.assertEqual(mvt_history_list[2].getObject(),
                      balance_line)
    self.assertEqual([30, 40, 60], [b.total_price for b in mvt_history_list])

    # There is also one line on payable account
    node_uid = self.account_module.payable.getUid()
    mvt_history_list = stool.getMovementHistoryList(
                              section_uid=self.section.getUid(),
                              node_uid=node_uid)
    self.assertEqual(1, len(mvt_history_list))
    self.assertEqual(mvt_history_list[0].getObject(),
                      balance_line2)

    balance.reindexObject()
    self.tic()

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
    self.tic()

    stool = self.portal.portal_simulation
    # the account 'receivable' has a balance of -100
    node_uid = self.account_module.receivable.getUid()
    self.assertEqual(-100, stool.getInventory(
                              section_uid=self.section.getUid(),
                              node_uid=node_uid))
    self.assertEqual(1, len(stool.getMovementHistoryList(
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
    self.tic()
    # let's try to reindex and check if values are still OK
    balance.reindexObject()
    self.tic()

    self.assertEqual(-150, stool.getInventory(
                              section_uid=self.section.getUid(),
                              node_uid=node_uid))
    movement_history_list = stool.getMovementHistoryList(
                              section_uid=self.section.getUid(),
                              node_uid=node_uid)
    self.assertEqual(2, len(movement_history_list))
    self.assertEqual(sorted([-50, -100]),
      sorted([x.total_quantity for x in movement_history_list]))


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
    self.tic()

    stool = self.portal.portal_simulation
    # the account 'receivable' has a balance of 100 after 2006/12/31
    node_uid = self.account_module.receivable.getUid()
    self.assertEqual(100, stool.getInventory(
                              at_date=DateTime(2006, 12, 31),
                              section_uid=self.section.getUid(),
                              node_uid=node_uid))
    self.assertEqual(1, len(stool.getMovementHistoryList(
                              at_date=DateTime(2006, 12, 31),
                              section_uid=self.section.getUid(),
                              node_uid=node_uid)))
    # and 0 before
    self.assertEqual(0, stool.getInventory(
                              at_date=DateTime(2005, 12, 31),
                              section_uid=self.section.getUid(),
                              node_uid=node_uid))
    self.assertEqual(0, len(stool.getMovementHistoryList(
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
    self.tic()

    stool = self.portal.portal_simulation
    # the account 'receivable' has a balance of 100
    node_uid = self.account_module.receivable.getUid()
    self.assertEqual(100, stool.getInventory(
                              parent_portal_type='Balance Transaction',
                              section_uid=self.section.getUid(),
                              node_uid=node_uid))
    # there is one line in getMovementHistoryList:
    mvt_history_list = stool.getMovementHistoryList(
                              parent_portal_type='Balance Transaction',
                              section_uid=self.section.getUid(),
                              node_uid=node_uid)
    self.assertEqual(1, len(mvt_history_list))

  def test_TemporaryClosing(self):
    organisation_module = self.organisation_module
    stool = self.portal.portal_simulation
    period = self.section.newContent(portal_type='Accounting Period')
    period.setStartDate(DateTime(2006, 1, 1))
    period.setStopDate(DateTime(2006, 12, 31))
    period.start()
    pl = self.portal.account_module.newContent(
              portal_type='Account',
              account_type='equity')

    transaction1 = self._makeOne(
        start_date=DateTime(2006, 1, 1),
        destination_section_value=organisation_module.client_1,
        portal_type='Sale Invoice Transaction',
        simulation_state='delivered',
        lines=(dict(source_value=self.account_module.goods_sales,
                    source_credit=100),
               dict(source_value=self.account_module.receivable,
                    source_debit=100)))

    self.portal.portal_workflow.doActionFor(
           period, 'stop_action',
           profit_and_loss_account=pl.getRelativeUrl())

    self.tic()

    self.assertEqual(100, stool.getInventory(
                              section_uid=self.section.getUid(),
                              node_uid=self.account_module.receivable.getUid()))

    self.assertEqual(-100, stool.getInventory(
                              section_uid=self.section.getUid(),
                              node_uid=pl.getUid()))

    # when period is temporary stopped, a balance transaction is created
    created_balance_transaction_list = self.portal.accounting_module.contentValues(
                                    portal_type='Balance Transaction')
    self.assertEqual(1, len(created_balance_transaction_list))

    self.portal.portal_workflow.doActionFor(
           period, 'restart_action' )

    self.tic()

    # when we restart, then this balance transaction is deleted
    created_balance_transaction_list = self.portal.accounting_module.contentValues(
                                    portal_type='Balance Transaction')
    self.assertEqual(0, len(created_balance_transaction_list))

    self.assertEqual(0, stool.getInventory(
                              section_uid=self.section.getUid(),
                              node_uid=pl.getUid()))
    self.assertEqual(100, stool.getInventory(
                              section_uid=self.section.getUid(),
                              node_uid=self.account_module.receivable.getUid()))



class TestAccountingExport(AccountingTestCase):
  """Test accounting export features with erp5_ods_style.
  """
  def test_export_transaction(self):
    # test we can export an accounting transaction as ODS
    accounting_transaction = self._makeOne(lines=(
              dict(source_value=self.account_module.payable,
                   quantity=200),))
    ods_data = accounting_transaction.Base_viewAsODS(
                    form_id='AccountingTransaction_view')
    from Products.ERP5OOo.OOoUtils import OOoParser
    parser = OOoParser()
    parser.openFromString(ods_data)
    content_xml = parser.oo_files['content.xml']
    # just make sure that we have the correct account name
    self.assertEqual(
        '40 - Payable',
        self.account_module.payable.Account_getFormattedTitle())
    # check that this account name can be found in the content
    self.assertTrue('40 - Payable' in content_xml)
    # check that we don't have unknown categories
    self.assertFalse('???' in content_xml)


class TestTransactions(AccountingTestCase):
  """Test behaviours and utility scripts for Accounting Transactions.
  """

  def getBusinessTemplateList(self):
    return AccountingTestCase.getBusinessTemplateList(self) + \
        ('erp5_invoicing', 'erp5_simplified_invoicing')

  def _resetIdGenerator(self):
    # clear all existing ids in portal ids
      self.portal.portal_ids.clearGenerator(all=True)

  def test_SourceDestinationReference(self):
    # Check that source reference and destination reference are filled
    # automatically.
    self._resetIdGenerator()
    section_period_2001 = self.section.newContent(
                        portal_type='Accounting Period',
                        short_title='code-2001',
                        start_date=DateTime(2001, 01, 01),
                        stop_date=DateTime(2001, 12, 31))
    section_period_2001.start()
    section_period_2002 = self.section.newContent(
                        portal_type='Accounting Period',
                        short_title='code-2002',
                        start_date=DateTime(2002, 01, 01),
                        stop_date=DateTime(2002, 12, 31))
    section_period_2002.start()

    accounting_transaction = self._makeOne(
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2001, 01, 01),
              stop_date=DateTime(2001, 01, 01))
    self.portal.portal_workflow.doActionFor(
          accounting_transaction, 'stop_action')
    # The reference generated for the source section uses the short title from
    # the accounting period
    self.assertEqual('code-2001-1', accounting_transaction.getSourceReference())
    # This works, because we use
    # 'AccountingTransaction_getAccountingPeriodForSourceSection' script
    self.assertEqual(section_period_2001, accounting_transaction\
              .AccountingTransaction_getAccountingPeriodForSourceSection())
    # If no accounting period exists on this side, the transaction date is
    # used.
    self.assertEqual('2001-1', accounting_transaction.getDestinationReference())

    other_transaction = self._makeOne(
              destination_section_value=self.organisation_module.client_2,
              start_date=DateTime(2001, 01, 01),
              stop_date=DateTime(2001, 01, 01))
    self.portal.portal_workflow.doActionFor(other_transaction, 'stop_action')
    self.assertEqual('code-2001-2', other_transaction.getSourceReference())
    self.assertEqual('2001-1', other_transaction.getDestinationReference())

    next_year_transaction = self._makeOne(
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2002, 01, 01),
              stop_date=DateTime(2002, 01, 01))
    self.portal.portal_workflow.doActionFor(next_year_transaction, 'stop_action')
    self.assertEqual('code-2002-1', next_year_transaction.getSourceReference())
    self.assertEqual('2002-1', next_year_transaction.getDestinationReference())

  def test_SourceDestinationReferenceGroupAccounting(self):
    # Check that source reference and destination reference are filled
    # automatically when using multiple sections
    self._resetIdGenerator()
    section_period_2001 = self.main_section.newContent(
                        portal_type='Accounting Period',
                        short_title='code-2001',
                        start_date=DateTime(2001, 01, 01),
                        stop_date=DateTime(2001, 12, 31))
    section_period_2001.start()
    section_period_2002 = self.main_section.newContent(
                        portal_type='Accounting Period',
                        short_title='code-2002',
                        start_date=DateTime(2002, 01, 01),
                        stop_date=DateTime(2002, 12, 31))
    section_period_2002.start()

    accounting_transaction = self._makeOne(
              source_section_value=self.main_section,
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2001, 01, 01),
              stop_date=DateTime(2001, 01, 01))
    self.portal.portal_workflow.doActionFor(
          accounting_transaction, 'stop_action')
    # The reference generated for the source section uses the short title from
    # the accounting period
    self.assertEqual('code-2001-1', accounting_transaction.getSourceReference())
    # This works, because we use
    # 'AccountingTransaction_getAccountingPeriodForSourceSection' script
    self.assertEqual(section_period_2001, accounting_transaction\
              .AccountingTransaction_getAccountingPeriodForSourceSection())
    # If no accounting period exists on this side, the transaction date is
    # used.
    self.assertEqual('2001-1', accounting_transaction.getDestinationReference())

    other_section_transaction = self._makeOne(
              destination_section_value=self.organisation_module.client_2,
              start_date=DateTime(2001, 01, 01),
              stop_date=DateTime(2001, 01, 01))
    self.portal.portal_workflow.doActionFor(other_section_transaction, 'stop_action')
    # The numbering is shared by all the sections
    self.assertEqual('code-2001-2', other_section_transaction.getSourceReference())
    self.assertEqual('2001-1', other_section_transaction.getDestinationReference())

  def test_SourceDestinationReferenceSecurity(self):
    # Check that we don't need specific roles to set source reference and
    # destination reference, as long as we can pass the workflow transition
    self._resetIdGenerator()
    section_period_2001 = self.section.newContent(
                        portal_type='Accounting Period',
                        short_title='code-2001',
                        start_date=DateTime(2001, 01, 01),
                        stop_date=DateTime(2001, 12, 31))
    section_period_2001.start()

    accounting_transaction = self._makeOne(
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2001, 01, 01),
              stop_date=DateTime(2001, 01, 01))
    accounting_transaction.manage_permission('Modify portal content',
                                             roles=['Manager'], acquire=0)
    self.assertFalse(_checkPermission('Modify portal content',
                                      accounting_transaction))
    accounting_transaction.stop()
    self.assertEqual('code-2001-1', accounting_transaction.getSourceReference())

  def test_generate_sub_accounting_periods(self):
    accounting_period_2007 = self.section.newContent(
                                portal_type='Accounting Period',
                                start_date=DateTime('2007/01/01'),
                                stop_date=DateTime('2007/12/31'),)
    accounting_period_2007.start()

    accounting_period_2007.AccountingPeriod_createSecondaryPeriod(
          frequency='monthly', open_periods=1)
    sub_period_list = sorted(accounting_period_2007.contentValues(),
                              key=lambda x:x.getStartDate())
    self.assertEqual(12, len(sub_period_list))
    first_period = sub_period_list[0]
    self.assertEqual(DateTime(2007, 1, 1), first_period.getStartDate())
    self.assertEqual(DateTime(2007, 1, 31), first_period.getStopDate())
    self.assertEqual('2007-01', first_period.getShortTitle())
    self.assertEqual('January', first_period.getTitle())


  def test_SearchableText(self):
    accounting_transaction = self._makeOne(title='A new Transaction',
                                description="A description",
                                comment="Some comments")
    searchable_text = accounting_transaction.SearchableText()
    self.assertTrue('A new Transaction' in searchable_text)
    self.assertTrue('A description' in searchable_text)
    self.assertTrue('Some comments' in searchable_text)


  def test_Organisation_getMappingRelatedOrganisation(self):
    # the main section needs an accounting period to be treated as mapping
    # related by Organisation_getMappingRelatedOrganisation
    section_period_2001 = self.main_section.newContent(
                        portal_type='Accounting Period',
                        short_title='code-2001',
                        start_date=DateTime(2001, 01, 01),
                        stop_date=DateTime(2001, 12, 31))

    self.assertEqual(self.main_section,
        self.section.Organisation_getMappingRelatedOrganisation())
    self.assertEqual(self.main_section,
        self.main_section.Organisation_getMappingRelatedOrganisation())

    client = self.organisation_module.client_2
    self.assertEqual(None, client.getGroupValue())
    self.assertEqual(client,
        client.Organisation_getMappingRelatedOrganisation())


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
        eq(self.account_module.bank, line.getSourceValue())
      else:
        eq(quantity, line.getSourceDebit())
        eq(self.account_module.receivable, line.getSourceValue())
    # this transaction can be validated
    eq([], payment.checkConsistency())
    self.portal.portal_workflow.doActionFor(payment, 'stop_action')
    eq('stopped', payment.getSimulationState())

  def test_Invoice_createRelatedPaymentTransactionSimple(self):
    # Simple case of creating a related payment transaction.
    payment_node = self.section.newContent(portal_type='Bank Account')
    invoice = self._makeOne(
               destination_section_value=self.organisation_module.client_1,
               lines=(dict(source_value=self.account_module.goods_purchase,
                           source_debit=100),
                      dict(source_value=self.account_module.receivable,
                           source_credit=100)))
    payment = invoice.Invoice_createRelatedPaymentTransaction(
                                  node=self.account_module.bank.getRelativeUrl(),
                                  payment=payment_node.getRelativeUrl(),
                                  payment_mode='check',
                                  batch_mode=1)
    self._checkRelatedSalePayment(invoice, payment, payment_node, 100)

  def test_Invoice_createRelatedPaymentTransactionGroupedLines(self):
    # Simple creating a related payment transaction when grouping reference of
    # some lines is already set.
    payment_node = self.section.newContent(portal_type='Bank Account')
    invoice = self._makeOne(
               destination_section_value=self.organisation_module.client_1,
               lines=(dict(source_value=self.account_module.goods_purchase,
                           source_debit=100),
                      dict(source_value=self.account_module.receivable,
                           source_credit=60),
                      dict(source_value=self.account_module.receivable,
                           source_credit=40,
                           grouping_reference='A'),))

    payment = invoice.Invoice_createRelatedPaymentTransaction(
                                  node=self.account_module.bank.getRelativeUrl(),
                                  payment=payment_node.getRelativeUrl(),
                                  payment_mode='check',
                                  batch_mode=1)
    self._checkRelatedSalePayment(invoice, payment, payment_node, 60)

  def test_Invoice_createRelatedPaymentTransactionDifferentSection(self):
    # Simple creating a related payment transaction when we have two line for
    # 2 different destination sections.
    payment_node = self.section.newContent(portal_type='Bank Account')
    invoice = self._makeOne(
               destination_section_value=self.organisation_module.client_1,
               lines=(dict(source_value=self.account_module.goods_purchase,
                           source_debit=100),
                      dict(source_value=self.account_module.receivable,
                           source_credit=60),
                      dict(source_value=self.account_module.receivable,
                           source_credit=40,
                           destination_section_value=self.organisation_module.client_2),))

    payment = invoice.Invoice_createRelatedPaymentTransaction(
                                  node=self.account_module.bank.getRelativeUrl(),
                                  payment=payment_node.getRelativeUrl(),
                                  payment_mode='check',
                                  batch_mode=1)
    self._checkRelatedSalePayment(invoice, payment, payment_node, 60)

  def test_Invoice_createRelatedPaymentTransactionRelatedInvoice(self):
    # Simple creating a related payment transaction when we have related
    # transactions.
    payment_node = self.section.newContent(portal_type='Bank Account')
    invoice = self._makeOne(
               destination_section_value=self.organisation_module.client_1,
               lines=(dict(source_value=self.account_module.goods_purchase,
                           source_debit=100),
                      dict(source_value=self.account_module.receivable,
                           source_credit=100),))
    accounting_transaction = self._makeOne(
               destination_section_value=self.organisation_module.client_1,
               causality_value=invoice,
               lines=(dict(source_value=self.account_module.goods_purchase,
                           source_credit=20),
                      dict(source_value=self.account_module.receivable,
                           source_debit=20),))

    accounting_transaction.setCausalityValue(invoice)
    self.portal.portal_workflow.doActionFor(accounting_transaction,
                                           'stop_action')
    self.assertEqual('stopped', accounting_transaction.getSimulationState())
    self.tic()

    payment = invoice.Invoice_createRelatedPaymentTransaction(
                                  node=self.account_module.bank.getRelativeUrl(),
                                  payment=payment_node.getRelativeUrl(),
                                  payment_mode='check',
                                  batch_mode=1)
    self._checkRelatedSalePayment(invoice, payment, payment_node, 80)

  def test_Invoice_createRelatedPaymentTransactionRelatedInvoiceDifferentSide(self):
    # Simple creating a related payment transaction when we have related
    # transactions with different side
    payment_node = self.section.newContent(portal_type='Bank Account')
    invoice = self._makeOne(
               destination_section_value=self.organisation_module.client_1,
               lines=(dict(source_value=self.account_module.goods_purchase,
                           source_debit=100),
                      dict(source_value=self.account_module.receivable,
                           source_credit=100),))
    accounting_transaction = self._makeOne(
               source_section_value=self.organisation_module.client_1,
               destination_section_value=self.section,
               causality_value=invoice,
               lines=(dict(destination_value=self.account_module.goods_purchase,
                           destination_credit=20),
                      dict(destination_value=self.account_module.receivable,
                           destination_debit=20),))
    self.portal.portal_workflow.doActionFor(accounting_transaction,
                                            'stop_action')
    self.assertEqual('stopped', accounting_transaction.getSimulationState())
    self.tic()

    payment = invoice.Invoice_createRelatedPaymentTransaction(
                                  node=self.account_module.bank.getRelativeUrl(),
                                  payment=payment_node.getRelativeUrl(),
                                  payment_mode='check',
                                  batch_mode=1)
    self._checkRelatedSalePayment(invoice, payment, payment_node, 80)

  def test_Invoice_createRelatedPaymentTransactionRelatedInvoiceDraft(self):
    # Simple creating a related payment transaction when we have related
    # transactions in draft/cancelled state (they are ignored)
    payment_node = self.section.newContent(portal_type='Bank Account')
    invoice = self._makeOne(
               destination_section_value=self.organisation_module.client_1,
               lines=(dict(source_value=self.account_module.goods_purchase,
                           source_debit=100),
                      dict(source_value=self.account_module.receivable,
                           source_credit=100),))
    accounting_transaction = self._makeOne(
               destination_section_value=self.organisation_module.client_1,
               causality_value=invoice,
               lines=(dict(source_value=self.account_module.goods_purchase,
                           source_credit=20),
                      dict(source_value=self.account_module.receivable,
                           source_debit=20),))

    other_accounting_transaction = self._makeOne(
               destination_section_value=self.organisation_module.client_1,
               causality_value=invoice,
               lines=(dict(source_value=self.account_module.goods_purchase,
                           source_credit=20),
                      dict(source_value=self.account_module.receivable,
                           source_debit=20),))

    other_accounting_transaction.cancel()
    self.tic()

    payment = invoice.Invoice_createRelatedPaymentTransaction(
                                  node=self.account_module.bank.getRelativeUrl(),
                                  payment=payment_node.getRelativeUrl(),
                                  payment_mode='check',
                                  batch_mode=1)
    self._checkRelatedSalePayment(invoice, payment, payment_node, 100)

  def test_Invoice_createRelatedPaymentTransactionDifferentCurrency(self):
    payment_node = self.section.newContent(portal_type='Bank Account')
    invoice = self._makeOne(
               destination_section_value=self.organisation_module.client_1,
               resource_value=self.portal.currency_module.usd,
               lines=(dict(source_value=self.account_module.goods_purchase,
                           source_debit=100,
                           source_asset_debit=150),
                      dict(source_value=self.account_module.receivable,
                           source_credit=100,
                           source_asset_credit=150),))

    payment = invoice.Invoice_createRelatedPaymentTransaction(
                                  node=self.account_module.bank.getRelativeUrl(),
                                  payment=payment_node.getRelativeUrl(),
                                  payment_mode='check',
                                  batch_mode=1)
    self.assertEqual(self.portal.currency_module.usd,
                      payment.getResourceValue())
    line_list = payment.getMovementList()
    self.assertEqual(2, len(line_list))
    for line in line_list:
      if line.getSourceValue() == self.account_module.receivable:
        self.assertEqual(100, line.getSourceDebit())
        # there's no asset price
        self.assertEqual(None, line.getSourceTotalAssetPrice())
      else:
        self.assertEqual(self.account_module.bank, line.getSourceValue())
        self.assertEqual(100, line.getSourceCredit())
        self.assertEqual(None, line.getSourceTotalAssetPrice())

  # tests for Invoice_getRemainingTotalPayablePrice
  def test_Invoice_getRemainingTotalPayablePriceDeletedPayment(self):
    """Checks in case of deleted Payments related to invoice"""
    # Simple case of creating a related payment transaction.
    payment_node = self.section.newContent(portal_type='Bank Account')
    invoice = self._makeOne(
               destination_section_value=self.organisation_module.client_1,
               lines=(dict(source_value=self.account_module.goods_purchase,
                           source_debit=100),
                      dict(source_value=self.account_module.receivable,
                           source_credit=100)))
    payment = invoice.Invoice_createRelatedPaymentTransaction(
                                  node=self.account_module.bank.getRelativeUrl(),
                                  payment=payment_node.getRelativeUrl(),
                                  payment_mode='check',
                                  batch_mode=1)
    self.tic()
    remaining_price = invoice.Invoice_getRemainingTotalPayablePrice()
    self.assertEqual(-100, remaining_price)
    payment.delete()
    self.tic()
    remaining_price = invoice.Invoice_getRemainingTotalPayablePrice()
    self.assertEqual(-100, remaining_price)

  # tests for Grouping References
  def test_GroupingReferenceResetedOnCopyPaste(self):
    accounting_module = self.portal.accounting_module
    for portal_type in accounting_module.getVisibleAllowedContentTypeList():
      accounting_transaction = accounting_module.newContent(
                            portal_type=portal_type)
      line = accounting_transaction.newContent(
                  id = 'line_with_grouping_reference',
                  grouping_reference='A',
                  grouping_date=DateTime(),
                  portal_type=transaction_to_line_mapping[portal_type])

      cp = accounting_module.manage_copyObjects(ids=[accounting_transaction.getId()])
      copy_id = accounting_module.manage_pasteObjects(cp)[0]['new_id']
      self.assertFalse(accounting_module[copy_id]\
          .line_with_grouping_reference.getGroupingReference())
      self.assertFalse(accounting_module[copy_id]\
          .line_with_grouping_reference.getGroupingDate())

  def test_AccountingTransaction_lineResetGroupingReference(self):
    invoice = self._makeOne(
               title='First Invoice',
               destination_section_value=self.organisation_module.client_1,
               lines=(dict(source_value=self.account_module.goods_purchase,
                           source_debit=100),
                      dict(source_value=self.account_module.receivable,
                           source_credit=100,
                           id='line_with_grouping_reference',
                           grouping_date=DateTime(),
                           grouping_reference='A'),))
    invoice_line = invoice.line_with_grouping_reference

    other_account_invoice = self._makeOne(
               title='Other Account Invoice',
               destination_section_value=self.organisation_module.client_1,
               lines=(dict(source_value=self.account_module.goods_purchase,
                           source_debit=100),
                      dict(source_value=self.account_module.goods_sales,
                           source_credit=100,
                           id='line_with_grouping_reference',
                           grouping_date=DateTime(),
                           grouping_reference='A'),))
    other_account_line = other_account_invoice.line_with_grouping_reference

    other_section_invoice = self._makeOne(
               title='Other Section Invoice',
               destination_section_value=self.organisation_module.client_2,
               lines=(dict(source_value=self.account_module.goods_purchase,
                           source_debit=100),
                      dict(source_value=self.account_module.receivable,
                           source_credit=100,
                           id='line_with_grouping_reference',
                           grouping_date=DateTime(),
                           grouping_reference='A'),))
    other_section_line = other_section_invoice.line_with_grouping_reference

    other_letter_invoice = self._makeOne(
               title='Other letter Invoice',
               destination_section_value=self.organisation_module.client_1,
               lines=(dict(source_value=self.account_module.goods_purchase,
                           source_debit=100),
                      dict(source_value=self.account_module.receivable,
                           source_credit=100,
                           id='line_with_grouping_reference',
                           grouping_date=DateTime(),
                           grouping_reference='B'),))
    other_letter_line = other_letter_invoice.line_with_grouping_reference

    payment = self._makeOne(
               title='First Invoice Payment',
               portal_type='Payment Transaction',
               source_payment_value=self.section.newContent(
                                            portal_type='Bank Account'),
               destination_section_value=self.organisation_module.client_1,
               lines=(dict(source_value=self.account_module.receivable,
                           id='line_with_grouping_reference',
                           grouping_reference='A',
                           grouping_date=DateTime(),
                           source_debit=100),
                      dict(source_value=self.account_module.bank,
                           source_credit=100,)))
    payment_line = payment.line_with_grouping_reference

    # reset from the payment line, the invoice line from the same group will be
    # ungrouped
    payment_line.AccountingTransactionLine_resetGroupingReference()
    self.assertFalse(payment_line.getGroupingReference())
    self.assertFalse(payment_line.getGroupingDate())
    self.assertFalse(invoice_line.getGroupingReference())
    self.assertFalse(invoice_line.getGroupingDate())

    # other lines are not touched:
    self.assertTrue(other_account_line.getGroupingReference())
    self.assertTrue(other_account_line.getGroupingDate())
    self.assertTrue(other_section_line.getGroupingReference())
    self.assertTrue(other_section_line.getGroupingDate())
    self.assertTrue(other_letter_line.getGroupingDate())

  def test_automatically_setting_grouping_reference(self):
    invoice = self._makeOne(
               title='First Invoice',
               start_date=DateTime(2012, 1, 2),
               destination_section_value=self.organisation_module.client_1,
               lines=(dict(source_value=self.account_module.goods_purchase,
                           source_debit=100),
                      dict(source_value=self.account_module.receivable,
                           source_credit=100,
                           id='line_for_grouping_reference',)))
    invoice_line = invoice.line_for_grouping_reference

    payment = self._makeOne(
               title='First Invoice Payment',
               portal_type='Payment Transaction',
               simulation_state='delivered',
               start_date=DateTime(2012, 1, 3),
               causality_value=invoice,
               source_payment_value=self.section.newContent(
                                            portal_type='Bank Account'),
               destination_section_value=self.organisation_module.client_1,
               lines=(dict(source_value=self.account_module.receivable,
                           id='line_for_grouping_reference',
                           source_debit=100),
                      dict(source_value=self.account_module.bank,
                           source_credit=100,)))
    payment_line = payment.line_for_grouping_reference

    self.assertFalse(invoice_line.getGroupingReference())
    self.assertFalse(invoice_line.getGroupingDate())
    self.assertFalse(payment_line.getGroupingReference())
    self.assertFalse(payment_line.getGroupingDate())

    # lines match, they are automatically grouped
    invoice.stop()
    self.assertTrue(invoice_line.getGroupingReference())
    self.assertTrue(payment_line.getGroupingReference())
    # the grouping date is set to the latest date of all grouped lines
    self.assertEqual(DateTime(2012, 1, 3), invoice_line.getGroupingDate())
    self.assertEqual(DateTime(2012, 1, 3), payment_line.getGroupingDate())

    # when restarting, grouping is removed
    invoice.restart()
    self.tic()
    self.assertFalse(invoice_line.getGroupingReference())
    self.assertFalse(invoice_line.getGroupingDate())
    self.assertFalse(payment_line.getGroupingReference())
    self.assertFalse(payment_line.getGroupingDate())

    # when stopping again, grouping is set again
    invoice.stop()
    self.assertTrue(invoice_line.getGroupingReference())
    self.assertTrue(payment_line.getGroupingReference())
    self.assertEqual(DateTime(2012, 1, 3), invoice_line.getGroupingDate())
    self.assertEqual(DateTime(2012, 1, 3), payment_line.getGroupingDate())

  def test_automatically_setting_grouping_reference_same_group(self):
    # invoice is for section, payment is for main_section

    # the main section needs an accounting period to be treated as mapping
    # related by Organisation_getMappingRelatedOrganisation
    section_period_2001 = self.main_section.newContent(
                        portal_type='Accounting Period',
                        short_title='code-2001',
                        start_date=DateTime(2001, 01, 01),
                        stop_date=DateTime(2001, 12, 31))

    invoice = self._makeOne(
               title='First Invoice',
               destination_section_value=self.organisation_module.client_1,
               lines=(dict(source_value=self.account_module.goods_purchase,
                           source_debit=100),
                      dict(source_value=self.account_module.receivable,
                           source_credit=100,
                           id='line_for_grouping_reference',)))
    invoice_line = invoice.line_for_grouping_reference

    payment = self._makeOne(
               title='First Invoice Payment',
               portal_type='Payment Transaction',
               simulation_state='delivered',
               causality_value=invoice,
               source_section_value=self.main_section,
               source_payment_value=self.main_section.newContent(
                                            portal_type='Bank Account'),
               destination_section_value=self.organisation_module.client_1,
               lines=(dict(source_value=self.account_module.receivable,
                           id='line_for_grouping_reference',
                           source_debit=100),
                      dict(source_value=self.account_module.bank,
                           source_credit=100,)))
    payment_line = payment.line_for_grouping_reference

    self.assertFalse(invoice_line.getGroupingReference())
    self.assertFalse(payment_line.getGroupingReference())

    # lines match, they are automatically grouped
    invoice.stop()
    self.assertTrue(invoice_line.getGroupingReference())
    self.assertTrue(payment_line.getGroupingReference())

    # when restarting, grouping is removed
    invoice.restart()
    self.tic()
    self.assertFalse(invoice_line.getGroupingReference())
    self.assertFalse(payment_line.getGroupingReference())
    invoice.stop()
    self.assertTrue(invoice_line.getGroupingReference())
    self.assertTrue(payment_line.getGroupingReference())

  def test_automatically_setting_grouping_reference_only_related(self):
    invoice = self._makeOne(
               title='First Invoice',
               destination_section_value=self.organisation_module.client_1,
               lines=(dict(source_value=self.account_module.goods_purchase,
                           source_debit=100),
                      dict(source_value=self.account_module.receivable,
                           source_credit=100,
                           id='line_for_grouping_reference',)))
    invoice_line = invoice.line_for_grouping_reference

    payment = self._makeOne(
               title='First Invoice Payment',
               portal_type='Payment Transaction',
               simulation_state='delivered',
               # payment is not related with invoice, so no automatic grouping
               # will occur
               source_payment_value=self.section.newContent(
                                            portal_type='Bank Account'),
               destination_section_value=self.organisation_module.client_1,
               lines=(dict(source_value=self.account_module.receivable,
                           id='line_for_grouping_reference',
                           source_debit=100),
                      dict(source_value=self.account_module.bank,
                           source_credit=100,)))
    payment_line = payment.line_for_grouping_reference

    self.assertFalse(invoice_line.getGroupingReference())
    self.assertFalse(payment_line.getGroupingReference())

    invoice.stop()
    self.assertFalse(invoice_line.getGroupingReference())
    self.assertFalse(payment_line.getGroupingReference())

  def test_automatically_setting_grouping_reference_same_section(self):
    invoice = self._makeOne(
               title='First Invoice',
               destination_section_value=self.organisation_module.client_1,
               lines=(dict(source_value=self.account_module.goods_purchase,
                           source_debit=100),
                      dict(source_value=self.account_module.receivable,
                           source_credit=100,
                           id='line_for_grouping_reference',)))
    invoice_line = invoice.line_for_grouping_reference

    payment = self._makeOne(
               title='First Invoice Payment',
               portal_type='Payment Transaction',
               simulation_state='delivered',
               causality_value=invoice,
               source_payment_value=self.section.newContent(
                                            portal_type='Bank Account'),
               destination_section_value=self.organisation_module.client_2,
               lines=(dict(source_value=self.account_module.receivable,
                           id='line_for_grouping_reference',
                           source_debit=100),
                      dict(source_value=self.account_module.bank,
                           source_credit=100,)))
    payment_line = payment.line_for_grouping_reference

    self.assertFalse(invoice_line.getGroupingReference())
    self.assertFalse(payment_line.getGroupingReference())

    # different sections, no grouping
    invoice.stop()
    self.assertFalse(invoice_line.getGroupingReference())
    self.assertFalse(payment_line.getGroupingReference())

  def test_automatically_unsetting_grouping_reference_when_cancelling(self):
    invoice = self._makeOne(
               title='First Invoice',
               destination_section_value=self.organisation_module.client_1,
               lines=(dict(source_value=self.account_module.goods_purchase,
                           source_debit=100),
                      dict(source_value=self.account_module.receivable,
                           source_credit=100,
                           id='line_for_grouping_reference',)))
    invoice_line = invoice.line_for_grouping_reference

    payment = self._makeOne(
               title='First Invoice Payment',
               portal_type='Payment Transaction',
               simulation_state='delivered',
               causality_value=invoice,
               source_payment_value=self.section.newContent(
                                            portal_type='Bank Account'),
               destination_section_value=self.organisation_module.client_1,
               lines=(dict(source_value=self.account_module.receivable,
                           id='line_for_grouping_reference',
                           source_debit=100),
                      dict(source_value=self.account_module.bank,
                           source_credit=100,)))
    payment_line = payment.line_for_grouping_reference

    invoice.stop()
    self.assertTrue(invoice_line.getGroupingReference())
    self.assertTrue(payment_line.getGroupingReference())

    invoice.cancel()
    self.tic()
    self.assertFalse(invoice_line.getGroupingReference())
    self.assertFalse(payment_line.getGroupingReference())

  def test_automatically_setting_grouping_reference_in_one_invoice(self):
    # this invoice will group it itself
    invoice = self._makeOne(
               title='One Invoice',
               simulation_state='stopped',
               destination_section_value=self.organisation_module.client_1,
               lines=(dict(source_value=self.account_module.receivable,
                           source_debit=100),
                      dict(source_value=self.account_module.receivable,
                           source_credit=100, )))
    self.tic()
    for line in invoice.contentValues():
      self.assertTrue(line.getGroupingReference())

    invoice.restart()
    self.tic()
    for line in invoice.contentValues():
      self.assertFalse(line.getGroupingReference())

    invoice.stop()
    self.tic()
    for line in invoice.contentValues():
      self.assertTrue(line.getGroupingReference())

  def test_roundDebitCredit_raises_if_big_difference(self):
    invoice = self._makeOne(
      portal_type='Sale Invoice Transaction',
      lines=(dict(source_value=self.account_module.goods_sales,
                source_debit=100.032345),
           dict(source_value=self.account_module.receivable,
                source_credit=100.000001)))
    precision = invoice.getQuantityPrecisionFromResource(invoice.getResource())
    invoice.newContent(portal_type='Invoice Line', quantity=1, price=100)
    self.assertRaises(invoice.AccountingTransaction_roundDebitCredit)

  def test_roundDebitCredit_when_payable_is_different_total_price(self):
    invoice = self._makeOne(
      portal_type='Purchase Invoice Transaction',
      stop_date=DateTime(),
      destination_section_value=self.section,
      source_section_value=self.organisation_module.supplier,
      lines=(dict(source_value=self.account_module.goods_purchase,
                id="expense",
                destination_debit=100.000001),
           dict(source_value=self.account_module.payable,
                id="payable",
                destination_credit=100.012345)))
    precision = invoice.getQuantityPrecisionFromResource(invoice.getResource())
    invoice.newContent(portal_type='Invoice Line', quantity=1, price=100)
    line_list = invoice.getMovementList(
                    portal_type=invoice.getPortalAccountingMovementTypeList())
    self.assertNotEqual(0.0,
      sum([round(g.getQuantity(), precision) for g in line_list]))
    invoice.AccountingTransaction_roundDebitCredit()
    line_list = invoice.getMovementList(
                 portal_type=invoice.getPortalAccountingMovementTypeList())
    self.assertEqual(0.0,
      sum([round(g.getQuantity(), precision) for g in line_list]))
    self.assertEqual(100.00, invoice.payable.getDestinationCredit())
    self.assertEqual(100.00, invoice.expense.getDestinationDebit())
    self.assertEqual([], invoice.checkConsistency())

  def test_roundDebitCredit_when_payable_is_equal_total_price(self):
    invoice = self._makeOne(
      portal_type='Purchase Invoice Transaction',
      stop_date=DateTime(),
      destination_section_value=self.section,
      source_section_value=self.organisation_module.supplier,
      lines=(dict(source_value=self.account_module.goods_purchase,
                id="expense",
                destination_debit=100.012345),
           dict(source_value=self.account_module.payable,
                id="payable",
               destination_credit=100.000001)))
    precision = invoice.getQuantityPrecisionFromResource(invoice.getResource())
    invoice.newContent(portal_type='Invoice Line', quantity=1, price=100)
    line_list = invoice.getMovementList(
                    portal_type=invoice.getPortalAccountingMovementTypeList())
    self.assertNotEqual(0.0,
      sum([round(g.getQuantity(), precision) for g in line_list]))
    invoice.AccountingTransaction_roundDebitCredit()
    line_list = invoice.getMovementList(
                 portal_type=invoice.getPortalAccountingMovementTypeList())
    self.assertEqual(0.0,
      sum([round(g.getQuantity(), precision) for g in line_list]))
    self.assertEqual(100.00, invoice.payable.getDestinationCredit())
    self.assertEqual(100.00, invoice.expense.getDestinationDebit())
    self.assertEqual([], invoice.checkConsistency())

  def test_roundDebitCredit_when_receivable_is_equal_total_price(self):
    invoice = self._makeOne(
      portal_type='Sale Invoice Transaction',
      stop_date=DateTime(),
      destination_section_value=self.section,
      source_section_value=self.section,
      lines=(dict(source_value=self.account_module.goods_sales,
                id="income",
                source_credit=100.012345),
           dict(source_value=self.account_module.receivable,
                id="receivable",
                source_debit=100.000001)))
    precision = invoice.getQuantityPrecisionFromResource(invoice.getResource())
    invoice.newContent(portal_type='Invoice Line', quantity=1, price=100)
    line_list = invoice.getMovementList(
                    portal_type=invoice.getPortalAccountingMovementTypeList())
    self.assertNotEqual(sum([round(g.getQuantity(), precision) for g in line_list]),
      0.0)
    invoice.AccountingTransaction_roundDebitCredit()
    line_list = invoice.getMovementList(
                 portal_type=invoice.getPortalAccountingMovementTypeList())
    self.assertEqual(sum([round(g.getQuantity(), precision) for g in line_list]),
      0.0)
    self.assertEqual(100.00, invoice.income.getSourceCredit())
    self.assertEqual(100.00, invoice.receivable.getSourceDebit())
    self.assertEqual([], invoice.checkConsistency())

  def test_roundDebitCredit_when_receivable_is_different_total_price(self):
    invoice = self._makeOne(
      portal_type='Sale Invoice Transaction',
      stop_date=DateTime(),
      destination_section_value=self.section,
      source_section_value=self.section,
      lines=(dict(source_value=self.account_module.goods_sales,
                id="income",
                source_credit=100.000001),
           dict(source_value=self.account_module.receivable,
                id="receivable",
                source_debit=100.012345)))
    precision = invoice.getQuantityPrecisionFromResource(invoice.getResource())
    invoice.newContent(portal_type='Invoice Line', quantity=1, price=100)
    line_list = invoice.getMovementList(
                    portal_type=invoice.getPortalAccountingMovementTypeList())
    self.assertNotEqual(sum([round(g.getQuantity(), precision) for g in line_list]),
      0.0)
    invoice.AccountingTransaction_roundDebitCredit()
    line_list = invoice.getMovementList(
                 portal_type=invoice.getPortalAccountingMovementTypeList())
    self.assertEqual(sum([round(g.getQuantity(), precision) for g in line_list]),
      0.0)
    self.assertEqual(100.00, invoice.income.getSourceCredit())
    self.assertEqual(100.00, invoice.receivable.getSourceDebit())
    self.assertEqual([], invoice.checkConsistency())

  def test_AccountingTransaction_getTotalDebitCredit(self):
    # source view
    accounting_transaction = self._makeOne(
               portal_type='Accounting Transaction',
               start_date=DateTime('2007/01/02'),
               destination_section_value=self.organisation_module.client_1,
               lines=(dict(source_value=self.account_module.payable,
                           destination_value=self.account_module.receivable,
                           source_debit=500),
                      dict(source_value=self.account_module.receivable,
                           destination_value=self.account_module.payable,
                           source_credit=400)))
    self.assertTrue(accounting_transaction.AccountingTransaction_isSourceView())
    self.assertEqual(500, accounting_transaction.AccountingTransaction_getTotalDebit())
    self.assertEqual(400, accounting_transaction.AccountingTransaction_getTotalCredit())

    # destination view
    accounting_transaction = self._makeOne(
               portal_type='Accounting Transaction',
               start_date=DateTime('2007/01/02'),
               source_section_value=self.organisation_module.client_1,
               destination_section_value=self.section,
               lines=(dict(source_value=self.account_module.payable,
                           destination_value=self.account_module.receivable,
                           destination_debit=500),
                      dict(source_value=self.account_module.receivable,
                           destination_value=self.account_module.payable,
                           destination_credit=400)))
    self.assertFalse(accounting_transaction.AccountingTransaction_isSourceView())
    self.assertEqual(500, accounting_transaction.AccountingTransaction_getTotalDebit())
    self.assertEqual(400, accounting_transaction.AccountingTransaction_getTotalCredit())

    # source view, with conversion on our side
    accounting_transaction = self._makeOne(
               portal_type='Accounting Transaction',
               start_date=DateTime('2007/01/02'),
               destination_section_value=self.organisation_module.client_1,
               lines=(dict(source_value=self.account_module.payable,
                           destination_value=self.account_module.receivable,
                           source_asset_debit=50,
                           source_debit=500),
                      dict(source_value=self.account_module.receivable,
                           destination_value=self.account_module.payable,
                           source_asset_credit=40,
                           source_credit=400)))
    self.assertTrue(accounting_transaction.AccountingTransaction_isSourceView())
    self.assertEqual(50, accounting_transaction.AccountingTransaction_getTotalDebit())
    self.assertEqual(40, accounting_transaction.AccountingTransaction_getTotalCredit())

    # destination view, with conversion on our side
    accounting_transaction = self._makeOne(
               portal_type='Accounting Transaction',
               start_date=DateTime('2007/01/02'),
               source_section_value=self.organisation_module.client_1,
               destination_section_value=self.section,
               lines=(dict(source_value=self.account_module.payable,
                           destination_value=self.account_module.receivable,
                           destination_asset_debit=50,
                           destination_debit=500),
                      dict(source_value=self.account_module.receivable,
                           destination_value=self.account_module.payable,
                           destination_asset_credit=40,
                           destination_credit=400)))
    self.assertFalse(accounting_transaction.AccountingTransaction_isSourceView())
    self.assertEqual(50, accounting_transaction.AccountingTransaction_getTotalDebit())
    self.assertEqual(40, accounting_transaction.AccountingTransaction_getTotalCredit())

    # source view, with conversion on other side
    accounting_transaction = self._makeOne(
               portal_type='Accounting Transaction',
               start_date=DateTime('2007/01/02'),
               destination_section_value=self.organisation_module.client_1,
               lines=(dict(source_value=self.account_module.payable,
                           destination_value=self.account_module.receivable,
                           destination_asset_debit=50,
                           source_debit=500),
                      dict(source_value=self.account_module.receivable,
                           destination_value=self.account_module.payable,
                           destination_asset_credit=40,
                           source_credit=400)))
    self.assertTrue(accounting_transaction.AccountingTransaction_isSourceView())
    self.assertEqual(500, accounting_transaction.AccountingTransaction_getTotalDebit())
    self.assertEqual(400, accounting_transaction.AccountingTransaction_getTotalCredit())

    # destination view, with conversion on other side
    accounting_transaction = self._makeOne(
               portal_type='Accounting Transaction',
               start_date=DateTime('2007/01/02'),
               source_section_value=self.organisation_module.client_1,
               destination_section_value=self.section,
               lines=(dict(source_value=self.account_module.payable,
                           destination_value=self.account_module.receivable,
                           source_asset_debit=50,
                           destination_debit=500),
                      dict(source_value=self.account_module.receivable,
                           destination_value=self.account_module.payable,
                           source_asset_credit=40,
                           destination_credit=400)))
    self.assertFalse(accounting_transaction.AccountingTransaction_isSourceView())
    self.assertEqual(500, accounting_transaction.AccountingTransaction_getTotalDebit())
    self.assertEqual(400, accounting_transaction.AccountingTransaction_getTotalCredit())

  def test_Account_getDestinationSectionItemList(self):
    organisation1 = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            title='Organisation 1')
    organisation2 = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            title='Organisation 2')
    self._makeOne(
              portal_type='Sale Invoice Transaction',
              simulation_state='delivered',
              destination_section_value=organisation1,
              start_date=DateTime(2006, 2, 2),
              lines=(dict(source_value=self.portal.account_module.receivable,
                          source_debit=100),
                     dict(source_value=self.portal.account_module.goods_sales,
                          source_credit=100.00)))
    self.assertEqual([('', ''),
                       ('Organisation 1 (Organisation)',
                        organisation1.getRelativeUrl())],
                       self.portal.Account_getDestinationSectionItemList())

class TestAccountingWithSequences(ERP5TypeTestCase):
  """The first test for Accounting
  """

  def getBusinessTemplateList(self):
    """Returns list of BT to be installed."""
    return ('erp5_core_proxy_field_legacy', 'erp5_base', 'erp5_pdm',
            'erp5_simulation', 'erp5_trade', 'erp5_accounting',
            'erp5_simulation_test')

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
  sale_invoice_transaction_line_portal_type = 'Sale Invoice Transaction Line'
  purchase_invoice_portal_type      = 'Purchase Invoice Transaction'
  purchase_invoice_transaction_line_portal_type = \
                'Purchase Invoice Transaction Line'

  start_date = DateTime(2004, 01, 01)
  stop_date  = DateTime(2004, 12, 31)

  default_region = 'europe/west/france'

  def getTitle(self):
    return "Accounting"

  def afterSetUp(self):
    """Prepare the test."""
    self.workflow_tool = self.portal.portal_workflow
    self.organisation_module = self.portal.organisation_module
    self.account_module = self.portal.account_module
    self.accounting_module = self.portal.accounting_module
    self.createCategories()
    self.createCurrencies()
    self.createEntities()
    self.createAccounts()
    self.validateRules()

    # setup preference for the vendor group
    self.pref = self.portal.portal_preferences.newContent(
         portal_type='Preference', preferred_section_category='group/vendor',
         preferred_accounting_transaction_section_category='group/vendor',
         priority=Priority.USER )
    self.workflow_tool.doActionFor(self.pref, 'enable_action')

  def beforeTearDown(self):
    """Cleanup for next test.
    """
    self.abort()
    for folder in (self.accounting_module, self.portal.portal_simulation):
      folder.manage_delObjects([i for i in folder.objectIds()])

    # Some tests commits transaction, some other does not, so accounts and
    # organisations created in this tests will not always be present at this
    # point
    folder = self.portal.account_module
    for account in self.account_list:
      if account.getId() in folder.objectIds():
        folder.manage_delObjects([account.getId()])
    folder = self.portal.organisation_module
    for entity in (self.client, self.vendor, self.other_vendor):
      if entity.getId() in folder.objectIds():
        folder.manage_delObjects([entity.getId()])

    self.tic()

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
            id=cat,)
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

  def createEntities(self):
    """Create entities. """
    self.client = self.getOrganisationModule().newContent(
        title = 'Client',
        portal_type = self.organisation_portal_type,
        group = "client",
        price_currency = "currency_module/USD")
    self.section = self.vendor = self.getOrganisationModule().newContent(
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
    self.assertEqual(accounting_period.getSimulationState(),
                      'started')

  def stepStopAccountingPeriod(self, sequence, **kw):
    """Stops the Accounting Period."""
    accounting_period = sequence.get('accounting_period')
    # take any account for profit and loss account, here we don't care
    profit_and_loss_account = self.portal.account_module.contentValues()[0]
    self.getPortal().portal_workflow.doActionFor(
           accounting_period, 'stop_action',
           profit_and_loss_account=profit_and_loss_account.getRelativeUrl())
    self.assertEqual(accounting_period.getSimulationState(),
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
    self.portal.portal_workflow.doActionFor(
           accounting_period, 'deliver_action', )
    self.assertEqual(accounting_period.getSimulationState(),
                      'delivered')

  def stepCheckAccountingPeriodDelivered(self, sequence, **kw):
    """Check the Accounting Period is delivered."""
    accounting_period = sequence.get('accounting_period')
    self.assertEqual(accounting_period.getSimulationState(),
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
      self.tic()
    else:
      self.EUR = currency_module.EUR
      self.USD = currency_module.USD
      self.YEN = currency_module.YEN

  def stepCreateCurrencies(self, sequence, **kw) :
    """Create some currencies. """
    sequence.edit(EUR=self.EUR, USD=self.USD, YEN=self.YEN)

  def createAccounts(self):
    """Create some accounts.
    """
    account_module = self.portal.account_module
    receivable = self.receivable_account = account_module.newContent(
          title = 'receivable',
          portal_type = self.account_portal_type,
          account_type = 'asset/receivable' )
    payable = self.payable_account = account_module.newContent(
          title = 'payable',
          portal_type = self.account_portal_type,
          account_type = 'liability/payable' )
    expense = self.expense_account = account_module.newContent(
          title = 'expense',
          portal_type = self.account_portal_type,
          account_type = 'expense' )
    income = self.income_account = account_module.newContent(
          title = 'income',
          portal_type = self.account_portal_type,
          account_type = 'income' )
    collected_vat = self.collected_vat_account = account_module.newContent(
          title = 'collected_vat',
          portal_type = self.account_portal_type,
          account_type = 'liability/payable/collected_vat' )
    refundable_vat = self.refundable_vat_account = account_module.newContent(
          title = 'refundable_vat',
          portal_type = self.account_portal_type,
          account_type = 'asset/receivable/refundable_vat' )
    bank = self.bank_account = self.account_module.newContent(
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
      self.assertTrue('Site Error' not in account.view())
      self.assertEqual(account.getValidationState(), 'validated')
    self.tic()

  def stepCreateAccounts(self, sequence, **kw) :
    """Create necessary accounts. """
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
      invoice = self.portal.accounting_module.newContent(
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
    invoice = self.portal.accounting_module.newContent(
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
      self.assertEqual(invoice.getSimulationState(), 'draft')

  def stepCheckInvoicesAreStopped(self, sequence, **kw) :
    """Checks invoices are in stopped state."""
    invoice_list = sequence.get('invoice_list')
    for invoice in invoice_list:
      self.assertEqual(invoice.getSimulationState(), 'stopped')

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

      self.assertEqual(calculated_balance,
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
      self.assertEqual(calculated_balance,
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
    self.assertTrue('Site Error' not in accounting_module.view())
    self.assertNotEquals(
          len(portal.getPortalAccountingMovementTypeList()), 0)
    self.assertNotEquals(
          len(portal.getPortalAccountingTransactionTypeList()), 0)
    for accounting_portal_type in accounting_module.allowedContentTypes():
      accounting_transaction = accounting_module.newContent(
            portal_type = accounting_portal_type.getId(),
            source_section_value = source_section_value,
            destination_section_value = destination_section_value,
            resource_value = resource_value )
      self.assertTrue('Site Error' not in accounting_transaction.view())
      self.assertEqual( accounting_transaction.getSourceSectionValue(),
                         source_section_value )
      self.assertEqual( accounting_transaction.getDestinationSectionValue(),
                         destination_section_value )
      self.assertEqual( accounting_transaction.getResourceValue(),
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
          self.assertTrue('Site Error' not in line.view())
          # section and resource is acquired from parent transaction.
          self.assertEqual( line.getDestinationSectionValue(),
                             destination_section_value )
          self.assertEqual( line.getDestinationSectionTitle(),
                             destination_section_title )
          self.assertEqual( line.getSourceSectionValue(),
                             source_section_value )
          self.assertEqual( line.getSourceSectionTitle(),
                             source_section_title )
          self.assertEqual( line.getResourceValue(),
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
    accounting_transaction = self.portal.accounting_module.newContent(
      portal_type=portal_type,
      start_date=kw['start_date'],
      stop_date=kw['stop_date'],
      resource_value=kw['resource_value'],
      source_section_value=kw['source_section_value'],
      destination_section_value=kw['destination_section_value'],
      created_by_builder = 1 # prevent the init script from
                             # creating lines.
    )
    income = accounting_transaction.newContent(
                  id='income',
                  portal_type=line_portal_type,
                  quantity=-quantity,
                  source_value=kw.get('income_account', self.income_account),
                  destination_value=kw.get('expense_account',
                                              self.expense_account), )
    self.assertTrue(income.getSource() != None)
    self.assertTrue(income.getDestination() != None)

    receivable = accounting_transaction.newContent(
                  id='receivable',
                  portal_type=line_portal_type,
                  quantity=quantity,
                  source_value=kw.get('receivable_account',
                                          self.receivable_account),
                  destination_value=kw.get('payable_account',
                                            self.payable_account), )
    self.assertTrue(receivable.getSource() != None)
    self.assertTrue(receivable.getDestination() != None)
    if reindex:
      self.tic()
    if check_consistency:
      self.assertTrue(len(accounting_transaction.checkConsistency()) == 0,
         "Check consistency failed : %s" % accounting_transaction.checkConsistency())
    return accounting_transaction

  def test_createAccountingTransaction(self):
    """Make sure acounting transactions created by createAccountingTransaction
    method are valid.
    """
    accounting_transaction = self.createAccountingTransaction()
    self.assertEqual(self.vendor, accounting_transaction.getSourceSectionValue())
    self.assertEqual(self.client, accounting_transaction.getDestinationSectionValue())
    self.assertEqual(self.EUR, accounting_transaction.getResourceValue())
    self.assertTrue(accounting_transaction.AccountingTransaction_isSourceView())

    self.workflow_tool.doActionFor(accounting_transaction, 'stop_action')
    self.assertEqual('stopped', accounting_transaction.getSimulationState())
    self.assertEqual([] , accounting_transaction.checkConsistency())

  def stepCreateValidAccountingTransaction(self, sequence,
                                          sequence_list=None, **kw) :
    """Creates a valid accounting transaction and put it in
    the sequence as `transaction` key. """
    accounting_transaction = self.createAccountingTransaction(
                            resource_value=sequence.get('EUR'),
                            source_section_value=sequence.get('vendor'),
                            destination_section_value=sequence.get('client'),
                            income_account=sequence.get('income_account'),
                            expense_account=sequence.get('expense_account'),
                            receivable_account=sequence.get('receivable_account'),
                            payable_account=sequence.get('payable_account'), )
    sequence.edit(
      transaction = accounting_transaction,
      income = accounting_transaction.income,
      receivable = accounting_transaction.receivable
    )

  def stepValidateNoDate(self, sequence, sequence_list=None, **kw) :
    """When no date is defined, validation should be impossible.

    Actually, we could say that if we have source_section, we need start_date,
    and if we have destination section, we need stop_date only, but we decided
    to update a date (of start_date / stop_date) using the other one if one is
    missing. (ie. stop_date defaults automatically to start_date if not set and
    start_date is set to stop_date in the workflow script if not set.
    """
    accounting_transaction = sequence.get('transaction')
    old_stop_date = accounting_transaction.getStopDate()
    old_start_date = accounting_transaction.getStartDate()
    accounting_transaction.setStopDate(None)
    if accounting_transaction.getStopDate() != None :
      accounting_transaction.setStartDate(None)
      accounting_transaction.setStopDate(None)
    self.assertRaises(ValidationFailed,
        self.getWorkflowTool().doActionFor,
        accounting_transaction,
        'stop_action')
    accounting_transaction.setStartDate(old_start_date)
    accounting_transaction.setStopDate(old_stop_date)
    self.getWorkflowTool().doActionFor(accounting_transaction, 'stop_action')
    self.assertEqual(accounting_transaction.getSimulationState(), 'stopped')

  def stepValidateNoSection(self, sequence, sequence_list=None, **kw) :
    """Check validation behaviour related to section & mirror_section.
    When no source section is defined, we are in one of the following
    cases :
      o if we use payable or receivable account, the validation should
        be refused.
      o if we do not use any payable or receivable accounts and we have
      a destination section, validation should be ok.
    """
    accounting_transaction = sequence.get('transaction')
    old_source_section = accounting_transaction.getSourceSection()
    old_destination_section = accounting_transaction.getDestinationSection()
    # default transaction uses payable accounts, so validating without
    # source section is refused.
    accounting_transaction.setSourceSection(None)
    self.assertRaises(ValidationFailed,
        self.getWorkflowTool().doActionFor,
        accounting_transaction,
        'stop_action')
    # ... as well as validation without destination section
    accounting_transaction.setSourceSection(old_source_section)
    accounting_transaction.setDestinationSection(None)
    self.assertRaises(ValidationFailed,
        self.getWorkflowTool().doActionFor,
        accounting_transaction,
        'stop_action')
    # mirror section can be set only on the line
    for line in accounting_transaction.getMovementList() :
      line.setDestinationSection(old_destination_section)
    try:
      self.getWorkflowTool().doActionFor(accounting_transaction, 'stop_action')
      self.assertEqual(accounting_transaction.getSimulationState(), 'stopped')
    except ValidationFailed, err :
      self.assert_(0, "Validation failed : %s" % err.msg)

    # if we do not use any payable / receivable account, then we can
    # validate the transaction without setting the mirror section.
    for side in (SOURCE, ): # DESTINATION) :
      # TODO: for now, we only test for source, as it makes no sense to use for
      # destination section only. We could theoritically support it.

      # get a new valid transaction
      accounting_transaction = self.createAccountingTransaction()
      expense_account = sequence.get('expense_account')
      for line in accounting_transaction.getMovementList() :
        line.edit( source_value = expense_account,
                   destination_value = expense_account )
      if side == SOURCE :
        accounting_transaction.setDestinationSection(None)
      else :
        accounting_transaction.setSourceSection(None)
      try:
        self.getWorkflowTool().doActionFor(accounting_transaction, 'stop_action')
        self.assertEqual(accounting_transaction.getSimulationState(), 'stopped')
      except ValidationFailed, err :
        self.assert_(0, "Validation failed : %s" % err.msg)

  def stepValidateNoCurrency(self, sequence, sequence_list=None, **kw) :
    """Check validation behaviour related to currency.
    """
    accounting_transaction = sequence.get('transaction')
    old_resource = accounting_transaction.getResource()
    accounting_transaction.setResource(None)
    self.assertRaises(ValidationFailed,
        self.getWorkflowTool().doActionFor,
        accounting_transaction,
        'stop_action')
    # setting a dummy relationship is not enough, resource must be a
    # currency
    accounting_transaction.setResourceValue(
         self.portal.product_module.newContent(portal_type='Product'))
    self.assertRaises(ValidationFailed,
        self.getWorkflowTool().doActionFor,
        accounting_transaction,
        'stop_action')

  def stepValidateClosedAccount(self, sequence, sequence_list=None, **kw) :
    """Check validation behaviour related to closed accounts.
    If an account is blocked, then it's impossible to validate a
    transaction related to this account.
    """
    accounting_transaction = sequence.get('transaction')
    account = accounting_transaction.getMovementList()[0].getSourceValue()
    self.getWorkflowTool().doActionFor(account, 'invalidate_action')
    self.assertEqual(account.getValidationState(), 'invalidated')
    self.assertRaises(ValidationFailed,
        self.getWorkflowTool().doActionFor,
        accounting_transaction,
        'stop_action')
    # reopen the account for other tests
    account.validate()
    self.assertEqual(account.getValidationState(), 'validated')

  def stepValidateNoAccounts(self, sequence, sequence_list=None, **kw) :
    """Simple check that the validation is refused when we do not have
    accounts correctly defined on lines.
    """
    accounting_transaction = sequence.get('transaction')
    # no account at all is refused
    for line in accounting_transaction.getMovementList():
      line.setSource(None)
      line.setDestination(None)
    self.assertRaises(ValidationFailed,
        self.getWorkflowTool().doActionFor,
        accounting_transaction,
        'stop_action')

    # only one line without account and with a quantity is also refused
    accounting_transaction = self.createAccountingTransaction()
    accounting_transaction.getMovementList()[0].setSource(None)
    accounting_transaction.getMovementList()[0].setDestination(None)
    self.assertRaises(ValidationFailed,
        self.getWorkflowTool().doActionFor,
        accounting_transaction,
        'stop_action')

    # but if we have a line with 0 quantity on both sides, we can
    # validate the transaction and delete this line.
    accounting_transaction = self.createAccountingTransaction()
    line_count = len(accounting_transaction.getMovementList())
    accounting_transaction.newContent(
        portal_type = self.accounting_transaction_line_portal_type)
    self.getWorkflowTool().doActionFor(accounting_transaction, 'stop_action')
    self.assertEqual(accounting_transaction.getSimulationState(), 'stopped')
    self.assertEqual(line_count, len(accounting_transaction.getMovementList()))

    # 0 quantity, but a destination asset price => do not delete the
    # line
    accounting_transaction = self.createAccountingTransaction()
    new_line = accounting_transaction.newContent(
        portal_type = self.accounting_transaction_line_portal_type)
    self.assertEqual(len(accounting_transaction.getMovementList()), 3)
    line_list = accounting_transaction.getMovementList()
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
      self.getWorkflowTool().doActionFor(accounting_transaction, 'stop_action')
      self.assertEqual(accounting_transaction.getSimulationState(), 'stopped')
    except ValidationFailed, err :
      self.assert_(0, "Validation failed : %s" % err.msg)

  def stepValidateNotBalanced(self, sequence, sequence_list=None, **kw) :
    """Check validation behaviour when transaction is not balanced.
    """
    accounting_transaction = sequence.get('transaction')
    accounting_transaction.getMovementList()[0].setQuantity(4325)
    self.assertRaises(ValidationFailed,
        self.getWorkflowTool().doActionFor,
        accounting_transaction,
        'stop_action')

    # asset price have priority (ie. if asset price is not balanced,
    # refuses validation even if quantity is balanced)
    accounting_transaction = self.createAccountingTransaction(resource_value=self.YEN)
    line_list = accounting_transaction.getMovementList()
    line_list[0].setDestinationTotalAssetPrice(10)
    line_list[1].setDestinationTotalAssetPrice(100)
    self.assertRaises(ValidationFailed,
        self.getWorkflowTool().doActionFor,
        accounting_transaction,
        'stop_action')

    accounting_transaction = self.createAccountingTransaction(resource_value=self.YEN)
    line_list = accounting_transaction.getMovementList()
    line_list[0].setSourceTotalAssetPrice(10)
    line_list[1].setSourceTotalAssetPrice(100)
    self.assertRaises(ValidationFailed,
        self.getWorkflowTool().doActionFor,
        accounting_transaction,
        'stop_action')

    # only asset price needs to be balanced
    accounting_transaction = self.createAccountingTransaction(resource_value=self.YEN)
    line_list = accounting_transaction.getMovementList()
    line_list[0].setSourceTotalAssetPrice(100)
    line_list[0].setDestinationTotalAssetPrice(100)
    line_list[0].setQuantity(432432)
    line_list[1].setSourceTotalAssetPrice(-100)
    line_list[1].setDestinationTotalAssetPrice(-100)
    line_list[1].setQuantity(32546787)
    try:
      self.getWorkflowTool().doActionFor(accounting_transaction, 'stop_action')
      self.assertEqual(accounting_transaction.getSimulationState(), 'stopped')
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
    def useBankAccount(accounting_transaction):
      """Modify the transaction, so that a line will use an account member of
      account_type/cash/bank , which requires to use a payment category.
      """
      # get the default and replace income account by bank
      income_account_found = 0
      for line in accounting_transaction.getMovementList() :
        source_account = line.getSourceValue()
        if source_account.isMemberOf('account_type/income') :
          income_account_found = 1
          line.edit( source_value = sequence.get('bank_account'),
                     destination_value = sequence.get('bank_account') )
      self.assertTrue(income_account_found)
    # XXX
    accounting_transaction = sequence.get('transaction')
    useBankAccount(accounting_transaction)
    self.assertRaises(ValidationFailed,
        self.getWorkflowTool().doActionFor,
        accounting_transaction,
        'stop_action')

    source_section_value = accounting_transaction.getSourceSectionValue()
    destination_section_value = accounting_transaction.getDestinationSectionValue()
    for ptype in self.getPortal().getPortalPaymentNodeTypeList() :
      source_payment_value = source_section_value.newContent(
                                  portal_type = ptype, )
      destination_payment_value = destination_section_value.newContent(
                                  portal_type = ptype, )
      accounting_transaction = self.createAccountingTransaction(
                      destination_section_value=self.other_vendor)
      useBankAccount(accounting_transaction)

      # payment node have to be set on both sides if both sides have accounting
      # lines
      accounting_transaction.setSourcePaymentValue(source_payment_value)
      accounting_transaction.setDestinationPaymentValue(None)
      self.assertRaises(ValidationFailed,
          self.getWorkflowTool().doActionFor,
          accounting_transaction,
          'stop_action')
      accounting_transaction.setSourcePaymentValue(None)
      accounting_transaction.setDestinationPaymentValue(destination_payment_value)
      self.assertRaises(ValidationFailed,
          self.getWorkflowTool().doActionFor,
          accounting_transaction,
          'stop_action')
      accounting_transaction.setSourcePaymentValue(source_payment_value)
      accounting_transaction.setDestinationPaymentValue(destination_payment_value)
      try:
        self.getWorkflowTool().doActionFor(accounting_transaction, 'stop_action')
        self.assertEqual(accounting_transaction.getSimulationState(), 'stopped')
      except ValidationFailed, err :
        self.fail("Validation failed : %s" % err.msg)

  def stepValidateRemoveEmptyLines(self, sequence, sequence_list=None, **kw):
    """Check validating a transaction remove empty lines. """
    accounting_transaction = sequence.get('transaction')
    lines_count = len(accounting_transaction.getMovementList())
    empty_lines_count = 0
    for line in accounting_transaction.getMovementList():
      if line.getSourceTotalAssetPrice() ==  \
         line.getDestinationTotalAssetPrice() == 0:
        empty_lines_count += 1
    if empty_lines_count == 0:
      accounting_transaction.newContent(
            portal_type=self.accounting_transaction_line_portal_type)

    self.getWorkflowTool().doActionFor(accounting_transaction, 'stop_action')
    self.assertEqual(len(accounting_transaction.getMovementList()),
                      lines_count - empty_lines_count)

    # we don't remove empty lines if there is only empty lines
    another_accounting_transaction = self.portal.accounting_module.newContent(
                      portal_type=self.accounting_transaction_portal_type,
                      start_date=accounting_transaction.getStartDate(),
                      resource=accounting_transaction.getResource(),
                      source_section=accounting_transaction.getSourceSection(),
                      destination_section=accounting_transaction.getDestinationSection(),
                      created_by_builder=1)
    for i in range(3):
      another_accounting_transaction.newContent(
            portal_type=self.accounting_transaction_line_portal_type)
    lines_count = len(another_accounting_transaction.getMovementList())
    self.getWorkflowTool().doActionFor(another_accounting_transaction, 'stop_action')
    self.assertEqual(len(another_accounting_transaction.getMovementList()), lines_count)

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
      stepStopAccountingPeriod
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


class TestAccountingTransactionTemplate(AccountingTestCase):
  """A test for Accounting Transaction Template
  """

  def getTitle(self):
    return "Accounting Transaction Template"

  def disableUserPreferenceList(self):
    """Disable existing User preferences."""
    for preference in self.portal.portal_preferences.objectValues():
      if preference.getPriority() == Priority.USER:
        preference.disable()

  def test_Template(self):
    self.disableUserPreferenceList()
    self.createUserAndlogin('claudie')
    preference = self.portal.portal_preferences.newContent('Preference')
    preference.priority = Priority.USER
    preference.enable()

    self.tic()

    document = self.accounting_module.newContent(
                    portal_type='Accounting Transaction')
    document.edit(title='My Accounting Transaction')
    document.Base_makeTemplateFromDocument(form_id=None)

    self.tic()

    self.assertEqual(len(preference.objectIds()), 1)

    # make sure that subobjects are not unindexed after making template.
    subobject_uid = document.objectValues()[0].getUid()
    self.assertEqual(len(self.portal.portal_catalog(uid=subobject_uid)), 1)

    self.accounting_module.manage_delObjects(ids=[document.getId()])

    self.tic()

    template = preference.objectValues()[0]

    cp = preference.manage_copyObjects(ids=[template.getId()],
                                       REQUEST=None, RESPONSE=None)
    new_document_list = self.accounting_module.manage_pasteObjects(cp)
    new_document_id = new_document_list[0]['new_id']
    new_document = self.accounting_module[new_document_id]
    new_document.makeTemplateInstance()

    self.tic()

    self.assertEqual(new_document.getTitle(), 'My Accounting Transaction')

  def test_Base_doAction(self):
    # test creating a template using Base_doAction script (this is what
    # erp5_xhtml_style does)
    self.disableUserPreferenceList()
    self.createUserAndlogin('claudie')
    preference = self.portal.portal_preferences.newContent('Preference')
    preference.priority = Priority.USER
    preference.enable()

    self.tic()

    document = self.accounting_module.newContent(
                              portal_type='Accounting Transaction')
    document.edit(title='My Accounting Transaction')
    document.Base_makeTemplateFromDocument(form_id=None)

    template = preference.objectValues()[0]
    ret = self.accounting_module.Base_doAction(
        select_action='template %s' % template.getRelativeUrl(),
        form_id='', cancel_url='')
    self.assertTrue('Template%20created.' in ret, ret)
    self.assertEqual(2, len(self.accounting_module.contentValues()))


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestAccountingWithSequences))
  suite.addTest(unittest.makeSuite(TestTransactions))
  suite.addTest(unittest.makeSuite(TestAccounts))
  suite.addTest(unittest.makeSuite(TestClosingPeriod))
  suite.addTest(unittest.makeSuite(TestTransactionValidation))
  suite.addTest(unittest.makeSuite(TestAccountingExport))
  suite.addTest(unittest.makeSuite(TestAccountingTransactionTemplate))
  return suite
