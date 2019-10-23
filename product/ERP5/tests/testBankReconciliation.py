#############################################################################
#
# Copyright (c) 2014 Nexedi SA and Contributors. All Rights Reserved.
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

"""Tests Bank Reconciliation
"""

import unittest

from DateTime import DateTime

from Products.DCWorkflow.DCWorkflow import ValidationFailed

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5ReportTestCase
from Products.ERP5.tests.testAccounting import AccountingTestCase

class TestBankReconciliation(AccountingTestCase, ERP5ReportTestCase):
  """Test Bank Reconciliation

  """
  def getBusinessTemplateList(self):
    return AccountingTestCase.getBusinessTemplateList(self) + (
        'erp5_bank_reconciliation',)

  def afterSetUp(self):
    AccountingTestCase.afterSetUp(self)
    self.bank_account = self.section.newContent(
        portal_type='Bank Account',
        price_currency_value=self.portal.currency_module.euro)
    self.bank_account.validate()
    self.tic()

  def test_BankReconciliation_getAccountingTransactionLineList(self):
    account_module = self.account_module
    payment1 = self._makeOne(
              portal_type='Payment Transaction',
              simulation_state='delivered',
              title='First',
              reference='P1',
              source_payment_value=self.bank_account,
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2014, 1, 1),
              lines=(dict(source_value=account_module.bank,
                          source_debit=100,
                          id='bank'),
                     dict(source_value=account_module.receivable,
                          source_credit=100)))

    payment2 = self._makeOne(
              portal_type='Payment Transaction',
              simulation_state='delivered',
              title='Second',
              reference='P2',
              source_payment_value=self.bank_account,
              destination_section_value=self.organisation_module.client_2,
              start_date=DateTime(2014, 1, 2),
              lines=(dict(source_value=account_module.bank,
                          source_debit=200,
                          id='bank'),
                     dict(source_value=account_module.receivable,
                          source_credit=200)))

    payment3 = self._makeOne(
              portal_type='Payment Transaction',
              simulation_state='delivered',
              title='Not in range',
              source_payment_value=self.bank_account,
              start_date=DateTime(2014, 2, 1),
              lines=(dict(source_value=account_module.bank,
                          source_debit=700,
                          id='bank'),
                     dict(source_value=account_module.receivable,
                          source_credit=700)))

    bank_reconciliation = self.portal.bank_reconciliation_module.newContent(
        portal_type='Bank Reconciliation',
        source_section_value=self.section,
        source_payment_value=self.bank_account,
        stop_date=DateTime(2014, 1, 31))
    self.tic()

    line_list = bank_reconciliation.BankReconciliation_getAccountingTransactionLineList()
    self.assertEqual([payment1.bank, payment2.bank],
                     [line.getObject() for line in line_list])

    # The user can search in the listbox
    line_list = bank_reconciliation.BankReconciliation_getAccountingTransactionLineList(
        Movement_getExplanationTitle='First', # XXX this is the column name
    )
    self.assertEqual([payment1.bank, ],
                     [line.getObject() for line in line_list])

    line_list = bank_reconciliation.BankReconciliation_getAccountingTransactionLineList(
        Movement_getExplanationReference='P2',
    )
    self.assertEqual([payment2.bank, ],
                     [line.getObject() for line in line_list])

    line_list = bank_reconciliation.BankReconciliation_getAccountingTransactionLineList(
        Movement_getMirrorSectionTitle=self.portal.organisation_module.client_2.getTitle(),
    )
    self.assertEqual([payment2.bank, ],
                     [line.getObject() for line in line_list])

    # We manually reconcile.
    payment1.bank.setAggregateValue(bank_reconciliation)
    self.tic()
    # Now the listbox only show non reconciled transactions
    line_list = bank_reconciliation.BankReconciliation_getAccountingTransactionLineList()
    self.assertEqual([payment2.bank, ],
                     [line.getObject() for line in line_list])

    # This listbox can also be used to unreconcile some previously reconciled
    # transactions.
    line_list = bank_reconciliation.BankReconciliation_getAccountingTransactionLineList(
       reconciliation_mode="unreconcile",
    )
    self.assertEqual([payment1.bank, ],
                     [line.getObject() for line in line_list])


  def test_BankReconciliation_getReconciledAccountBalance(self):
    account_module = self.account_module
    payment1 = self._makeOne(
              portal_type='Payment Transaction',
              simulation_state='delivered',
              source_payment_value=self.bank_account,
              start_date=DateTime(2014, 1, 1),
              lines=(dict(source_value=account_module.bank,
                          source_debit=100,
                          id='bank'),
                     dict(source_value=account_module.receivable,
                          source_credit=100)))

    payment2 = self._makeOne(
              portal_type='Payment Transaction',
              simulation_state='delivered',
              source_payment_value=self.bank_account,
              start_date=DateTime(2014, 2, 1),
              lines=(dict(source_value=account_module.bank,
                          source_debit=200,
                          id='bank'),
                     dict(source_value=account_module.receivable,
                          source_credit=200)))

    bank_reconciliation = self.portal.bank_reconciliation_module.newContent(
        portal_type='Bank Reconciliation',
        source_section_value=self.section,
        source_payment_value=self.bank_account,
        stop_date=DateTime(2014, 1, 31))
    self.tic()

    self.assertEqual(100,
        bank_reconciliation.BankReconciliation_getAccountBalance())

    # At this point nothing is reconciled.
    self.assertEqual(0,
        bank_reconciliation.BankReconciliation_getReconciledAccountBalance())

    # Reconciling sets an aggregate relation from payment line to Bank
    # Reconciliation
    payment1.bank.setAggregateValue(bank_reconciliation)
    self.tic()
    # Once the payment line is reconciled, the it is counted in reconciled
    # balance
    self.assertEqual(100,
        bank_reconciliation.BankReconciliation_getReconciledAccountBalance())

    # Payment lines reconciled later are not counted.
    another_bank_reconciliation = self.portal.bank_reconciliation_module.newContent(
        portal_type='Bank Reconciliation',
        source_section_value=self.section,
        source_payment_value=self.bank_account,
        stop_date=DateTime(2014, 3, 31))
    payment2.bank.setAggregateValue(another_bank_reconciliation)
    self.tic()

    self.assertEqual(100,
        bank_reconciliation.BankReconciliation_getReconciledAccountBalance())
    self.assertEqual(100 + 200,
        another_bank_reconciliation.BankReconciliation_getReconciledAccountBalance())

    # "simple" account balance is same as reconciled, as everything is
    # reconciled in this test
    self.assertEqual(100,
        bank_reconciliation.BankReconciliation_getAccountBalance())
    self.assertEqual(100 + 200,
        another_bank_reconciliation.BankReconciliation_getAccountBalance())


  def test_BankReconciliation_fastInput(self):
    account_module = self.account_module
    payment1 = self._makeOne(
              portal_type='Payment Transaction',
              simulation_state='delivered',
              title='First',
              reference='P1',
              source_payment_value=self.bank_account,
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2014, 1, 1),
              lines=(dict(source_value=account_module.bank,
                          source_debit=100,
                          id='bank'),
                     dict(source_value=account_module.receivable,
                          source_credit=100)))

    payment2 = self._makeOne(
              portal_type='Payment Transaction',
              simulation_state='delivered',
              title='Second',
              reference='P2',
              source_payment_value=self.bank_account,
              destination_section_value=self.organisation_module.client_2,
              start_date=DateTime(2014, 1, 2),
              lines=(dict(source_value=account_module.bank,
                          source_debit=200,
                          id='bank'),
                     dict(source_value=account_module.receivable,
                          source_credit=200)))

    bank_reconciliation = self.portal.bank_reconciliation_module.newContent(
        portal_type='Bank Reconciliation',
        source_section_value=self.section,
        source_payment_value=self.bank_account,
        stop_date=DateTime(2014, 1, 31))
    self.tic()

    # View the dialog, to make sure we can display it and to reset selection
    self.portal.REQUEST.set('reset', 1)
    bank_reconciliation.BankReconciliation_viewBankReconciliationFastInputDialog()
    # Call the fast input action script
    list_selection_name = bank_reconciliation\
        .BankReconciliation_viewBankReconciliationFastInputDialog.listbox.get_value(
            'selection_name')
    bank_reconciliation.BankReconciliation_reconcileTransactionList(
        list_selection_name=list_selection_name,
        uids=(payment1.bank.getUid(),),
        reconciliation_mode='reconcile')
    self.tic()

    self.assertEqual(bank_reconciliation, payment1.bank.getAggregateValue())
    self.assertEqual(None, payment2.bank.getAggregateValue())

    # View the dialog, to make sure we can display it and to reset selection
    self.portal.REQUEST.set('reset', 1)
    bank_reconciliation.BankReconciliation_viewBankReconciliationFastInputDialog()
    # Call the fast input action script
    list_selection_name = bank_reconciliation\
        .BankReconciliation_viewBankReconciliationFastInputDialog.listbox.get_value(
            'selection_name')
    bank_reconciliation.BankReconciliation_reconcileTransactionList(
        list_selection_name=list_selection_name,
        uids=(payment1.bank.getUid(),),
        reconciliation_mode='unreconcile')
    self.tic()

    self.assertEqual(None, payment1.bank.getAggregateValue())
    self.assertEqual(None, payment2.bank.getAggregateValue())

  def test_BankReconciliation_Workflow(self):
    account_module = self.account_module
    payment1 = self._makeOne(
              portal_type='Payment Transaction',
              simulation_state='delivered',
              source_payment_value=self.bank_account,
              start_date=DateTime(2014, 1, 1),
              lines=(dict(source_value=account_module.bank,
                          source_debit=100,
                          id='bank'),
                     dict(source_value=account_module.receivable,
                          source_credit=100)))

    bank_reconciliation = self.portal.bank_reconciliation_module.newContent(
        portal_type='Bank Reconciliation',
        source_section_value=self.section,
        source_payment_value=self.bank_account,
        quantity_range_max=0,
        stop_date=DateTime(2014, 1, 31))
    self.tic()

    doActionFor = self.portal.portal_workflow.doActionFor
    self.assertEqual('draft', bank_reconciliation.getValidationState())
    doActionFor(bank_reconciliation, 'open_action')
    self.assertEqual('open', bank_reconciliation.getValidationState())
    doActionFor(bank_reconciliation, 'close_action')
    self.assertEqual('closed', bank_reconciliation.getValidationState())
    doActionFor(bank_reconciliation, 'open_action')
    self.assertEqual('open', bank_reconciliation.getValidationState())

    # Cancel has an interaction to remove all the reconciliations
    payment1.bank.setAggregateValue(bank_reconciliation)
    self.tic()

    doActionFor(bank_reconciliation, 'cancel_action')
    self.assertEqual('cancelled', bank_reconciliation.getValidationState())
    self.tic()
    self.assertEqual(None, payment1.bank.getAggregateValue())

  def test_BankReconciliation_Constraint(self):
    # Add the property sheet for this test.
    self._addPropertySheet('Bank Reconciliation',
        'BankReconciliationConstraint')

    account_module = self.account_module
    previous_bank_reconciliation = self.portal.bank_reconciliation_module.newContent(
        portal_type='Bank Reconciliation',
        source_section_value=self.section,
        source_payment_value=self.bank_account,
        quantity_range_max=100,
        stop_date=DateTime(2014, 1, 31))
    previous_bank_reconciliation.open()

    payment1 = self._makeOne(
              portal_type='Payment Transaction',
              simulation_state='delivered',
              source_payment_value=self.bank_account,
              start_date=DateTime(2014, 1, 1),
              lines=(dict(source_value=account_module.bank,
                          source_debit=100,
                          aggregate_value=previous_bank_reconciliation,
                          id='bank'),
                     dict(source_value=account_module.receivable,
                          source_credit=100)))

    payment2 = self._makeOne(
              portal_type='Payment Transaction',
              simulation_state='delivered',
              source_payment_value=self.bank_account,
              start_date=DateTime(2014, 2, 1),
              lines=(dict(source_value=account_module.bank,
                          source_debit=200,
                          id='bank'),
                     dict(source_value=account_module.receivable,
                          source_credit=200)))

    bank_reconciliation = self.portal.bank_reconciliation_module.newContent(
        portal_type='Bank Reconciliation',
        source_section_value=self.section,
        source_payment_value=self.bank_account,
        stop_date=DateTime(2014, 2, 28))
    bank_reconciliation.open()

    constraint = self.portal.portal_property_sheets.BankReconciliationConstraint
    self.assertEqual([], constraint.checkConsistency(bank_reconciliation))

    # reconciled balance must match
    bank_reconciliation.setQuantityRangeMax(10)
    self.assertEqual(1, len(bank_reconciliation.checkConsistency()))
    bank_reconciliation.setQuantityRangeMax(100)
    self.assertEqual(0, len(bank_reconciliation.checkConsistency()))

    self.assertEqual(0, len(previous_bank_reconciliation.checkConsistency()))
    previous_bank_reconciliation.setQuantityRangeMax(10)
    self.assertEqual(1, len(previous_bank_reconciliation.checkConsistency()))
    previous_bank_reconciliation.setQuantityRangeMax(100)

    # Previous reconciled balance must match as well
    bank_reconciliation.setStartDate(DateTime(2014, 1, 31))
    bank_reconciliation.setQuantityRangeMin(10)
    self.assertEqual(1, len(bank_reconciliation.checkConsistency()))

    # These constraints are only verified when we go from open to close state.
    # (that is why the bank reconciliation have been openned for the
    # assertions above)
    with self.assertRaises(ValidationFailed):
      self.portal.portal_workflow.doActionFor(
        bank_reconciliation,
        'close_action')

    bank_reconciliation.setQuantityRangeMin(100)
    self.assertEqual(0, len(bank_reconciliation.checkConsistency()))
    self.portal.portal_workflow.doActionFor(
        bank_reconciliation,
        'close_action')

    bank_reconciliation.setQuantityRangeMax(10)
    # we can pass the transition
    self.portal.portal_workflow.doActionFor(
        bank_reconciliation,
        'open_action')

  def test_BankReconciliation_Report(self):
    account_module = self.account_module
    bank_reconciliation = self.portal.bank_reconciliation_module.newContent(
        portal_type='Bank Reconciliation',
        source_section_value=self.section,
        source_payment_value=self.bank_account,
        quantity_range_max=100,
        stop_date=DateTime(2014, 1, 31))
    bank_reconciliation.open()

    payment1 = self._makeOne(
              portal_type='Payment Transaction',
              simulation_state='delivered',
              source_payment_value=self.bank_account,
              start_date=DateTime(2014, 1, 1),
              lines=(dict(source_value=account_module.bank,
                          source_debit=100,
                          aggregate_value=bank_reconciliation,
                          id='bank'),
                     dict(source_value=account_module.receivable,
                          source_credit=100)))

    payment2 = self._makeOne(
              portal_type='Payment Transaction',
              simulation_state='delivered',
              source_payment_value=self.bank_account,
              start_date=DateTime(2014, 1, 2),
              lines=(dict(source_value=account_module.bank,
                          source_debit=200,
                          id='bank'),
                     dict(source_value=account_module.receivable,
                          source_credit=200)))

    report_section_list = self.getReportSectionList(
                               bank_reconciliation,
                               'BankReconciliation_viewBankReconciliationReport')
    self.assertEqual(3, len(report_section_list))

    # First report is just the bank reconciliation view
    self.assertEqual('BankReconciliation_view', report_section_list[0].form_id)

    # Then we have the reconciled lines
    self.assertEqual({'reconciliation_mode': 'unreconcile',
                      'title': 'Reconciled Transactions'},
                      report_section_list[1].selection_params)
    line_list = self.getListBoxLineList(report_section_list[1])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(1, len(data_line_list))
    self.checkLineProperties(data_line_list[0],
                             debit=100, credit=0)

    # And finally the non reconciled lines
    line_list = self.getListBoxLineList(report_section_list[2])
    self.assertEqual({'reconciliation_mode': 'reconcile',
                      'title': 'Not Reconciled Transactions'},
                      report_section_list[2].selection_params)
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(1, len(data_line_list))
    self.checkLineProperties(data_line_list[0],
                             debit=200, credit=0)

  def test_BankReconciliation_selectNonReconciled(self):
    account_module = self.account_module
    payment1 = self._makeOne(
              portal_type='Payment Transaction',
              simulation_state='delivered',
              source_payment_value=self.bank_account,
              start_date=DateTime(2014, 1, 1),
              lines=(dict(source_value=account_module.bank,
                          source_debit=100,
                          id='bank'),
                     dict(source_value=account_module.receivable,
                          source_credit=100)))

    payment2 = self._makeOne(
              portal_type='Payment Transaction',
              simulation_state='delivered',
              source_payment_value=self.bank_account,
              start_date=DateTime(2014, 2, 1),
              lines=(dict(source_value=account_module.bank,
                          source_debit=200,
                          id='bank'),
                     dict(source_value=account_module.receivable,
                          source_credit=200)))

    bank_reconciliation = self.portal.bank_reconciliation_module.newContent(
        portal_type='Bank Reconciliation',
        source_section_value=self.section,
        source_payment_value=self.bank_account,
        stop_date=DateTime(2014, 1, 31))
    self.tic()

    # we can display the dialog without error
    bank_reconciliation.BankReconciliation_viewSelectNonReconciledTransactionListDialog()
    bank_reconciliation.BankReconciliation_selectNonReconciledTransactionList()
    self.tic()

    # All lines with date < stop_date are reconciled
    self.assertEqual(bank_reconciliation, payment1.bank.getAggregateValue())
    self.assertEqual(None, payment2.bank.getAggregateValue())

  def test_BankReconciliation_multiple_section_using_same_bank_account(self):
    account_module = self.account_module
    self.bank_account.invalidate()
    main_section_bank_account = self.main_section.newContent(
        portal_type='Bank Account',
        price_currency_value=self.portal.currency_module.euro)
    main_section_bank_account.validate()
    
    payment1 = self._makeOne(
              portal_type='Payment Transaction',
              simulation_state='delivered',
              source_payment_value=main_section_bank_account,
              start_date=DateTime(2014, 1, 1),
              lines=(dict(source_value=account_module.bank,
                          source_debit=100,
                          id='bank'),
                     dict(source_value=account_module.receivable,
                          source_credit=100)))

    payment2 = self._makeOne(
              portal_type='Payment Transaction',
              simulation_state='delivered',
              source_section_value=self.main_section,
              source_payment_value=main_section_bank_account,
              start_date=DateTime(2014, 1, 2),
              lines=(dict(source_value=account_module.bank,
                          source_debit=200,
                          id='bank'),
                     dict(source_value=account_module.receivable,
                          source_credit=200)))

    bank_reconciliation = self.portal.bank_reconciliation_module.newContent(
        portal_type='Bank Reconciliation',
        source_section_value=self.main_section,
        source_payment_value=main_section_bank_account,
        stop_date=DateTime(2014, 1, 31))
    self.tic()

    self.assertEqual(300, bank_reconciliation.BankReconciliation_getAccountBalance())
    self.assertEqual(
      [payment1.bank, payment2.bank],
      [x.getObject() for x in bank_reconciliation.BankReconciliation_getAccountingTransactionLineList()])
    
    list_selection_name = bank_reconciliation\
        .BankReconciliation_viewBankReconciliationFastInputDialog.listbox.get_value(
            'selection_name')
    bank_reconciliation.BankReconciliation_reconcileTransactionList(
        list_selection_name=list_selection_name,
        uids=(payment1.bank.getUid(), ),
        reconciliation_mode='reconcile')
    self.tic()
    self.assertEqual(100, bank_reconciliation.BankReconciliation_getReconciledAccountBalance())

  def test_BankReconciliation_internal_transaction(self):
    # Allow internal invoice in accounting module
    module_allowed_type_list = self.portal.portal_types[
        'Accounting Transaction Module'].getTypeAllowedContentTypeList()
    self.portal.portal_types[
        'Accounting Transaction Module'].setTypeAllowedContentTypeList(
          module_allowed_type_list + ['Internal Invoice Transaction',])

    account_module = self.account_module
    main_section_bank_account = self.main_section.newContent(
        portal_type='Bank Account',
        price_currency_value=self.portal.currency_module.euro)
    main_section_bank_account.validate()
    
    internal_transaction = self.portal.accounting_module.newContent(
        portal_type='Internal Invoice Transaction',
        source_section_value=self.section,
        source_payment_value=self.bank_account,
        destination_section_value=self.main_section,
        destination_payment_value=main_section_bank_account,
        resource_value=self.portal.currency_module.euro,
        start_date=DateTime(2014, 1, 1))
    internal_transaction.newContent(
        portal_type='Internal Invoice Transaction Line',
        source_value=account_module.bank,
        destination_value=account_module.bank,
        source_debit=100,
        id='bank')

    internal_transaction.newContent(
        portal_type='Internal Invoice Transaction Line',
        destination_value=account_module.payable,
        source_value=account_module.receivable,
        source_credit=100)
    internal_transaction.start()
    internal_transaction.stop()

    # this internal_transaction.bank line exists in both reconciliation for
    # `section` and for `main_section` and can be reconciled independently by
    # each section
    bank_reconciliation_for_main_section = self.portal.bank_reconciliation_module.newContent(
        portal_type='Bank Reconciliation',
        title='Bank Reconcilisation for Main Section',
        source_section_value=self.main_section,
        source_payment_value=main_section_bank_account,
        stop_date=DateTime(2014, 1, 31))
    self.tic()

    self.assertEqual(-100, bank_reconciliation_for_main_section.BankReconciliation_getAccountBalance())
    self.assertEqual(
        [internal_transaction.bank, ],
        [x.getObject() for x in
            bank_reconciliation_for_main_section.BankReconciliation_getAccountingTransactionLineList()])

    bank_reconciliation_for_section = self.portal.bank_reconciliation_module.newContent(
        portal_type='Bank Reconciliation',
        title='Bank Reconcilisation for Section',
        source_section_value=self.section,
        source_payment_value=self.bank_account,
        stop_date=DateTime(2014, 1, 31))
    self.tic()

    self.assertEqual(100, bank_reconciliation_for_section.BankReconciliation_getAccountBalance())
    self.assertEqual(
        [internal_transaction.bank, ],
        [x.getObject() for x in
            bank_reconciliation_for_section.BankReconciliation_getAccountingTransactionLineList()])
    
    # if `section` reconciles, the line is not reconciled for `main_section`
    list_selection_name = bank_reconciliation_for_section\
        .BankReconciliation_viewBankReconciliationFastInputDialog.listbox.get_value(
            'selection_name')
    bank_reconciliation_for_section.BankReconciliation_reconcileTransactionList(
        list_selection_name=list_selection_name,
        uids=(internal_transaction.bank.getUid(), ),
        reconciliation_mode='reconcile')
    self.tic()
    # reconciled for `section`
    self.assertEqual(100, bank_reconciliation_for_section.BankReconciliation_getReconciledAccountBalance())
    self.assertEqual(
        [],
        [x.getObject() for x in
            bank_reconciliation_for_section.BankReconciliation_getAccountingTransactionLineList()])
    # Not reconciled for `main_section`
    self.assertEqual(0, bank_reconciliation_for_main_section.BankReconciliation_getReconciledAccountBalance())
    self.assertEqual(
        [internal_transaction.bank, ],
        [x.getObject() for x in
            bank_reconciliation_for_main_section.BankReconciliation_getAccountingTransactionLineList()])

    self.assertItemsEqual(
        [bank_reconciliation_for_section],
        internal_transaction.bank.getAggregateValueList())

    # if `main_section` also reconcile, line will be reconciled for both
    list_selection_name = bank_reconciliation_for_main_section\
        .BankReconciliation_viewBankReconciliationFastInputDialog.listbox.get_value(
            'selection_name')
    bank_reconciliation_for_main_section.BankReconciliation_reconcileTransactionList(
        list_selection_name=list_selection_name,
        uids=(internal_transaction.bank.getUid(), ),
        reconciliation_mode='reconcile')
    self.tic()
    # Reconciled for `main_section`
    self.assertEqual(-100, bank_reconciliation_for_main_section.BankReconciliation_getReconciledAccountBalance())
    self.assertEqual(
        [],
        [x.getObject() for x in
            bank_reconciliation_for_main_section.BankReconciliation_getAccountingTransactionLineList()])
    # Still reconciled for `section`
    self.assertEqual(100, bank_reconciliation_for_section.BankReconciliation_getReconciledAccountBalance())
    self.assertEqual(
        [],
        [x.getObject() for x in
            bank_reconciliation_for_section.BankReconciliation_getAccountingTransactionLineList()])

    self.assertItemsEqual(
        [bank_reconciliation_for_section, bank_reconciliation_for_main_section],
        internal_transaction.bank.getAggregateValueList())


    # if `section` un-reconcile, line will be not reconciled for `section`, but still reconciled for `main_section`
    list_selection_name = bank_reconciliation_for_section\
        .BankReconciliation_viewBankReconciliationFastInputDialog.listbox.get_value(
            'selection_name')
    bank_reconciliation_for_section.BankReconciliation_reconcileTransactionList(
        list_selection_name=list_selection_name,
        uids=(internal_transaction.bank.getUid(), ),
        reconciliation_mode='unreconcile')
    self.tic()
    # no longer reconciled for `section`
    self.assertEqual(0, bank_reconciliation_for_section.BankReconciliation_getReconciledAccountBalance())
    self.assertEqual(
        [internal_transaction.bank,],
        [x.getObject() for x in
            bank_reconciliation_for_section.BankReconciliation_getAccountingTransactionLineList()])
    # Still reconciled for `main_section`
    self.assertEqual(-100, bank_reconciliation_for_main_section.BankReconciliation_getReconciledAccountBalance())
    self.assertEqual(
        [],
        [x.getObject() for x in
            bank_reconciliation_for_main_section.BankReconciliation_getAccountingTransactionLineList()])

    self.assertItemsEqual(
        [bank_reconciliation_for_main_section],
        internal_transaction.bank.getAggregateValueList())


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestBankReconciliation))
  return suite
