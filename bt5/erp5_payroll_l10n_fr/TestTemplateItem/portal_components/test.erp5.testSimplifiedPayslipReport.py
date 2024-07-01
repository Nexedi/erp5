# -*- coding: utf-8 -*-
#############################################################################
#
# Copyright (c) 2002-2015 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from DateTime import DateTime
from PIL import Image
from io import BytesIO
import math
import os.path
from Products.Localizer.itools.i18n.accept import AcceptLanguage
import six


class TestSimplifiedPayslipReport(ERP5TypeTestCase):
  def getTitle(self):
    return "Simplified Payslip Report"

  def beforeTearDown(self):
    test_pay_sheet_transaction = self.portal.accounting_module.test_pay_sheet_transaction
    test_pay_sheet_transaction.setStartDate(DateTime("2018/01/01"))
    self.tic()

  def computeImageRenderingRootMeanSquare(self, image_data_1, image_data_2):
    """
      Compute and return the RMS (Root Mean Square) of image_data_1 and 2.
      This value can be used to compare two images in rendering point of view.

      Both image_data should be in the same quality as most as possible
      (better compare lossless format) to reduce quality differences beside
      rendering differences.
    """
    # https://duckduckgo.com/?q=python+compare+images&ia=qa
    # https://stackoverflow.com/a/1927681/
    # http://snipplr.com/view/757/compare-two-pil-images-in-python/
    # http://effbot.org/zone/pil-comparing-images.htm
    # http://effbot.org/imagingbook/image.htm
    image1 = Image.open(BytesIO(image_data_1))
    image2 = Image.open(BytesIO(image_data_2))

    # image can be converted into greyscale without transparency
    h1 = image1.histogram()
    h2 = image2.histogram()
    rms = math.sqrt(sum((a - b) ** 2 for a, b in zip(h1, h2)) / len(h1))

    # Note:
    # - rms is ~5300.0 same page, bmp without alpha and bmp transparent back
    # - rms is ~1125.7 same page, jpg and bmp images
    # - rms is ~512.9 cover (big title + short title) and introduction page
    # - rms is ~1.0 if date is 2017-06-07 vs 2017-06-06 with bmp images
    return rms

  def assertImageRenderingEquals(self, test_image_data, expected_image_data, message="Images rendering differs", max_rms=10.0):
    rms = self.computeImageRenderingRootMeanSquare(test_image_data, expected_image_data)
    if rms <= max_rms:
      return
    from Products.ERP5Type.tests.runUnitTest import log_directory
    if log_directory:
      with open(os.path.join(log_directory, '%s-expected.png' % self.id()), 'wb') as f:
        f.write(expected_image_data)
      with open(os.path.join(log_directory, '%s-actual.png' % self.id()), 'wb') as f:
        f.write(test_image_data)
    raise AssertionError("%(message)s\nRMS: %(rms)s > %(max_rms)s\nAssertionError: %(message)s" % {
      "message": message,
      "rms": rms,
      "max_rms": max_rms,
    })

  def test_01_payslip_content(self):
    test_pay_sheet_transaction = self.portal.accounting_module.test_pay_sheet_transaction
    """
      from 01/01/18 to 30/09/18
      amount_of_remuneration_evolution = gross_salary * 2.2% - CSG * 1.7%
      from 01/10/2018
      amount_of_remuneration_evolution = gross_salary * 3.15% - CSG * 1.7%
    """
    expected_payslip_content = {
    "gross_salary": 2250.0,
    "net_salary_before_income_tax": 8707.33,
    "net_salary": 8589.75,
    "currency": "€",
    "amount_of_remuneration_evolution":  2250 * 0.022 - 2305.53 * 0.017,
    "income_tax_dict": {'employee_price': -0.051, 'employee_total_price': -117.58, 'base': 2305.535},
    "total_pay_by_employer": 9854.24,
    "total_contribution_relief": 468.88
    }
    payslip_content = test_pay_sheet_transaction.PaySheetTransaction_getPayslipData()
    for key, value in six.iteritems(expected_payslip_content):
      self.assertAlmostEqual(value, payslip_content[key])

    expected_non_contribution_dict_list= [
      {'title': 'AMOUNT NON SUBJECT TO CONTRIBUTION', 'base': 0, 'employee_price': 0, 'employee_total_price': 0, 'employer_price': 0, 'employer_total_price': 0},
      {'title': 'Remboursement transport en commun', 'base': 14.0, 'employee_price': None, 'employee_total_price': 14.0, 'employer_price': None, 'employer_total_price': None},
      {'title': 'Plvt cheques vacances', 'base': -44.0, 'employee_price': None, 'employee_total_price': -44.0, 'employer_price': None, 'employer_total_price': None},
      {'title': 'Remboursement internet', 'base': 0.0, 'employee_price': None, 'employee_total_price': 0.0, 'employer_price': None, 'employer_total_price': None},
      {'title': 'Tickets restaurant', 'base': -3.2, 'employee_price': 4.0, 'employee_total_price': -12.8, 'employer_price': 4.0, 'employer_total_price': -19.2},
      {'title': 'TOTAL AMOUNTS NON SUBJECT TO CONTRIBUTIONS', 'base': 0, 'employee_price': 0, 'employee_total_price': -42.8, 'employer_price': 0, 'employer_total_price': -19.2}
    ]

    non_contribution_dict_list = payslip_content['non_contribution_dict_list']
    self.assertEqual(len(non_contribution_dict_list), len(expected_non_contribution_dict_list))
    for index in  range(len(expected_non_contribution_dict_list)):
      expected_value_dict = expected_non_contribution_dict_list[index]
      value_dict = non_contribution_dict_list[index]
      for key, value in six.iteritems(expected_value_dict):
        self.assertEqual(value_dict[key], value)

    expected_contribution_dict_list = [
      {'title': 'FIRST NAME LAST NAME', 'base': 0, 'employee_price': 0, 'employee_total_price': 0, 'employer_price': 0, 'employer_total_price': 0},
      {'title': 'Salaire de base', 'base': 2250.0, 'employee_price': None, 'employee_total_price': None, 'employer_price': None, 'employer_total_price': None},
      {'title': 'GROSS SALARY', 'base': 2250.0, 'employee_price': 0, 'employee_total_price': 0, 'employer_price': 0, 'employer_total_price': 0},
      {'title': 'Prime exceptionnelle pouvoir achat', 'base': 1000.0, 'employee_price': None, 'employee_total_price': None, 'employer_price': None, 'employer_total_price': None},
      {'title': 'Prime interessement PEE', 'base': 6000.0, 'employee_price': None, 'employee_total_price': None, 'employer_price': None, 'employer_total_price': None},
      {'title': 'HEALTH', 'base': 0, 'employee_price': 0, 'employee_total_price': 0, 'employer_price': 0, 'employer_total_price': 0},
      {'title': 'Assurance maladie', 'base': 2250.0, 'employee_price': -0.0075, 'employee_total_price': -16.88, 'employer_price': -0.128, 'employer_total_price': -288.0},
      {'title': 'Mutuelle CIC PP', 'base': 79.16, 'employee_price': None, 'employee_total_price': None, 'employer_price': -1.0, 'employer_total_price': -79.16},
      {'title': 'Mutuelle CIC Famille 2015 TA', 'base': 2250.0, 'employee_price': -0.008, 'employee_total_price': -18.0, 'employer_price': None, 'employer_total_price': None},
      {'title': 'Prevoyance Generali TA', 'base': 2250.0, 'employee_price': None, 'employee_total_price': None, 'employer_price': -0.007, 'employer_total_price': -15.75},
      {'title': 'WORK ACCIDENT-OCCUPATIONAL DISEASE', 'base': 2250.0, 'employee_price': 0, 'employee_total_price': 0, 'employer_price': -0.011, 'employer_total_price': -24.75},
      {'title': 'RETIREMENT', 'base': 0, 'employee_price': 0, 'employee_total_price': 0, 'employer_price': 0, 'employer_total_price': 0},
      {'title': 'Assurance vieillesse', 'base': 2250.0, 'employee_price': -0.0685, 'employee_total_price': -154.13, 'employer_price': -0.085, 'employer_total_price': -191.25},
      {'title': 'GMP', 'base': 322.82, 'employee_price': -0.078, 'employee_total_price': -25.18, 'employer_price': -0.1275, 'employer_total_price': -41.16},
      {'title': 'CET', 'base': 2250.0, 'employee_price': -0.0013, 'employee_total_price': -2.92, 'employer_price': -0.0022, 'employer_total_price': -4.95},
      {'title': 'Retraite complementaire IRNEO TA', 'base': 2250.0, 'employee_price': -0.031, 'employee_total_price': -69.75, 'employer_price': -0.0465, 'employer_total_price': -104.63},
      {'title': 'AGFF TA', 'base': 2250.0, 'employee_price': -0.008, 'employee_total_price': -18.0, 'employer_price': -0.012, 'employer_total_price': -27.0},
      {'title': 'Assurance vieillesse deplafonnée', 'base': 2250.0, 'employee_price': -0.003, 'employee_total_price': -6.75, 'employer_price': -0.018, 'employer_total_price': -40.5},
      {'title': 'FAMILY-SOCAL SECURITY', 'base': 2250.0, 'employee_price': 0, 'employee_total_price': 0, 'employer_price': -0.0345, 'employer_total_price': -77.625},
      {'title': 'UNEMPLOYMENT INSURANCE', 'base': 2250.0, 'employee_price': -0.02424, 'employee_total_price': -54.54, 'employer_price': -0.04336, 'employer_total_price': -97.56},
      {'title': 'OTHER EMPLOYER CONTRIBUTIONS', 'base': 94.91, 'employee_price': 0, 'employee_total_price': 0, 'employer_price': -0.08, 'employer_total_price': -7.5927999999999995},
      {'title': 'OTHER EMPLOYER CONTRIBUTIONS', 'base': 2250.0, 'employee_price': 0, 'employee_total_price': 0, 'employer_price': -0.024, 'employer_total_price': -54.0},
      {'title': 'CSG NON TAXABLE TO INCOME TAX', 'base': 0, 'employee_price': 0, 'employee_total_price': 0, 'employer_price': 0, 'employer_total_price': 0},
      {'title': 'CSG non deductible', 'base': 2305.53, 'employee_price': -0.029, 'employee_total_price': -66.86, 'employer_price': None, 'employer_total_price': None},
      {'title': 'CSG/CRDS TAXABLE TO INCOME TAX', 'base': 0, 'employee_price': 0, 'employee_total_price': 0, 'employer_price': 0, 'employer_total_price': 0},
      {'title': 'CSG/CRDS imposible a impot sur le  revenu', 'base': 2305.53, 'employee_price': -0.029, 'employee_total_price': -66.86, 'employer_price': None, 'employer_total_price': None},
      {'title': 'CONTRIBUTION RELIEF', 'base': 468.88, 'employee_price': 0, 'employee_total_price': 0, 'employer_price': 1.0, 'employer_total_price': 468.88},
      {'title': 'TOTAL CONTRIBUTIONS', 'base': 0, 'employee_price': 0, 'employee_total_price': -499.87, 'employer_price': 0, 'employer_total_price': -585.04}
    ]

    contribution_dict_list = payslip_content['contribution_dict_list']
    self.assertEqual(len(contribution_dict_list), len(expected_contribution_dict_list))
    for index in  range(len(expected_contribution_dict_list)):
      expected_value_dict = expected_contribution_dict_list[index]
      value_dict = contribution_dict_list[index]
      for key, value in six.iteritems(expected_value_dict):
        self.assertAlmostEqual(value_dict[key], value)

    test_pay_sheet_transaction.setStartDate(DateTime("2020/01/01"))
    self.tic()
    self.assertEqual(test_pay_sheet_transaction.PaySheetTransaction_getPayslipData()['amount_of_remuneration_evolution'], 2250 * 0.0315 - 2305.53 * 0.017)

  def test_02_payslip_view(self):
    test_pay_sheet_transaction = self.portal.accounting_module.test_pay_sheet_transaction
    expected_image = self.portal.image_module.pay_sheet_transaction_expected_image
    image_source_pdf_doc = self.portal.document_module.pay_sheet_transaction_image_source_pdf_doc
    self.app.REQUEST["AcceptLanguage"] = AcceptLanguage()
    self.app.REQUEST["AcceptLanguage"].set("*", 0)
    pdf_data = test_pay_sheet_transaction.PaySheetTransaction_printPayslipReport(format="pdf")
    image_source_pdf_doc.setData(pdf_data)
    self.tic()
    _, png = image_source_pdf_doc.convert("png", frame=0, quality=100)
    self.assertImageRenderingEquals(bytes(png), bytes(expected_image.getData()))

  def test_03_payslip_holiday(self):
    for i in self.portal.portal_catalog(
      portal_type= ('Leave Request', 'Holiday Acquisition'),
      destination_uid= self.portal.person_module.test_pay_sheet_transaction_user.getUid(),
      simulation_state = 'confirmed'
    ):
      i.cancel()
    self.tic()
    service = self.portal.service_module.newContent(portal_type='Service')
    leave_request = self.portal.leave_request_module.newContent(
      portal_type='Leave Request',
      destination = 'person_module/test_pay_sheet_transaction_user',
      resource_value = service
    )
    leave_request.newContent(
      portal_type='Leave Request Period',
      start_date = DateTime('2018/01/02'),
      stop_date = DateTime('2018/01/03'),
      resource_value = service,
      quantity=2)
    leave_request.edit(
      effective_date = DateTime('2018/01/31')
    )
    leave_request.plan()
    leave_request.confirm()
    self.tic()
    payslip_data = self.portal.accounting_module.test_pay_sheet_transaction.PaySheetTransaction_generatePayslipReport(batch=1)
    self.assertEqual(payslip_data["report_data"]["total_holiday_this_year"], -2)
    self.assertEqual(payslip_data["report_data"]["taken_holiday"], 2)
    leave_request.edit(
      effective_date = DateTime('2018/02/01')
    )
    self.tic()
    payslip_data = self.portal.accounting_module.test_pay_sheet_transaction.PaySheetTransaction_generatePayslipReport(batch=1)
    self.assertEqual(payslip_data["report_data"]["total_holiday_this_year"], 0)
    self.assertEqual(payslip_data["report_data"]["taken_holiday"], 0)

    holiday_acquisition = self.portal.holiday_acquisition_module.newContent(
      portal_type='Holiday Acquisition',
      quantity=3,
      start_date= DateTime('2018/01/31'),
      stop_date = DateTime('2018/01/31'),
      resource_value = service,
      destination = 'person_module/test_pay_sheet_transaction_user'
    )
    holiday_acquisition.plan()
    holiday_acquisition.confirm()
    leave_request.edit(
      effective_date = DateTime('2018/01/31')
    )
    self.tic()
    payslip_data = self.portal.accounting_module.test_pay_sheet_transaction.PaySheetTransaction_generatePayslipReport(batch=1)
    self.assertEqual(payslip_data["report_data"]["total_holiday_this_year"], 1)
    self.assertEqual(payslip_data["report_data"]["taken_holiday"], 2)
    holiday_acquisition = self.portal.holiday_acquisition_module.newContent(
      portal_type='Holiday Acquisition',
      quantity=3,
      start_date= DateTime('2017/12/31'),
      stop_date = DateTime('2017/12/31'),
      resource_value = service,
      destination = 'person_module/test_pay_sheet_transaction_user')
    holiday_acquisition.plan()
    holiday_acquisition.confirm()
    self.tic()
    payslip_data = self.portal.accounting_module.test_pay_sheet_transaction.PaySheetTransaction_generatePayslipReport(batch=1)
    self.assertEqual(payslip_data["report_data"]["total_holiday_this_year"], 3)
    self.assertEqual(payslip_data["report_data"]["taken_holiday"], 2)
    self.assertEqual(payslip_data["report_data"]["total_holiday_year_before"], 1)
    holiday_acquisition.edit(quantity = 1)
    self.tic()
    payslip_data = self.portal.accounting_module.test_pay_sheet_transaction.PaySheetTransaction_generatePayslipReport(batch=1)
    self.assertEqual(payslip_data["report_data"]["total_holiday_this_year"], 2)
    self.assertEqual(payslip_data["report_data"]["taken_holiday"], 2)
    self.assertEqual(payslip_data["report_data"]["total_holiday_year_before"], 0)
