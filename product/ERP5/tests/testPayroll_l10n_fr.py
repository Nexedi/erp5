##############################################################################
#
# Copyright (c) 2007-2009 Nexedi SA and Contributors. All Rights Reserved.
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
  test cases related to french localisation. Scripts inclued in
  erp5_payroll_l10n_fr will be tested here.
"""

from Products.ERP5Type.tests.Sequence import SequenceList
from Products.ERP5.tests.testPayroll import TestPayrollMixin
from DateTime import DateTime

class TestPayroll_l10n_fr(TestPayrollMixin):

  PAYSHEET_WITH_SLICE_SEQUENCE_STRING = '''
               CreateBasicPaysheet
               PaysheetSetModelAndApplyIt
               PaysheetCreateLabourPaySheetLine
  ''' + TestPayrollMixin.BUSINESS_PATH_CREATION_SEQUENCE_STRING + '''
               CheckUpdateAggregatedAmountListReturnUsingSlices
               PaysheetApplyTransformation
               Tic
               CheckPaysheetLineAreCreatedUsingSlices
               CheckPaysheetLineAmountsUsingSlices
               CheckUpdateAggregatedAmountListReturnNothing
               CheckPaysheetLineAmountsUsingSlices
  '''

  def getTitle(self):
    return "Payroll_l10n_fr"

  def getBusinessTemplateList(self):
    """ """
    return TestPayrollMixin.getBusinessTemplateList(self) +\
          ('erp5_calendar', 'erp5_payroll_l10n_fr',)

  def stepCheckYearToDateSliceAmount(self, sequence=None, **kw):
    paysheet_module = self.portal.getDefaultModule(portal_type=\
        'Pay Sheet Transaction')
    paysheet_list = paysheet_module.contentValues(portal_type=\
        'Pay Sheet Transaction')
    self.assertEqual(len(paysheet_list), 2) # 2 paysheet have been created
                                             # for this test

    # set nice date on paysheet (ie. one paysheet per month)
    paysheet_list[0].setStartDate(DateTime('2009/06/01'))
    paysheet_list[0].setStopDate(DateTime('2009/06/30'))
    paysheet_list[1].setStartDate(DateTime('2009/07/01'))
    paysheet_list[1].setStopDate(DateTime('2009/07/31'))
    for paysheet in paysheet_list:
      # the script used for calculation only take into account stopped or
      # delivered paysheet
      paysheet.stop()
    self.tic()

    base_contribution = 'base_contribution/base_amount/payroll/report/salary/gross'
    # here, check how much is contributed to the slices
    # the slices defined for this tax are :
    # - 0 to 200
    # - 200 to 400
    # - 400 to 5000
    # the salary is of 3000
    self.assertEqual(400, # 200 from the 1st paysheet + 200 from the 2e
        paysheet_list[1].PaySheetTransaction_getYearToDateSlice(
            base_contribution, 'salary_range/france/slice_0_to_200'))
    self.assertEqual(400, # 200 from the 1st paysheet + 200 from the 2e
        paysheet_list[1].PaySheetTransaction_getYearToDateSlice(\
            base_contribution, 'salary_range/france/slice_200_to_400'))
    self.assertEqual(5200, # (3000 - 400)*2
        paysheet_list[1].PaySheetTransaction_getYearToDateSlice(\
            base_contribution, 'salary_range/france/slice_400_to_5000'))

  def test_01_getYearToDateSlice(self):
    '''Check that is possible to calculate the total amount spend on a slice
    since the begining of the year.
    '''
    sequence_list = SequenceList()
    sequence_string = """
               CreateUrssafService
               CreateLabourService
               CreateEmployer
               CreateEmployee
               CreatePriceCurrency
               CreateModelWithSlices
               SetCurrencyOnModel
               ModelCreateUrssafModelLineWithSlices
               UrssafModelLineWithSlicesCreateMovements
    """ + self.PAYSHEET_WITH_SLICE_SEQUENCE_STRING +\
          self.PAYSHEET_WITH_SLICE_SEQUENCE_STRING + """
               CheckYearToDateSliceAmount
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

import unittest
def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestPayroll_l10n_fr))
  return suite
