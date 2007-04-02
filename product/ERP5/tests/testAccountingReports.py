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


class TestAccountingReports(AccountingTestCase):
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

  def getTitle(self):
    return "Accounting Reports"

  # utility methods for ERP5 Report
  def getReportSectionList(self, report_name):
    """Get the list of report sections in a report."""
    report = getattr(self.portal, report_name)
    report_method = getattr(self.portal, report.report_method)
    return report_method()

  def getListBoxLineList(self, report_section):
    """Render the listbox in a report section, return None if no listbox exists
    in the report_section.
    """
    result = None
    here = report_section.getObject(self.portal)
    report_section.pushReport(self.portal)
    form = getattr(here, report_section.getFormId())
    if form.has_field('listbox'):
      result = form.listbox.get_value('default',
                                      render_format='list',
                                      REQUEST=self.portal.REQUEST)
    report_section.popReport(self.portal)
    return result

  def checkLineProperties(self, line, **kw):
    """Check properties of a report line.
    """
    for k, v in kw.items():
      self.assertEquals(v, line.getColumnProperty(k),
          '`%s`: expected: %r actual: %r' % (k, v, line.getColumnProperty(k)))
    
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
              destination_section_value=self.organisation_module.client_2,
              start_date=DateTime(2006, 2, 2),
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
    request_form['portal_type'] = ['Sale Invoice Transaction']
    request_form['simulation_state'] = ['delivered']
    
    report_section_list = self.getReportSectionList(
                               'AccountingTransactionModule_viewJournalReport')
    self.assertEquals(1, len(report_section_list))
    
    # precision is set in the REQUEST (so that fields know how to format)
    precision = self.portal.REQUEST.get('precision')
    self.assertEquals(2, precision)
    
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    # we have 3 transactions, with 3 lines each
    self.assertEquals(9, len(data_line_list))
    
    # test columns values
    line = data_line_list[0]
    self.assertEquals(line.column_id_list,
        ['specific_reference', 'date', 'title', 'node_title',
         'mirror_section_title', 'debit', 'credit'])
    
    # First Transaction
    self.checkLineProperties(data_line_list[0],
                            specific_reference=first.getSourceReference(),
                            date=DateTime(2006, 2, 2),
                            title='First One',
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
                            node_title='4457',
                            mirror_section_title='Client 1',
                            debit=0,
                            credit=19.60)
    self.checkLineProperties(data_line_list[2],
                            specific_reference='',
                            date=None,
                            title='',
                            node_title='7',
                            mirror_section_title='Client 1',
                            debit=0,
                            credit=100)

    # Second Transaction
    self.checkLineProperties(data_line_list[3],
                            specific_reference=second.getSourceReference(),
                            date=DateTime(2006, 2, 2),
                            title='Second One',
                            node_title='41',
                            mirror_section_title='Client 2',
                            debit=239.20,
                            credit=0)
    self.checkLineProperties(data_line_list[4],
                            specific_reference='',
                            date=None,
                            title='',
                            node_title='4457',
                            mirror_section_title='Client 2',
                            debit=0,
                            credit=39.20)
    self.checkLineProperties(data_line_list[5],
                            specific_reference='',
                            date=None,
                            title='',
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
                            node_title='41',
                            mirror_section_title='John Smith',
                            debit=358.80,
                            credit=0)
    self.checkLineProperties(data_line_list[7],
                            specific_reference='',
                            date=None,
                            title='',
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
                            node_title='7',
                            mirror_section_title='John Smith',
                            debit=0,
                            credit=300)
    
    # Stat Line
    stat_line = line_list[-1]
    self.failUnless(stat_line.isStatLine())
    self.failIf(stat_line.getColumnProperty('specific_reference'))
    self.failIf(stat_line.getColumnProperty('date'))
    self.failIf(stat_line.getColumnProperty('title'))
    self.failIf(stat_line.getColumnProperty('node_title'))
    self.failIf(stat_line.getColumnProperty('mirror_section_title'))
    # when printing the report, the field does the rounding, so we can round in
    # the test
    self.assertEquals(717.60, round(stat_line.getColumnProperty('debit'),
                                    precision))
    self.assertEquals(717.60, round(stat_line.getColumnProperty('credit'),
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
    request_form['portal_type'] = ['Payment Transaction']
    request_form['simulation_state'] = ['delivered']
    request_form['payment'] = bank1.getRelativeUrl()
    
    report_section_list = self.getReportSectionList(
                               'AccountingTransactionModule_viewJournalReport')
    self.assertEquals(1, len(report_section_list))
    
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    # we have 1 transactions with 2 lines
    self.assertEquals(2, len(data_line_list))
    
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
    self.failUnless(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], debit=100, credit=100)


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
              simulation_state='delivered',
              source_payment_value=bank2,
              destination_section_value=self.organisation_module.client_1,
              start_date=DateTime(2006, 2, 3),
              lines=(dict(source_value=account_module.receivable,
                          source_debit=800.0),
                     dict(source_value=account_module.bank,
                          source_credit=800.0)))
    
    return bank1, (t1, t2, t3, t4, t5, t6, t7, t8)


  def testAccountStatement(self):
    # Simple Account Statement for "Receivable" account
    self.createAccountStatementDataSet()
    
    # set request variables and render                 
    request_form = self.portal.REQUEST.form
    request_form['node'] = \
                self.portal.account_module.receivable.getRelativeUrl()
    request_form['at_date'] = DateTime(2006, 2, 2)
    request_form['section_category'] = 'group/demo_group'
    request_form['simulation_state'] = ['delivered']
    
    report_section_list = self.getReportSectionList(
                               'AccountModule_viewAccountStatementReport')
    self.assertEquals(1, len(report_section_list))
    
    # precision is set in the REQUEST (so that fields know how to format)
    precision = self.portal.REQUEST.get('precision')
    self.assertEquals(2, precision)
    
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    # we have 6 transactions, because 7th is after
    self.assertEquals(6, len(data_line_list))
    
    # test columns values
    line = data_line_list[0]
    self.assertEquals(line.column_id_list,
        ['Movement_getSpecificReference', 'date',
         'Movement_getExplanationTitle', 'Movement_getMirrorSectionTitle',
         'debit', 'credit', 'running_total_price'])
    
    self.checkLineProperties(data_line_list[0],
                             Movement_getSpecificReference='1',
                             date=DateTime(2006, 2, 1),
                             Movement_getExplanationTitle='Transaction 1',
                             Movement_getMirrorSectionTitle='Client 1',
                             debit=100,
                             credit=0,
                             running_total_price=100)
    
    self.checkLineProperties(data_line_list[1],
                             Movement_getSpecificReference='2',
                             date=DateTime(2006, 2, 1, 0, 1),
                             Movement_getExplanationTitle='Transaction 2',
                             Movement_getMirrorSectionTitle='Client 1',
                             debit=0,
                             credit=200,
                             running_total_price=-100)
    
    self.checkLineProperties(data_line_list[2],
                             Movement_getSpecificReference='3',
                             date=DateTime(2006, 2, 2, 0, 2),
                             Movement_getExplanationTitle='Transaction 3',
                             Movement_getMirrorSectionTitle='Client 1',
                             debit=300,
                             credit=0,
                             running_total_price=200)

    self.checkLineProperties(data_line_list[3],
                             Movement_getSpecificReference='4',
                             date=DateTime(2006, 2, 2, 0, 3),
                             Movement_getExplanationTitle='Transaction 4',
                             Movement_getMirrorSectionTitle='Client 2',
                             debit=400,
                             credit=0,
                             running_total_price=600)

    self.checkLineProperties(data_line_list[4],
                             Movement_getSpecificReference='5',
                             date=DateTime(2006, 2, 2, 0, 4),
                             Movement_getExplanationTitle='Transaction 5',
                             Movement_getMirrorSectionTitle='John Smith',
                             debit=500,
                             credit=0,
                             running_total_price=1100)

    self.checkLineProperties(data_line_list[5],
                             Movement_getSpecificReference='6',
                             date=DateTime(2006, 2, 2, 0, 5),
                             Movement_getExplanationTitle='Transaction 6',
                             Movement_getMirrorSectionTitle='Client 1',
                             debit=600,
                             credit=0,
                             running_total_price=1700)

    self.failUnless(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1],
                             Movement_getSpecificReference=None,
                             date=None,
                             Movement_getExplanationTitle=None,
                             Movement_getMirrorSectionTitle=None,
                             debit=1900,
                             credit=200,
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
    request_form['simulation_state'] = ['delivered']
    
    report_section_list = self.getReportSectionList(
                               'AccountModule_viewAccountStatementReport')
    self.assertEquals(1, len(report_section_list))
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    # we have 1 summary line and 4 transactions
    self.assertEquals(5, len(data_line_list))
 
    self.checkLineProperties(data_line_list[0],
                             Movement_getSpecificReference='Previous Balance',
                             date=DateTime(2006, 2, 2),
                             Movement_getExplanationTitle='',
                             Movement_getMirrorSectionTitle='',
                             debit=100,
                             credit=200,
                             running_total_price=-100)
    
    self.checkLineProperties(data_line_list[1],
                             Movement_getSpecificReference='3',
                             date=DateTime(2006, 2, 2, 0, 2),
                             Movement_getExplanationTitle='Transaction 3',
                             Movement_getMirrorSectionTitle='Client 1',
                             debit=300,
                             credit=0,
                             running_total_price=200)

    self.checkLineProperties(data_line_list[2],
                             Movement_getSpecificReference='4',
                             date=DateTime(2006, 2, 2, 0, 3),
                             Movement_getExplanationTitle='Transaction 4',
                             Movement_getMirrorSectionTitle='Client 2',
                             debit=400,
                             credit=0,
                             running_total_price=600)

    self.checkLineProperties(data_line_list[3],
                             Movement_getSpecificReference='5',
                             date=DateTime(2006, 2, 2, 0, 4),
                             Movement_getExplanationTitle='Transaction 5',
                             Movement_getMirrorSectionTitle='John Smith',
                             debit=500,
                             credit=0,
                             running_total_price=1100)

    self.checkLineProperties(data_line_list[4],
                             Movement_getSpecificReference='6',
                             date=DateTime(2006, 2, 2, 0, 5),
                             Movement_getExplanationTitle='Transaction 6',
                             Movement_getMirrorSectionTitle='Client 1',
                             debit=600,
                             credit=0,
                             running_total_price=1700)

    self.failUnless(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], debit=1900, credit=200,)


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
    request_form['simulation_state'] = ['delivered']
    
    report_section_list = self.getReportSectionList(
                               'AccountModule_viewAccountStatementReport')
    self.assertEquals(1, len(report_section_list))
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertNotEquals('Previous Balance',
          data_line_list[0].getColumnProperty('Movement_getSpecificReference'))

    
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
    request_form['section_category'] = 'group/demo_group'
    request_form['simulation_state'] = ['delivered']
    
    report_section_list = self.getReportSectionList(
                                    'AccountModule_viewAccountStatementReport')
    self.assertEquals(1, len(report_section_list))
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEquals(1, len(data_line_list))

    self.checkLineProperties(data_line_list[0],
                             Movement_getSpecificReference='4',
                             date=DateTime(2006, 2, 2, 0, 3),
                             Movement_getExplanationTitle='Transaction 4',
                             Movement_getMirrorSectionTitle='Client 2',
                             debit=400,
                             credit=0,
                             running_total_price=400)
    
    self.failUnless(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], debit=400, credit=0)


  def testAccountStatementSimulationState(self):
    # Simulation State parameter is taken into account.
    self.createAccountStatementDataSet()
    
    # set request variables and render
    request_form = self.portal.REQUEST.form
    request_form['node'] = \
                  self.portal.account_module.receivable.getRelativeUrl()
    request_form['at_date'] = DateTime(2006, 2, 2)
    request_form['section_category'] = 'group/demo_group'
    request_form['simulation_state'] = ['stopped', 'confirmed']

    report_section_list = self.getReportSectionList(
                                    'AccountModule_viewAccountStatementReport')
    self.assertEquals(1, len(report_section_list))
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    self.assertEquals(1, len(data_line_list))
    
    self.checkLineProperties(data_line_list[0],
                             Movement_getSpecificReference='7',
                             date=DateTime(2006, 2, 2, 0, 6),
                             Movement_getExplanationTitle='Transaction 7',
                             Movement_getMirrorSectionTitle='Client 1',
                             debit=700,
                             credit=0,
                             running_total_price=700)
    
    self.failUnless(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], debit=700, credit=0)


  def testTrialBalance(self):
    # Simple test of trial balance
    # we will use the same data set as account statement
    self.createAccountStatementDataSet(use_two_bank_accounts=0)

    # set request variables and render
    request_form = self.portal.REQUEST.form
    request_form['from_date'] = DateTime(2006, 1, 1)
    request_form['at_date'] = DateTime(2006, 12, 31)
    request_form['section_category'] = 'group/demo_group'
    request_form['simulation_state'] = ['stopped', 'delivered']
    request_form['show_empty_accounts'] = 1
    request_form['expand_accounts'] = 0

    report_section_list = self.getReportSectionList(
                                    'AccountModule_viewTrialBalanceReport')
    self.assertEquals(1, len(report_section_list))
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
    
    # all accounts are present
    self.assertEquals(
          len(self.portal.account_module.contentValues(portal_type='Account')),
          len(data_line_list))
    
    self.assertEquals(['node_id', 'node_title',
           'initial_debit_balance', 'debit', 'final_debit_balance',
           'initial_credit_balance', 'credit', 'final_credit_balance',
           'final_balance_if_debit', 'final_balance_if_credit'],
           data_line_list[0].column_id_list)
    
    # account are sorted by GAP Id
    self.checkLineProperties(data_line_list[0], node_id='1',
        node_title='Equity', initial_debit_balance=0, initial_credit_balance=0,
        debit=0, credit=0, final_debit_balance=0, final_credit_balance=0,
        final_balance_if_debit=0, final_balance_if_credit=0)
    
    self.checkLineProperties(data_line_list[1], node_id='2',
        node_title='Fixed Assets', initial_debit_balance=0,
        initial_credit_balance=0, debit=0, credit=0, final_debit_balance=0,
        final_credit_balance=0, final_balance_if_debit=0,
        final_balance_if_credit=0)
    
    self.checkLineProperties(data_line_list[2], node_id='3',
        # XXX isn't "Inventory" a better name here ?
        node_title='Stocks', initial_debit_balance=0, initial_credit_balance=0,
        debit=0, credit=0, final_debit_balance=0, final_credit_balance=0,
        final_balance_if_debit=0, final_balance_if_credit=0)
    
    self.checkLineProperties(data_line_list[3], node_id='40',
        node_title='Payable', initial_debit_balance=0, initial_credit_balance=0,
        debit=200, credit=100, final_debit_balance=200, final_credit_balance=100,
        final_balance_if_debit=100, final_balance_if_credit=0,)
    
    self.checkLineProperties(data_line_list[4], node_id='41',
        node_title='Receivable', initial_debit_balance=0,
        initial_credit_balance=0, debit=3400, credit=200,
        final_debit_balance=3400, final_credit_balance=200,
        final_balance_if_debit=3200, final_balance_if_credit=0,)
    
    self.checkLineProperties(data_line_list[5], node_id='4456',
        node_title='Refundable VAT 10%', initial_debit_balance=0,
        initial_credit_balance=0, debit=0, credit=0, final_debit_balance=0,
        final_credit_balance=0, final_balance_if_debit=0,
        final_balance_if_credit=0)
    
    self.checkLineProperties(data_line_list[6], node_id='4457',
        node_title='Collected VAT 10%', initial_debit_balance=0,
        initial_credit_balance=0, debit=0, credit=0, final_debit_balance=0,
        final_credit_balance=0, final_balance_if_debit=0,
        final_balance_if_credit=0)
    
    self.checkLineProperties(data_line_list[7], node_id='5',
        node_title='Bank (Bank1)', initial_debit_balance=0,
        initial_credit_balance=0, debit=0, credit=3300, final_debit_balance=0,
        final_credit_balance=3300, final_balance_if_debit=0,
        final_balance_if_credit=3300,)
    
    self.checkLineProperties(data_line_list[8], node_id='6',
        node_title='Goods Purchase', initial_debit_balance=0,
        initial_credit_balance=0, debit=0, credit=0, final_debit_balance=0,
        final_credit_balance=0, final_balance_if_credit=0,
        final_balance_if_debit=0)
    
    self.checkLineProperties(data_line_list[9], node_id='7',
        node_title='Goods Sales', initial_debit_balance=0,
        initial_credit_balance=0, debit=0, credit=0, final_debit_balance=0,
        final_credit_balance=0, final_balance_if_debit=0,
        final_balance_if_credit=0)
    
    self.failUnless(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], node_id=None, node_title=None,
        initial_debit_balance=0, initial_credit_balance=0, debit=3600,
        credit=3600, final_debit_balance=3600, final_credit_balance=3600,
        final_balance_if_debit=None, final_balance_if_credit=None)

    
  def testTrialBalanceExpandAccounts(self):
    # Test of "expand accounts" feature of trial balance
    self.createAccountStatementDataSet()

    # set request variables and render
    request_form = self.portal.REQUEST.form
    request_form['from_date'] = DateTime(2006, 1, 1)
    request_form['at_date'] = DateTime(2006, 2, 2)
    request_form['section_category'] = 'group/demo_group'
    request_form['simulation_state'] = ['delivered']
    request_form['show_empty_accounts'] = 0
    request_form['expand_accounts'] = 1

    report_section_list = self.getReportSectionList(
                                    'AccountModule_viewTrialBalanceReport')
    self.assertEquals(1, len(report_section_list))
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
 
    self.assertEquals(6, len(data_line_list))

    # account are sorted by GAP Id
    self.checkLineProperties(data_line_list[0], node_id='40',
        node_title='Payable (Client 1)', initial_debit_balance=0,
        initial_credit_balance=0, debit=200, credit=100,
        final_debit_balance=200, final_credit_balance=100,
        final_balance_if_debit=100, final_balance_if_credit=0)
    
    self.checkLineProperties(data_line_list[1], node_id='41',
        node_title='Receivable (Client 1)', initial_debit_balance=0,
        initial_credit_balance=0, debit=1000, credit=200,
        final_debit_balance=1000, final_credit_balance=200,
        final_balance_if_debit=800, final_balance_if_credit=0)
    
    self.checkLineProperties(data_line_list[2], node_id='41',
        node_title='Receivable (Client 2)', initial_debit_balance=0,
        initial_credit_balance=0, debit=400, credit=0, final_debit_balance=400,
        final_credit_balance=0, final_balance_if_debit=400,
        final_balance_if_credit=0)
    
    self.checkLineProperties(data_line_list[3], node_id='41',
        node_title='Receivable (John Smith)', initial_debit_balance=0,
        initial_credit_balance=0, debit=500, credit=0,
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
    
    self.failUnless(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], node_id=None, node_title=None,
        initial_debit_balance=0, initial_credit_balance=0, debit=2100,
        credit=2100, final_debit_balance=2100, final_credit_balance=2100,
        final_balance_if_debit=None, final_balance_if_credit=None)


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
              source_reference='0',
              simulation_state='delivered',
              start_date=DateTime(2006, 1, 1),
              lines=(dict(source_value=account_module.payable,
                          source_credit=600.0,
                          destination_section_value=
                              self.organisation_module.client_1,),
                     dict(source_value=account_module.receivable,
                          source_debit=400.0,
                          destination_section_value=
                              self.organisation_module.client_2,),
                     dict(source_value=account_module.equity,
                          source_debit=200)))
    
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
    request_form['simulation_state'] = ['delivered']
    request_form['show_empty_accounts'] = 0
    request_form['expand_accounts'] = 0

    report_section_list = self.getReportSectionList(
                                    'AccountModule_viewTrialBalanceReport')
    self.assertEquals(1, len(report_section_list))
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
 
    self.assertEquals(5, len(data_line_list))

    # account are sorted by GAP Id
    # TODO: sort by "gap normalized path"
    self.checkLineProperties(data_line_list[0], node_id='1',
        node_title='Equity', initial_debit_balance=200,
        initial_credit_balance=0, debit=0, credit=0,
        final_debit_balance=200, final_credit_balance=0,
        final_balance_if_debit=200, final_balance_if_credit=0)
    
    self.checkLineProperties(data_line_list[1], node_id='40',
        node_title='Payable', initial_debit_balance=0,
        initial_credit_balance=600, debit=200, credit=100,
        final_debit_balance=200, final_credit_balance=700,
        final_balance_if_debit=0, final_balance_if_credit=500)
    
    self.checkLineProperties(data_line_list[2], node_id='41',
        node_title='Receivable', initial_debit_balance=400,
        initial_credit_balance=0, debit=1950, credit=200,
        final_debit_balance=2350, final_credit_balance=200,
        final_balance_if_debit=2150, final_balance_if_credit=0)
    
    self.checkLineProperties(data_line_list[3], node_id='5',
        node_title='Bank (Bank1)', initial_debit_balance=0,
        initial_credit_balance=0, debit=0, credit=1800,
        final_debit_balance=0, final_credit_balance=1800,
        final_balance_if_debit=0, final_balance_if_credit=1800,)
    
    self.checkLineProperties(data_line_list[4], node_id='7',
        node_title='Goods Sales', initial_debit_balance=0,
        initial_credit_balance=0, debit=0, credit=50,
        final_debit_balance=0, final_credit_balance=50,
        final_balance_if_debit=0, final_balance_if_credit=50,)
    
    self.failUnless(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], node_id=None, node_title=None,
        initial_debit_balance=600, initial_credit_balance=600, debit=2150,
        credit=2150, final_debit_balance=2750, final_credit_balance=2750,
        final_balance_if_debit=None, final_balance_if_credit=None)

  def testTrialBalanceDifferentCurrencies(self):
    # Test of trial balance and different currencies
    account_module = self.portal.account_module
    
    self._makeOne(
              portal_type='Accounting Transaction',
              title='Transaction in EUR (our currency)',
              resource_value='currency_module/euro',
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
    request_form['simulation_state'] = ['delivered']
    request_form['show_empty_accounts'] = 0
    request_form['expand_accounts'] = 0

    report_section_list = self.getReportSectionList(
                                    'AccountModule_viewTrialBalanceReport')
    self.assertEquals(1, len(report_section_list))
    line_list = self.getListBoxLineList(report_section_list[0])
    data_line_list = [l for l in line_list if l.isDataLine()]
 
    self.assertEquals(2, len(data_line_list))

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
    
    self.failUnless(line_list[-1].isStatLine())
    self.checkLineProperties(line_list[-1], node_id=None, node_title=None,
        initial_debit_balance=0, initial_credit_balance=0, debit=500,
        credit=500, final_debit_balance=500, final_credit_balance=500,
        final_balance_if_debit=None, final_balance_if_credit=None)
  
    
def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestAccountingReports))
  return suite

