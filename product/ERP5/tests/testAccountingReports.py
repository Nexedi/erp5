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
from Products.ERP5Form.Selection import Selection


class TestAccountingReports(AccountingTestCase):
  """Test Accounting reports"""

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
    line = data_line_list[0]
    self.assertEquals(first.getSourceReference(),
                      line.getColumnProperty('specific_reference'))
    self.assertEquals(DateTime(2006, 2, 2),
                      line.getColumnProperty('date'))
    self.assertEquals('First One', line.getColumnProperty('title'))
    self.assertEquals('41', line.getColumnProperty('node_title'))
    self.assertEquals('Client 1',
                      line.getColumnProperty('mirror_section_title'))
    self.assertEquals(119.60, line.getColumnProperty('debit'))
    self.assertEquals(0, line.getColumnProperty('credit'))
    line = data_line_list[1]
    # some values are only present when we display the first line of the
    # transaction (this is a way to see different transactions)
    self.failIf(line.getColumnProperty('specific_reference'))
    self.failIf(line.getColumnProperty('date'))
    self.failIf(line.getColumnProperty('title'))
    self.assertEquals('4457', line.getColumnProperty('node_title'))
    self.assertEquals('Client 1',
                      line.getColumnProperty('mirror_section_title'))
    self.assertEquals(0, line.getColumnProperty('debit'))
    self.assertEquals(19.60, line.getColumnProperty('credit'))
    line = data_line_list[2]
    self.failIf(line.getColumnProperty('specific_reference'))
    self.failIf(line.getColumnProperty('date'))
    self.failIf(line.getColumnProperty('title'))
    self.assertEquals('7', line.getColumnProperty('node_title'))
    self.assertEquals('Client 1',
                      line.getColumnProperty('mirror_section_title'))
    self.assertEquals(0, line.getColumnProperty('debit'))
    self.assertEquals(100.00, line.getColumnProperty('credit'))

    # Second Transaction
    line = data_line_list[3]
    self.assertEquals(second.getSourceReference(),
                      line.getColumnProperty('specific_reference'))
    self.assertEquals(DateTime(2006, 2, 2), line.getColumnProperty('date'))
    self.assertEquals('Second One', line.getColumnProperty('title'))
    self.assertEquals('41', line.getColumnProperty('node_title'))
    self.assertEquals('Client 2',
                      line.getColumnProperty('mirror_section_title'))
    self.assertEquals(239.20, line.getColumnProperty('debit'))
    self.assertEquals(0, line.getColumnProperty('credit'))
    line = data_line_list[4]
    self.failIf(line.getColumnProperty('specific_reference'))
    self.failIf(line.getColumnProperty('date'))
    self.failIf(line.getColumnProperty('title'))
    self.assertEquals('4457', line.getColumnProperty('node_title'))
    self.assertEquals('Client 2',
                      line.getColumnProperty('mirror_section_title'))
    self.assertEquals(0, line.getColumnProperty('debit'))
    self.assertEquals(39.20, line.getColumnProperty('credit'))
    line = data_line_list[5]
    self.failIf(line.getColumnProperty('specific_reference'))
    self.failIf(line.getColumnProperty('date'))
    self.failIf(line.getColumnProperty('title'))
    self.assertEquals('7', line.getColumnProperty('node_title'))
    self.assertEquals('Client 2',
                      line.getColumnProperty('mirror_section_title'))
    self.assertEquals(0, line.getColumnProperty('debit'))
    self.assertEquals(200, line.getColumnProperty('credit'))

    # Third Transaction
    line = data_line_list[6]
    self.assertEquals(third.getSourceReference(),
                      line.getColumnProperty('specific_reference'))
    self.assertEquals(DateTime(2006, 2, 2, 2, 2), # 2006/02/02 will be
                              # displayed, but this rendering level cannot be
                              # tested with this framework
                      line.getColumnProperty('date'))
    self.assertEquals('Third One', line.getColumnProperty('title'))
    self.assertEquals('41', line.getColumnProperty('node_title'))
    self.assertEquals('John Smith',
                      line.getColumnProperty('mirror_section_title'))
    self.assertEquals(358.80, line.getColumnProperty('debit'))
    self.assertEquals(0, line.getColumnProperty('credit'))
    line = data_line_list[7]
    self.failIf(line.getColumnProperty('specific_reference'))
    self.failIf(line.getColumnProperty('date'))
    self.failIf(line.getColumnProperty('title'))
    self.assertEquals('4457', line.getColumnProperty('node_title'))
    self.assertEquals('John Smith',
                      line.getColumnProperty('mirror_section_title'))
    self.assertEquals(0, line.getColumnProperty('debit'))
    self.assertEquals(58.80, line.getColumnProperty('credit'))
    line = data_line_list[8]
    self.failIf(line.getColumnProperty('specific_reference'))
    self.failIf(line.getColumnProperty('date'))
    # If a title is set on the line, we can see it on this report
    self.assertEquals('Line Title', line.getColumnProperty('title'))
    self.assertEquals('7', line.getColumnProperty('node_title'))
    self.assertEquals('John Smith',
                      line.getColumnProperty('mirror_section_title'))
    self.assertEquals(0, line.getColumnProperty('debit'))
    self.assertEquals(300.0, line.getColumnProperty('credit'))

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
    
    line = data_line_list[0]
    self.assertEquals(transaction.getSourceReference(),
                      line.getColumnProperty('specific_reference'))
    self.assertEquals(DateTime(2006, 2, 2),
                      line.getColumnProperty('date'))
    self.assertEquals('Good One', line.getColumnProperty('title'))
    self.assertEquals('41', line.getColumnProperty('node_title'))
    self.assertEquals('Client 1',
                      line.getColumnProperty('mirror_section_title'))
    self.assertEquals(100.00, line.getColumnProperty('debit'))
    self.assertEquals(0, line.getColumnProperty('credit'))
    line = data_line_list[1]
    # some values are only present when we display the first line of the
    # transaction (this is a way to see different transactions)
    self.failIf(line.getColumnProperty('specific_reference'))
    self.failIf(line.getColumnProperty('date'))
    self.failIf(line.getColumnProperty('title'))
    self.assertEquals('5', line.getColumnProperty('node_title'))
    self.assertEquals('Client 1',
                      line.getColumnProperty('mirror_section_title'))
    self.assertEquals(0, line.getColumnProperty('debit'))
    self.assertEquals(100.00, line.getColumnProperty('credit'))
    
    # Stat Line
    stat_line = line_list[-1]
    self.failUnless(stat_line.isStatLine())
    self.assertEquals(100, stat_line.getColumnProperty('debit'))
    self.assertEquals(100, stat_line.getColumnProperty('credit'))


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestAccountingReports))
  return suite

