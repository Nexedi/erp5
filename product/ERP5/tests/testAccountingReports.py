#############################################################################
#
# Copyright (c) 2006 Nexedi SA and Contributors. All Rights Reserved.
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

"""Tests Standards ERP5 Accounting Reports
"""

import unittest

from DateTime import DateTime

from Products.ERP5.tests.testAccounting import AccountingTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5ReportTestCase
from Products.ERP5Type.UnrestrictedMethod import UnrestrictedMethod

class TestAccountingReports(AccountingTestCase, ERP5ReportTestCase):
  """Test Accounting reports

  Test basic cases of gathering data to render reports, the purpose of those
  tests is to exercise basic reporting features to make sure no regression
  happen. Input data used for tests usually contain edge cases, for example:
    * movements at the boundaries of the period.
    * movements with other simulation states.
    * movements with node in the section_category we want to exclude (Persons).
    * movements with source & destination for other sections.
    ...
  """

  def testJournal(self):
    # Journal report.
    # this will be a journal for 2006/02/02, for Sale Invoice Transaction
    # portal type. Many cases are covered by this test.

    account_module = self.account_module
    # before the date
    self._makeOne(
              portal_type='Accounting Transaction',
              simulation_state='delivered',
              start_date=DateTime(2006, 1, 1),
              lines=(dict(source_value=account_module.equity,
                          source_debit=100),
                     dict(source_value=account_module.stocks,
                          source_credit=100)))

    # during the period
    first = self._makeOne(
              portal_type='Sale Invoice Transaction',
              title='First One',
              simulation_state='delivered',
              reference='1',
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2006, 2, 2),
              lines=(dict(source_value=account_module.receivable,
                          source_debit=119.60),
                     dict(source_value=account_module.collected_vat,
                          source_credit=19.60),
                     dict(source_value=account_module.goods_sales,
                          source_credit=100.00)))

    second = self._makeOne(
              portal_type='Sale Invoice Transaction',
              title='Second One',
              simulation_state='delivered',
              reference='2',
              destination_section_value=self.organisation_module.client_2,
              start_date=DateTime(2006, 2, 2, 1, 1), # XXX we have to force
              # different values of hour minutes, because /for now/ sorting is
              # done on date, uid. Sorting on [source|destination]_reference
              # would be too heavy, and we just want a sort on date, with a
              # stable order (hence the cheap sort on uid)
              lines=(dict(source_value=account_module.receivable,
                          source_debit=239.20),
                     dict(source_value=account_module.collected_vat,
                          source_credit=39.20),
                     dict(source_value=account_module.goods_sales,
                          source_credit=200.00)))

    third = self._makeOne(
              title='Third One',
              portal_type='Sale Invoice Transaction',
              simulation_state='delivered',
              reference='3',
              # with a person member of the group
              destination_section_value=self.person_module.john_smith,
              start_date=DateTime(2006, 2, 2, 2, 2), # with hour:minutes
              lines=(dict(source_value=account_module.receivable,
                          destination_value=account_module.receivable,
                          source_debit=358.80),
                     dict(source_value=account_module.collected_vat,
                          source_credit=58.80),
                     dict(source_value=account_module.goods_sales,
                          # with a title on the line
                          title='Line Title',
                          source_credit=300.00)))

    # another portal type
    self._makeOne(
              portal_type='Accounting Transaction',
              simulation_state='delivered',
              start_date=DateTime(2006, 2, 2),
              lines=(dict(source_value=account_module.equity,
                          source_debit=111),
                     dict(source_value=account_module.stocks,
                          source_credit=111)))

    # after the period
    self._makeOne(
              portal_type='Sale Invoice Transaction',
              simulation_state='delivered',
              destination_section_value=self.organisation_module.client_2,
              start_date=DateTime(2006, 2, 3),
              lines=(dict(source_value=account_module.receivable,
                          source_debit=598.00),
                     dict(source_value=account_module.collected_vat,
                          source_credit=98.00),
                     dict(source_value=account_module.goods_sales,
                          source_credit=500.00)))

    # set request variables and render
    request_form = self.portal.REQUEST.form
    request_form['at_date'] = DateTime(2006, 2, 2)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['portal_type'] = ['Sale Invoice Transaction']
    request_form['simulation_state'] = ['delivered']
    request_form['hide_analytic'] = False

    report_section_list = self.getReportSectionList(
                               self.portal.accounting_module,
                               'AccountingTransactionModule_viewJournalReport')
    self.assertEqual(1, len(report_section_list))
    # currency is present in the report
    self.assertEqual('currency_module/euro', self.portal.
     AccountingTransactionModule_viewJournalReport.your_currency.get_value('default'))

    # precision is set in the REQUEST (so that fields know how to format)
    precision = self.portal.REQUEST.get('precision')
    self.assertEqual(2, precision)

    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    # we have 3 transactions, with 3 lines each
    self.assertEqual(9, len(data_line_list))

    # test columns values
    line = data_line_list[0]
    self.assertEqual(line.column_id_list,
        ['specific_reference', 'date', 'title', 'parent_reference',
          'node_title', 'mirror_section_title', 'debit', 'credit'])

    # First Transaction
    self.checkLineProperties(data_line_list[0],
                            specific_reference=first.getSourceReference(),
                            date=DateTime(2006, 2, 2),
                            title='First One',
                            parent_reference='1',
                            node_title='41',
                            mirror_section_title='Client 1',
                            debit=119.60,
                            credit=0)
    # some values are only present when we display the first line of the
    # transaction (this is a way to see different transactions)
    self.checkLineProperties(data_line_list[1],
                            specific_reference='',
                            date=None,
                            title='',
                            parent_reference='',
                            node_title='4457',
                            mirror_section_title='Client 1',
                            debit=0,
                            credit=19.60)
    self.checkLineProperties(data_line_list[2],
                            specific_reference='',
                            date=None,
                            title='',
                            parent_reference='',
                            node_title='7',
                            mirror_section_title='Client 1',
                            debit=0,
                            credit=100)

    # Second Transaction
    self.checkLineProperties(data_line_list[3],
                            specific_reference=second.getSourceReference(),
                            date=DateTime(2006, 2, 2, 1, 1),
                            title='Second One',
                            parent_reference='2',
                            node_title='41',
                            mirror_section_title='Client 2',
                            debit=239.20,
                            credit=0)
    self.checkLineProperties(data_line_list[4],
                            specific_reference='',
                            date=None,
                            title='',
                            parent_reference='',
                            node_title='4457',
                            mirror_section_title='Client 2',
                            debit=0,
                            credit=39.20)
    self.checkLineProperties(data_line_list[5],
                            specific_reference='',
                            date=None,
                            title='',
                            parent_reference='',
                            node_title='7',
                            mirror_section_title='Client 2',
                            debit=0,
                            credit=200)

    # Third Transaction
    self.checkLineProperties(data_line_list[6],
                            specific_reference=third.getSourceReference(),
                            date=DateTime(2006, 2, 2, 2, 2),# 2006/02/02 will
                              # be displayed, but this rendering level cannot
                              # be tested with this framework
                            title='Third One',
                            parent_reference='3',
                            node_title='41',
                            mirror_section_title='John Smith',
                            debit=358.80,
                            credit=0)
    self.checkLineProperties(data_line_list[7],
                            specific_reference='',
                            date=None,
                            title='',
                            parent_reference='',
                            node_title='4457',
                            mirror_section_title='John Smith',
                            debit=0,
                            credit=58.80)
    self.checkLineProperties(data_line_list[8],
                            specific_reference='',
                            date=None,
                            # If a title is set on the line, we can see it on
                            # this report
                            title='Line Title',
                            parent_reference='',
                            node_title='7',
                            mirror_section_title='John Smith',
                            debit=0,
                            credit=300)

    # Stat Line
    stat_line = line_list[-1]
    self.assertTrue(stat_line.isStatLine())
    self.assertFalse(stat_line.getColumnProperty('specific_reference'))
    self.assertFalse(stat_line.getColumnProperty('date'))
    self.assertFalse(stat_line.getColumnProperty('title'))
    self.assertFalse(stat_line.getColumnProperty('parent_reference'))
    self.assertFalse(stat_line.getColumnProperty('node_title'))
    self.assertFalse(stat_line.getColumnProperty('mirror_section_title'))
    # when printing the report, the field does the rounding, so we can round in
    # the test
    self.assertEqual(717.60, round(stat_line.getColumnProperty('debit'),
                                    precision))
    self.assertEqual(717.60, round(stat_line.getColumnProperty('credit'),
                                    precision))

  def testJournalTransactionsWithoutThirdParty(self):
    # Journal report

    account_module = self.account_module

    # during the period
    first = self._makeOne(
              portal_type='Accounting Transaction',
              title='First One',
              simulation_state='delivered',
              start_date=DateTime(2006, 2, 2),
              lines=(dict(source_value=account_module.receivable,
                          source_debit=119.60),
                     dict(source_value=account_module.collected_vat,
                          source_credit=19.60),
                     dict(source_value=account_module.goods_sales,
                          source_credit=100.00)))
    self.assertEqual(None, first.getDestinationSectionValue())

    second = self._makeOne(
              portal_type='Accounting Transaction',
              title='Second One',
              simulation_state='delivered',
              destination_section_value=self.section,
              source_section=None,
              source_section_value=None,
              start_date=DateTime(2006, 2, 2, 1, 1),
              lines=(dict(destination_value=account_module.receivable,
                          destination_debit=119.60),
                     dict(destination_value=account_module.collected_vat,
                          destination_credit=19.60),
                     dict(destination_value=account_module.goods_sales,
                          destination_credit=100.00)))
    self.assertEqual(None, second.getSourceSectionValue())


    # set request variables and render
    request_form = self.portal.REQUEST.form
    request_form['at_date'] = DateTime(2006, 2, 2)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['portal_type'] = ['Accounting Transaction']
    request_form['simulation_state'] = ['delivered']
    request_form['hide_analytic'] = False

    report_section_list = self.getReportSectionList(
                               self.portal.accounting_module,
                               'AccountingTransactionModule_viewJournalReport')
    self.assertEqual(1, len(report_section_list))

    # precision is set in the REQUEST (so that fields know how to format)
    precision = self.portal.REQUEST.get('precision')
    self.assertEqual(2, precision)

    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    # we have 2 transactions, with 3 lines
    self.assertEqual(6, len(data_line_list))

    # test columns values
    line = data_line_list[0]
    self.assertEqual(line.column_id_list,
        ['specific_reference', 'date', 'title', 'parent_reference', 'node_title',
         'mirror_section_title', 'debit', 'credit'])

    # First Transaction
    self.checkLineProperties(data_line_list[0],
                            specific_reference=first.getSourceReference(),
                            date=DateTime(2006, 2, 2),
                            title='First One',
                            node_title='41',
                            debit=119.60,
                            credit=0)
    # some values are only present when we display the first line of the
    # transaction (this is a way to see different transactions)
    self.checkLineProperties(data_line_list[1],
                            specific_reference='',
                            date=None,
                            title='',
                            node_title='4457',
                            debit=0,
                            credit=19.60)
    self.checkLineProperties(data_line_list[2],
                            specific_reference='',
                            date=None,
                            title='',
                            node_title='7',
                            debit=0,
                            credit=100)
    # second transaction
    self.checkLineProperties(data_line_list[3],
                            specific_reference=second.getDestinationReference(),
                            date=DateTime(2006, 2, 2, 1, 1),
                            title='Second One',
                            node_title='41',
                            debit=119.60,
                            credit=0)
    # some values are only present when we display the first line of the
    # transaction (this is a way to see different transactions)
    self.checkLineProperties(data_line_list[4],
                            specific_reference='',
                            date=None,
                            title='',
                            node_title='4457',
                            debit=0,
                            credit=19.60)
    self.checkLineProperties(data_line_list[5],
                            specific_reference='',
                            date=None,
                            title='',
                            node_title='7',
                            debit=0,
                            credit=100)

     # Stat Line
    stat_line = line_list[-1]
    self.assertTrue(stat_line.isStatLine())
    self.assertFalse(stat_line.getColumnProperty('specific_reference'))
    self.assertFalse(stat_line.getColumnProperty('date'))
    self.assertFalse(stat_line.getColumnProperty('title'))
    self.assertFalse(stat_line.getColumnProperty('node_title'))
    self.assertFalse(stat_line.getColumnProperty('mirror_section_title'))
    # when printing the report, the field does the rounding, so we can round in
    # the test
    self.assertEqual(239.20, round(stat_line.getColumnProperty('debit'),
                                    precision))
    self.assertEqual(239.20, round(stat_line.getColumnProperty('credit'),
                                    precision))


  def testJournalWithBankAccount(self):
    # Journal report when selecting a bank account
    # this will be a journal for 2006/02/02, whith two bank accounts

    account_module = self.account_module

    bank1 = self.section.newContent(portal_type='Bank Account')
    bank1.validate()
    bank2 = self.section.newContent(portal_type='Bank Account')
    bank2.validate()

    transaction = self._makeOne(
              portal_type='Payment Transaction',
              title='Good One',
              simulation_state='delivered',
              source_payment_value=bank1,
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2006, 2, 2),
              lines=(dict(source_value=account_module.receivable,
                          source_debit=100.0),
                     dict(source_value=account_module.bank,
                          source_credit=100.0)))

    self._makeOne(
              portal_type='Payment Transaction',
              title='Other One',
              simulation_state='delivered',
              source_payment_value=bank2,
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2006, 2, 2),
              lines=(dict(source_value=account_module.receivable,
                          source_debit=200.0),
                     dict(source_value=account_module.bank,
                          source_credit=200.0)))


    # set request variables and render
    request_form = self.portal.REQUEST.form
    request_form['at_date'] = DateTime(2006, 2, 2)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['portal_type'] = ['Payment Transaction']
    request_form['simulation_state'] = ['delivered']
    request_form['payment'] = bank1.getRelativeUrl()
    request_form['hide_analytic'] = False

    report_section_list = self.getReportSectionList(
                               self.portal.accounting_module,
                               'AccountingTransactionModule_viewJournalReport')
    self.assertEqual(1, len(report_section_list))

    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    # we have 1 transactions with 2 lines
    self.assertEqual(2, len(data_line_list))

    self.checkLineProperties(data_line_list[0],
                            specific_reference=transaction.getSourceReference(),
                            date=DateTime(2006, 2, 2),
                            title='Good One',
                            node_title='41',
                            mirror_section_title='Client 1',
                            debit=100,
                            credit=0)
    self.checkLineProperties(data_line_list[1],
                            specific_reference='',
                            date=None,
                            title='',
                            node_title='5',
                            mirror_section_title='Client 1',
                            debit=0,
                            credit=100)

    # Stat Line
    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], debit=100, credit=100)

  def testJournalProject(self):
    self.createProjectAndFunctionDataSet()
    request_form = self.portal.REQUEST.form
    request_form['at_date'] = DateTime(2006, 2, 2)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['portal_type'] = ['Sale Invoice Transaction']
    request_form['simulation_state'] = ['delivered']
    request_form['project'] = self.project_1.getRelativeUrl()
    request_form['hide_analytic'] = True

    report_section_list = self.getReportSectionList(
                               self.portal.accounting_module,
                               'AccountingTransactionModule_viewJournalReport')
    self.assertEqual(1, len(report_section_list))

    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(2, len(data_line_list))

    # test columns values
    line = data_line_list[0]
    self.assertEqual(line.column_id_list,
        ['specific_reference', 'date', 'title', 'parent_reference',
          'node_title', 'mirror_section_title', 'debit', 'credit'])

    self.checkLineProperties(data_line_list[0],
                             node_title='41',
                             mirror_section_title='Client 1',
                             debit=500,
                             credit=0)
    self.checkLineProperties(data_line_list[1],
                             node_title='7',
                             debit=0,
                             credit=500)
    stat_line = line_list[-1]
    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], debit=500, credit=500)

  def testJournalLedger(self):
    self.createLedgerDataSet()
    request_form = self.portal.REQUEST.form
    request_form['at_date'] = DateTime(2006, 2, 2)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['portal_type'] = ['Sale Invoice Transaction']
    request_form['simulation_state'] = ['delivered']
    request_form['ledger'] = 'ledger/accounting/general'
    request_form['hide_analytic'] = True

    report_section_list = self.getReportSectionList(
                               self.portal.accounting_module,
                               'AccountingTransactionModule_viewJournalReport')
    self.assertEqual(1, len(report_section_list))

    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(2, len(data_line_list))

    self.checkLineProperties(data_line_list[0],
                             node_title='41',
                             mirror_section_title='Client 1',
                             debit=500,
                             credit=0)
    self.checkLineProperties(data_line_list[1],
                             node_title='7',
                             debit=0,
                             credit=500)
    stat_line = line_list[-1]
    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], debit=500, credit=500)

  def createAccountStatementDataSet(self, use_two_bank_accounts=1):
    """Create transactions for Account statement report.

    use_two_bank_accounts -- use two different bank accounts, otherwise always
    use one bank account for all created transactions.
    """
    account_module = self.account_module
    bank1 = self.section.newContent(portal_type='Bank Account', title='Bank1')
    bank1.validate()
    if use_two_bank_accounts:
      bank2 = self.section.newContent(portal_type='Bank Account',
                                      title='Bank2')
      bank2.validate()
    else:
      bank2 = bank1

    # before
    t1 = self._makeOne(
              portal_type='Accounting Transaction',
              title='Transaction 1',
              source_reference='1',
              reference='ref1',
              simulation_state='delivered',
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2006, 2, 1),
              lines=(dict(source_value=account_module.receivable,
                          source_debit=100.0),
                     dict(source_value=account_module.payable,
                          source_credit=100.0)))

    t2 = self._makeOne(
              portal_type='Accounting Transaction',
              title='Transaction 2',
              source_reference='2',
              reference='ref2',
              simulation_state='delivered',
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2006, 2, 1, 0, 1),
              lines=(dict(source_value=account_module.payable,
                          source_debit=200.0),
                     dict(source_value=account_module.receivable,
                          source_credit=200.0)))

    # in the period
    t3 = self._makeOne(
              portal_type='Payment Transaction',
              title='Transaction 3',
              source_reference='3',
              reference='ref3',
              simulation_state='delivered',
              source_payment_value=bank1,
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2006, 2, 2, 0, 2),
              lines=(dict(source_value=account_module.receivable,
                          source_debit=300.0),
                     dict(source_value=account_module.bank,
                          source_credit=300.0)))

    t4 = self._makeOne(
              portal_type='Payment Transaction',
              title='Transaction 4',
              destination_reference='4',
              reference='ref4',
              simulation_state='delivered',
              destination_section_value=self.section,
              destination_payment_value=bank1,
              source_section_value=self.organisation_module.client_2,
              stop_date=DateTime(2006, 2, 2, 0, 3),
              start_date=DateTime(2006, 2, 1),
              lines=(dict(destination_value=account_module.receivable,
                          destination_debit=400.0),
                     dict(destination_value=account_module.bank,
                          destination_credit=400.0)))

    t5 = self._makeOne(
              portal_type='Accounting Transaction',
              title='Transaction 5',
              source_reference='5',
              reference='ref5',
              simulation_state='delivered',
              source_payment_value=bank2,
              destination_section_value=self.person_module.john_smith,
              start_date=DateTime(2006, 2, 2, 0, 4),
              lines=(dict(source_value=account_module.receivable,
                          source_debit=500.0),
                     dict(source_value=account_module.bank,
                          source_credit=500.0)))

    t6 = self._makeOne(
              portal_type='Purchase Invoice Transaction',
              title='Transaction 6',
              destination_reference='6',
              reference='ref6',
              simulation_state='delivered',
              destination_payment_value=bank2,
              source_section_value=self.organisation_module.client_1,
              stop_date=DateTime(2006, 2, 2, 0, 5),
              lines=(dict(destination_value=account_module.receivable,
                          destination_debit=600.0),
                     dict(destination_value=account_module.bank,
                          destination_credit=600.0)))

    # another simulation state
    t7 = self._makeOne(
              portal_type='Accounting Transaction',
              title='Transaction 7',
              source_reference='7',
              reference='ref7',
              simulation_state='stopped',
              source_payment_value=bank2,
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2006, 2, 2, 0, 6),
              lines=(dict(source_value=account_module.receivable,
                          source_debit=700.0),
                     dict(source_value=account_module.bank,
                          source_credit=700.0)))

    # after the period
    t8 = self._makeOne(
              portal_type='Accounting Transaction',
              title='Transaction 8',
              source_reference='8',
              reference='ref8',
              simulation_state='delivered',
              source_payment_value=bank2,
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2006, 2, 3),
              lines=(dict(source_value=account_module.receivable,
                          source_debit=800.0),
                     dict(source_value=account_module.bank,
                          source_credit=800.0)))

    return bank1, (t1, t2, t3, t4, t5, t6, t7, t8)

  def createAccountStatementDataSetOnTwoPeriods(self):
    """Create accounting transactions on two periods, one transaction in 2005,
    two transactions in 2006.
    """
    account_module = self.account_module

    # before
    t1 = self._makeOne(
              portal_type='Sale Invoice Transaction',
              title='Transaction 1',
              reference='ref1',
              source_reference='1',
              simulation_state='delivered',
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2005, 12, 31),
              lines=(dict(source_value=account_module.receivable,
                          source_debit=100.0),
                     dict(source_value=account_module.goods_sales,
                          source_credit=100.0)))

    t2 = self._makeOne(
              portal_type='Sale Invoice Transaction',
              title='Transaction 2',
              reference='ref2',
              source_reference='2',
              simulation_state='delivered',
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2006, 1, 1),
              lines=(dict(source_value=account_module.receivable,
                          source_debit=200.0),
                     dict(source_value=account_module.goods_sales,
                          source_credit=200.0)))

    t3 = self._makeOne(
              portal_type='Sale Invoice Transaction',
              title='Transaction 3',
              reference='ref3',
              source_reference='3',
              simulation_state='delivered',
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2006, 2, 2),
              lines=(dict(source_value=account_module.receivable,
                          source_debit=300.0),
                     dict(source_value=account_module.goods_sales,
                          source_credit=300.0)))

    return t1, t2, t3

  @UnrestrictedMethod
  def createProjectAndFunctionDataSet(self):
    # create some functions
    function = self.portal.portal_categories.function
    if function._getOb('a', None) is None:
      function.newContent(portal_type='Category', id='a')
    self.function_a = function['a']
    if function._getOb('b', None) is None:
      function.newContent(portal_type='Category', id='b')
    self.function_b = function['b']
    # create some projects
    self.project_1 = self.portal.project_module.newContent(
                          portal_type='Project',
                          reference='P1',
                          title='Project 1')
    self.project_2 = self.portal.project_module.newContent(
                          portal_type='Project',
                          reference='P2',
                          title='Project 2')

    account_module = self.portal.account_module
    self._makeOne(
              portal_type='Sale Invoice Transaction',
              title='Function a Project 1',
              source_reference='1',
              simulation_state='delivered',
              reference='FaP1',
              destination_section_value=self.organisation_module.client_1,
              source_function_value=self.function_a,
              source_project_value=self.project_1,
              start_date=DateTime(2006, 2, 2),
              lines=(dict(source_value=account_module.receivable,
                          source_debit=500.0),
                     dict(source_value=account_module.goods_sales,
                          source_credit=500.0)))
    self._makeOne(
              portal_type='Sale Invoice Transaction',
              title='Function b Project 2',
              source_reference='2',
              reference='FbP2',
              simulation_state='delivered',
              destination_section_value=self.organisation_module.client_1,
              source_function_value=self.function_b,
              source_project_value=self.project_2,
              start_date=DateTime(2006, 2, 2),
              lines=(dict(source_value=account_module.receivable,
                          source_debit=300.0),
                     dict(source_value=account_module.goods_sales,
                          source_credit=300.0)))
    self._makeOne(
              portal_type='Sale Invoice Transaction',
              title='No function no project',
              source_reference='3',
              reference='nono',
              simulation_state='delivered',
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2006, 2, 2),
              lines=(dict(source_value=account_module.receivable,
                          source_debit=700.0),
                     dict(source_value=account_module.goods_sales,
                          source_credit=700.0)))

  def createMirrorSectionRoleDataSet(self):
    account_module = self.portal.account_module
    self._makeOne(
              portal_type='Sale Invoice Transaction',
              title='Invoice to a client',
              source_reference='1',
              simulation_state='delivered',
              reference='Ic',
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2006, 2, 2),
              lines=(dict(source_value=account_module.receivable,
                          source_debit=500.0),
                     dict(source_value=account_module.goods_sales,
                          source_credit=500.0)))
    self._makeOne(
              portal_type='Sale Invoice Transaction',
              title='Invoice to a supplier',
              source_reference='2',
              reference='Is',
              simulation_state='delivered',
              destination_section_value=self.organisation_module.supplier,
              start_date=DateTime(2006, 2, 2),
              lines=(dict(source_value=account_module.receivable,
                          source_debit=300.0),
                     dict(source_value=account_module.goods_sales,
                          source_credit=300.0)))

  @UnrestrictedMethod
  def createLedgerCategory(self):
    ledger = self.portal.portal_categories.ledger
    self.accounting_ledger = ledger.get('accounting', None)
    if self.accounting_ledger is None:
      self.accounting_ledger = ledger.newContent(portal_type='Category',
                                                 id='accounting')
    if self.accounting_ledger.get('general', None) is None:
      self.accounting_ledger.newContent(portal_type='Category', id='general')
    if self.accounting_ledger.get('detailed', None) is None:
      self.accounting_ledger.newContent(portal_type='Category', id='detailed')

  def createLedgerDataSet(self):
    # create some ledgers
    self.createLedgerCategory()

    account_module = self.portal.account_module
    self._makeOne(
              portal_type='Sale Invoice Transaction',
              title='Ledger detailed',
              reference='lad',
              simulation_state='delivered',
              destination_section_value=self.organisation_module.client_1,
              ledger='accounting/detailed',
              start_date=DateTime(2006, 2, 2),
              lines=(dict(source_value=account_module.receivable,
                          source_debit=300.0),
                     dict(source_value=account_module.goods_sales,
                          source_credit=300.0),
                     dict(source_value=account_module.receivable,
                          source_debit=200.0),
                     dict(source_value=account_module.goods_sales,
                          source_credit=200.0)))

    self._makeOne(
              portal_type='Sale Invoice Transaction',
              title='Ledger general',
              reference='lag',
              simulation_state='delivered',
              destination_section_value=self.organisation_module.client_1,
              ledger='accounting/general',
              start_date=DateTime(2006, 2, 2),
              lines=(dict(source_value=account_module.receivable,
                          source_debit=500.0),
                     dict(source_value=account_module.goods_sales,
                          source_credit=500.0)))

  def test_Resource_zGetMovementHistoryList(self):
    # Check if Resource_zGetMovementHistoryList works fine with derived_merge optimizer.
    # see https://bugs.launchpad.net/maria/+bug/985828
    q = self.portal.erp5_sql_connection.manage_test
    tmp = q("show variables like 'optimizer_switch'")
    optimizer_switch_dict = dict([x.split('=') for x in tmp[0][1].split(',')])
    q("SET optimizer_switch = 'derived_merge=on'")
    try:
      self.testAccountStatement()
    finally:
      q("SET optimizer_switch = 'derived_merge=%s'" % \
          optimizer_switch_dict.get('derived_merge', 'off'))

  def testAccountStatement(self):
    # Simple Account Statement for "Receivable" account
    self.createAccountStatementDataSet()

    # set request variables and render
    request_form = self.portal.REQUEST.form
    request_form['node'] = \
                self.portal.account_module.receivable.getRelativeUrl()
    request_form['at_date'] = DateTime(2006, 2, 2)
    request_form['section_category'] = 'group/demo_group/sub1'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']
    request_form['hide_analytic'] = False
    request_form['export'] = False

    report_section_list = self.getReportSectionList(
                               self.portal.accounting_module,
                               'AccountModule_viewAccountStatementReport')
    self.assertEqual(1, len(report_section_list))

    # precision is set in the REQUEST (so that fields know how to format)
    precision = self.portal.REQUEST.get('precision')
    self.assertEqual(2, precision)

    # currency is present in the report
    self.assertEqual('currency_module/euro', self.portal.
        AccountModule_viewAccountStatementReport.your_currency.get_value('default'))

    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    # we have 6 transactions, because 7th is after
    self.assertEqual(6, len(data_line_list))

    # test columns values
    line = data_line_list[0]
    self.assertEqual(line.column_id_list,
        ['date', 'Movement_getSpecificReference', 'mirror_section_title',
        'Movement_getExplanationTitleAndAnalytics', 'debit_price',
        'credit_price', 'running_total_price', 'grouping_reference',
        'grouping_date', 'getTranslatedSimulationStateTitle'])

    self.checkLineProperties(data_line_list[0],
        Movement_getSpecificReference='1',
        date=DateTime(2006, 2, 1),
        mirror_section_title='Client 1',
        Movement_getExplanationTitleAndAnalytics='Transaction 1\nref1',
        debit_price=100,
        credit_price=0,
        running_total_price=100)

    self.checkLineProperties(data_line_list[1],
        Movement_getSpecificReference='2',
        date=DateTime(2006, 2, 1, 0, 1),
        mirror_section_title='Client 1',
        Movement_getExplanationTitleAndAnalytics='Transaction 2\nref2',
        debit_price=0,
        credit_price=200,
        running_total_price=-100)

    self.checkLineProperties(data_line_list[2],
        Movement_getSpecificReference='3',
        date=DateTime(2006, 2, 2, 0, 2),
        Movement_getExplanationTitleAndAnalytics='Transaction 3\nref3',
        debit_price=300,
        credit_price=0,
        running_total_price=200)

    self.checkLineProperties(data_line_list[3],
        Movement_getSpecificReference='4',
        date=DateTime(2006, 2, 2, 0, 3),
        Movement_getExplanationTitleAndAnalytics='Transaction 4\nref4',
        debit_price=400,
        credit_price=0,
        running_total_price=600)

    self.checkLineProperties(data_line_list[4],
        Movement_getSpecificReference='5',
        date=DateTime(2006, 2, 2, 0, 4),
        Movement_getExplanationTitleAndAnalytics='Transaction 5\nref5',
        debit_price=500,
        credit_price=0,
        running_total_price=1100)

    self.checkLineProperties(data_line_list[5],
        Movement_getSpecificReference='6',
        date=DateTime(2006, 2, 2, 0, 5),
        Movement_getExplanationTitleAndAnalytics='Transaction 6\nref6',
        debit_price=600,
        credit_price=0,
        running_total_price=1700)

    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1],
        Movement_getSpecificReference=None,
        date=None,
        Movement_getExplanationTitleAndAnalytics=None,
        debit_price=1900,
        credit_price=200,
        running_total_price=None)


  def testAccountStatementFromDateSummary(self):
    # A from date summary shows balance at the beginning of the period
    self.createAccountStatementDataSet()

    # set request variables and render
    request_form = self.portal.REQUEST.form
    request_form['node'] = \
                self.portal.account_module.receivable.getRelativeUrl()
    request_form['from_date'] = DateTime(2006, 2, 2)
    request_form['at_date'] = DateTime(2006, 2, 2)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']
    request_form['hide_analytic'] = False
    request_form['export'] = False

    report_section_list = self.getReportSectionList(
                               self.portal.accounting_module,
                               'AccountModule_viewAccountStatementReport')
    self.assertEqual(1, len(report_section_list))
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    # we have 1 summary line and 4 transactions
    self.assertEqual(5, len(data_line_list))

    self.checkLineProperties(data_line_list[0],
        Movement_getSpecificReference='Previous Balance',
        date=DateTime(2006, 2, 2),
        Movement_getExplanationTitleAndAnalytics=None,
        debit_price=100,
        credit_price=200,
        running_total_price=-100)

    self.checkLineProperties(data_line_list[1],
        Movement_getSpecificReference='3',
        date=DateTime(2006, 2, 2, 0, 2),
        Movement_getExplanationTitleAndAnalytics='Transaction 3\nref3',
        debit_price=300,
        credit_price=0,
        running_total_price=200)

    self.checkLineProperties(data_line_list[2],
        Movement_getSpecificReference='4',
        date=DateTime(2006, 2, 2, 0, 3),
        Movement_getExplanationTitleAndAnalytics='Transaction 4\nref4',
        debit_price=400,
        credit_price=0,
        running_total_price=600)

    self.checkLineProperties(data_line_list[3],
        Movement_getSpecificReference='5',
        date=DateTime(2006, 2, 2, 0, 4),
        Movement_getExplanationTitleAndAnalytics='Transaction 5\nref5',
        debit_price=500,
        credit_price=0,
        running_total_price=1100)

    self.checkLineProperties(data_line_list[4],
        Movement_getSpecificReference='6',
        date=DateTime(2006, 2, 2, 0, 5),
        Movement_getExplanationTitleAndAnalytics='Transaction 6\nref6',
        debit_price=600,
        credit_price=0,
        running_total_price=1700)

    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], debit_price=1900, credit_price=200,)


  def testAccountStatementFromDateSummaryEmpty(self):
    # A from date summary shows balance at the beginning of the period, but
    # avoids showing a '0' line
    self.createAccountStatementDataSet()

    # set request variables and render
    request_form = self.portal.REQUEST.form
    request_form['node'] = \
                self.portal.account_module.receivable.getRelativeUrl()
    request_form['from_date'] = DateTime(2000, 2, 2)
    request_form['at_date'] = DateTime(2006, 2, 2)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']
    request_form['hide_analytic'] = False
    request_form['export'] = False

    report_section_list = self.getReportSectionList(
                               self.portal.accounting_module,
                               'AccountModule_viewAccountStatementReport')
    self.assertEqual(1, len(report_section_list))
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertNotEquals('Previous Balance',
          data_line_list[0].getColumnProperty('Movement_getSpecificReference'))


  def createHideGroupingDataSet(self):
    account_module = self.account_module
    # before the date
    self._makeOne(
              portal_type='Accounting Transaction',
              simulation_state='delivered',
              start_date=DateTime(2006, 1, 1),
              lines=(dict(source_value=account_module.equity,
                          source_debit=100),
                     dict(source_value=account_module.stocks,
                          source_credit=100)))

    first = self._makeOne(
              portal_type='Sale Invoice Transaction',
              title='Grouped during period',
              simulation_state='delivered',
              reference='1',
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2006, 2, 2),
              lines=(dict(source_value=account_module.receivable,
                          grouping_reference='A',
                          grouping_date=DateTime(2006, 2, 2),
                          source_debit=119.60),
                     dict(source_value=account_module.collected_vat,
                          source_credit=19.60),
                     dict(source_value=account_module.goods_sales,
                          source_credit=100.00)))

    second = self._makeOne(
              portal_type='Sale Invoice Transaction',
              title='Grouped after period',
              simulation_state='delivered',
              reference='ref2',
              source_reference='2',
              destination_section_value=self.organisation_module.client_2,
              start_date=DateTime(2006, 2, 3),
              lines=(dict(source_value=account_module.receivable,
                          grouping_reference='B',
                          grouping_date=DateTime(2006, 3, 2),
                          source_debit=239.20),
                     dict(source_value=account_module.collected_vat,
                          source_credit=39.20),
                     dict(source_value=account_module.goods_sales,
                          source_credit=200.00)))

  def testAccountStatementHideGrouping(self):
    """Simple test for hide grouping on account statement.
    """
    self.createHideGroupingDataSet()
    request_form = self.portal.REQUEST.form
    request_form['node'] = \
                self.portal.account_module.receivable.getRelativeUrl()
    request_form['at_date'] = DateTime(2006, 3, 1)
    request_form['section_category'] = 'group/demo_group/sub1'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']
    request_form['hide_analytic'] = False
    request_form['omit_grouping_reference'] = True
    request_form['export'] = False

    report_section_list = self.getReportSectionList(
                               self.portal.accounting_module,
                               'AccountModule_viewAccountStatementReport')
    self.assertEqual(1, len(report_section_list))

    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    # we have 1 transactions, because 1st is grouped during the period.
    self.assertEqual(1, len(data_line_list))

    self.checkLineProperties(data_line_list[0],
        Movement_getSpecificReference='2',
        date=DateTime(2006, 2, 3),
        Movement_getExplanationTitleAndAnalytics='Grouped after period\nref2',
        grouping_reference='B',
        grouping_date=DateTime(2006, 3, 2),
        debit_price=239.20,
        credit_price=0,
        running_total_price=239.20)

    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1],
        Movement_getSpecificReference=None,
        date=None,
        # The bottom line remain the same as when showing
        # grouped lines
        debit_price=358.80,
        credit_price=0,
        running_total_price=None)

  def testGeneralLedgerHideGrouping(self):
    # similar to testAccountStatementHideGrouping, but in general ledger.
    self.createHideGroupingDataSet()

    request_form = self.portal.REQUEST.form
    request_form['from_date'] = DateTime(2006, 1, 1)
    request_form['at_date'] = DateTime(2006, 3, 1)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']
    request_form['hide_analytic'] = False
    request_form['gap_list'] = ['my_country/my_accounting_standards/4/41']
    request_form['omit_grouping_reference'] = True
    request_form['export'] = False

    report_section_list = self.getReportSectionList(
                                    self.portal.accounting_module,
                                    'AccountModule_viewGeneralLedgerReport')
    # Except the stat, we only have one report section, because Client 1 is
    # grouped in the period.
    self.assertEqual(2, len(report_section_list))

    self.assertEqual('41 - Receivable (Client 2)',
                      report_section_list[0].getTitle())
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]

    # report layout
    self.assertEqual( ['date', 'Movement_getSpecificReference', 'mirror_section_title',
        'Movement_getExplanationTitleAndAnalytics', 'debit_price',
        'credit_price', 'running_total_price', 'grouping_reference',
        'grouping_date', 'getTranslatedSimulationStateTitle'],
        data_line_list[0].column_id_list)

    self.assertEqual(1, len(data_line_list))
    self.checkLineProperties(data_line_list[0],
          Movement_getSpecificReference='2',
          mirror_section_title='Client 2',
          Movement_getExplanationTitleAndAnalytics='Grouped after period\nref2',
          grouping_reference='B',
          grouping_date=DateTime(2006, 3, 2),
          date=DateTime(2006, 2, 3),
          debit_price=239.20, credit_price=0, running_total_price=239.20, )

    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1],
          Movement_getSpecificReference=None,
          Movement_getExplanationTitleAndAnalytics=None,
          date=None,
          debit_price=239.20, credit_price=0, )

    self.assertEqual('Total', report_section_list[1].getTitle())
    line_list = self.getListBoxLineList(report_section_list[1])
    data_line_list = [l for l in line_list if l.isDataLine()]
    # report layout
    self.assertEqual(['debit_price', 'credit_price'], data_line_list[0].column_id_list)
    self.assertEqual(1, len(data_line_list))

    # The bottom line remain the same as when showing grouped lines
    self.checkLineProperties(data_line_list[0], debit_price=358.80, credit_price=0)


  def testAccountStatementFromDateDetailedSummary(self):
    # Detailed from date summary shows all lines corresponding to the balance
    # at the beginning of the period.
    # For this it relies on grouping reference property.

    # create documents
    account_module = self.account_module
    bank = self.section.newContent(portal_type='Bank Account', title='Bank')
    bank.validate()
    # before
    # this one will not have grouping reference
    t1 = self._makeOne(
              portal_type='Accounting Transaction',
              title='Transaction 1',
              reference='ref1',
              source_reference='1',
              simulation_state='delivered',
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2006, 2, 1),
              lines=(dict(source_value=account_module.receivable,
                          source_debit=100.0),
                     dict(source_value=account_module.payable,
                          source_credit=100.0)))

    t2 = self._makeOne(
              portal_type='Sale Invoice Transaction',
              title='Transaction 2',
              reference='ref2',
              source_reference='2',
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2006, 2, 2),
              lines=(dict(source_value=account_module.receivable,
                          grouping_reference='A',
                          source_debit=200.0),
                     dict(source_value=account_module.payable,
                          source_credit=200.0)))

    # payment related to t2 invoice
    t3 = self._makeOne(
              portal_type='Payment Transaction',
              title='Transaction 3',
              reference='ref3',
              source_reference='3',
              simulation_state='delivered',
              causality_value=t2,
              payment_mode='payment_mode',
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2006, 2, 3),
              lines=(dict(source_value=account_module.bank,
                          source_debit=200.0),
                     dict(source_value=account_module.receivable,
                          grouping_reference='A',
                          source_credit=200.0)))
    # we validate t2 later, otherwise grouping reference will be cleaned up
    t2.stop()
    t2.deliver()

    # Another invoice, grouped with a payment transaction in the period
    t4 = self._makeOne(
              portal_type='Sale Invoice Transaction',
              title='Transaction 4',
              reference='ref4',
              source_reference='4',
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2006, 2, 4),
              lines=(dict(source_value=account_module.receivable,
                          grouping_reference='B',
                          grouping_date=DateTime(2006, 3, 1),
                          source_debit=400.0),
                     dict(source_value=account_module.payable,
                          source_credit=400.0)))
    t5 = self._makeOne(
              portal_type='Payment Transaction',
              title='Transaction 5',
              reference='ref5',
              source_reference='5',
              simulation_state='delivered',
              causality_value=t4,
              payment_mode='payment_mode',
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2006, 3, 1),
              lines=(dict(source_value=account_module.bank,
                          source_debit=400.0),
                     dict(source_value=account_module.receivable,
                          grouping_reference='B',
                          grouping_date=DateTime(2006, 3, 1),
                          source_credit=400.0)))
    t4.stop()
    t4.deliver()
    self.tic()

    # set request variables and render
    request_form = self.portal.REQUEST.form
    request_form['node'] = \
                self.portal.account_module.receivable.getRelativeUrl()
    request_form['from_date'] = DateTime(2006, 2, 25)
    request_form['at_date'] = DateTime(2006, 6, 1)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']
    request_form['detailed_from_date_summary'] = 1
    request_form['hide_analytic'] = False
    request_form['export'] = False

    report_section_list = self.getReportSectionList(
                               self.portal.accounting_module,
                               'AccountModule_viewAccountStatementReport')
    # the report has 4 sections,
    self.assertEqual(4, len(report_section_list))
    # but 2 of them are only titles
    report_section_list = [r for r in report_section_list if r.form_id]
    self.assertEqual(2, len(report_section_list))

    # the first section contains explanation of non grouped lines before the
    # period
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    # We only have lines for the transaction 1 which is not grouped, and for
    # transaction 4, which is grouped with lines in the period.
    self.assertEqual(2, len(data_line_list))
    self.checkLineProperties(data_line_list[0],
        Movement_getSpecificReference='1',
        date=DateTime(2006, 2, 1),
        Movement_getExplanationTitleAndAnalytics='Transaction 1\nref1',
        debit_price=100,
        credit_price=0,)
    self.checkLineProperties(data_line_list[1],
        Movement_getSpecificReference='4',
        date=DateTime(2006, 2, 4),
        Movement_getExplanationTitleAndAnalytics='Transaction 4\nref4',
        debit_price=400,
        credit_price=0,)
    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], debit_price=500, credit_price=0)

    # Second section is for previous balance summary and lines in the period,
    # ie only transaction 5
    line_list = self.getListBoxLineList(report_section_list[1])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(2, len(data_line_list))
    self.checkLineProperties(data_line_list[0],
        Movement_getSpecificReference='Previous Balance',
        date=DateTime(2006, 2, 25),
        running_total_price=500,
        debit_price=700,
        credit_price=200,)
    self.checkLineProperties(data_line_list[1],
        Movement_getSpecificReference='5',
        date=DateTime(2006, 3, 1),
        Movement_getExplanationTitleAndAnalytics='Transaction 5\nref5',
        running_total_price=100,
        debit_price=0,
        credit_price=400,)
    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], debit_price=700, credit_price=600)


  def _createAccountStatementGroupedAtFromDateDataSet(self):
    # create data set where the first transaction is grouped with another
    # transaction on 2006/02/25, but with hour:minutes, which use to cause some
    # bugs with the "non grouped lines from previous period" in the account
    # statement.
    account_module = self.account_module
    bank = self.section.newContent(portal_type='Bank Account', title='Bank')
    bank.validate()
    # before
    # this one will not have grouping reference
    t1 = self._makeOne(
              portal_type='Accounting Transaction',
              title='Transaction 1',
              reference='ref1',
              source_reference='1',
              simulation_state='delivered',
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2006, 2, 1),
              lines=(dict(source_value=account_module.receivable,
                          source_debit=100.0),
                     dict(source_value=account_module.payable,
                          source_credit=100.0)))

    # This one will be grouped exactly at from_date
    t2 = self._makeOne(
              portal_type='Sale Invoice Transaction',
              title='Transaction 2',
              reference='ref2',
              source_reference='2',
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2006, 2, 2),
              lines=(dict(source_value=account_module.receivable,
                          grouping_reference='A',
                          grouping_date=DateTime(2006, 2, 25, 2, 3),
                          source_debit=200.0),
                     dict(source_value=account_module.payable,
                          source_credit=200.0)))

    # payment related to t2 invoice
    t3 = self._makeOne(
              portal_type='Payment Transaction',
              title='Transaction 3',
              reference='ref3',
              source_reference='3',
              simulation_state='delivered',
              causality_value=t2,
              payment_mode='payment_mode',
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2006, 2, 25, 2, 3),
              lines=(dict(source_value=account_module.bank,
                          source_debit=200.0),
                     dict(source_value=account_module.receivable,
                          grouping_reference='A',
                          grouping_date=DateTime(2006, 2, 25, 2, 3),
                          source_credit=200.0)))
    # we validate t2 later, otherwise grouping reference will be cleaned up
    t2.stop()
    t2.deliver()

    # Another invoice in the period
    t4 = self._makeOne(
              portal_type='Sale Invoice Transaction',
              title='Transaction 4',
              reference='ref4',
              source_reference='4',
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2006, 3, 1),
              lines=(dict(source_value=account_module.receivable,
                          source_debit=400.0),
                     dict(source_value=account_module.payable,
                          source_credit=400.0)))
    t4.stop()
    t4.deliver()
    self.tic()


  def testAccountStatementFromDateDetailedSummaryGroupedAtFromDate(self):
    # at the exact date of the grouped transaction
    self._createAccountStatementGroupedAtFromDateDataSet()

    # set request variables and render
    request_form = self.portal.REQUEST.form
    request_form['node'] = \
                self.portal.account_module.receivable.getRelativeUrl()
    request_form['from_date'] = DateTime(2006, 2, 25)
    request_form['at_date'] = DateTime(2006, 6, 1)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']
    request_form['detailed_from_date_summary'] = 1
    request_form['hide_analytic'] = False
    request_form['export'] = False

    report_section_list = self.getReportSectionList(
                               self.portal.accounting_module,
                               'AccountModule_viewAccountStatementReport')
    # the report has 4 sections,
    self.assertEqual(4, len(report_section_list))
    # but 2 of them are only titles
    report_section_list = [r for r in report_section_list if r.form_id]
    self.assertEqual(2, len(report_section_list))

    # the first section contains explanation of non grouped lines before the
    # period
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    # We only have line for transactions 1 and 2 which are not grouped
    self.assertEqual(2, len(data_line_list))
    self.checkLineProperties(data_line_list[0],
        Movement_getSpecificReference='1',
        date=DateTime(2006, 2, 1),
        Movement_getExplanationTitleAndAnalytics='Transaction 1\nref1',
        debit_price=100,
        credit_price=0,)
    self.checkLineProperties(data_line_list[1],
        Movement_getSpecificReference='2',
        date=DateTime(2006, 2, 2),
        Movement_getExplanationTitleAndAnalytics='Transaction 2\nref2',
        debit_price=200,
        credit_price=0,)
    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], debit_price=300, credit_price=0)

    # Second section is for previous balance summary and lines in the period,
    # transaction 3 and transaction 4
    line_list = self.getListBoxLineList(report_section_list[1])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(3, len(data_line_list))
    self.checkLineProperties(data_line_list[0],
        Movement_getSpecificReference='Previous Balance',
        date=DateTime(2006, 2, 25),
        Movement_getExplanationTitleAndAnalytics=None,
        running_total_price=300,
        debit_price=300,
        credit_price=0,)
    self.checkLineProperties(data_line_list[1],
        Movement_getSpecificReference='3',
        date=DateTime(2006, 2, 25, 2, 3),
        Movement_getExplanationTitleAndAnalytics='Transaction 3\nref3',
        running_total_price=100,
        debit_price=0,
        credit_price=200,)
    self.checkLineProperties(data_line_list[2],
        Movement_getSpecificReference='4',
        date=DateTime(2006, 3, 1),
        Movement_getExplanationTitleAndAnalytics='Transaction 4\nref4',
        running_total_price=500,
        debit_price=400,
        credit_price=0,)
    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], debit_price=700, credit_price=200)

  def testAccountStatementFromDateDetailedSummaryGroupedAtFromDateCase2(self):
    # The day after the date of the grouped transaction
    self._createAccountStatementGroupedAtFromDateDataSet()

    # set request variables and render
    request_form = self.portal.REQUEST.form
    request_form['node'] = \
                self.portal.account_module.receivable.getRelativeUrl()
    request_form['from_date'] = DateTime(2006, 2, 26)
    request_form['at_date'] = DateTime(2006, 6, 1)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']
    request_form['detailed_from_date_summary'] = 1
    request_form['hide_analytic'] = False
    request_form['export'] = False

    report_section_list = self.getReportSectionList(
                               self.portal.accounting_module,
                               'AccountModule_viewAccountStatementReport')
    # the report has 4 sections,
    self.assertEqual(4, len(report_section_list))
    # but 2 of them are only titles
    report_section_list = [r for r in report_section_list if r.form_id]
    self.assertEqual(2, len(report_section_list))

    # the first section contains explanation of non grouped lines before the
    # period
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    # We only have line for transaction 1 which are not grouped
    self.assertEqual(1, len(data_line_list))
    self.checkLineProperties(data_line_list[0],
        Movement_getSpecificReference='1',
        date=DateTime(2006, 2, 1),
        Movement_getExplanationTitleAndAnalytics='Transaction 1\nref1',
        debit_price=100,
        credit_price=0,)
    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], debit_price=100, credit_price=0)

    # Second section is for previous balance summary and lines in the period,
    # transaction 4
    line_list = self.getListBoxLineList(report_section_list[1])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(2, len(data_line_list))
    self.checkLineProperties(data_line_list[0],
        Movement_getSpecificReference='Previous Balance',
        date=DateTime(2006, 2, 26),
        running_total_price=100,
        debit_price=300,
        credit_price=200,)
    self.checkLineProperties(data_line_list[1],
        Movement_getSpecificReference='4',
        date=DateTime(2006, 3, 1),
        Movement_getExplanationTitleAndAnalytics='Transaction 4\nref4',
        running_total_price=500,
        debit_price=400,
        credit_price=0,)
    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], debit_price=700, credit_price=200)

  def testAccountStatementFromDateDetailedSummaryZeroTransaction(self):
    # Edge case regression #20170911-1AD62FB
    t0 = self._makeOne(
        portal_type='Accounting Transaction',
        title='Transaction 0',
        reference='ref0',
        source_reference='0',
        simulation_state='planned',
        destination_section_value=self.organisation_module.client_1,
        start_date=DateTime(2006, 1, 31),
        lines=(dict(source_value=self.portal.account_module.receivable,
                    id='receivable_line',
                    source_debit=0),
               dict(source_value=self.portal.account_module.payable,
                    source_credit=0)))
    self.assertFalse(t0.receivable_line.hasGroupingReference())
    self._createAccountStatementGroupedAtFromDateDataSet()

    # set request variables and render
    request_form = self.portal.REQUEST.form
    request_form['node'] = \
                self.portal.account_module.receivable.getRelativeUrl()
    request_form['from_date'] = DateTime(2006, 2, 26)
    request_form['at_date'] = DateTime(2006, 6, 1)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered', 'planned']
    request_form['detailed_from_date_summary'] = 1
    request_form['hide_analytic'] = False
    request_form['export'] = False

    report_section_list = self.getReportSectionList(
        self.portal.accounting_module,
        'AccountModule_viewAccountStatementReport')
    self.assertEqual(4, len(report_section_list))
    report_section_list = [r for r in report_section_list if r.form_id]
    self.assertEqual(2, len(report_section_list))

    # the first section contains explanation of non grouped lines before the
    # period
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    # We have lines for transaction 0 and 1 which are not grouped
    self.assertEqual(2, len(data_line_list))
    self.checkLineProperties(data_line_list[0],
                             Movement_getSpecificReference='0',
                             date=DateTime(2006, 1, 31),
                             Movement_getExplanationTitleAndAnalytics='Transaction 0\nref0',
                             debit_price=0,
                             credit_price=0,)
    self.checkLineProperties(data_line_list[1],
                             Movement_getSpecificReference='1',
                             date=DateTime(2006, 2, 1),
                             Movement_getExplanationTitleAndAnalytics='Transaction 1\nref1',
                             debit_price=100,
                             credit_price=0,)
    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], debit_price=100, credit_price=0)

  def testAccountStatementPeriodDateForExpenseAccounts(self):
    # Account statement for expense or income account will not show
    # transactions from previous periods.
    self.createAccountStatementDataSetOnTwoPeriods()

    # set request variables and render
    request_form = self.portal.REQUEST.form
    request_form['node'] = \
                self.portal.account_module.goods_sales.getRelativeUrl()
    request_form['from_date'] = DateTime(2006, 1, 1)
    request_form['at_date'] = DateTime(2006, 2, 2)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']
    request_form['hide_analytic'] = False
    request_form['export'] = False

    report_section_list = self.getReportSectionList(
                               self.portal.accounting_module,
                               'AccountModule_viewAccountStatementReport')
    self.assertEqual(1, len(report_section_list))

    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    # we have 3 transactions, but only 2 are in the period
    self.assertEqual(2, len(data_line_list))

    self.checkLineProperties(data_line_list[0],
        Movement_getSpecificReference='2',
        date=DateTime(2006, 1, 1),
        Movement_getExplanationTitleAndAnalytics='Transaction 2\nref2',
        debit_price=0,
        credit_price=200,
        running_total_price=-200)

    self.checkLineProperties(data_line_list[1],
        Movement_getSpecificReference='3',
        date=DateTime(2006, 2, 2),
        Movement_getExplanationTitleAndAnalytics='Transaction 3\nref3',
        debit_price=0,
        credit_price=300,
        running_total_price=-500)

    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], debit_price=0, credit_price=500)


  def testAccountStatementPeriodDateAndInitialBalanceForStdAccounts(self):
    # Initial balance in Account Statement for standard account: the initial
    # balance is the balance at the beginning of the period + movements in the
    # period.

    self.createAccountStatementDataSetOnTwoPeriods()

    t1b = self._makeOne(
              portal_type='Sale Invoice Transaction',
              title='Transaction 1b',
              reference='ref1b',
              source_reference='1b',
              simulation_state='delivered',
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2006, 1, 2),
              lines=(dict(source_value=self.account_module.goods_sales,
                          source_debit=21.0),
                     dict(source_value=self.account_module.receivable,
                          source_credit=21.0)))


    # set request variables and render
    request_form = self.portal.REQUEST.form
    request_form['node'] = \
                self.portal.account_module.receivable.getRelativeUrl()
    request_form['from_date'] = DateTime(2006, 2, 2)
    request_form['at_date'] = DateTime(2006, 2, 2)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']
    request_form['hide_analytic'] = False
    request_form['export'] = False

    report_section_list = self.getReportSectionList(
                               self.portal.accounting_module,
                               'AccountModule_viewAccountStatementReport')
    self.assertEqual(1, len(report_section_list))

    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(2, len(data_line_list))
    self.checkLineProperties(data_line_list[0],
        Movement_getSpecificReference='Previous Balance',
        date=DateTime(2006, 2, 2),
        section_title='My Organisation',
        Movement_getExplanationTitleAndAnalytics=None,
        grouping_date=None,
        grouping_reference=None,
        debit_price=300,
        credit_price=21,
        running_total_price=279)

    self.checkLineProperties(data_line_list[1],
        Movement_getSpecificReference='3',
        date=DateTime(2006, 2, 2),
        Movement_getExplanationTitleAndAnalytics='Transaction 3\nref3',
        debit_price=300,
        credit_price=0,
        running_total_price=579)

    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], debit_price=600, credit_price=21)

  def testAccountStatementPeriodDateEqualsFromDate(self):
    # Initial balance in Account Statement for standard account: the initial
    # balance is the balance at the beginning of the period + movements in the
    # period.
    # This is for the special case whe the period start date is equals to the
    # start date

    self.createAccountStatementDataSetOnTwoPeriods()

    t1b = self._makeOne(
              portal_type='Sale Invoice Transaction',
              title='Transaction 1b',
              reference='ref1b',
              source_reference='1b',
              simulation_state='delivered',
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2005, 12, 13),
              lines=(dict(source_value=self.account_module.goods_sales,
                          source_debit=21.0),
                     dict(source_value=self.account_module.receivable,
                          source_credit=21.0)))

    # set request variables and render
    request_form = self.portal.REQUEST.form
    request_form['node'] = \
                self.portal.account_module.receivable.getRelativeUrl()
    request_form['from_date'] = DateTime(2006, 1, 1)
    request_form['at_date'] = DateTime(2006, 2, 2)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']
    request_form['hide_analytic'] = False
    request_form['export'] = False

    report_section_list = self.getReportSectionList(
                               self.portal.accounting_module,
                               'AccountModule_viewAccountStatementReport')
    self.assertEqual(1, len(report_section_list))

    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(3, len(data_line_list))

    self.checkLineProperties(data_line_list[0],
        Movement_getSpecificReference='Previous Balance',
        date=DateTime(2006, 1, 1),
        Movement_getExplanationTitleAndAnalytics=None,
        debit_price=79,
        credit_price=0,
        running_total_price=79)

    self.checkLineProperties(data_line_list[1],
        Movement_getSpecificReference='2',
        date=DateTime(2006, 1, 1),
        Movement_getExplanationTitleAndAnalytics='Transaction 2\nref2',
        debit_price=200,
        credit_price=0,
        running_total_price=279)

    self.checkLineProperties(data_line_list[2],
        Movement_getSpecificReference='3',
        date=DateTime(2006, 2, 2),
        Movement_getExplanationTitleAndAnalytics='Transaction 3\nref3',
        debit_price=300,
        credit_price=0,
        running_total_price=579)

    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], debit_price=579, credit_price=0)


  def testAccountStatementPeriodDateAndInitialBalanceForExpenseAccounts(self):
    # Account statement for expense or income account will not show
    # transactions from previous periods (also for the Initial Balance line)
    self.createAccountStatementDataSetOnTwoPeriods()

    # set request variables and render
    request_form = self.portal.REQUEST.form
    request_form['node'] = \
                self.portal.account_module.goods_sales.getRelativeUrl()
    request_form['from_date'] = DateTime(2006, 2, 2)
    request_form['at_date'] = DateTime(2006, 2, 2)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']
    request_form['hide_analytic'] = False
    request_form['export'] = False

    report_section_list = self.getReportSectionList(
                               self.portal.accounting_module,
                               'AccountModule_viewAccountStatementReport')
    self.assertEqual(1, len(report_section_list))

    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(2, len(data_line_list))
    self.checkLineProperties(data_line_list[0],
        Movement_getSpecificReference='Previous Balance',
        date=DateTime(2006, 2, 2),
        debit_price=0,
        credit_price=200,
        running_total_price=-200)

    self.checkLineProperties(data_line_list[1],
        Movement_getSpecificReference='3',
        date=DateTime(2006, 2, 2),
        Movement_getExplanationTitleAndAnalytics='Transaction 3\nref3',
        debit_price=0,
        credit_price=300,
        running_total_price=-500)

    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], debit_price=0, credit_price=500)


  def testAccountStatementOverMultiplePeriodsForExpenseAccounts(self):
    # Account statement for expense or income account can be used over multiple
    # periods
    self.createAccountStatementDataSetOnTwoPeriods()

    # set request variables and render
    request_form = self.portal.REQUEST.form
    request_form['node'] = \
                self.portal.account_module.goods_sales.getRelativeUrl()
    request_form['from_date'] = DateTime(2005, 2, 2)
    request_form['at_date'] = DateTime(2006, 2, 2)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']
    request_form['hide_analytic'] = False
    request_form['export'] = False

    report_section_list = self.getReportSectionList(
                               self.portal.accounting_module,
                               'AccountModule_viewAccountStatementReport')
    self.assertEqual(1, len(report_section_list))

    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(3, len(data_line_list))
    self.checkLineProperties(data_line_list[0],
        Movement_getSpecificReference='1',
        date=DateTime(2005, 12, 31),
        Movement_getExplanationTitleAndAnalytics='Transaction 1\nref1',
        debit_price=0,
        credit_price=100,
        running_total_price=-100)

    self.checkLineProperties(data_line_list[1],
        Movement_getSpecificReference='2',
        date=DateTime(2006, 1, 1),
        Movement_getExplanationTitleAndAnalytics='Transaction 2\nref2',
        debit_price=0,
        credit_price=200,
        running_total_price=-300)

    self.checkLineProperties(data_line_list[2],
        Movement_getSpecificReference='3',
        date=DateTime(2006, 2, 2),
        Movement_getExplanationTitleAndAnalytics='Transaction 3\nref3',
        debit_price=0,
        credit_price=300,
        running_total_price=-600)

    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], debit_price=0, credit_price=600)


  def testAccountStatementMirrorSection(self):
    # 'Mirror Section' parameter is taken into account.
    self.createAccountStatementDataSet()

    # set request variables and render
    request_form = self.portal.REQUEST.form
    request_form['node'] = \
                self.portal.account_module.receivable.getRelativeUrl()
    request_form['mirror_section'] = \
                self.portal.organisation_module.client_2.getRelativeUrl()
    request_form['from_date'] = DateTime(2006, 2, 2)
    request_form['at_date'] = DateTime(2006, 2, 2)
    request_form['section_category'] = 'group/demo_group/sub1'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']
    request_form['hide_analytic'] = False
    request_form['export'] = False

    report_section_list = self.getReportSectionList(
                                    self.portal.accounting_module,
                                    'AccountModule_viewAccountStatementReport')
    self.assertEqual(1, len(report_section_list))
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(1, len(data_line_list))

    line = data_line_list[0]
    self.checkLineProperties(data_line_list[0],
        Movement_getSpecificReference='4',
        date=DateTime(2006, 2, 2, 0, 3),
        Movement_getExplanationTitleAndAnalytics='Transaction 4\nref4',
        debit_price=400,
        credit_price=0,
        running_total_price=400)

    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], debit_price=400, credit_price=0)


  def testAccountStatementSimulationState(self):
    # Simulation State parameter is taken into account.
    self.createAccountStatementDataSet()

    # set request variables and render
    request_form = self.portal.REQUEST.form
    request_form['node'] = \
                  self.portal.account_module.receivable.getRelativeUrl()
    request_form['at_date'] = DateTime(2006, 2, 2)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['stopped', 'confirmed']
    request_form['hide_analytic'] = False
    request_form['export'] = False

    report_section_list = self.getReportSectionList(
                                    self.portal.accounting_module,
                                    'AccountModule_viewAccountStatementReport')
    self.assertEqual(1, len(report_section_list))
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(1, len(data_line_list))

    self.checkLineProperties(data_line_list[0],
        Movement_getSpecificReference='7',
        date=DateTime(2006, 2, 2, 0, 6),
        Movement_getExplanationTitleAndAnalytics='Transaction 7\nref7',
        debit_price=700,
        credit_price=0,
        running_total_price=700)

    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], debit_price=700, credit_price=0)


  def testAccountStatementCancellationAmount(self):
    # Account statement with cancellation amount set on lines
    account_module = self.account_module
    t1 = self._makeOne(
              portal_type='Accounting Transaction',
              title='Transaction 1',
              source_reference='1',
              simulation_state='delivered',
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2006, 2, 1, 0, 1),
              lines=(dict(source_value=account_module.payable,
                          source_debit=100.0,),
                     dict(source_value=account_module.receivable,
                          source_debit=-100.0,
                          cancellation_amount=True)))

    t2 = self._makeOne(
              portal_type='Accounting Transaction',
              title='Transaction 2',
              source_reference='2',
              simulation_state='delivered',
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2006, 2, 1, 0, 2),
              lines=(dict(source_value=account_module.payable,
                          source_credit=200.0),
                     dict(source_value=account_module.receivable,
                          source_credit=-200.0,
                          cancellation_amount=True)))

    # set request variables and render
    request_form = self.portal.REQUEST.form
    request_form['node'] = \
                self.portal.account_module.receivable.getRelativeUrl()
    request_form['from_date'] = DateTime(2006, 1, 1)
    request_form['at_date'] = DateTime(2006, 12, 31)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']
    request_form['hide_analytic'] = False
    request_form['export'] = False

    report_section_list = self.getReportSectionList(
                               self.portal.accounting_module,
                               'AccountModule_viewAccountStatementReport')
    self.assertEqual(1, len(report_section_list))
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(2, len(data_line_list))

    self.checkLineProperties(data_line_list[0],
        Movement_getSpecificReference='1',
        date=DateTime(2006, 2, 1, 0, 1),
        debit_price=-100,
        credit_price=0,
        running_total_price=-100)

    self.checkLineProperties(data_line_list[1],
        Movement_getSpecificReference='2',
        date=DateTime(2006, 2, 1, 0, 2),
        debit_price=0,
        credit_price=-200,
        running_total_price=100)

    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], debit_price=-100, credit_price=-200,)


  def testAccountStatementSameSectionSameNode(self):
    # Account statement with a movement on the same section and the same node
    account_module = self.account_module
    t1 = self._makeOne(
              portal_type='Accounting Transaction',
              title='Transaction 1',
              source_reference='Source Reference',
              destination_reference='Destination Reference',
              simulation_state='delivered',
              source_section_value=self.section,
              destination_section_value=self.section,
              start_date=DateTime(2006, 2, 1),
              lines=(dict(source_value=account_module.payable,
                          destination_value=account_module.payable,
                          source_debit=100.0,),
                     dict(source_value=account_module.receivable,
                          destination_value=account_module.receivable,
                          source_credit=100.0,)))

    # set request variables and render
    request_form = self.portal.REQUEST.form
    request_form['node'] = \
                self.portal.account_module.receivable.getRelativeUrl()
    request_form['from_date'] = DateTime(2006, 1, 1)
    request_form['at_date'] = DateTime(2006, 12, 31)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']
    request_form['hide_analytic'] = False
    request_form['export'] = False

    report_section_list = self.getReportSectionList(
                               self.portal.accounting_module,
                               'AccountModule_viewAccountStatementReport')
    self.assertEqual(1, len(report_section_list))
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(2, len(data_line_list))
    self.assertEqual(
        {line.getColumnProperty('Movement_getSpecificReference')
         for line in data_line_list},
        {'Source Reference', 'Destination Reference'})

    for line in data_line_list:
      if line.getColumnProperty('Movement_getSpecificReference')\
              == 'Source Reference':
        self.checkLineProperties(line,
                                 Movement_getSpecificReference='Source Reference',
                                 date=DateTime(2006, 2, 1),
                                 debit_price=0,
                                 credit_price=100,)
      else:
        self.checkLineProperties(line,
                                 Movement_getSpecificReference='Destination Reference',
                                 date=DateTime(2006, 2, 1),
                                 debit_price=100,
                                 credit_price=0,)

    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], debit_price=100, credit_price=100)


  def testAccountStatementMultipleSection(self):
    # When there are multiple sections for the same group, an extra column
    # is added for the section
    account_module = self.portal.account_module
    t1 = self._makeOne(
              portal_type='Accounting Transaction',
              title='Transaction 1',
              reference='ref1',
              source_reference='1',
              simulation_state='delivered',
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2006, 2, 1),
              lines=(dict(source_value=account_module.receivable,
                          source_debit=100.0),
                     dict(source_value=account_module.payable,
                          source_credit=100.0)))

    t2 = self._makeOne(
              portal_type='Accounting Transaction',
              title='Transaction 2',
              reference='ref2',
              source_reference='2',
              source_section_value=self.main_section,
              simulation_state='delivered',
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2006, 2, 1, 0, 1),
              lines=(dict(source_value=account_module.payable,
                          source_debit=200.0),
                     dict(source_value=account_module.receivable,
                          source_credit=200.0)))

    # set request variables and render
    request_form = self.portal.REQUEST.form
    request_form['node'] = \
                self.portal.account_module.receivable.getRelativeUrl()
    request_form['at_date'] = DateTime(2006, 2, 2)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']
    request_form['hide_analytic'] = False
    request_form['export'] = False

    report_section_list = self.getReportSectionList(
                                    self.portal.accounting_module,
                                    'AccountModule_viewAccountStatementReport')
    self.assertEqual(1, len(report_section_list))
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(2, len(data_line_list))

    self.checkLineProperties(data_line_list[0],
         Movement_getSpecificReference='1',
         date=DateTime(2006, 2, 1),
         section_title='My Organisation',
         Movement_getExplanationTitleAndAnalytics='Transaction 1\nref1',
         debit_price=100,
         credit_price=0,
         running_total_price=100)

    self.checkLineProperties(data_line_list[1],
        Movement_getSpecificReference='2',
        date=DateTime(2006, 2, 1, 0, 1),
        section_title='My Master Organisation',
        Movement_getExplanationTitleAndAnalytics='Transaction 2\nref2',
        debit_price=0,
        credit_price=200,
        running_total_price=-100)

    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], debit_price=100, credit_price=200)

  def testAccountStatementProject(self):
    # test account statement to a project
    self.createProjectAndFunctionDataSet()

    request_form = self.portal.REQUEST.form
    request_form['node'] = \
                self.portal.account_module.receivable.getRelativeUrl()
    request_form['from_date'] = DateTime(2006, 1, 1)
    request_form['at_date'] = DateTime(2006, 12, 31)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']
    request_form['project'] = self.project_1.getRelativeUrl()
    request_form['hide_analytic'] = False
    request_form['export'] = False

    report_section_list = self.getReportSectionList(
                                    self.portal.accounting_module,
                                    'AccountModule_viewAccountStatementReport')
    self.assertEqual(1, len(report_section_list))

    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(1, len(data_line_list))
    self.checkLineProperties(data_line_list[0],
          Movement_getSpecificReference='1',
          Movement_getExplanationTitleAndAnalytics=
            'Function a Project 1\nFaP1',
          date=DateTime(2006, 2, 2),
          debit_price=500, credit_price=0, running_total_price=500, )
    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], debit_price=500, credit_price=0)


  def testAccountStatementNoProject(self):
    # test account statement to no project
    self.createProjectAndFunctionDataSet()

    request_form = self.portal.REQUEST.form
    request_form['node'] = \
                self.portal.account_module.receivable.getRelativeUrl()
    request_form['from_date'] = DateTime(2006, 1, 1)
    request_form['at_date'] = DateTime(2006, 12, 31)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']
    request_form['project'] = 'None'
    request_form['hide_analytic'] = False
    request_form['export'] = False

    report_section_list = self.getReportSectionList(
                                    self.portal.accounting_module,
                                    'AccountModule_viewAccountStatementReport')
    self.assertEqual(1, len(report_section_list))

    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(1, len(data_line_list))
    self.checkLineProperties(data_line_list[0],
          Movement_getSpecificReference='3',
          Movement_getExplanationTitleAndAnalytics=
            'No function no project\nnono',
          date=DateTime(2006, 2, 2),
          debit_price=700, credit_price=0, running_total_price=700, )
    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], debit_price=700, credit_price=0)


  def testAccountStatementLedger(self):
    # test account statement on a ledger
    self.createLedgerDataSet()

    request_form = self.portal.REQUEST.form
    request_form['node'] = \
                self.portal.account_module.receivable.getRelativeUrl()
    request_form['from_date'] = DateTime(2006, 1, 1)
    request_form['at_date'] = DateTime(2006, 12, 31)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']
    request_form['ledger'] = 'ledger/accounting/general'
    request_form['hide_analytic'] = False
    request_form['export'] = False

    report_section_list = self.getReportSectionList(
                                    self.portal.accounting_module,
                                    'AccountModule_viewAccountStatementReport')
    self.assertEqual(1, len(report_section_list))

    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(1, len(data_line_list))
    self.checkLineProperties(data_line_list[0],
          Movement_getExplanationTitleAndAnalytics=
            'Ledger general\nlag',
          date=DateTime(2006, 2, 2),
          debit_price=500, credit_price=0, running_total_price=500, )
    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], debit_price=500, credit_price=0)


  def testTrialBalance(self):
    # Simple test of trial balance
    # we will use the same data set as account statement
    self.createAccountStatementDataSet(use_two_bank_accounts=0)

    # set request variables and render
    request_form = self.portal.REQUEST.form
    request_form['from_date'] = DateTime(2006, 1, 1)
    request_form['at_date'] = DateTime(2006, 12, 31)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['stopped', 'delivered']
    request_form['show_empty_accounts'] = 1
    request_form['expand_accounts'] = 0
    request_form['per_account_class_summary'] = 0
    request_form['show_detailed_balance_columns'] = 1

    report_section_list = self.getReportSectionList(
                                    self.portal.accounting_module,
                                    'AccountModule_viewTrialBalanceReport')
    self.assertEqual(1, len(report_section_list))
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]

    # currency is present in the report
    self.assertEqual('currency_module/euro', self.portal.
        AccountModule_viewTrialBalanceReport.your_currency.get_value('default'))

    # all accounts are present
    self.assertEqual(
          len(self.portal.account_module.contentValues(portal_type='Account')),
          len(data_line_list))

    self.assertEqual(['node_id', 'node_title',
           'initial_debit_balance', 'initial_credit_balance',
           'initial_balance', 'debit', 'credit', 'final_debit_balance',
           'final_credit_balance', 'final_balance', 'final_balance_if_debit',
           'final_balance_if_credit'],
           data_line_list[0].column_id_list)

    # account are sorted by GAP Id
    self.checkLineProperties(data_line_list[0], node_id='1',
        node_title='Equity', initial_debit_balance=0, initial_credit_balance=0,
        initial_balance=0, debit=0, credit=0, final_debit_balance=0,
        final_credit_balance=0, final_balance=0, final_balance_if_debit=0,
        final_balance_if_credit=0)

    self.checkLineProperties(data_line_list[1], node_id='2',
        node_title='Fixed Assets', initial_debit_balance=0,
        initial_credit_balance=0, initial_balance=0, debit=0, credit=0,
        final_debit_balance=0, final_credit_balance=0, final_balance=0,
        final_balance_if_debit=0, final_balance_if_credit=0)

    self.checkLineProperties(data_line_list[2], node_id='3',
        node_title='Stocks', initial_debit_balance=0, initial_credit_balance=0,
        initial_balance=0, debit=0, credit=0, final_debit_balance=0,
        final_credit_balance=0, final_balance=0, final_balance_if_debit=0,
        final_balance_if_credit=0)

    self.checkLineProperties(data_line_list[3], node_id='40',
        node_title='Payable', initial_debit_balance=0,
        initial_credit_balance=0, initial_balance=0, debit=200, credit=100,
        final_debit_balance=200, final_credit_balance=100, final_balance=100,
        final_balance_if_debit=100, final_balance_if_credit=0,)

    self.checkLineProperties(data_line_list[4], node_id='41',
        node_title='Receivable', initial_debit_balance=0,
        initial_credit_balance=0, initial_balance=0, debit=3400, credit=200,
        final_debit_balance=3400, final_credit_balance=200, final_balance=3200,
        final_balance_if_debit=3200, final_balance_if_credit=0,)

    self.checkLineProperties(data_line_list[5], node_id='4456',
        node_title='Refundable VAT 10%', initial_debit_balance=0,
        initial_credit_balance=0, initial_balance=0, debit=0, credit=0,
        final_debit_balance=0, final_credit_balance=0, final_balance=0,
        final_balance_if_debit=0, final_balance_if_credit=0)

    self.checkLineProperties(data_line_list[6], node_id='4457',
        node_title='Collected VAT 10%', initial_debit_balance=0,
        initial_credit_balance=0, initial_balance=0, debit=0, credit=0,
        final_debit_balance=0, final_credit_balance=0, final_balance=0,
        final_balance_if_debit=0, final_balance_if_credit=0)

    self.checkLineProperties(data_line_list[7], node_id='5',
        node_title='Bank (Bank1)', initial_debit_balance=0,
        initial_credit_balance=0, initial_balance=0, debit=0, credit=3300,
        final_debit_balance=0, final_credit_balance=3300, final_balance=-3300,
        final_balance_if_debit=0, final_balance_if_credit=3300,)

    self.checkLineProperties(data_line_list[8], node_id='6',
        node_title='Goods Purchase', initial_debit_balance=0,
        initial_credit_balance=0, initial_balance=0, debit=0, credit=0,
        final_debit_balance=0, final_credit_balance=0, final_balance=0,
        final_balance_if_debit=0, final_balance_if_credit=0)

    self.checkLineProperties(data_line_list[9], node_id='7',
        node_title='Goods Sales', initial_debit_balance=0,
        initial_credit_balance=0, initial_balance=0, debit=0, credit=0,
        final_debit_balance=0, final_credit_balance=0, final_balance=0,
        final_balance_if_debit=0, final_balance_if_credit=0)

    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], node_id=None, node_title=None,
        initial_debit_balance=0, initial_credit_balance=0, initial_balance=0,
        debit=3600, credit=3600, final_debit_balance=3600,
        final_credit_balance=3600, final_balance=0,
        final_balance_if_debit=3300, final_balance_if_credit=3300)

  def testTrialBalanceNoDetailedBalanceColumns(self):
    # Simple test of trial balance with option "show_detailed_balance_columns"
    # turned off.
    # we will use the same data set as account statement
    self.createAccountStatementDataSet(use_two_bank_accounts=0)

    # set request variables and render
    request_form = self.portal.REQUEST.form
    request_form['from_date'] = DateTime(2006, 1, 1)
    request_form['at_date'] = DateTime(2006, 12, 31)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['stopped', 'delivered']
    request_form['show_empty_accounts'] = 1
    request_form['expand_accounts'] = 0
    request_form['per_account_class_summary'] = 0
    request_form['show_detailed_balance_columns'] = 0

    report_section_list = self.getReportSectionList(
                                    self.portal.accounting_module,
                                    'AccountModule_viewTrialBalanceReport')
    self.assertEqual(1, len(report_section_list))
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]

    self.assertEqual(
        ['node_id', 'node_title', 'initial_balance', 'debit', 'credit',
        'final_balance', ],
        data_line_list[0].column_id_list)

    # account are sorted by GAP Id
    self.checkLineProperties(data_line_list[0], node_id='1',
        node_title='Equity', initial_balance=0, debit=0, credit=0,
        final_balance=0)

    self.checkLineProperties(data_line_list[1], node_id='2',
        node_title='Fixed Assets', initial_balance=0, debit=0, credit=0,
        final_balance=0)

    self.checkLineProperties(data_line_list[2], node_id='3',
        node_title='Stocks', initial_balance=0, debit=0, credit=0,
        final_balance=0)

    self.checkLineProperties(data_line_list[3], node_id='40',
        node_title='Payable',
        initial_balance=0, debit=200, credit=100,
        final_balance=100)

    self.checkLineProperties(data_line_list[4], node_id='41',
        node_title='Receivable',
        initial_balance=0, debit=3400, credit=200,
        final_balance=3200)

    self.checkLineProperties(data_line_list[5], node_id='4456',
        node_title='Refundable VAT 10%', initial_balance=0, debit=0, credit=0,
        final_balance=0)

    self.checkLineProperties(data_line_list[6], node_id='4457',
        node_title='Collected VAT 10%', initial_balance=0, debit=0, credit=0,
        final_balance=0)

    self.checkLineProperties(data_line_list[7], node_id='5',
        node_title='Bank (Bank1)', initial_balance=0, debit=0, credit=3300,
        final_balance=-3300)

    self.checkLineProperties(data_line_list[8], node_id='6',
        node_title='Goods Purchase', initial_balance=0, debit=0, credit=0,
        final_balance=0)

    self.checkLineProperties(data_line_list[9], node_id='7',
        node_title='Goods Sales', initial_balance=0, debit=0, credit=0,
        final_balance=0)

    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], node_id=None, node_title=None,
        initial_balance=0, debit=3600, credit=3600, final_balance=0)

  def testTrialBalanceMultipleSection(self):
    account_module = self.portal.account_module
    t1 = self._makeOne(
              portal_type='Accounting Transaction',
              title='Transaction 1',
              source_reference='1',
              simulation_state='delivered',
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2006, 2, 1),
              lines=(dict(source_value=account_module.receivable,
                          source_debit=100.0),
                     dict(source_value=account_module.payable,
                          source_credit=100.0)))

    t2 = self._makeOne(
              portal_type='Accounting Transaction',
              title='Transaction 2',
              source_reference='2',
              source_section_value=self.main_section,
              simulation_state='delivered',
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2006, 2, 1, 0, 1),
              lines=(dict(source_value=account_module.payable,
                          source_debit=200.0),
                     dict(source_value=account_module.receivable,
                          source_credit=200.0)))

    # set request variables and render
    request_form = self.portal.REQUEST.form
    request_form['from_date'] = DateTime(2006, 1, 1)
    request_form['at_date'] = DateTime(2006, 2, 2)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']
    request_form['show_empty_accounts'] = 0
    request_form['expand_accounts'] = 0
    request_form['per_account_class_summary'] = 0
    request_form['group_analytic'] = ["section"]
    request_form['show_detailed_balance_columns'] = 1

    report_section_list = self.getReportSectionList(
                                    self.portal.accounting_module,
                                    'AccountModule_viewTrialBalanceReport')
    self.assertEqual(1, len(report_section_list))
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]

    self.assertEqual(['node_id', 'node_title',
           'section_uid', 'Movement_getSectionPriceCurrency',
           'initial_debit_balance', 'initial_credit_balance',
           'initial_balance', 'debit', 'credit', 'final_debit_balance',
           'final_credit_balance', 'final_balance',
           'final_balance_if_debit', 'final_balance_if_credit'],
           data_line_list[0].column_id_list)

    self.assertEqual(4, len(data_line_list))
    self.checkLineProperties(data_line_list[0],
        node_id='40', node_title='Payable',
        section_uid='My Master Organisation', Movement_getSectionPriceCurrency='EUR',
        initial_debit_balance=0, initial_credit_balance=0,
        debit=200, credit=0, final_debit_balance=200, final_credit_balance=0,
        final_balance_if_debit=200, final_balance_if_credit=0)
    self.checkLineProperties(data_line_list[1],
        node_id='41', node_title='Receivable',
        section_uid='My Master Organisation', Movement_getSectionPriceCurrency='EUR',
        initial_debit_balance=0, initial_credit_balance=0,
        debit=0, credit=200, final_debit_balance=0, final_credit_balance=200,
        final_balance_if_debit=0, final_balance_if_credit=200)
    self.checkLineProperties(data_line_list[2],
        node_id='40', node_title='Payable',
        section_uid='My Organisation', Movement_getSectionPriceCurrency='EUR',
        initial_debit_balance=0, initial_credit_balance=0,
        debit=0, credit=100, final_debit_balance=0, final_credit_balance=100,
        final_balance_if_debit=0, final_balance_if_credit=100)
    self.checkLineProperties(data_line_list[3],
        node_id='41', node_title='Receivable',
        section_uid='My Organisation', Movement_getSectionPriceCurrency='EUR',
        initial_debit_balance=0, initial_credit_balance=0,
        debit=100, credit=0, final_debit_balance=100, final_credit_balance=0,
        final_balance_if_debit=100, final_balance_if_credit=0)

    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], node_id=None, node_title=None,
        initial_debit_balance=0, initial_credit_balance=0, debit=300,
        credit=300, final_debit_balance=300, final_credit_balance=300,
        final_balance_if_debit=300, final_balance_if_credit=300)

  def testTrialBalanceExpandAccounts(self):
    # Test of "expand accounts" feature of trial balance
    self.createAccountStatementDataSet()

    # set request variables and render
    request_form = self.portal.REQUEST.form
    request_form['from_date'] = DateTime(2006, 1, 1)
    request_form['at_date'] = DateTime(2006, 2, 2)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']
    request_form['show_empty_accounts'] = 0
    request_form['expand_accounts'] = 1
    request_form['per_account_class_summary'] = 0
    request_form['group_analytic'] = []
    request_form['show_detailed_balance_columns'] = 1

    report_section_list = self.getReportSectionList(
                                    self.portal.accounting_module,
                                    'AccountModule_viewTrialBalanceReport')
    self.assertEqual(1, len(report_section_list))
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]

    self.assertEqual(6, len(data_line_list))

    self.assertEqual(['node_id', 'node_title', 'mirror_section_title',
      'initial_debit_balance', 'initial_credit_balance', 'initial_balance',
      'debit', 'credit', 'final_debit_balance', 'final_credit_balance',
      'final_balance', 'final_balance_if_debit', 'final_balance_if_credit'],
      data_line_list[0].column_id_list)

    # account are sorted by GAP Id
    self.checkLineProperties(data_line_list[0], node_id='40',
        node_title='Payable', mirror_section_title='Client 1',
        initial_debit_balance=0, initial_credit_balance=0, debit=200,
        credit=100, final_debit_balance=200, final_credit_balance=100,
        final_balance_if_debit=100, final_balance_if_credit=0)

    self.checkLineProperties(data_line_list[1], node_id='41',
        node_title='Receivable', mirror_section_title='Client 1',
        initial_debit_balance=0, initial_credit_balance=0, debit=1000,
        credit=200, final_debit_balance=1000, final_credit_balance=200,
        final_balance_if_debit=800, final_balance_if_credit=0)

    self.checkLineProperties(data_line_list[2], node_id='41',
        node_title='Receivable', mirror_section_title='Client 2',
        initial_debit_balance=0, initial_credit_balance=0, debit=400, credit=0,
        final_debit_balance=400, final_credit_balance=0,
        final_balance_if_debit=400, final_balance_if_credit=0)

    self.checkLineProperties(data_line_list[3], node_id='41',
        node_title='Receivable', mirror_section_title='John Smith',
        initial_debit_balance=0, initial_credit_balance=0, debit=500, credit=0,
        final_debit_balance=500, final_credit_balance=0,
        final_balance_if_debit=500, final_balance_if_credit=0,)

    self.checkLineProperties(data_line_list[4], node_id='5',
        node_title='Bank (Bank1)', initial_debit_balance=0,
        initial_credit_balance=0, debit=0, credit=700,
        final_debit_balance=0, final_credit_balance=700,
        final_balance_if_debit=0, final_balance_if_credit=700,)

    self.checkLineProperties(data_line_list[5], node_id='5',
        node_title='Bank (Bank2)', initial_debit_balance=0,
        initial_credit_balance=0, debit=0, credit=1100,
        final_debit_balance=0, final_credit_balance=1100,
        final_balance_if_debit=0, final_balance_if_credit=1100,)

    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], node_id=None, node_title=None,
        initial_debit_balance=0, initial_credit_balance=0, debit=2100,
        credit=2100, final_debit_balance=2100, final_credit_balance=2100,
        final_balance_if_debit=1800, final_balance_if_credit=1800)


  def testTrialBalancePreviousPeriod(self):
    # Test of trial balance and previous period
    self.createAccountStatementDataSet(use_two_bank_accounts=0)
    account_module = self.portal.account_module
    # previous period
    self._makeOne(
              portal_type='Accounting Transaction',
              title='Transaction -1',
              source_reference='-1',
              simulation_state='delivered',
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2005, 2, 2),
              lines=(dict(source_value=account_module.goods_purchase,
                          source_debit=600.0),
                     dict(source_value=account_module.goods_sales,
                          source_credit=600.0),))

    # balance transaction
    self._makeOne(
              portal_type='Balance Transaction',
              title='Transaction 0',
              destination_reference='0',
              simulation_state='delivered',
              start_date=DateTime(2006, 1, 1),
              lines=(dict(destination_value=account_module.payable,
                          destination_credit=600.0,
                          source_section_value=
                              self.organisation_module.client_1,),
                     dict(destination_value=account_module.receivable,
                          destination_debit=400.0,
                          source_section_value=
                              self.organisation_module.client_2,),
                     dict(destination_value=account_module.equity,
                          destination_debit=200)))

    # one more transaction in the period, because our testing data does not
    # include the sales
    self._makeOne(
              portal_type='Sale Invoice Transaction',
              title='Transaction 0.5',
              source_reference='0.5',
              simulation_state='delivered',
              destination_section_value=self.organisation_module.client_2,
              start_date=DateTime(2006, 1, 1),
              lines=(dict(source_value=account_module.goods_sales,
                          source_credit=50.0),
                     dict(source_value=account_module.receivable,
                          source_debit=50.0),))

    # set request variables and render
    request_form = self.portal.REQUEST.form
    request_form['from_date'] = DateTime(2006, 1, 1)
    request_form['at_date'] = DateTime(2006, 2, 2)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']
    request_form['show_empty_accounts'] = 0
    request_form['expand_accounts'] = 0
    request_form['per_account_class_summary'] = 0
    request_form['show_detailed_balance_columns'] = 1
    request_form['group_analytic'] = []

    report_section_list = self.getReportSectionList(
                                    self.portal.accounting_module,
                                    'AccountModule_viewTrialBalanceReport')
    self.assertEqual(1, len(report_section_list))
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]

    self.assertEqual(5, len(data_line_list))

    # account are sorted by GAP Id
    # TODO: sort by "gap normalized path"
    self.checkLineProperties(data_line_list[0], node_id='1',
        node_title='Equity', initial_debit_balance=200,
        initial_credit_balance=0, initial_balance=200, debit=0, credit=0,
        final_debit_balance=200, final_credit_balance=0, final_balance=200,
        final_balance_if_debit=200, final_balance_if_credit=0)

    self.checkLineProperties(data_line_list[1], node_id='40',
        node_title='Payable', initial_debit_balance=0,
        initial_credit_balance=600, initial_balance=-600, debit=200,
        credit=100, final_debit_balance=200, final_credit_balance=700,
        final_balance=-500, final_balance_if_debit=0,
        final_balance_if_credit=500)

    self.checkLineProperties(data_line_list[2], node_id='41',
        node_title='Receivable', initial_debit_balance=400,
        initial_credit_balance=0, initial_balance=400, debit=1950, credit=200,
        final_debit_balance=2350, final_credit_balance=200, final_balance=2150,
        final_balance_if_debit=2150, final_balance_if_credit=0)

    self.checkLineProperties(data_line_list[3], node_id='5',
        node_title='Bank (Bank1)', initial_debit_balance=0,
        initial_credit_balance=0, initial_balance=0, debit=0, credit=1800,
        final_debit_balance=0, final_credit_balance=1800, final_balance=-1800,
        final_balance_if_debit=0, final_balance_if_credit=1800,)

    self.checkLineProperties(data_line_list[4], node_id='7',
        node_title='Goods Sales', initial_debit_balance=0,
        initial_credit_balance=0, initial_balance=0, debit=0, credit=50,
        final_debit_balance=0, final_credit_balance=50, final_balance=-50,
        final_balance_if_debit=0, final_balance_if_credit=50,)

    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], node_id=None, node_title=None,
        initial_debit_balance=600, initial_credit_balance=600,
        initial_balance=0, debit=2150,
        credit=2150, final_debit_balance=2750, final_credit_balance=2750,
        final_balance=0,
        final_balance_if_debit=2350, final_balance_if_credit=2350)

  def testTrialBalanceInitialBalance(self):
    # Test of trial balance and initial balance
    account_module = self.portal.account_module
    # previous period
    self._makeOne(
              portal_type='Accounting Transaction',
              title='Transaction -2',
              source_reference='-2',
              simulation_state='delivered',
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2006, 2, 1),
              lines=(dict(source_value=account_module.payable,
                          source_debit=400.0),
                     dict(source_value=account_module.receivable,
                          source_credit=400.0),))
    self._makeOne(
              portal_type='Accounting Transaction',
              title='Transaction -1',
              source_reference='-1',
              simulation_state='delivered',
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2006, 2, 2),
              lines=(dict(source_value=account_module.receivable,
                          source_debit=600.0),
                     dict(source_value=account_module.payable,
                          source_credit=600.0),))

    # set request variables and render
    request_form = self.portal.REQUEST.form
    request_form['from_date'] = DateTime(2007, 1, 1)
    request_form['at_date'] = DateTime(2007, 12, 31)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']
    request_form['show_empty_accounts'] = 0
    request_form['expand_accounts'] = 0
    request_form['per_account_class_summary'] = 0
    request_form['show_detailed_balance_columns'] = 1
    request_form['group_analytic'] = []

    report_section_list = self.getReportSectionList(
                                    self.portal.accounting_module,
                                    'AccountModule_viewTrialBalanceReport')
    self.assertEqual(1, len(report_section_list))
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]

    self.assertEqual(2, len(data_line_list))

    self.checkLineProperties(data_line_list[0], node_id='40',
        node_title='Payable', initial_debit_balance=0,
        initial_credit_balance=200, debit=0, credit=0,
        final_debit_balance=0, final_credit_balance=200,
        final_balance_if_debit=0, final_balance_if_credit=200)

    self.checkLineProperties(data_line_list[1], node_id='41',
        node_title='Receivable', initial_debit_balance=200,
        initial_credit_balance=0, debit=0, credit=0,
        final_debit_balance=200, final_credit_balance=0,
        final_balance_if_debit=200, final_balance_if_credit=0)

    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], node_id=None, node_title=None,
        initial_debit_balance=200, initial_credit_balance=200, debit=0,
        credit=0, final_debit_balance=200, final_credit_balance=200,
        final_balance_if_debit=200, final_balance_if_credit=200)

  def testTrialBalanceInitialBalanceMultiMirrorSectionExpandAccount(self):
    # Test of trial balance and initial balance with multiple mirror_section
    account_module = self.portal.account_module
    # previous period
    self._makeOne(
              portal_type='Accounting Transaction',
              title='Transaction -2',
              source_reference='-2',
              simulation_state='delivered',
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2006, 2, 1),
              lines=(dict(source_value=account_module.payable,
                          source_debit=400.0),
                     dict(source_value=account_module.receivable,
                          source_credit=400.0),))
    self._makeOne(
              portal_type='Accounting Transaction',
              title='Transaction -1',
              source_reference='-1',
              simulation_state='delivered',
              destination_section_value=self.organisation_module.client_2,
              start_date=DateTime(2006, 2, 2),
              lines=(dict(source_value=account_module.receivable,
                          source_debit=600.0),
                     dict(source_value=account_module.payable,
                          source_credit=600.0),))

    # set request variables and render
    request_form = self.portal.REQUEST.form
    request_form['from_date'] = DateTime(2007, 1, 1)
    request_form['at_date'] = DateTime(2007, 12, 31)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']
    request_form['show_empty_accounts'] = 0
    request_form['expand_accounts'] = 1
    request_form['per_account_class_summary'] = 0
    request_form['show_detailed_balance_columns'] = 1
    request_form['group_analytic'] = []

    report_section_list = self.getReportSectionList(
                                    self.portal.accounting_module,
                                    'AccountModule_viewTrialBalanceReport')
    self.assertEqual(1, len(report_section_list))
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(4, len(data_line_list))

    self.checkLineProperties(data_line_list[0], node_id='40',
        node_title='Payable', mirror_section_title='Client 1',
        initial_debit_balance=400, initial_credit_balance=0, debit=0, credit=0,
        final_debit_balance=400, final_credit_balance=0,
        final_balance_if_debit=400, final_balance_if_credit=0)

    self.checkLineProperties(data_line_list[1], node_id='40',
        node_title='Payable', mirror_section_title='Client 2',
        initial_debit_balance=0, initial_credit_balance=600, debit=0, credit=0,
        final_debit_balance=0, final_credit_balance=600,
        final_balance_if_debit=0, final_balance_if_credit=600)

    self.checkLineProperties(data_line_list[2], node_id='41',
        node_title='Receivable', mirror_section_title='Client 1', initial_debit_balance=0,
        initial_credit_balance=400, debit=0, credit=0,
        final_debit_balance=0, final_credit_balance=400,
        final_balance_if_debit=0, final_balance_if_credit=400)

    self.checkLineProperties(data_line_list[3], node_id='41',
        node_title='Receivable', mirror_section_title='Client 2',
        initial_debit_balance=600, initial_credit_balance=0, debit=0, credit=0,
        final_debit_balance=600, final_credit_balance=0,
        final_balance_if_debit=600, final_balance_if_credit=0)

    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], node_id=None, node_title=None,
        initial_debit_balance=1000, initial_credit_balance=1000, debit=0,
        credit=0, final_debit_balance=1000, final_credit_balance=1000,
        final_balance_if_debit=1000, final_balance_if_credit=1000)

  def testTrialBalanceInitialBalanceMultiMirrorSectionNoExpandAccount(self):
    # Test of trial balance and initial balance with multiple mirror_section,
    # without expanding accounts. This is the same as
    # testTrialBalanceInitialBalanceMultiMirrorSectionExpandAccount, but we
    # don't use the "Expand other parties". The initial debit & credit must be
    # the same as without this option
    account_module = self.portal.account_module
    # previous period
    self._makeOne(
              portal_type='Accounting Transaction',
              title='Transaction -2',
              source_reference='-2',
              simulation_state='delivered',
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2006, 2, 1),
              lines=(dict(source_value=account_module.payable,
                          source_debit=400.0),
                     dict(source_value=account_module.receivable,
                          source_credit=400.0),))
    self._makeOne(
              portal_type='Accounting Transaction',
              title='Transaction -1',
              source_reference='-1',
              simulation_state='delivered',
              destination_section_value=self.organisation_module.client_2,
              start_date=DateTime(2006, 2, 2),
              lines=(dict(source_value=account_module.receivable,
                          source_debit=600.0),
                     dict(source_value=account_module.payable,
                          source_credit=600.0),))

    # set request variables and render
    request_form = self.portal.REQUEST.form
    request_form['from_date'] = DateTime(2007, 1, 1)
    request_form['at_date'] = DateTime(2007, 12, 31)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']
    request_form['show_empty_accounts'] = 0
    request_form['expand_accounts'] = 0
    request_form['per_account_class_summary'] = 0
    request_form['show_detailed_balance_columns'] = 1
    request_form['group_analytic'] = []

    report_section_list = self.getReportSectionList(
                                    self.portal.accounting_module,
                                    'AccountModule_viewTrialBalanceReport')
    self.assertEqual(1, len(report_section_list))
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]

    self.assertEqual(2, len(data_line_list))

    self.checkLineProperties(data_line_list[0], node_id='40',
        node_title='Payable', initial_debit_balance=400,
        initial_credit_balance=600, debit=0, credit=0,
        final_debit_balance=400, final_credit_balance=600,
        final_balance_if_debit=0, final_balance_if_credit=200)

    self.checkLineProperties(data_line_list[1], node_id='41',
        node_title='Receivable', initial_debit_balance=600,
        initial_credit_balance=400, debit=0, credit=0,
        final_debit_balance=600, final_credit_balance=400,
        final_balance_if_debit=200, final_balance_if_credit=0)

    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], node_id=None, node_title=None,
        initial_debit_balance=1000, initial_credit_balance=1000, debit=0,
        credit=0, final_debit_balance=1000, final_credit_balance=1000,
        final_balance_if_debit=200, final_balance_if_credit=200)


  def testTrialBalanceInitialBalanceBalanceTransaction(self):
    # Test of trial balance and initial balance with balance transactions.
    # Unlike other transactions balance transactions passed the first day of
    # the period will count as "initial balance", not as movement in the period
    account_module = self.portal.account_module

    self._makeOne(
              portal_type='Balance Transaction',
              title='Transaction 0',
              destination_reference='0',
              simulation_state='delivered',
              source_section_value=self.organisation_module.client_1,
              start_date=DateTime(2007, 1, 1),
              lines=(dict(destination_value=account_module.payable,
                          destination_debit=100.0),
                     dict(destination_value=account_module.receivable,
                          destination_credit=100.0),))
    self._makeOne(
              portal_type='Accounting Transaction',
              title='Transaction 1',
              source_reference='1',
              simulation_state='delivered',
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2007, 1, 1),
              lines=(dict(source_value=account_module.payable,
                          source_debit=10.0),
                     dict(source_value=account_module.receivable,
                          source_credit=10.0),))

    # set request variables and render
    request_form = self.portal.REQUEST.form
    request_form['from_date'] = DateTime(2007, 1, 1)
    request_form['at_date'] = DateTime(2007, 12, 31)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']
    request_form['show_empty_accounts'] = 0
    request_form['expand_accounts'] = 0
    request_form['per_account_class_summary'] = 0
    request_form['show_detailed_balance_columns'] = 1
    request_form['group_analytic'] = []

    report_section_list = self.getReportSectionList(
                                    self.portal.accounting_module,
                                    'AccountModule_viewTrialBalanceReport')
    self.assertEqual(1, len(report_section_list))
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]

    self.assertEqual(2, len(data_line_list))

    self.checkLineProperties(data_line_list[0], node_id='40',
        node_title='Payable', initial_debit_balance=100,
        initial_credit_balance=0, debit=10, credit=0,
        final_debit_balance=110, final_credit_balance=0,
        final_balance_if_debit=110, final_balance_if_credit=0)

    self.checkLineProperties(data_line_list[1], node_id='41',
        node_title='Receivable', initial_debit_balance=0,
        initial_credit_balance=100, debit=0, credit=10,
        final_debit_balance=0, final_credit_balance=110,
        final_balance_if_debit=0, final_balance_if_credit=110)

    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], node_id=None, node_title=None,
        initial_debit_balance=100, initial_credit_balance=100, debit=10,
        credit=10, final_debit_balance=110, final_credit_balance=110,
        final_balance_if_debit=110, final_balance_if_credit=110)


  def testTrialBalanceInitialBalanceBalanceTransactionDifferentFromDate(self):
    # Test of trial balance and initial balance with balance transactions, but
    # with a from_date which differs from the balance transaction date.
    account_module = self.portal.account_module

    self._makeOne(
              portal_type='Balance Transaction',
              title='Transaction 0',
              destination_reference='0',
              simulation_state='delivered',
              source_section_value=self.organisation_module.client_1,
              start_date=DateTime(2007, 1, 1),
              lines=(dict(destination_value=account_module.payable,
                          destination_debit=100.0),
                     dict(destination_value=account_module.receivable,
                          destination_credit=100.0),))
    self._makeOne(
              portal_type='Accounting Transaction',
              title='Transaction 1',
              source_reference='1',
              simulation_state='delivered',
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2007, 1, 3),
              lines=(dict(source_value=account_module.payable,
                          source_debit=10.0),
                     dict(source_value=account_module.receivable,
                          source_credit=10.0),))

    # set request variables and render
    request_form = self.portal.REQUEST.form
    request_form['from_date'] = DateTime(2007, 1, 2)
    request_form['at_date'] = DateTime(2007, 12, 31)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']
    request_form['show_empty_accounts'] = 0
    request_form['expand_accounts'] = 0
    request_form['per_account_class_summary'] = 0
    request_form['show_detailed_balance_columns'] = 1
    request_form['group_analytic'] = []

    report_section_list = self.getReportSectionList(
                                    self.portal.accounting_module,
                                    'AccountModule_viewTrialBalanceReport')
    self.assertEqual(1, len(report_section_list))
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]

    self.assertEqual(2, len(data_line_list))

    self.checkLineProperties(data_line_list[0], node_id='40',
        node_title='Payable', initial_debit_balance=100,
        initial_credit_balance=0, debit=10, credit=0,
        final_debit_balance=110, final_credit_balance=0,
        final_balance_if_debit=110, final_balance_if_credit=0)

    self.checkLineProperties(data_line_list[1], node_id='41',
        node_title='Receivable', initial_debit_balance=0,
        initial_credit_balance=100, debit=0, credit=10,
        final_debit_balance=0, final_credit_balance=110,
        final_balance_if_debit=0, final_balance_if_credit=110)

    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], node_id=None, node_title=None,
        initial_debit_balance=100, initial_credit_balance=100, debit=10,
        credit=10, final_debit_balance=110, final_credit_balance=110,
        final_balance_if_debit=110, final_balance_if_credit=110)


  def testTrialBalanceInitialBalanceWithPeriod(self):
    # Test of trial balance and initial balance
    account_module = self.portal.account_module

    # previous period
    self._makeOne(
              portal_type='Accounting Transaction',
              title='Transaction -2',
              source_reference='-2',
              simulation_state='delivered',
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2006, 2, 1),
              lines=(dict(source_value=account_module.payable,
                          source_debit=400.0),
                     dict(source_value=account_module.receivable,
                          source_credit=400.0),))
    self._makeOne(
              portal_type='Accounting Transaction',
              title='Transaction -1',
              source_reference='-1',
              simulation_state='delivered',
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2006, 2, 2),
              lines=(dict(source_value=account_module.receivable,
                          source_debit=600.0),
                     dict(source_value=account_module.payable,
                          source_credit=600.0),))

    # current period, but before from date
    self._makeOne(
              portal_type='Accounting Transaction',
              title='Transaction 0',
              source_reference='0',
              simulation_state='delivered',
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2007, 1, 3),
              lines=(dict(source_value=account_module.payable,
                          source_debit=111.0),
                     dict(source_value=account_module.receivable,
                          source_credit=111.0),))

    # set request variables and render
    request_form = self.portal.REQUEST.form
    request_form['from_date'] = DateTime(2007, 2, 1)
    request_form['at_date'] = DateTime(2007, 12, 31)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']
    request_form['show_empty_accounts'] = 0
    request_form['expand_accounts'] = 0
    request_form['per_account_class_summary'] = 0
    request_form['group_analytic'] = []
    request_form['show_detailed_balance_columns'] = 1

    report_section_list = self.getReportSectionList(
                                    self.portal.accounting_module,
                                    'AccountModule_viewTrialBalanceReport')
    self.assertEqual(1, len(report_section_list))
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]

    self.assertEqual(2, len(data_line_list))

    self.checkLineProperties(data_line_list[0], node_id='40',
        node_title='Payable', initial_debit_balance=111,
        initial_credit_balance=200, debit=0, credit=0,
        final_debit_balance=111, final_credit_balance=200,
        final_balance_if_debit=0, final_balance_if_credit=89)

    self.checkLineProperties(data_line_list[1], node_id='41',
        node_title='Receivable', initial_debit_balance=200,
        initial_credit_balance=111, debit=0, credit=0,
        final_debit_balance=200, final_credit_balance=111,
        final_balance_if_debit=89, final_balance_if_credit=0)

    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], node_id=None, node_title=None,
        initial_debit_balance=311, initial_credit_balance=311, debit=0,
        credit=0, final_debit_balance=311, final_credit_balance=311,
        final_balance_if_debit=89, final_balance_if_credit=89)


  def testTrialBalanceInitialBalancePeriodStartDateBalanceTransaction(self):
    # Test of trial balance and initial balance with balance transactions and
    # transactions between period start date and from date
    # This is a combination of
    account_module = self.portal.account_module

    self._makeOne(
              portal_type='Balance Transaction',
              title='Transaction 0',
              destination_reference='0',
              simulation_state='delivered',
              source_section_value=self.organisation_module.client_1,
              start_date=DateTime(2007, 1, 1),
              lines=(dict(destination_value=account_module.payable,
                          destination_debit=100.0),
                     dict(destination_value=account_module.receivable,
                          destination_credit=100.0),))
    self._makeOne(
              portal_type='Accounting Transaction',
              title='Transaction 1',
              source_reference='1',
              simulation_state='delivered',
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2007, 1, 1),
              lines=(dict(source_value=account_module.payable,
                          source_debit=10.0),
                     dict(source_value=account_module.receivable,
                          source_credit=10.0),))

    # set request variables and render
    request_form = self.portal.REQUEST.form
    request_form['from_date'] = DateTime(2007, 1, 1)
    request_form['at_date'] = DateTime(2007, 12, 31)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']
    request_form['show_empty_accounts'] = 0
    request_form['expand_accounts'] = 0
    request_form['per_account_class_summary'] = 0
    request_form['group_analytic'] = []
    request_form['show_detailed_balance_columns'] = 1

    report_section_list = self.getReportSectionList(
                                    self.portal.accounting_module,
                                    'AccountModule_viewTrialBalanceReport')
    self.assertEqual(1, len(report_section_list))
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]

    self.assertEqual(2, len(data_line_list))
    self.checkLineProperties(data_line_list[0], node_id='40',
        node_title='Payable', initial_debit_balance=100,
        initial_credit_balance=0, debit=10, credit=0,
        final_debit_balance=110, final_credit_balance=0,
        final_balance_if_debit=110, final_balance_if_credit=0)

    self.checkLineProperties(data_line_list[1], node_id='41',
        node_title='Receivable', initial_debit_balance=0,
        initial_credit_balance=100, debit=0, credit=10,
        final_debit_balance=0, final_credit_balance=110,
        final_balance_if_debit=0, final_balance_if_credit=110)

    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], node_id=None, node_title=None,
        initial_debit_balance=100, initial_credit_balance=100, debit=10,
        credit=10, final_debit_balance=110, final_credit_balance=110,
        final_balance_if_debit=110, final_balance_if_credit=110)


  def testTrialBalanceDifferentCurrencies(self):
    # Test of trial balance and different currencies
    account_module = self.portal.account_module

    self._makeOne(
              portal_type='Accounting Transaction',
              title='Transaction in EUR (our currency)',
              resource='currency_module/euro',
              source_reference='1',
              simulation_state='delivered',
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2006, 2, 2),
              lines=(dict(source_value=account_module.payable,
                          source_debit=200.0),
                     dict(source_value=account_module.receivable,
                          source_credit=200.0),))

    self._makeOne(
              portal_type='Accounting Transaction',
              title='Transaction in USD',
              resource='currency_module/usd',
              source_reference='2',
              simulation_state='delivered',
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2006, 2, 2),
              lines=(dict(source_value=account_module.payable,
                          source_debit=600.0,
                          source_asset_debit=300.0,
                          destination_asset_credit=400.0),
                     dict(source_value=account_module.receivable,
                          source_credit=600.0,
                          source_asset_credit=300.0,
                          destination_asset_debit=400.0),))

    # set request variables and render
    request_form = self.portal.REQUEST.form
    request_form['from_date'] = DateTime(2006, 1, 1)
    request_form['at_date'] = DateTime(2006, 2, 2)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']
    request_form['show_empty_accounts'] = 0
    request_form['expand_accounts'] = 0
    request_form['per_account_class_summary'] = 0
    request_form['group_analytic'] = []
    request_form['show_detailed_balance_columns'] = 1

    report_section_list = self.getReportSectionList(
                                    self.portal.accounting_module,
                                    'AccountModule_viewTrialBalanceReport')
    self.assertEqual(1, len(report_section_list))
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]

    self.assertEqual(2, len(data_line_list))

    self.checkLineProperties(data_line_list[0], node_id='40',
        node_title='Payable', initial_debit_balance=0,
        initial_credit_balance=0, debit=500, credit=0,
        final_debit_balance=500, final_credit_balance=0,
        final_balance_if_debit=500, final_balance_if_credit=0)

    self.checkLineProperties(data_line_list[1], node_id='41',
        node_title='Receivable', initial_debit_balance=0,
        initial_credit_balance=0, debit=0, credit=500,
        final_debit_balance=0, final_credit_balance=500,
        final_balance_if_debit=0, final_balance_if_credit=500)

    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], node_id=None, node_title=None,
        initial_debit_balance=0, initial_credit_balance=0, debit=500,
        credit=500, final_debit_balance=500, final_credit_balance=500,
        final_balance_if_debit=500, final_balance_if_credit=500)

  def testTrialBalanceGAPFilter(self):
    # Test of GAP filter on trial balance
    self.createAccountStatementDataSet()

    # set request variables and render
    request_form = self.portal.REQUEST.form
    request_form['from_date'] = DateTime(2006, 1, 1)
    request_form['at_date'] = DateTime(2006, 2, 2)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']
    request_form['show_empty_accounts'] = 0
    request_form['expand_accounts'] = 1
    request_form['gap_list'] = ['my_country/my_accounting_standards/4']
    request_form['per_account_class_summary'] = 0
    request_form['group_analytic'] = []
    request_form['show_detailed_balance_columns'] = 1

    report_section_list = self.getReportSectionList(
                                    self.portal.accounting_module,
                                    'AccountModule_viewTrialBalanceReport')
    self.assertEqual(1, len(report_section_list))
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]

    self.assertEqual(4, len(data_line_list))

    # account are sorted by GAP Id
    self.checkLineProperties(data_line_list[0], node_id='40',
        node_title='Payable', mirror_section_title='Client 1',
        initial_debit_balance=0, initial_credit_balance=0, debit=200,
        credit=100, final_debit_balance=200, final_credit_balance=100,
        final_balance_if_debit=100, final_balance_if_credit=0)

    self.checkLineProperties(data_line_list[1], node_id='41',
        node_title='Receivable', mirror_section_title='Client 1',
        initial_debit_balance=0, initial_credit_balance=0, debit=1000,
        credit=200, final_debit_balance=1000, final_credit_balance=200,
        final_balance_if_debit=800, final_balance_if_credit=0)

    self.checkLineProperties(data_line_list[2], node_id='41',
        node_title='Receivable', mirror_section_title='Client 2',
        initial_debit_balance=0, initial_credit_balance=0, debit=400, credit=0,
        final_debit_balance=400, final_credit_balance=0,
        final_balance_if_debit=400, final_balance_if_credit=0)

    self.checkLineProperties(data_line_list[3], node_id='41',
        node_title='Receivable', mirror_section_title='John Smith',
        initial_debit_balance=0, initial_credit_balance=0, debit=500, credit=0,
        final_debit_balance=500, final_credit_balance=0,
        final_balance_if_debit=500, final_balance_if_credit=0,)

    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], node_id=None, node_title=None,
        initial_debit_balance=0, initial_credit_balance=0, debit=2100,
        credit=300, final_debit_balance=2100, final_credit_balance=300,
        final_balance_if_debit=1800, final_balance_if_credit=0)


  def testTrialBalanceAccountClassSummary(self):
    # Test of trial balance with per "account class" summary
    account_module = self.portal.account_module
    self._makeOne(
              portal_type='Accounting Transaction',
              title='Transaction 1',
              source_reference='1',
              simulation_state='delivered',
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2006, 2, 1),
              lines=(dict(source_value=account_module.payable,
                          source_debit=400.0),
                     dict(source_value=account_module.receivable,
                          source_credit=400.0),))
    self._makeOne(
              portal_type='Accounting Transaction',
              title='Transaction 2',
              source_reference='2',
              simulation_state='delivered',
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2006, 2, 2),
              lines=(dict(source_value=account_module.receivable,
                          source_debit=600.0),
                     dict(source_value=account_module.payable,
                          source_credit=600.0),))

    # set request variables and render
    request_form = self.portal.REQUEST.form
    request_form['from_date'] = DateTime(2006, 1, 1)
    request_form['at_date'] = DateTime(2006, 12, 31)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']
    request_form['show_empty_accounts'] = 0
    request_form['expand_accounts'] = 0
    request_form['per_account_class_summary'] = 1
    request_form['group_analytic'] = []
    request_form['show_detailed_balance_columns'] = 1

    report_section_list = self.getReportSectionList(
                                    self.portal.accounting_module,
                                    'AccountModule_viewTrialBalanceReport')
    self.assertEqual(1, len(report_section_list))
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]

    self.assertEqual(4, len(data_line_list))

    self.checkLineProperties(data_line_list[0], node_id='40',
        node_title='Payable', initial_debit_balance=0,
        initial_credit_balance=0, debit=400, credit=600,
        final_debit_balance=400, final_credit_balance=600,
        final_balance_if_debit=0, final_balance_if_credit=200)

    self.checkLineProperties(data_line_list[1], node_id='41',
        node_title='Receivable', initial_debit_balance=0,
        initial_credit_balance=0, debit=600, credit=400,
        final_debit_balance=600, final_credit_balance=400,
        final_balance_if_debit=200, final_balance_if_credit=0)

    # The summary line for 4 class
    self.checkLineProperties(data_line_list[2],
        node_title='Total for class 4', initial_debit_balance=0,
        initial_credit_balance=0, debit=1000, credit=1000,
        final_debit_balance=1000, final_credit_balance=1000,
        final_balance_if_debit=200, final_balance_if_credit=200)
    # an empty line for style
    self.checkLineProperties(data_line_list[3], node_title=' ')

    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], node_id=None, node_title=None,
        initial_debit_balance=0, initial_credit_balance=0, debit=1000,
        credit=1000, final_debit_balance=1000, final_credit_balance=1000,
        final_balance_if_debit=200, final_balance_if_credit=200)

  def testTrialBalancePortalType(self):
    # portal_type filter on trial balance
    self.createAccountStatementDataSet()

    # set request variables and render
    request_form = self.portal.REQUEST.form
    request_form['from_date'] = DateTime(2006, 1, 1)
    request_form['at_date'] = DateTime(2006, 12, 31)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['stopped', 'delivered']
    request_form['show_empty_accounts'] = 0
    request_form['expand_accounts'] = 0
    request_form['per_account_class_summary'] = 0
    request_form['portal_type'] = ['Purchase Invoice Transaction']
    request_form['group_analytic'] = []
    request_form['show_detailed_balance_columns'] = 1

    report_section_list = self.getReportSectionList(
                                    self.portal.accounting_module,
                                    'AccountModule_viewTrialBalanceReport')
    self.assertEqual(1, len(report_section_list))
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(2, len(data_line_list))

    self.checkLineProperties(data_line_list[0], node_id='41',
        node_title='Receivable', initial_debit_balance=0,
        initial_credit_balance=0, debit=600, credit=0,
        final_debit_balance=600, final_credit_balance=0,
        final_balance_if_debit=600, final_balance_if_credit=0,)

    self.checkLineProperties(data_line_list[1], node_id='5',
        node_title='Bank (Bank2)', initial_debit_balance=0,
        initial_credit_balance=0, debit=0, credit=600, final_debit_balance=0,
        final_credit_balance=600, final_balance_if_debit=0,
        final_balance_if_credit=600,)

    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], node_id=None, node_title=None,
        initial_debit_balance=0, initial_credit_balance=0, debit=600,
        credit=600, final_debit_balance=600, final_credit_balance=600,
        final_balance_if_debit=600, final_balance_if_credit=600)

  def testTrialBalanceFunction(self):
    # trial balance restricted to a function
    self.createProjectAndFunctionDataSet()
    # set request variables and render
    request_form = self.portal.REQUEST.form
    request_form['from_date'] = DateTime(2006, 1, 1)
    request_form['at_date'] = DateTime(2006, 12, 31)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['stopped', 'delivered']
    request_form['per_account_class_summary'] = 0
    request_form['show_empty_accounts'] = 0
    request_form['per_account_class_summary'] = 0
    request_form['function'] = 'function/a'
    request_form['group_analytic'] = []
    request_form['show_detailed_balance_columns'] = 1

    report_section_list = self.getReportSectionList(
                                    self.portal.accounting_module,
                                    'AccountModule_viewTrialBalanceReport')
    self.assertEqual(1, len(report_section_list))
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(2, len(data_line_list))

    self.checkLineProperties(data_line_list[0], node_id='41',
        node_title='Receivable', initial_debit_balance=0,
        initial_credit_balance=0, debit=500, credit=0,
        final_debit_balance=500, final_credit_balance=0,
        final_balance_if_debit=500, final_balance_if_credit=0,)

    self.checkLineProperties(data_line_list[1], node_id='7',
        node_title='Goods Sales', initial_debit_balance=0,
        initial_credit_balance=0, debit=0, credit=500, final_debit_balance=0,
        final_credit_balance=500, final_balance_if_debit=0,
        final_balance_if_credit=500,)

    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], node_id=None, node_title=None,
        initial_debit_balance=0, initial_credit_balance=0, debit=500,
        credit=500, final_debit_balance=500, final_credit_balance=500,
        final_balance_if_debit=500, final_balance_if_credit=500)


  def testTrialBalanceFunctionWithCache(self):
    # trial balance restricted to a function
    # Make it fill cache by asking it a later date
    self.createProjectAndFunctionDataSet()
    # set request variables and render
    request_form = self.portal.REQUEST.form
    request_form['at_date'] = DateTime(2010, 12, 31)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['stopped', 'delivered']
    request_form['per_account_class_summary'] = 0
    request_form['show_empty_accounts'] = 0
    request_form['per_account_class_summary'] = 0
    request_form['function'] = ''
    request_form['group_analytic'] = ["function"]
    request_form['show_detailed_balance_columns'] = 1
    report_section_list = self.portal.accounting_module.AccountModule_getTrialBalanceReportSectionList()
    line_list = self.getListBoxLineList(report_section_list[0])
    # XXX where is the end of this test ?


  def testTrialBalanceProject(self):
    # trial balance restricted to a project
    self.createProjectAndFunctionDataSet()

    # set request variables and render
    request_form = self.portal.REQUEST.form
    request_form['from_date'] = DateTime(2006, 1, 1)
    request_form['at_date'] = DateTime(2006, 12, 31)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['stopped', 'delivered']
    request_form['per_account_class_summary'] = 0
    request_form['show_empty_accounts'] = 0
    request_form['per_account_class_summary'] = 0
    request_form['project'] = self.project_1.getRelativeUrl()
    request_form['group_analytic'] = []
    request_form['show_detailed_balance_columns'] = 1

    report_section_list = self.getReportSectionList(
                                    self.portal.accounting_module,
                                    'AccountModule_viewTrialBalanceReport')
    self.assertEqual(1, len(report_section_list))
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(2, len(data_line_list))

    self.checkLineProperties(data_line_list[0], node_id='41',
        node_title='Receivable', initial_debit_balance=0,
        initial_credit_balance=0, debit=500, credit=0,
        final_debit_balance=500, final_credit_balance=0,
        final_balance_if_debit=500, final_balance_if_credit=0,)

    self.checkLineProperties(data_line_list[1], node_id='7',
        node_title='Goods Sales', initial_debit_balance=0,
        initial_credit_balance=0, debit=0, credit=500, final_debit_balance=0,
        final_credit_balance=500, final_balance_if_debit=0,
        final_balance_if_credit=500,)

    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], node_id=None, node_title=None,
        initial_debit_balance=0, initial_credit_balance=0, debit=500,
        credit=500, final_debit_balance=500, final_credit_balance=500,
        final_balance_if_debit=500, final_balance_if_credit=500)

  def testTrialBalanceNoProject(self):
    # trial balance restricted to no project
    self.createProjectAndFunctionDataSet()

    # set request variables and render
    request_form = self.portal.REQUEST.form
    request_form['from_date'] = DateTime(2006, 1, 1)
    request_form['at_date'] = DateTime(2006, 12, 31)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['stopped', 'delivered']
    request_form['per_account_class_summary'] = 0
    request_form['show_empty_accounts'] = 0
    request_form['per_account_class_summary'] = 0
    request_form['project'] = 'None'
    request_form['group_analytic'] = []
    request_form['show_detailed_balance_columns'] = 1

    report_section_list = self.getReportSectionList(
                                    self.portal.accounting_module,
                                    'AccountModule_viewTrialBalanceReport')
    self.assertEqual(1, len(report_section_list))
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(2, len(data_line_list))

    self.checkLineProperties(data_line_list[0], node_id='41',
        node_title='Receivable', initial_debit_balance=0,
        initial_credit_balance=0, debit=700, credit=0,
        final_debit_balance=700, final_credit_balance=0,
        final_balance_if_debit=700, final_balance_if_credit=0,)

    self.checkLineProperties(data_line_list[1], node_id='7',
        node_title='Goods Sales', initial_debit_balance=0,
        initial_credit_balance=0, debit=0, credit=700, final_debit_balance=0,
        final_credit_balance=700, final_balance_if_debit=0,
        final_balance_if_credit=700,)

    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], node_id=None, node_title=None,
        initial_debit_balance=0, initial_credit_balance=0, debit=700,
        credit=700, final_debit_balance=700, final_credit_balance=700,
        final_balance_if_debit=700, final_balance_if_credit=700)


  def testTrialBalanceMirrorSectionRole(self):
    # trial balance restricted to a mirror section role
    self.createMirrorSectionRoleDataSet()

    # set request variables and render
    request_form = self.portal.REQUEST.form
    request_form['from_date'] = DateTime(2006, 1, 1)
    request_form['at_date'] = DateTime(2006, 12, 31)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['stopped', 'delivered']
    request_form['mirror_section_category_list'] = ['role/supplier']
    request_form['per_account_class_summary'] = 0
    request_form['show_empty_accounts'] = 0
    request_form['per_account_class_summary'] = 0
    request_form['group_analytic'] = []
    request_form['show_detailed_balance_columns'] = 1

    report_section_list = self.getReportSectionList(
                                    self.portal.accounting_module,
                                    'AccountModule_viewTrialBalanceReport')
    self.assertEqual(1, len(report_section_list))
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(2, len(data_line_list))

    self.checkLineProperties(data_line_list[0], node_id='41',
        node_title='Receivable', initial_debit_balance=0,
        initial_credit_balance=0, debit=300, credit=0,
        final_debit_balance=300, final_credit_balance=0,
        final_balance_if_debit=300, final_balance_if_credit=0,)

    self.checkLineProperties(data_line_list[1], node_id='7',
        node_title='Goods Sales', initial_debit_balance=0,
        initial_credit_balance=0, debit=0, credit=300, final_debit_balance=0,
        final_credit_balance=300, final_balance_if_debit=0,
        final_balance_if_credit=300,)

    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], node_id=None, node_title=None,
        initial_debit_balance=0, initial_credit_balance=0, debit=300,
        credit=300, final_debit_balance=300, final_credit_balance=300,
        final_balance_if_debit=300, final_balance_if_credit=300)

  def testTrialBalanceLedger(self):
    # trial balance restricted to a ledger
    self.createLedgerDataSet()

    # set request variables and render
    request_form = self.portal.REQUEST.form
    request_form['from_date'] = DateTime(2006, 1, 1)
    request_form['at_date'] = DateTime(2006, 12, 31)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['stopped', 'delivered']
    request_form['show_empty_accounts'] = 0
    request_form['expand_accounts'] = 0
    request_form['per_account_class_summary'] = 0
    request_form['portal_type'] = ['Sale Invoice Transaction']
    request_form['group_analytic'] = []
    request_form['show_detailed_balance_columns'] = 1

    # only get transactions belonging to ledger.accounting.general
    request_form['ledger'] = 'ledger/accounting/general'

    report_section_list = self.getReportSectionList(
                                    self.portal.accounting_module,
                                    'AccountModule_viewTrialBalanceReport')
    self.assertEqual(1, len(report_section_list))
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(2, len(data_line_list))

    self.checkLineProperties(data_line_list[0], node_id='41',
        node_title='Receivable', initial_debit_balance=0,
        initial_credit_balance=0, debit=500, credit=0,
        final_debit_balance=500, final_credit_balance=0,
        final_balance_if_debit=500, final_balance_if_credit=0,)

    self.checkLineProperties(data_line_list[1], node_id='7',
        node_title='Goods Sales', initial_debit_balance=0,
        initial_credit_balance=0, debit=0, credit=500, final_debit_balance=0,
        final_credit_balance=500, final_balance_if_debit=0,
        final_balance_if_credit=500,)

    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], node_id=None, node_title=None,
        initial_debit_balance=0, initial_credit_balance=0, debit=500,
        credit=500, final_debit_balance=500, final_credit_balance=500,
        final_balance_if_debit=500, final_balance_if_credit=500)

  def testTrialBalanceWithMultipleLedger(self):
    # trial balance restricted to a ledger
    self.createLedgerDataSet()

    # get a report on both ledgers
    request_form = self.portal.REQUEST.form
    request_form['from_date'] = DateTime(2006, 1, 1)
    request_form['at_date'] = DateTime(2006, 12, 31)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['stopped', 'delivered']
    request_form['show_empty_accounts'] = 0
    request_form['expand_accounts'] = 0
    request_form['per_account_class_summary'] = 0
    request_form['portal_type'] = ['Sale Invoice Transaction']
    request_form['group_analytic'] = []
    request_form['show_detailed_balance_columns'] = 1
    request_form['ledger'] = ['ledger/accounting/general',
                              'ledger/accounting/detailed']

    report_section_list = self.getReportSectionList(
                                    self.portal.accounting_module,
                                    'AccountModule_viewTrialBalanceReport')
    self.assertEqual(1, len(report_section_list))
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(2, len(data_line_list))

    self.checkLineProperties(data_line_list[0], node_id='41',
        node_title='Receivable', initial_debit_balance=0,
        initial_credit_balance=0, debit=1000, credit=0,
        final_debit_balance=1000, final_credit_balance=0,
        final_balance_if_debit=1000, final_balance_if_credit=0,)

    self.checkLineProperties(data_line_list[1], node_id='7',
        node_title='Goods Sales', initial_debit_balance=0,
        initial_credit_balance=0, debit=0, credit=1000, final_debit_balance=0,
        final_credit_balance=1000, final_balance_if_debit=0,
        final_balance_if_credit=1000,)

    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], node_id=None, node_title=None,
        initial_debit_balance=0, initial_credit_balance=0, debit=1000,
        credit=1000, final_debit_balance=1000, final_credit_balance=1000,
        final_balance_if_debit=1000, final_balance_if_credit=1000)

  def testTrialBalanceNoLedger(self):
    # trial balance with no filter on ledger
    # it is expected to return a report on all movements
    self.createLedgerDataSet()

    # Document with no ledger
    self._makeOne(
              portal_type='Sale Invoice Transaction',
              title='Ledger general',
              reference='noledger',
              simulation_state='delivered',
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2006, 2, 2),
              lines=(dict(source_value=self.portal.account_module.receivable,
                          source_debit=400.0),
                     dict(source_value=self.portal.account_module.goods_sales,
                          source_credit=400.0)))

    # set request variables and render
    request_form = self.portal.REQUEST.form
    request_form['from_date'] = DateTime(2006, 1, 1)
    request_form['at_date'] = DateTime(2006, 12, 31)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['stopped', 'delivered']
    request_form['ledger'] = 'None'
    request_form['show_empty_accounts'] = 0
    request_form['expand_accounts'] = 0
    request_form['per_account_class_summary'] = 0
    request_form['portal_type'] = ['Sale Invoice Transaction']
    request_form['group_analytic'] = []
    request_form['show_detailed_balance_columns'] = 1

    report_section_list = self.getReportSectionList(
                                    self.portal.accounting_module,
                                    'AccountModule_viewTrialBalanceReport')
    self.assertEqual(1, len(report_section_list))
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(2, len(data_line_list))

    self.checkLineProperties(data_line_list[0], node_id='41',
        node_title='Receivable', initial_debit_balance=0,
        initial_credit_balance=0, debit=400, credit=0,
        final_debit_balance=400, final_credit_balance=0,
        final_balance_if_debit=400, final_balance_if_credit=0,)

    self.checkLineProperties(data_line_list[1], node_id='7',
        node_title='Goods Sales', initial_debit_balance=0,
        initial_credit_balance=0, debit=0, credit=400, final_debit_balance=0,
        final_credit_balance=400, final_balance_if_debit=0,
        final_balance_if_credit=400,)

    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], node_id=None, node_title=None,
        initial_debit_balance=0, initial_credit_balance=0, debit=400,
        credit=400, final_debit_balance=400, final_credit_balance=400,
        final_balance_if_debit=400, final_balance_if_credit=400)

  def testGeneralLedger(self):
    # Simple test of general ledger
    # we will use the same data set as account statement
    self.createAccountStatementDataSet(use_two_bank_accounts=0)

    # set request variables and render
    request_form = self.portal.REQUEST.form
    request_form['from_date'] = DateTime(2006, 1, 1)
    request_form['at_date'] = DateTime(2006, 12, 31)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']
    request_form['hide_analytic'] = False
    request_form['export'] = False

    report_section_list = self.getReportSectionList(
                                    self.portal.accounting_module,
                                    'AccountModule_viewGeneralLedgerReport')
    self.assertEqual(6, len(report_section_list))

    self.assertEqual('40 - Payable (Client 1)',
                      report_section_list[0].getTitle())
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]

    # The box showing parameters summary in
    # Account_viewAccountingTransactionList is not rendered here.
    report_section = report_section_list[0]
    report_section.pushReport(self.portal)
    form = getattr(self.portal, report_section.form_id)
    # we test that this form only shows a listbox
    for group in form.get_groups():
      if group != 'hidden':
        for field in form.get_fields_in_group(group):
          if field.getId() != 'listbox':
            self.fail('Field %s should not be visible' % field.getId())
    report_section.popReport(self.portal)

    # currency is present in the report
    self.assertEqual('currency_module/euro', self.portal.
        AccountModule_viewGeneralLedgerReport.your_currency.get_value('default'))

    # report layout
    self.assertEqual( ['date', 'Movement_getSpecificReference', 'mirror_section_title',
        'Movement_getExplanationTitleAndAnalytics', 'debit_price',
        'credit_price', 'running_total_price', 'grouping_reference',
        'grouping_date', 'getTranslatedSimulationStateTitle'],
        data_line_list[0].column_id_list)

    self.assertEqual(2, len(data_line_list))
    self.checkLineProperties(data_line_list[0],
          Movement_getSpecificReference='1',
          mirror_section_title='Client 1',
          Movement_getExplanationTitleAndAnalytics='Transaction 1\nref1',
          date=DateTime(2006, 2, 1),
          debit_price=0, credit_price=100, running_total_price=-100, )

    self.checkLineProperties(data_line_list[1],
          Movement_getSpecificReference='2',
          Movement_getExplanationTitleAndAnalytics='Transaction 2\nref2',
          date=DateTime(2006, 2, 1, 0, 1),
          debit_price=200, credit_price=0, running_total_price=100, )

    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1],
          Movement_getSpecificReference=None,
          Movement_getExplanationTitleAndAnalytics=None,
          date=None,
          debit_price=200, credit_price=100, )

    self.assertEqual('41 - Receivable (Client 1)',
                      report_section_list[1].getTitle())
    line_list = self.getListBoxLineList(report_section_list[1])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(5, len(data_line_list))
    self.checkLineProperties(data_line_list[0],
          Movement_getSpecificReference='1',
          Movement_getExplanationTitleAndAnalytics='Transaction 1\nref1',
          date=DateTime(2006, 2, 1),
          debit_price=100, credit_price=0, running_total_price=100, )

    self.checkLineProperties(data_line_list[1],
          Movement_getSpecificReference='2',
          Movement_getExplanationTitleAndAnalytics='Transaction 2\nref2',
          date=DateTime(2006, 2, 1, 0, 1),
          debit_price=0, credit_price=200, running_total_price=-100, )

    self.checkLineProperties(data_line_list[2],
          Movement_getSpecificReference='3',
          Movement_getExplanationTitleAndAnalytics='Transaction 3\nref3',
          date=DateTime(2006, 2, 2, 0, 2),
          debit_price=300, credit_price=0, running_total_price=200, )

    self.checkLineProperties(data_line_list[3],
          Movement_getSpecificReference='6',
          Movement_getExplanationTitleAndAnalytics='Transaction 6\nref6',
          date=DateTime(2006, 2, 2, 0, 5),
          debit_price=600, credit_price=0, running_total_price=800, )

    self.checkLineProperties(data_line_list[4],
          Movement_getSpecificReference='8',
          Movement_getExplanationTitleAndAnalytics='Transaction 8\nref8',
          date=DateTime(2006, 2, 3),
          debit_price=800, credit_price=0, running_total_price=1600, )

    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1],
          Movement_getSpecificReference=None,
          Movement_getExplanationTitleAndAnalytics=None,
          date=None,
          debit_price=1800, credit_price=200, )

    self.assertEqual('41 - Receivable (Client 2)',
                      report_section_list[2].getTitle())
    line_list = self.getListBoxLineList(report_section_list[2])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(1, len(data_line_list))
    self.checkLineProperties(data_line_list[0],
          Movement_getSpecificReference='4',
          Movement_getExplanationTitleAndAnalytics='Transaction 4\nref4',
          date=DateTime(2006, 2, 2, 0, 3),
          debit_price=400, credit_price=0, running_total_price=400, )

    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], debit_price=400, credit_price=0, )

    self.assertEqual('41 - Receivable (John Smith)',
                      report_section_list[3].getTitle())
    line_list = self.getListBoxLineList(report_section_list[3])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(1, len(data_line_list))
    self.checkLineProperties(data_line_list[0],
          Movement_getSpecificReference='5',
          Movement_getExplanationTitleAndAnalytics='Transaction 5\nref5',
          date=DateTime(2006, 2, 2, 0, 4),
          debit_price=500, credit_price=0, running_total_price=500, )

    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], debit_price=500, credit_price=0, )

    self.assertEqual('5 - Bank (Bank1)',
                      report_section_list[4].getTitle())
    line_list = self.getListBoxLineList(report_section_list[4])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(5, len(data_line_list))
    self.checkLineProperties(data_line_list[0],
          Movement_getSpecificReference='3',
          Movement_getExplanationTitleAndAnalytics='Transaction 3\nref3',
          date=DateTime(2006, 2, 2, 0, 2),
          debit_price=0, credit_price=300, running_total_price=-300, )

    self.checkLineProperties(data_line_list[1],
          Movement_getSpecificReference='4',
          Movement_getExplanationTitleAndAnalytics='Transaction 4\nref4',
          date=DateTime(2006, 2, 2, 0, 3),
          debit_price=0, credit_price=400, running_total_price=-700, )

    self.checkLineProperties(data_line_list[2],
          Movement_getSpecificReference='5',
          Movement_getExplanationTitleAndAnalytics='Transaction 5\nref5',
          date=DateTime(2006, 2, 2, 0, 4),
          debit_price=0, credit_price=500, running_total_price=-1200, )

    self.checkLineProperties(data_line_list[3],
          Movement_getSpecificReference='6',
          Movement_getExplanationTitleAndAnalytics='Transaction 6\nref6',
          date=DateTime(2006, 2, 2, 0, 5),
          debit_price=0, credit_price=600, running_total_price=-1800, )

    self.checkLineProperties(data_line_list[4],
          Movement_getSpecificReference='8',
          Movement_getExplanationTitleAndAnalytics='Transaction 8\nref8',
          date=DateTime(2006, 2, 3),
          debit_price=0, credit_price=800, running_total_price=-2600, )

    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], debit_price=0, credit_price=2600, )

    self.assertEqual('Total', report_section_list[5].getTitle())
    line_list = self.getListBoxLineList(report_section_list[5])
    data_line_list = [l for l in line_list if l.isDataLine()]
    # report layout
    self.assertEqual(['debit_price', 'credit_price'], data_line_list[0].column_id_list)
    self.assertEqual(1, len(data_line_list))
    self.checkLineProperties(data_line_list[0], debit_price=2900, credit_price=2900)

  def testGeneralLedgerInitialBalance(self):
    # Initial balance line on GL
    # we will use the same data set as account statement
    self.createAccountStatementDataSetOnTwoPeriods()

    # set request variables and render
    request_form = self.portal.REQUEST.form
    request_form['from_date'] = DateTime(2006, 2, 1)
    request_form['at_date'] = DateTime(2006, 12, 31)
    request_form['gap_list'] = [
        'my_country/my_accounting_standards/4/41']
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']
    request_form['hide_analytic'] = False
    request_form['export'] = False

    report_section_list = self.getReportSectionList(
        self.portal.accounting_module,
        'AccountModule_viewGeneralLedgerReport')
    self.assertEqual(2, len(report_section_list))

    self.assertEqual(
        '41 - Receivable (Client 1)',
        report_section_list[0].getTitle())
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]

    self.assertEqual(2, len(data_line_list))
    self.checkLineProperties(
        data_line_list[0],
        Movement_getSpecificReference='Previous Balance',
        mirror_section_title='Client 1',
        date=DateTime(2006, 2, 1),
        debit_price=300,
        credit_price=0,
        running_total_price=300, )

    self.checkLineProperties(
        data_line_list[1],
        Movement_getSpecificReference='3',
        Movement_getExplanationTitleAndAnalytics='Transaction 3\nref3',
        date=DateTime(2006, 2, 2),
        debit_price=300,
        credit_price=0,
        running_total_price=600, )

    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1],
          Movement_getSpecificReference=None,
          Movement_getExplanationTitleAndAnalytics=None,
          date=None,
          debit_price=600, credit_price=0, )

    self.assertEqual('Total', report_section_list[1].getTitle())
    line_list = self.getListBoxLineList(report_section_list[1])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(1, len(data_line_list))
    self.checkLineProperties(
        data_line_list[0],
        debit_price=600,
        credit_price=0)

  def testGeneralLedgerExportInitialBalance(self):
    # Initial balance on GL export
    # we will use the same data set as account statement
    self.createAccountStatementDataSetOnTwoPeriods()

    # set request variables and render
    request_form = self.portal.REQUEST.form
    request_form['from_date'] = DateTime(2006, 2, 1)
    request_form['at_date'] = DateTime(2006, 12, 31)
    request_form['gap_list'] = [
        'my_country/my_accounting_standards/4/41']
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']
    request_form['hide_analytic'] = False
    request_form['export'] = True

    report_section_list = self.getReportSectionList(
        self.portal.accounting_module,
        'AccountModule_viewGeneralLedgerReport')
    self.assertEqual(1, len(report_section_list))

    # export mode has no section headers
    self.assertEqual(None, report_section_list[0].getTitle())
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]

    self.assertEqual(2, len(data_line_list))
    self.checkLineProperties(
        data_line_list[0],
        Movement_getSpecificReference='Previous Balance',
        mirror_section_title='Client 1',
        date=DateTime(2006, 2, 1),
        debit_price=300,
        credit_price=0, )

    self.checkLineProperties(
        data_line_list[1],
        Movement_getSpecificReference='3',
        mirror_section_title='Client 1',
        date=DateTime(2006, 2, 2),
        debit_price=300,
        credit_price=0, )

    self.assertFalse(line_list[-1].isStatLine())

  def testGeneralLedgerGAPFilter(self):
    # General Ledger filtered by GAP category
    # we will use the same data set as account statement
    self.createAccountStatementDataSet(use_two_bank_accounts=0)

    # set request variables and render
    request_form = self.portal.REQUEST.form
    request_form['from_date'] = DateTime(2006, 1, 1)
    request_form['at_date'] = DateTime(2006, 12, 31)
    request_form['gap_list'] = ['my_country/my_accounting_standards/4/40']
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']
    request_form['hide_analytic'] = False
    request_form['export'] = False

    report_section_list = self.getReportSectionList(
                                    self.portal.accounting_module,
                                    'AccountModule_viewGeneralLedgerReport')
    self.assertEqual(2, len(report_section_list))

    self.assertEqual('40 - Payable (Client 1)',
                      report_section_list[0].getTitle())
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]

    self.assertEqual(2, len(data_line_list))
    self.checkLineProperties(data_line_list[0],
          Movement_getSpecificReference='1',
          Movement_getExplanationTitleAndAnalytics='Transaction 1\nref1',
          date=DateTime(2006, 2, 1),
          debit_price=0, credit_price=100, running_total_price=-100, )

    self.checkLineProperties(data_line_list[1],
          Movement_getSpecificReference='2',
          Movement_getExplanationTitleAndAnalytics='Transaction 2\nref2',
          date=DateTime(2006, 2, 1, 0, 1),
          debit_price=200, credit_price=0, running_total_price=100, )

    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1],
          Movement_getSpecificReference=None,
          Movement_getExplanationTitleAndAnalytics=None,
          date=None,
          debit_price=200, credit_price=100, )

    self.assertEqual('Total', report_section_list[1].getTitle())
    line_list = self.getListBoxLineList(report_section_list[1])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(1, len(data_line_list))
    self.checkLineProperties(data_line_list[0], debit_price=200, credit_price=100)

  def testGeneralLedgerGAPFilterSameGAPSelectedTwice(self):
    # General Ledger filtered by GAP category. Edge case: selecting
    # a gap and its parent. This use to double the amount because
    # node is twice member of node_category

    # we will use the same data set as account statement
    self.createAccountStatementDataSetOnTwoPeriods()

    # set request variables and render
    request_form = self.portal.REQUEST.form
    request_form['from_date'] = DateTime(2006, 2, 1)
    request_form['at_date'] = DateTime(2006, 12, 31)
    # Here we select 4 and 41
    request_form['gap_list'] = [
        'my_country/my_accounting_standards/4',
        'my_country/my_accounting_standards/4/41']

    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']
    request_form['hide_analytic'] = False
    request_form['export'] = False

    report_section_list = self.getReportSectionList(
        self.portal.accounting_module,
        'AccountModule_viewGeneralLedgerReport')
    self.assertEqual(2, len(report_section_list))

    self.assertEqual(
        '41 - Receivable (Client 1)',
        report_section_list[0].getTitle())
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]

    self.assertEqual(2, len(data_line_list))
    self.checkLineProperties(
        data_line_list[0],
        Movement_getSpecificReference='Previous Balance',
        date=DateTime(2006, 2, 1),
        debit_price=300,
        credit_price=0,
        running_total_price=300, )

    self.checkLineProperties(
        data_line_list[1],
        Movement_getSpecificReference='3',
        Movement_getExplanationTitleAndAnalytics='Transaction 3\nref3',
        date=DateTime(2006, 2, 2),
        debit_price=300,
        credit_price=0,
        running_total_price=600, )

    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1],
          Movement_getSpecificReference=None,
          Movement_getExplanationTitleAndAnalytics=None,
          date=None,
          debit_price=600, credit_price=0, )

    self.assertEqual('Total', report_section_list[1].getTitle())
    line_list = self.getListBoxLineList(report_section_list[1])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(1, len(data_line_list))
    self.checkLineProperties(
        data_line_list[0],
        debit_price=600,
        credit_price=0)

  def testGeneralLedgerFunction(self):
    # general ledger restricted to a function
    self.createProjectAndFunctionDataSet()

    request_form = self.portal.REQUEST.form
    request_form['from_date'] = DateTime(2006, 1, 1)
    request_form['at_date'] = DateTime(2006, 12, 31)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']
    request_form['function'] = 'function/a'
    request_form['hide_analytic'] = False
    request_form['export'] = False

    report_section_list = self.getReportSectionList(
                                    self.portal.accounting_module,
                                    'AccountModule_viewGeneralLedgerReport')
    self.assertEqual(3, len(report_section_list))

    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(1, len(data_line_list))
    self.checkLineProperties(data_line_list[0],
          Movement_getSpecificReference='1',
          Movement_getExplanationTitleAndAnalytics=
            'Function a Project 1\nFaP1',
          date=DateTime(2006, 2, 2),
          debit_price=500, credit_price=0, running_total_price=500, )
    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], debit_price=500, credit_price=0)

    line_list = self.getListBoxLineList(report_section_list[1])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(1, len(data_line_list))
    self.checkLineProperties(data_line_list[0],
          Movement_getSpecificReference='1',
          Movement_getExplanationTitleAndAnalytics=
            'Function a Project 1\nFaP1',
          date=DateTime(2006, 2, 2),
          debit_price=0, credit_price=500, running_total_price=-500, )
    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], debit_price=0, credit_price=500)

    line_list = self.getListBoxLineList(report_section_list[2])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(1, len(data_line_list))
    self.checkLineProperties(data_line_list[0], debit_price=500, credit_price=500)

  def testGeneralLedgerNoProject(self):
    # general ledger restricted to no project
    self.createProjectAndFunctionDataSet()

    request_form = self.portal.REQUEST.form
    request_form['from_date'] = DateTime(2006, 1, 1)
    request_form['at_date'] = DateTime(2006, 12, 31)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']
    request_form['project'] = 'None'
    request_form['hide_analytic'] = False
    request_form['export'] = False

    report_section_list = self.getReportSectionList(
                                    self.portal.accounting_module,
                                    'AccountModule_viewGeneralLedgerReport')
    self.assertEqual(3, len(report_section_list))

    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(1, len(data_line_list))
    self.checkLineProperties(data_line_list[0],
          Movement_getSpecificReference='3',
          Movement_getExplanationTitleAndAnalytics='No function no project\nnono',
          date=DateTime(2006, 2, 2),
          debit_price=700, credit_price=0, running_total_price=700, )
    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], debit_price=700, credit_price=0)

    line_list = self.getListBoxLineList(report_section_list[1])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(1, len(data_line_list))
    self.checkLineProperties(data_line_list[0],
          Movement_getSpecificReference='3',
          Movement_getExplanationTitleAndAnalytics='No function no project\nnono',
          date=DateTime(2006, 2, 2),
          debit_price=0, credit_price=700, running_total_price=-700, )
    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], debit_price=0, credit_price=700)

    line_list = self.getListBoxLineList(report_section_list[2])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(1, len(data_line_list))
    self.checkLineProperties(data_line_list[0], debit_price=700,
        credit_price=700)

  def testGeneralLedgerProject(self):
    # general ledger restricted to a project
    self.createProjectAndFunctionDataSet()

    request_form = self.portal.REQUEST.form
    request_form['from_date'] = DateTime(2006, 1, 1)
    request_form['at_date'] = DateTime(2006, 12, 31)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']
    request_form['project'] = self.project_1.getRelativeUrl()
    request_form['hide_analytic'] = False
    request_form['export'] = False

    report_section_list = self.getReportSectionList(
                                    self.portal.accounting_module,
                                    'AccountModule_viewGeneralLedgerReport')
    self.assertEqual(3, len(report_section_list))

    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(1, len(data_line_list))
    self.checkLineProperties(data_line_list[0],
          Movement_getSpecificReference='1',
          Movement_getExplanationTitleAndAnalytics='Function a Project 1\nFaP1',
          date=DateTime(2006, 2, 2),
          debit_price=500, credit_price=0, running_total_price=500, )
    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], debit_price=500, credit_price=0)

    line_list = self.getListBoxLineList(report_section_list[1])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(1, len(data_line_list))
    self.checkLineProperties(data_line_list[0],
          Movement_getSpecificReference='1',
          Movement_getExplanationTitleAndAnalytics='Function a Project 1\nFaP1',
          date=DateTime(2006, 2, 2),
          debit_price=0, credit_price=500, running_total_price=-500, )
    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], debit_price=0, credit_price=500)

    line_list = self.getListBoxLineList(report_section_list[2])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(1, len(data_line_list))
    self.checkLineProperties(data_line_list[0], debit_price=500, credit_price=500)

  def testGeneralLedgerLedger(self):
    # general ledger restricted to a ledger
    self.createLedgerDataSet()

    request_form = self.portal.REQUEST.form
    request_form['from_date'] = DateTime(2006, 1, 1)
    request_form['at_date'] = DateTime(2006, 12, 31)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']
    request_form['ledger'] = 'ledger/accounting/general'
    request_form['hide_analytic'] = False
    request_form['export'] = False

    report_section_list = self.getReportSectionList(
                                    self.portal.accounting_module,
                                    'AccountModule_viewGeneralLedgerReport')
    self.assertEqual(3, len(report_section_list))

    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(1, len(data_line_list))
    self.checkLineProperties(data_line_list[0],
          Movement_getExplanationTitleAndAnalytics='Ledger general\nlag',
          date=DateTime(2006, 2, 2),
          debit_price=500, credit_price=0, running_total_price=500, )
    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], debit_price=500, credit_price=0)

    line_list = self.getListBoxLineList(report_section_list[1])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(1, len(data_line_list))
    self.checkLineProperties(data_line_list[0],
          Movement_getExplanationTitleAndAnalytics='Ledger general\nlag',
          date=DateTime(2006, 2, 2),
          debit_price=0, credit_price=500, running_total_price=-500, )
    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], debit_price=0, credit_price=500)

    line_list = self.getListBoxLineList(report_section_list[2])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(1, len(data_line_list))
    self.checkLineProperties(data_line_list[0], debit_price=500, credit_price=500)

  def testGeneralLedgerMirrorSectionRole(self):
    # general ledger restricted to a mirror section role
    self.createMirrorSectionRoleDataSet()

    request_form = self.portal.REQUEST.form
    request_form['from_date'] = DateTime(2006, 1, 1)
    request_form['at_date'] = DateTime(2006, 12, 31)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']
    request_form['mirror_section_category_list'] = ['role/supplier']
    request_form['hide_analytic'] = False
    request_form['export'] = False

    report_section_list = self.getReportSectionList(
                                    self.portal.accounting_module,
                                    'AccountModule_viewGeneralLedgerReport')
    self.assertEqual(3, len(report_section_list))

    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(1, len(data_line_list))
    self.checkLineProperties(data_line_list[0],
          Movement_getSpecificReference='2',
          Movement_getExplanationTitleAndAnalytics='Invoice to a supplier\nIs',
          date=DateTime(2006, 2, 2),
          debit_price=300, credit_price=0, running_total_price=300, )
    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], debit_price=300, credit_price=0)

    line_list = self.getListBoxLineList(report_section_list[1])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(1, len(data_line_list))
    self.checkLineProperties(data_line_list[0],
          Movement_getSpecificReference='2',
          Movement_getExplanationTitleAndAnalytics='Invoice to a supplier\nIs',
          date=DateTime(2006, 2, 2),
          debit_price=0, credit_price=300, running_total_price=-300, )
    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], debit_price=0, credit_price=300)

    line_list = self.getListBoxLineList(report_section_list[2])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(1, len(data_line_list))
    self.checkLineProperties(data_line_list[0], debit_price=300,
                             credit_price=300)

  def testProfitAndLoss(self):
    # Simple test of profit and loss
    self.createAccountStatementDataSet(use_two_bank_accounts=1)

    # set request variables and render
    request_form = self.portal.REQUEST.form
    request_form['at_date'] = DateTime(2006, 12, 31)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']

    # for now, we simply check that that the report is rendered with no error
    # and it produces valid odf
    from Products.ERP5OOo.tests.utils import Validator
    odf_validator = Validator()
    odf = self.portal.account_module.AccountModule_viewProfitAndLossReport()
    err_list = odf_validator.validate(odf)
    if err_list:
      self.fail(''.join(err_list))


  def testBalanceSheet(self):
    # Simple test of balance sheet
    self.createAccountStatementDataSet(use_two_bank_accounts=1)

    # set request variables and render
    request_form = self.portal.REQUEST.form
    request_form['at_date'] = DateTime(2006, 12, 31)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']

    # for now, we simply check that that the report is rendered with no error
    # and it produces valid odf
    from Products.ERP5OOo.tests.utils import Validator
    odf_validator = Validator()
    odf = self.portal.account_module.AccountModule_viewBalanceSheetReport()
    err_list = odf_validator.validate(odf)
    if err_list:
      self.fail(''.join(err_list))

  def testOtherPartiesReport(self):
    # Other parties report
    account_module = self.portal.account_module
    t1 = self._makeOne(
              portal_type='Accounting Transaction',
              title='Transaction 1',
              source_reference='1',
              simulation_state='delivered',
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2006, 2, 1),
              lines=(dict(source_value=account_module.receivable,
                          source_debit=100.0),
                     dict(source_value=account_module.goods_sales,
                          source_credit=100.0)))

    t2 = self._makeOne(
              portal_type='Accounting Transaction',
              title='Transaction 2',
              source_reference='2',
              simulation_state='delivered',
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2006, 2, 1, 0, 1),
              lines=(dict(source_value=account_module.payable,
                          source_debit=200.0),
                     dict(source_value=account_module.goods_sales,
                          source_credit=200.0)))

    request_form = self.portal.REQUEST.form
    request_form['at_date'] = DateTime(2006, 2, 1)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']
    request_form['omit_balanced_accounts'] = False
    request_form['omit_grouping_reference'] = True

    report_section_list = self.getReportSectionList(
                               self.portal.accounting_module,
                               'AccountModule_viewOtherPartiesReport')
    self.assertEqual(1, len(report_section_list))
    # the role is displayed in parenthesis
    self.assertEqual(report_section_list[0].getTitle(),
                      'Client 1 (Client)')
    # currency is present in the report
    self.assertEqual('currency_module/euro', self.portal.
        AccountModule_viewOtherPartiesReport.your_currency.get_value('default'))

    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(2, len(data_line_list))

    self.checkLineProperties(data_line_list[0],
          Movement_getExplanationTitle='Transaction 1',
          Movement_getExplanationTranslatedPortalType='Accounting Transaction',
          Movement_getNodeGapId='41',
          credit_price=0,
          debit_price=100,
          date=DateTime('2006/02/01'),
          getTranslatedSimulationStateTitle='Closed',
          running_total_price=100.0)

    self.checkLineProperties(data_line_list[1],
          Movement_getExplanationTitle='Transaction 2',
          Movement_getExplanationTranslatedPortalType='Accounting Transaction',
          Movement_getNodeGapId='40',
          credit_price=0,
          debit_price=200,
          date=DateTime(2006, 2, 1, 0, 1),
          getTranslatedSimulationStateTitle='Closed',
          running_total_price=300.0)

    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1],
          credit_price=0,
          debit_price=300,)

  def testOtherPartiesReportLedger(self):
    # Other parties report with a filter on ledger
    # This tests works because /for the moment/ any transaction between 2
    # entities belong to the same ledger
    self.createLedgerCategory()
    account_module = self.portal.account_module
    t1 = self._makeOne(
              portal_type='Accounting Transaction',
              title='Transaction 1',
              source_reference='1',
              simulation_state='delivered',
              ledger='accounting/general',
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2006, 2, 1),
              lines=(dict(source_value=account_module.receivable,
                          source_debit=100.0),
                     dict(source_value=account_module.goods_sales,
                          source_credit=100.0)))

    t2 = self._makeOne(
              portal_type='Accounting Transaction',
              title='Transaction 2',
              source_reference='2',
              simulation_state='delivered',
              ledger='accounting/general',
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2006, 2, 1, 0, 1),
              lines=(dict(source_value=account_module.payable,
                          source_debit=200.0),
                     dict(source_value=account_module.goods_sales,
                          source_credit=200.0)))

    t3 = self._makeOne(
              portal_type='Accounting Transaction',
              title='Transaction 3',
              source_reference='3',
              simulation_state='delivered',
              ledger='accounting/detailed',
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2006, 2, 1, 0, 2),
              lines=(dict(source_value=account_module.payable,
                          source_debit=400.0),
                     dict(source_value=account_module.goods_sales,
                          source_credit=400.0)))

    request_form = self.portal.REQUEST.form
    request_form['at_date'] = DateTime(2006, 2, 1)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']
    request_form['ledger'] = 'ledger/accounting/general'
    request_form['omit_balanced_accounts'] = False
    request_form['omit_grouping_reference'] = True

    report_section_list = self.getReportSectionList(
                               self.portal.accounting_module,
                               'AccountModule_viewOtherPartiesReport')
    self.assertEqual(1, len(report_section_list))
    # the role is displayed in parenthesis
    self.assertEqual(report_section_list[0].getTitle(),
                      'Client 1 (Client)')
    # currency is present in the report
    self.assertEqual('currency_module/euro', self.portal.
        AccountModule_viewOtherPartiesReport.your_currency.get_value('default'))

    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(2, len(data_line_list))

    self.checkLineProperties(data_line_list[0],
          Movement_getExplanationTitle='Transaction 1',
          Movement_getExplanationTranslatedPortalType='Accounting Transaction',
          Movement_getNodeGapId='41',
          credit_price=0,
          debit_price=100,
          date=DateTime('2006/02/01'),
          getTranslatedSimulationStateTitle='Closed',
          running_total_price=100.0)

    self.checkLineProperties(data_line_list[1],
          Movement_getExplanationTitle='Transaction 2',
          Movement_getExplanationTranslatedPortalType='Accounting Transaction',
          Movement_getNodeGapId='40',
          credit_price=0,
          debit_price=200,
          date=DateTime(2006, 2, 1, 0, 1),
          getTranslatedSimulationStateTitle='Closed',
          running_total_price=300.0)

    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1],
          credit_price=0,
          debit_price=300,)

  def createAgedBalanceDataSet(self, use_ledger=False):
    """Create data set for aged balance:
    2013/07/30: Purchase invoice 1 (500)
    2013/07/30: Sale invoice 2 (300)
    2013/09/09: Payment 1 (500)
    2013/08/08: Payment 2 (300)
    """
    account_module = self.account_module
    bank1 = self.section.newContent(portal_type='Bank Account', title='Bank1')
    bank1.validate()

    purchase1 = self._makeOne(
              portal_type='Purchase Invoice Transaction',
              title='Purchase invoice 1',
              destination_reference='1',
              source_reference='no',
              reference='ref1',
              simulation_state='delivered',
              ledger=('' if not use_ledger else 'accounting/general'),
              source_section_value=self.organisation_module.supplier,
              start_date=DateTime(2013, 7, 30),
              lines=(dict(destination_value=account_module.goods_purchase,
                          destination_debit=500.0),
                     dict(destination_value=account_module.payable,
                          destination_credit=500.0)))
    sale2 = self._makeOne(
              portal_type='Sale Invoice Transaction',
              title='Sale invoice 2',
              source_reference='2',
              destination_reference='no',
              reference='ref2',
              simulation_state='delivered',
              ledger=('' if not use_ledger else 'accounting/general'),
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2013, 7, 30),
              lines=(dict(source_value=account_module.goods_sales,
                          source_credit=300.0),
                     dict(source_value=account_module.receivable,
                          source_debit=300.0),))
    self.tic()
    payment3 = self._makeOne(
              portal_type='Payment Transaction',
              title='Payment 1',
              source_reference='3',
              destination_reference='no',
              simulation_state='delivered',
              ledger=('' if not use_ledger else 'accounting/general'),
              causality_value=purchase1,
              payment_mode='payment_mode',
              destination_section_value=self.organisation_module.supplier,
              start_date=DateTime(2013, 9, 9),
              lines=(dict(source_value=account_module.payable,
                          source_debit=500.0),
                     dict(source_value=account_module.bank,
                          source_credit=500.0)))

    payment4 = self._makeOne(
              portal_type='Payment Transaction',
              title='Payment 2',
              source_reference='4',
              destination_reference='4',
              simulation_state='delivered',
              causality_value=sale2,
              payment_mode='payment_mode',
              ledger=('' if not use_ledger else 'accounting/general'),
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2013, 8, 8),
              lines=(dict(source_value=account_module.bank,
                          source_debit=300.0),
                     dict(source_value=account_module.receivable,
                          source_credit=300.0)))
    self.tic()

    transaction_list = [purchase1, sale2, payment3, payment4]

    if use_ledger:
      self.createLedgerCategory()

      purchase5 = self._makeOne(
            portal_type='Purchase Invoice Transaction',
            title='Purchase invoice 3',
            destination_reference='5',
            source_reference='no',
            reference='ref5',
            simulation_state='delivered',
            ledger='accounting/detailed',
            source_section_value=self.organisation_module.supplier,
            start_date=DateTime(2013, 7, 30),
            lines=(dict(destination_value=account_module.goods_purchase,
                        destination_debit=700.0),
                   dict(destination_value=account_module.payable,
                        destination_credit=700.0)))
      sale6 = self._makeOne(
                portal_type='Sale Invoice Transaction',
                title='Sale invoice 4',
                source_reference='5',
                destination_reference='no',
                reference='ref6',
                simulation_state='delivered',
                ledger='accounting/detailed',
                destination_section_value=self.organisation_module.client_1,
                start_date=DateTime(2013, 7, 30),
                lines=(dict(source_value=account_module.goods_sales,
                            source_credit=900.0),
                       dict(source_value=account_module.receivable,
                            source_debit=900.0),))
      self.tic()

      payment7 = self._makeOne(
          portal_type='Payment Transaction',
          title='Payment 3',
          source_reference='6',
          destination_reference='no',
          simulation_state='delivered',
          ledger='accounting/detailed',
          causality_value=purchase5,
          payment_mode='payment_mode',
          destination_section_value=self.organisation_module.supplier,
          start_date=DateTime(2013, 9, 9),
          lines=(dict(source_value=account_module.payable,
                      source_debit=700.0),
                 dict(source_value=account_module.bank,
                      source_credit=700.0)))
      payment8 = self._makeOne(
              portal_type='Payment Transaction',
              title='Payment 4',
              source_reference='7',
              destination_reference='7',
              simulation_state='delivered',
              causality_value=sale6,
              payment_mode='payment_mode',
              ledger='accounting/detailed',
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2013, 8, 8),
              lines=(dict(source_value=account_module.bank,
                          source_debit=900.0),
                     dict(source_value=account_module.receivable,
                          source_credit=900.0)))
      self.tic()

      transaction_list.extend([purchase5, sale6, payment7, payment8])

    # we should have all receivable and payable lines grouped.
    for at in transaction_list:
      for line in at.getMovementList():
        if line.getSourceValue() in (account_module.receivable,
                                     account_module.payable) or\
      line.getDestinationValue() in (account_module.receivable,
                                     account_module.payable):
          self.assertTrue(line.getGroupingReference())
          self.assertTrue(line.getGroupingDate())

  def test_simple_aged_creditor_report_detailed(self):
    self.createAgedBalanceDataSet()
    request_form = self.portal.REQUEST.form
    request_form['at_date'] = DateTime(2013, 8, 1)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['detailed'] = True
    request_form['account_type'] = 'account_type/asset/receivable'
    request_form['period_list'] = (1, 2, 3)
    request_form['simulation_state'] = ['delivered']

    report_section_list = self.getReportSectionList(
                    self.portal.accounting_module,
                    'AccountingTransactionModule_viewAgedBalanceReport')
    self.assertEqual(1, len(report_section_list))

    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(1, len(data_line_list))

    self.checkLineProperties(data_line_list[0],
                             date=DateTime(2013, 7, 30),
                             mirror_section_title='Client 1',
                             portal_type='Sale Invoice Transaction',
                             explanation_title='Sale invoice 2',
                             total_price=300,
                             period_1=300)

  def test_simple_aged_creditor_report_summary(self):
    self.createAgedBalanceDataSet()
    request_form = self.portal.REQUEST.form
    request_form['at_date'] = DateTime(2013, 8, 1)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['detailed'] = False
    request_form['account_type'] = 'account_type/asset/receivable'
    request_form['period_list'] = (1, 2, 3)
    request_form['simulation_state'] = ['delivered']

    report_section_list = self.getReportSectionList(
                    self.portal.accounting_module,
                    'AccountingTransactionModule_viewAgedBalanceReport')
    self.assertEqual(1, len(report_section_list))

    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(1, len(data_line_list))

    self.checkLineProperties(data_line_list[0],
                             mirror_section_title='Client 1',
                             total_price=300,
                             period_1=300)

  def test_simple_aged_debtor_report_detailed(self):
    self.createAgedBalanceDataSet()
    request_form = self.portal.REQUEST.form
    request_form['at_date'] = DateTime(2013, 8, 1)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['detailed'] = True
    request_form['account_type'] = 'account_type/liability/payable'
    request_form['period_list'] = (1, 2, 3)
    request_form['simulation_state'] = ['delivered']

    report_section_list = self.getReportSectionList(
                    self.portal.accounting_module,
                    'AccountingTransactionModule_viewAgedBalanceReport')
    self.assertEqual(1, len(report_section_list))

    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(1, len(data_line_list))

    self.checkLineProperties(data_line_list[0],
                             date=DateTime(2013, 7, 30),
                             mirror_section_title='Supplier',
                             portal_type='Purchase Invoice Transaction',
                             explanation_title='Purchase invoice 1',
                             total_price=500,
                             period_1=500)

  def test_simple_aged_debtor_report_summary(self):
    self.createAgedBalanceDataSet()
    request_form = self.portal.REQUEST.form
    request_form['at_date'] = DateTime(2013, 8, 1)
    request_form['section_category_strict'] = False
    request_form['detailed'] = False
    request_form['section_category'] = 'group/demo_group'
    request_form['account_type'] = 'account_type/liability/payable'
    request_form['period_list'] = (1, 2, 3)
    request_form['simulation_state'] = ['delivered']

    report_section_list = self.getReportSectionList(
                    self.portal.accounting_module,
                    'AccountingTransactionModule_viewAgedBalanceReport')
    self.assertEqual(1, len(report_section_list))

    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(1, len(data_line_list))

    self.checkLineProperties(data_line_list[0],
                             mirror_section_title='Supplier',
                             total_price=500,
                             period_1=500)

  def test_simple_aged_creditor_with_ledger_report_summary(self):
    # Same test as above, with a filter on ledger
    # If ledger works properly, results should be the same as
    # test_simple_aged_creditor_report_summary
    self.createAgedBalanceDataSet(use_ledger=True)
    request_form = self.portal.REQUEST.form
    request_form['at_date'] = DateTime(2013, 8, 1)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['detailed'] = False
    request_form['account_type'] = 'account_type/asset/receivable'
    request_form['period_list'] = (1, 2, 3)
    request_form['simulation_state'] = ['delivered']
    request_form['ledger'] = 'ledger/accounting/general'

    report_section_list = self.getReportSectionList(
                    self.portal.accounting_module,
                    'AccountingTransactionModule_viewAgedBalanceReport')
    self.assertEqual(1, len(report_section_list))

    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(1, len(data_line_list))

    self.checkLineProperties(data_line_list[0],
                             mirror_section_title='Client 1',
                             total_price=300,
                             period_1=300)

  def test_simple_aged_debtor_with_ledger_report_summary(self):
    # Same test as above, with a filter on ledger
    # If ledger works properly, results should be the same as
    # test_simple_aged_creditor_report_summary
    self.createAgedBalanceDataSet(use_ledger=True)
    request_form = self.portal.REQUEST.form
    request_form['at_date'] = DateTime(2013, 8, 1)
    request_form['section_category_strict'] = False
    request_form['detailed'] = False
    request_form['section_category'] = 'group/demo_group'
    request_form['account_type'] = 'account_type/liability/payable'
    request_form['period_list'] = (1, 2, 3)
    request_form['simulation_state'] = ['delivered']
    request_form['ledger'] = 'ledger/accounting/general'

    report_section_list = self.getReportSectionList(
                    self.portal.accounting_module,
                    'AccountingTransactionModule_viewAgedBalanceReport')
    self.assertEqual(1, len(report_section_list))

    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(1, len(data_line_list))

    self.checkLineProperties(data_line_list[0],
                             mirror_section_title='Supplier',
                             total_price=500,
                             period_1=500)

  def test_simple_aged_debtor_report_sort_order(self):
    """Check the sort order of aged balance report.

    Lines must be sorted by third party, then by date.
    """
    zzz_supplier = self.portal.organisation_module.newContent(
        portal_type='Organisation',
        title='ZZZ Supplier'
    )
    purchase2 = self._makeOne(
        portal_type='Purchase Invoice Transaction',
        title='Purchase invoice 0',
        destination_reference='0',
        source_reference='no',
        description="This invoice should be last, because lines in aged balance "
                    "are sorted by supplier names.",
        reference='ref0',
        simulation_state='delivered',
        source_section_value=zzz_supplier,
        start_date=DateTime(2013, 6, 28),
        lines=(dict(destination_value=self.portal.account_module.goods_purchase,
                    destination_debit=300.0),
               dict(destination_value=self.portal.account_module.payable,
                    destination_credit=300.0)))
    self.createAgedBalanceDataSet()

    request_form = self.portal.REQUEST.form
    request_form['at_date'] = DateTime(2013, 8, 1)
    request_form['section_category_strict'] = False
    request_form['detailed'] = False
    request_form['section_category'] = 'group/demo_group'
    request_form['account_type'] = 'account_type/liability/payable'
    request_form['period_list'] = (1, 2, 3)
    request_form['simulation_state'] = ['delivered']

    report_section_list = self.getReportSectionList(
        self.portal.accounting_module,
        'AccountingTransactionModule_viewAgedBalanceReport')
    self.assertEqual(1, len(report_section_list))

    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(2, len(data_line_list))

    self.checkLineProperties(data_line_list[0],
                             mirror_section_title='Supplier',
                             total_price=500,
                             period_1=500)
    self.checkLineProperties(data_line_list[1],
                             mirror_section_title='ZZZ Supplier',
                             total_price=300,
                             period_3=300)


class TestAccountingReportsWithAnalytic(AccountingTestCase, ERP5ReportTestCase):

  def afterSetUp(self):
    AccountingTestCase.afterSetUp(self)
    self.login()
    # create some functions
    function = self.portal.portal_categories.function
    if function._getOb('a', None) is None:
      function.newContent(portal_type='Category', id='a')
    self.function_a = function['a']
    if function._getOb('b', None) is None:
      function.newContent(portal_type='Category', id='b')
    self.function_b = function['b']

    # create some product lines
    product_line = self.portal.portal_categories.product_line
    if product_line._getOb('pl1', None) is None:
      product_line.newContent(portal_type='Category', id='pl1')
    self.product_line_1 = product_line['pl1']

    # create some projects
    self.project_1 = self.portal.project_module.newContent(
                          portal_type='Project',
                          reference='P1',
                          title='Project 1')
    self.project_2 = self.portal.project_module.newContent(
                          portal_type='Project',
                          reference='P2',
                          title='Project 2')

    preference = self.portal.portal_preferences.getActivePreference()
    preference._edit(
        preferred_accounting_transaction_line_function_base_category='function',
        preferred_accounting_transaction_line_analytic_base_category_list=(
                                              'product_line', ),)
    account_module = self.portal.account_module
    uid_list = sorted([
        self.portal.portal_catalog.newUid(),
        self.portal.portal_catalog.newUid(),
        self.portal.portal_catalog.newUid(),])

    self._makeOne(
              portal_type='Sale Invoice Transaction',
              title='Detailed Transaction',
              reference='DT',
              source_reference='1',
              simulation_state='delivered',
              destination_section_value=self.portal.organisation_module.client_1,
              start_date=DateTime(2006, 2, 2),
              lines=(dict(source_value=account_module.receivable,
                          source_debit=1500.0),
                     dict(source_value=account_module.goods_sales,
                          uid=uid_list[0],
                          source_function_value=self.function_a,
                          source_project_value=self.project_1,
                          product_line_value=self.product_line_1,
                          source_credit=300.0),
                     dict(source_value=account_module.goods_sales,
                          uid=uid_list[1],
                          source_function_value=self.function_b,
                          source_project_value=self.project_1,
                          product_line_value=self.product_line_1,
                          source_credit=500.0),
                     dict(source_value=account_module.goods_sales,
                          uid=uid_list[2],
                          source_function_value=self.function_b,
                          source_project_value=self.project_2,
                          product_line_value=None,
                          source_credit=700.0),
                     ))
    self.tic()
    self.loginByUserName(self.username)

  def beforeTearDown(self):
    AccountingTestCase.beforeTearDown(self)
    preference = self.portal.portal_preferences.getActivePreference()
    preference._edit(
        preferred_accounting_transaction_line_function_base_category=None,
        preferred_accounting_transaction_line_analytic_base_category_list=())
    for module_id in ('project_module',):
      module = self.portal[module_id]
      module.manage_delObjects([x for x in module.objectIds()])
    self.commit()

  def testJournalAnalyticsShown(self):
    self.project_1.validate()
    self.project_2.validate()
    self.tic()
    request_form = self.portal.REQUEST.form
    request_form['at_date'] = DateTime(2006, 2, 2)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['portal_type'] = ['Sale Invoice Transaction']
    request_form['simulation_state'] = ['delivered']
    request_form['hide_analytic'] = False

    report_section_list = self.getReportSectionList(
                               self.portal.accounting_module,
                               'AccountingTransactionModule_viewJournalReport')
    self.assertEqual(1, len(report_section_list))

    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(4, len(data_line_list))

    # test columns values
    line = data_line_list[0]
    self.assertEqual(line.column_id_list,
        [ 'specific_reference', 'date', 'title', 'parent_reference',
          'function', 'project', 'product_line_translated_title',
          'node_title', 'mirror_section_title', 'debit', 'credit'])

    self.checkLineProperties(data_line_list[0],
                             project='',
                             function=None,
                             product_line_translated_title=None,
                             node_title='41',
                             mirror_section_title='Client 1',
                             debit=1500,
                             credit=0)
    self.checkLineProperties(data_line_list[1],
                             project='P1 - Project 1',
                             function='a',
                             product_line_translated_title='pl1',
                             node_title='7',
                             debit=0,
                             credit=300)
    self.checkLineProperties(data_line_list[2],
                             project='P1 - Project 1',
                             function='b',
                             product_line_translated_title='pl1',
                             node_title='7',
                             debit=0,
                             credit=500)
    self.checkLineProperties(data_line_list[3],
                             project='P2 - Project 2',
                             function='b',
                             product_line_translated_title=None,
                             node_title='7',
                             debit=0,
                             credit=700)

    stat_line = line_list[-1]
    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], debit=1500, credit=1500)

  def testJournalAnalyticsHidden(self):
    request_form = self.portal.REQUEST.form
    request_form['at_date'] = DateTime(2006, 2, 2)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['portal_type'] = ['Sale Invoice Transaction']
    request_form['simulation_state'] = ['delivered']
    request_form['hide_analytic'] = True

    report_section_list = self.getReportSectionList(
                               self.portal.accounting_module,
                               'AccountingTransactionModule_viewJournalReport')
    self.assertEqual(1, len(report_section_list))

    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(2, len(data_line_list))

    # test columns values
    line = data_line_list[0]
    self.assertEqual(line.column_id_list,
        ['specific_reference', 'date', 'title', 'parent_reference',
          'node_title', 'mirror_section_title', 'debit', 'credit'])

    self.checkLineProperties(data_line_list[0],
                             node_title='41',
                             mirror_section_title='Client 1',
                             debit=1500,
                             credit=0)
    # this line is the aggregation of 3 lines
    self.checkLineProperties(data_line_list[1],
                             node_title='7',
                             debit=0,
                             credit=1500)
    stat_line = line_list[-1]
    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], debit=1500, credit=1500)

  def testAccountStatementAnalyticsShown(self):
    self.project_1.validate()
    self.project_2.validate()
    self.tic()
    request_form = self.portal.REQUEST.form
    request_form['node'] = \
                self.portal.account_module.goods_sales.getRelativeUrl()
    request_form['at_date'] = DateTime(2006, 2, 2)
    request_form['section_category'] = 'group/demo_group/sub1'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']
    request_form['hide_analytic'] = False
    request_form['export'] = False

    report_section_list = self.getReportSectionList(
                               self.portal.accounting_module,
                               'AccountModule_viewAccountStatementReport')
    self.assertEqual(1, len(report_section_list))

    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(3, len(data_line_list))

    self.checkLineProperties(data_line_list[0],
        Movement_getExplanationTitleAndAnalytics='''Detailed Transaction
DT, a, P1 - Project 1, pl1''',
        debit_price=0,
        credit_price=300,
        running_total_price=-300)
    self.checkLineProperties(data_line_list[1],
        Movement_getExplanationTitleAndAnalytics='''Detailed Transaction
DT, b, P1 - Project 1, pl1''',
        debit_price=0,
        credit_price=500,
        running_total_price=-800)
    self.checkLineProperties(data_line_list[2],
        Movement_getExplanationTitleAndAnalytics='''Detailed Transaction
DT, b, P2 - Project 2''',
        debit_price=0,
        credit_price=700,
        running_total_price=-1500)

    stat_line = line_list[-1]
    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], debit_price=0, credit_price=1500)

  def testAccountStatementAnalyticsHidden(self):
    request_form = self.portal.REQUEST.form
    request_form['node'] = \
                self.portal.account_module.goods_sales.getRelativeUrl()
    request_form['at_date'] = DateTime(2006, 2, 2)
    request_form['section_category'] = 'group/demo_group/sub1'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']
    request_form['hide_analytic'] = True
    request_form['export'] = False

    report_section_list = self.getReportSectionList(
                               self.portal.accounting_module,
                               'AccountModule_viewAccountStatementReport')
    self.assertEqual(1, len(report_section_list))

    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(1, len(data_line_list))

    self.checkLineProperties(data_line_list[0],
                             debit_price=0,
                             credit_price=1500,
                             running_total_price=-1500)

    stat_line = line_list[-1]
    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], debit_price=0, credit_price=1500)

  def testAccountStatementAnalyticsExport(self):
    request_form = self.portal.REQUEST.form
    request_form['node'] = \
                self.portal.account_module.goods_sales.getRelativeUrl()
    request_form['at_date'] = DateTime(2006, 2, 2)
    request_form['section_category'] = 'group/demo_group/sub1'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']
    request_form['hide_analytic'] = False
    request_form['export'] = True

    report_section_list = self.getReportSectionList(
                               self.portal.accounting_module,
                               'AccountModule_viewAccountStatementReport')
    self.assertEqual(1, len(report_section_list))

    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(3, len(data_line_list))

    self.assertEqual(
        ['Movement_getNodeGapId', 'node_translated_title', 'section_title',
        'mirror_section_title', 'date', 'modification_date',
        'Movement_getSpecificReference',
        'Movement_getExplanationTranslatedPortalType',
        'Movement_getExplanationTitle', 'Movement_getExplanationReference',
        # those are analytics columns
        'function', 'product_line_translated_title',

        'debit_price', 'credit_price',
        'total_price', 'Movement_getSectionPriceCurrency', 'debit', 'credit',
        'total_quantity', 'resource_reference', 'Movement_getPaymentTitle',
        'payment_mode_translated_title', 'grouping_reference', 'grouping_date',
        'getTranslatedSimulationStateTitle'],
        data_line_list[0].column_id_list)

    self.checkLineProperties(data_line_list[0],
        Movement_getNodeGapId='7',
        node_translated_title='Goods Sales',
        section_title='My Organisation',
        mirror_section_title='Client 1',
        date=DateTime(2006, 2, 2),
        Movement_getSpecificReference='1',
        Movement_getExplanationTranslatedPortalType=
            'Sale Invoice Transaction',
        Movement_getExplanationTitle='Detailed Transaction',
        Movement_getExplanationReference='DT',
        function='a',
        product_line_translated_title='pl1',
        debit_price=0,
        credit_price=300,
        total_price=-300,
        Movement_getSectionPriceCurrency='EUR',
        debit=0, credit=300, total_quantity=-300,
        resource_reference='EUR',
        Movement_getPaymentTitle=None,
        payment_mode_translated_title=None,
        grouping_reference=None,
        grouping_date=None,
        getTranslatedSimulationStateTitle='Closed')

    self.checkLineProperties(data_line_list[1],
        Movement_getNodeGapId='7',
        node_translated_title='Goods Sales',
        section_title='My Organisation',
        mirror_section_title='Client 1',
        date=DateTime(2006, 2, 2),
        Movement_getSpecificReference='1',
        Movement_getExplanationTranslatedPortalType=
            'Sale Invoice Transaction',
        Movement_getExplanationTitle='Detailed Transaction',
        Movement_getExplanationReference='DT',
        function='b',
        product_line_translated_title='pl1',
        debit_price=0,
        credit_price=500,
        total_price=-500,
        Movement_getSectionPriceCurrency='EUR',
        debit=0, credit=500, total_quantity=-500,
        resource_reference='EUR',
        Movement_getPaymentTitle=None,
        payment_mode_translated_title=None,
        grouping_reference=None,
        grouping_date=None,
        getTranslatedSimulationStateTitle='Closed')

    self.checkLineProperties(data_line_list[2],
        Movement_getNodeGapId='7',
        node_translated_title='Goods Sales',
        section_title='My Organisation',
        mirror_section_title='Client 1',
        date=DateTime(2006, 2, 2),
        Movement_getSpecificReference='1',
        Movement_getExplanationTranslatedPortalType=
            'Sale Invoice Transaction',
        Movement_getExplanationTitle='Detailed Transaction',
        Movement_getExplanationReference='DT',
        function='b',
        product_line_translated_title=None,
        debit_price=0,
        credit_price=700,
        total_price=-700,
        Movement_getSectionPriceCurrency='EUR',
        debit=0, credit=700, total_quantity=-700,
        resource_reference='EUR',
        Movement_getPaymentTitle=None,
        payment_mode_translated_title=None,
        grouping_reference=None,
        grouping_date=None,
        getTranslatedSimulationStateTitle='Closed')

    # There is no stat line in export
    stat_line = line_list[-1]
    self.assertFalse(line_list[-1].isStatLine())

  def testGeneralLedgerAnalyticsShown(self):
    self.project_1.validate()
    self.project_2.validate()
    self.tic()
    request_form = self.portal.REQUEST.form
    request_form['from_date'] = DateTime(2006, 1, 1)
    request_form['at_date'] = DateTime(2006, 12, 31)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']
    request_form['hide_analytic'] = False
    request_form['export'] = False

    report_section_list = self.getReportSectionList(
                                    self.portal.accounting_module,
                                    'AccountModule_viewGeneralLedgerReport')
    self.assertEqual(3, len(report_section_list))

    line_list = self.getListBoxLineList(report_section_list[1])
    data_line_list = [l for l in line_list if l.isDataLine()]

    self.assertEqual( ['date', 'Movement_getSpecificReference',
      'mirror_section_title', 'Movement_getExplanationTitleAndAnalytics',
      'debit_price', 'credit_price', 'running_total_price',
      'grouping_reference', 'grouping_date',
      'getTranslatedSimulationStateTitle'],
        data_line_list[0].column_id_list)

    self.checkLineProperties(data_line_list[0],
        Movement_getExplanationTitleAndAnalytics='''Detailed Transaction
DT, a, P1 - Project 1, pl1''',
        debit_price=0,
        credit_price=300,
        running_total_price=-300)
    self.checkLineProperties(data_line_list[1],
        Movement_getExplanationTitleAndAnalytics='''Detailed Transaction
DT, b, P1 - Project 1, pl1''',
        debit_price=0,
        credit_price=500,
        running_total_price=-800)
    self.checkLineProperties(data_line_list[2],
        Movement_getExplanationTitleAndAnalytics='''Detailed Transaction
DT, b, P2 - Project 2''',
        debit_price=0,
        credit_price=700,
        running_total_price=-1500)

    stat_line = line_list[-1]
    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], debit_price=0, credit_price=1500)

    line_list = self.getListBoxLineList(report_section_list[2])

    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(1, len(data_line_list))
    self.checkLineProperties(data_line_list[0],
                             debit_price=1500,
                             credit_price=1500,)

  def testGeneralLedgerAnalyticsHidden(self):
    request_form = self.portal.REQUEST.form
    request_form['from_date'] = DateTime(2006, 1, 1)
    request_form['at_date'] = DateTime(2006, 12, 31)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']
    request_form['hide_analytic'] = True
    request_form['export'] = False

    report_section_list = self.getReportSectionList(
                                    self.portal.accounting_module,
                                    'AccountModule_viewGeneralLedgerReport')
    self.assertEqual(3, len(report_section_list))

    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual( ['date', 'Movement_getSpecificReference', 'mirror_section_title',
        'Movement_getExplanationTitleAndAnalytics', 'debit_price',
        'credit_price', 'running_total_price', 'grouping_reference',
        'grouping_date', 'getTranslatedSimulationStateTitle'],
        data_line_list[0].column_id_list)
    # receivable account
    self.assertEqual(1, len(data_line_list))
    self.checkLineProperties(data_line_list[0],
                             debit_price=1500,
                             credit_price=0,
                             running_total_price=1500)
    stat_line = line_list[-1]
    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], debit_price=1500, credit_price=0)
    # good sales account
    line_list = self.getListBoxLineList(report_section_list[1])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(1, len(data_line_list))
    self.checkLineProperties(data_line_list[0],
                             debit_price=0,
                             credit_price=1500,
                             running_total_price=-1500)
    stat_line = line_list[-1]
    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], debit_price=0, credit_price=1500)
    # summary
    line_list = self.getListBoxLineList(report_section_list[2])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(1, len(data_line_list))
    self.checkLineProperties(data_line_list[0],
                             debit_price=1500,
                             credit_price=1500,)

  def testGeneralLedgerExport(self):
    self.project_1.validate()
    self.project_2.validate()
    self.tic()
    request_form = self.portal.REQUEST.form
    request_form['from_date'] = DateTime(2006, 1, 1)
    request_form['at_date'] = DateTime(2006, 12, 31)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']
    request_form['hide_analytic'] = False
    request_form['export'] = True

    report_section_list = self.getReportSectionList(
                                    self.portal.accounting_module,
                                    'AccountModule_viewGeneralLedgerReport')
    # There are two report sections, but in reality they are merged into one
    self.assertEqual(2, len(report_section_list))
    # because merge_report_section_list is set to true
    self.assertTrue(self.portal.REQUEST.get('merge_report_section_list'))

    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(1, len(data_line_list))

    # all the columns configured in AccountModule_getGeneralLedgerColumnItemList
    # are displayed
    self.assertEqual(
        ['Movement_getNodeGapId', 'node_translated_title', 'section_title',
        'mirror_section_title', 'date', 'modification_date',
        'Movement_getSpecificReference',
        'Movement_getExplanationTranslatedPortalType',
        'Movement_getExplanationTitle', 'Movement_getExplanationReference',
        # those are analytics columns
        'function', 'project', 'product_line_translated_title',

        'debit_price', 'credit_price',
        'total_price', 'Movement_getSectionPriceCurrency', 'debit', 'credit',
        'total_quantity', 'resource_reference', 'Movement_getPaymentTitle',
        'payment_mode_translated_title', 'grouping_reference', 'grouping_date',
        'getTranslatedSimulationStateTitle'],
        data_line_list[0].column_id_list)
    self.assertEqual([x[0] for x in
        self.portal.accounting_module.AccountModule_getGeneralLedgerColumnItemList()],
        data_line_list[0].column_id_list)

    self.checkLineProperties(data_line_list[0],
        Movement_getNodeGapId='41',
        node_translated_title='Receivable',
        section_title='My Organisation',
        mirror_section_title='Client 1',
        date=DateTime(2006, 2, 2),
        Movement_getSpecificReference='1',
        Movement_getExplanationTranslatedPortalType=
            'Sale Invoice Transaction',
        Movement_getExplanationTitle='Detailed Transaction',
        Movement_getExplanationReference='DT',
        function='',
        project='',
        product_line_translated_title=None,
        debit_price=1500,
        credit_price=0,
        total_price=1500,
        Movement_getSectionPriceCurrency='EUR',
        debit=1500, credit=0, total_quantity=1500,
        resource_reference='EUR',
        Movement_getPaymentTitle=None,
        payment_mode_translated_title=None,
        grouping_reference=None,
        grouping_date=None,
        getTranslatedSimulationStateTitle='Closed')

    line_list = self.getListBoxLineList(report_section_list[1])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEqual(3, len(data_line_list))

    self.checkLineProperties(data_line_list[0],
        Movement_getNodeGapId='7',
        node_translated_title='Goods Sales',
        section_title='My Organisation',
        mirror_section_title='Client 1',
        date=DateTime(2006, 2, 2),
        Movement_getSpecificReference='1',
        Movement_getExplanationTranslatedPortalType=
            'Sale Invoice Transaction',
        Movement_getExplanationTitle='Detailed Transaction',
        Movement_getExplanationReference='DT',
        function='a',
        project='P1 - Project 1',
        product_line_translated_title='pl1',
        debit_price=0,
        credit_price=300,
        total_price=-300,
        Movement_getSectionPriceCurrency='EUR',
        debit=0, credit=300, total_quantity=-300,
        resource_reference='EUR',
        Movement_getPaymentTitle=None,
        payment_mode_translated_title=None,
        grouping_reference=None,
        grouping_date=None,
        getTranslatedSimulationStateTitle='Closed')

    self.checkLineProperties(data_line_list[1],
        Movement_getNodeGapId='7',
        node_translated_title='Goods Sales',
        section_title='My Organisation',
        mirror_section_title='Client 1',
        date=DateTime(2006, 2, 2),
        Movement_getSpecificReference='1',
        Movement_getExplanationTranslatedPortalType=
            'Sale Invoice Transaction',
        Movement_getExplanationTitle='Detailed Transaction',
        Movement_getExplanationReference='DT',
        function='b',
        project='P1 - Project 1',
        product_line_translated_title='pl1',
        debit_price=0,
        credit_price=500,
        total_price=-500,
        Movement_getSectionPriceCurrency='EUR',
        debit=0, credit=500, total_quantity=-500,
        resource_reference='EUR',
        Movement_getPaymentTitle=None,
        payment_mode_translated_title=None,
        grouping_reference=None,
        grouping_date=None,
        getTranslatedSimulationStateTitle='Closed')

    self.checkLineProperties(data_line_list[2],
        Movement_getNodeGapId='7',
        node_translated_title='Goods Sales',
        section_title='My Organisation',
        mirror_section_title='Client 1',
        date=DateTime(2006, 2, 2),
        Movement_getSpecificReference='1',
        Movement_getExplanationTranslatedPortalType=
            'Sale Invoice Transaction',
        Movement_getExplanationTitle='Detailed Transaction',
        Movement_getExplanationReference='DT',
        function='b',
        project='P2 - Project 2',
        product_line_translated_title=None,
        debit_price=0,
        credit_price=700,
        total_price=-700,
        Movement_getSectionPriceCurrency='EUR',
        debit=0, credit=700, total_quantity=-700,
        resource_reference='EUR',
        Movement_getPaymentTitle=None,
        payment_mode_translated_title=None,
        grouping_reference=None,
        grouping_date=None,
        getTranslatedSimulationStateTitle='Closed')

    stat_line = line_list[-1]
    # There is no stat in export mode
    self.assertFalse(line_list[-1].isStatLine())
    # There is not stat section either

  def testTrialBalanceGroupByProject(self):
    request_form = self.portal.REQUEST.form
    request_form['from_date'] = DateTime(2006, 1, 1)
    request_form['at_date'] = DateTime(2006, 2, 2)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']
    request_form['show_empty_accounts'] = 0
    request_form['expand_accounts'] = 0
    request_form['gap_list'] = ['my_country/my_accounting_standards/7']
    request_form['per_account_class_summary'] = 0
    request_form['show_detailed_balance_columns'] = 1
    request_form['group_analytic'] = ['project']

    report_section_list = self.getReportSectionList(
                                    self.portal.accounting_module,
                                    'AccountModule_viewTrialBalanceReport')
    self.assertEqual(1, len(report_section_list))
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]

    self.assertEqual(2, len(data_line_list))

    self.assertEqual(['node_id', 'node_title', 'project_uid',
      'initial_debit_balance', 'initial_credit_balance', 'initial_balance',
      'debit', 'credit', 'final_debit_balance', 'final_credit_balance',
      'final_balance', 'final_balance_if_debit', 'final_balance_if_credit'],
      data_line_list[0].column_id_list)

    self.checkLineProperties(data_line_list[0], node_id='7',
        node_title='Goods Sales', project_uid='P1 - Project 1',
        initial_debit_balance=0, initial_credit_balance=0, debit=0,
        credit=800, final_debit_balance=0, final_credit_balance=800,
        final_balance_if_debit=0, final_balance_if_credit=800)

    self.checkLineProperties(data_line_list[1], node_id='7',
        node_title='Goods Sales', project_uid='P2 - Project 2',
        initial_debit_balance=0, initial_credit_balance=0, debit=0,
        credit=700, final_debit_balance=0, final_credit_balance=700,
        final_balance_if_debit=0, final_balance_if_credit=700)

    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1],
        initial_debit_balance=0, initial_credit_balance=0, debit=0,
        credit=1500, final_debit_balance=0, final_credit_balance=1500,
        final_balance_if_debit=0, final_balance_if_credit=1500)

  def testTrialBalanceGroupByFunction(self):
    request_form = self.portal.REQUEST.form
    request_form['from_date'] = DateTime(2006, 1, 1)
    request_form['at_date'] = DateTime(2006, 2, 2)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']
    request_form['show_empty_accounts'] = 0
    request_form['expand_accounts'] = 0
    request_form['gap_list'] = ['my_country/my_accounting_standards/7']
    request_form['per_account_class_summary'] = 0
    request_form['show_detailed_balance_columns'] = 1
    request_form['group_analytic'] = ['function']

    report_section_list = self.getReportSectionList(
                                    self.portal.accounting_module,
                                    'AccountModule_viewTrialBalanceReport')
    self.assertEqual(1, len(report_section_list))
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]

    self.assertEqual(2, len(data_line_list))

    self.assertEqual(['node_id', 'node_title', 'function_uid',
      'initial_debit_balance', 'initial_credit_balance', 'initial_balance',
      'debit', 'credit', 'final_debit_balance', 'final_credit_balance',
      'final_balance', 'final_balance_if_debit', 'final_balance_if_credit'],
      data_line_list[0].column_id_list)

    self.checkLineProperties(data_line_list[0], node_id='7',
        node_title='Goods Sales', function_uid='a',
        initial_debit_balance=0, initial_credit_balance=0, debit=0,
        credit=300, final_debit_balance=0, final_credit_balance=300,
        final_balance_if_debit=0, final_balance_if_credit=300)

    self.checkLineProperties(data_line_list[1], node_id='7',
        node_title='Goods Sales', function_uid='b',
        initial_debit_balance=0, initial_credit_balance=0, debit=0,
        credit=1200, final_debit_balance=0, final_credit_balance=1200,
        final_balance_if_debit=0, final_balance_if_credit=1200)

    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1],
        initial_debit_balance=0, initial_credit_balance=0, debit=0,
        credit=1500, final_debit_balance=0, final_credit_balance=1500,
        final_balance_if_debit=0, final_balance_if_credit=1500)

  def testTrialBalanceGroupByProjectAndFunction(self):
    request_form = self.portal.REQUEST.form
    request_form['from_date'] = DateTime(2006, 1, 1)
    request_form['at_date'] = DateTime(2006, 2, 2)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']
    request_form['show_empty_accounts'] = 0
    request_form['expand_accounts'] = 0
    request_form['gap_list'] = ['my_country/my_accounting_standards/7']
    request_form['per_account_class_summary'] = 0
    request_form['show_detailed_balance_columns'] = 1
    request_form['group_analytic'] = ['function', 'project']

    report_section_list = self.getReportSectionList(
                                    self.portal.accounting_module,
                                    'AccountModule_viewTrialBalanceReport')
    self.assertEqual(1, len(report_section_list))
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]

    self.assertEqual(3, len(data_line_list))

    self.assertEqual(['node_id', 'node_title', 'function_uid', 'project_uid',
      'initial_debit_balance', 'initial_credit_balance', 'initial_balance',
      'debit', 'credit', 'final_debit_balance', 'final_credit_balance',
      'final_balance', 'final_balance_if_debit',
      'final_balance_if_credit'], data_line_list[0].column_id_list)

    self.checkLineProperties(data_line_list[0], node_id='7',
        node_title='Goods Sales', function_uid='a', project_uid='P1 - Project 1',
        initial_debit_balance=0, initial_credit_balance=0, debit=0,
        credit=300, final_debit_balance=0, final_credit_balance=300,
        final_balance_if_debit=0, final_balance_if_credit=300)

    self.checkLineProperties(data_line_list[1], node_id='7',
        node_title='Goods Sales', function_uid='b', project_uid='P1 - Project 1',
        initial_debit_balance=0, initial_credit_balance=0, debit=0,
        credit=500, final_debit_balance=0, final_credit_balance=500,
        final_balance_if_debit=0, final_balance_if_credit=500)

    self.checkLineProperties(data_line_list[2], node_id='7',
        node_title='Goods Sales', function_uid='b', project_uid='P2 - Project 2',
        initial_debit_balance=0, initial_credit_balance=0, debit=0,
        credit=700, final_debit_balance=0, final_credit_balance=700,
        final_balance_if_debit=0, final_balance_if_credit=700)

    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1],
        initial_debit_balance=0, initial_credit_balance=0, debit=0,
        credit=1500, final_debit_balance=0, final_credit_balance=1500,
        final_balance_if_debit=0, final_balance_if_credit=1500)

  def testTrialBalanceGroupByProductLine(self):
    self._makeOne(
              portal_type='Sale Invoice Transaction',
              title='Noise',
              source_reference='2',
              simulation_state='delivered',
              destination_section_value=self.portal.organisation_module.client_1,
              start_date=DateTime(2006, 2, 2),
              lines=(dict(source_value=self.portal.account_module.receivable,
                          source_debit=1100.0),
                     dict(source_value=self.portal.account_module.payable,
                          source_function_value=self.function_a,
                          source_project_value=self.project_1,
                          product_line_value=self.product_line_1,
                          source_credit=1100.0),))

    request_form = self.portal.REQUEST.form
    request_form['from_date'] = DateTime(2006, 1, 1)
    request_form['at_date'] = DateTime(2006, 2, 2)
    request_form['section_category'] = 'group/demo_group'
    request_form['section_category_strict'] = False
    request_form['simulation_state'] = ['delivered']
    request_form['show_empty_accounts'] = 0
    request_form['expand_accounts'] = 0
    request_form['gap_list'] = ['my_country/my_accounting_standards/7']
    request_form['per_account_class_summary'] = 0
    request_form['show_detailed_balance_columns'] = 1
    # in the dialog, categories are in the '_translated_title' form
    request_form['group_analytic'] = ['product_line_translated_title']
    self.assertTrue(
        ('Product Line', 'product_line_translated_title') in
      self.portal.accounting_module.AccountModule_viewTrialBalanceReportDialog\
        .your_group_analytic.get_value('items'))

    report_section_list = self.getReportSectionList(
                                    self.portal.accounting_module,
                                    'AccountModule_viewTrialBalanceReport')
    self.assertEqual(1, len(report_section_list))
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]

    self.assertEqual(1, len(data_line_list))

    self.assertEqual(['node_id', 'node_title', 'strict_product_line_uid',
      'initial_debit_balance', 'initial_credit_balance', 'initial_balance',
      'debit', 'credit', 'final_debit_balance', 'final_credit_balance',
      'final_balance', 'final_balance_if_debit', 'final_balance_if_credit'],
      data_line_list[0].column_id_list)

    self.checkLineProperties(data_line_list[0], node_id='7',
        node_title='Goods Sales', strict_product_line_uid='pl1',
        initial_debit_balance=0, initial_credit_balance=0, debit=0,
        credit=800, final_debit_balance=0, final_credit_balance=800,
        final_balance_if_debit=0, final_balance_if_credit=800)

    # Lines that does not have a product line are not displayed. This is a
    # technical limitation, we would have to left join to support this.
    self.assertTrue(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1],
        initial_debit_balance=0, initial_credit_balance=0, debit=0,
        credit=800, final_debit_balance=0, final_credit_balance=800,
        final_balance_if_debit=0, final_balance_if_credit=800)


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestAccountingReports))
  suite.addTest(unittest.makeSuite(TestAccountingReportsWithAnalytic))
  return suite

