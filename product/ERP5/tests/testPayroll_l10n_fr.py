##############################################################################
#
# Copyright (c) 2007 Nexedi SARL and Contributors. All Rights Reserved.
#          Fabien Morin <fabien.morin@gmail.com>
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
"""
  test cases related to french localisation (tranche A for example)
"""

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from Acquisition import aq_parent
from Products.ERP5.tests.testPayroll import TestPayrollMixin
from DateTime import DateTime
import transaction

class TestPayroll_l10n_fr(TestPayrollMixin):

  def getTitle(self):
    return "Payroll_l10n_fr"

  def getBusinessTemplateList(self):
    """ """
    return ('erp5_base', 'erp5_pdm', 'erp5_trade', 'erp5_accounting',
        'erp5_payroll', 'erp5_payroll_l10n_fr')

  def test_01_getYearToDateSlice(self):
    '''
      that slices works and we can caculate the total amount spend on a slice

    '''
    eur = self.portal.currency_module.EUR
    model = self.paysheet_model_module.newContent( \
            portal_type='Pay Sheet Model',
            variation_settings_category_list=self.variation_settings_category_list)
    model.setPriceCurrencyValue(eur)

    self.addSlice(model, 'salary_range/%s' % \
        self.france_settings_slice_a, 0, 1000)
    self.addSlice(model, 'salary_range/%s' % \
        self.france_settings_slice_b, 1000, 2000)
    self.addSlice(model, 'salary_range/%s' % \
        self.france_settings_slice_c, 2000, 10000000)
    self.addSlice(model, 'salary_range/%s' % \
        self.france_settings_forfait, 0, 10000000)

    urssaf_slice_list = [ 'salary_range/'+self.france_settings_slice_a,]
    urssaf_share_list = [ 'tax_category/'+self.tax_category_employee_share,]
    salary_slice_list = ['salary_range/'+self.france_settings_forfait,]
    salary_share_list = ['tax_category/'+self.tax_category_employee_share,]
    variation_category_list_urssaf = urssaf_share_list + urssaf_slice_list
    variation_category_list_salary = salary_share_list + salary_slice_list

    model_line_1 = self.createModelLine(model=model,
        id='model_line_1',
        variation_category_list=variation_category_list_salary,
        resource=self.labour,
        share_list=salary_share_list,
        slice_list=salary_slice_list,
        values=[[[10000, None],],],
        base_application_list=[],
        base_contribution_list=['base_amount/base_salary',
          'base_amount/gross_salary'])
    model_line_1.setIntIndex(1)

    model_line_2 = self.createModelLine(model=model,
        id='model_line_2',
        variation_category_list=variation_category_list_urssaf,
        resource=self.urssaf,
        share_list=urssaf_share_list,
        slice_list=urssaf_slice_list,
        values=[[[None, 0.8]],],
        source_value=self.payroll_service_organisation,
        base_application_list=[ 'base_amount/base_salary',],
        base_contribution_list=['base_amount/net_salary',])
    model_line_2.setIntIndex(2)
    
    model_line_3 = self.createModelLine(model=model,
        id='model_line_3',
        variation_category_list=variation_category_list_urssaf,
        resource=self.urssaf,
        share_list=urssaf_share_list,
        slice_list=urssaf_slice_list,
        values=[[[None, -0.1]],],
        source_value=self.payroll_service_organisation,
        base_application_list=[ 'base_amount/net_salary',],
        base_contribution_list=['base_amount/deductible_tax',])
    model_line_3.setIntIndex(3)

    # create a paysheet with two lines
    paysheet = self.portal.accounting_module.newContent(
                              portal_type='Pay Sheet Transaction',
                              specialise_value=model,
                              start_date=DateTime(2009, 07, 1),
                              stop_date=DateTime(2009, 07, 31))
    paysheet.PaySheetTransaction_applyModel()
    self.assertEquals(len(paysheet.contentValues(portal_type='Pay Sheet Line')), 0)
    # calculate the pay sheet
    pay_sheet_line_list = self.calculatePaySheet(paysheet=paysheet)
    self.assertEquals(len(paysheet.contentValues(portal_type='Pay Sheet Line')), 3)
    # check values on the paysheet
    line_list = paysheet.contentValues()
    self.assertEquals(line_list[0].contentValues()[0].getTotalPrice(), 10000)
    self.assertEquals(line_list[1].contentValues()[0].getTotalPrice(), 8000)
    self.assertEquals(line_list[2].contentValues()[0].getTotalPrice(), -800)
    paysheet.stop()

    # create anoter paysheet with two lines
    paysheet_2 = self.portal.accounting_module.newContent(
                              portal_type='Pay Sheet Transaction',
                              specialise_value=model,
                              start_date=DateTime(2009, 8, 1),
                              stop_date=DateTime(2009, 8, 31))
    paysheet_2.PaySheetTransaction_applyModel()
    self.assertEquals(len(paysheet_2.contentValues(portal_type='Pay Sheet Line')), 0)
    # calculate the pay sheet
    pay_sheet_line_list = self.calculatePaySheet(paysheet=paysheet_2)
    self.assertEquals(len(paysheet.contentValues(portal_type='Pay Sheet Line')), 3)
    # check values on the paysheet
    line_list = paysheet_2.contentValues()
    self.assertEquals(line_list[0].contentValues()[0].getTotalPrice(), 10000)
    self.assertEquals(line_list[1].contentValues()[0].getTotalPrice(), 8000)
    self.assertEquals(line_list[2].contentValues()[0].getTotalPrice(), -800)
    transaction.commit()
    self.tic()

    # here, check how much is contributed to the slices
    self.assertEquals(2000, # 1000 from the 1st paysheet + 1000 from the 2e
        paysheet_2.PaySheetTransaction_getYearToDateSlice(\
            'salary_range/france/tranche_a'))
    self.assertEquals(2000, # 1000 from the 1st paysheet + 1000 from the 2e
        paysheet_2.PaySheetTransaction_getYearToDateSlice(\
            'salary_range/france/tranche_b'))
    self.assertEquals(16000, # (10000 - 1000 - 1000)*2
        paysheet_2.PaySheetTransaction_getYearToDateSlice(\
            'salary_range/france/tranche_c'))

import unittest
def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestPayroll_l10n_fr))
  return suite
