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
import cStringIO
import math
import io
import base64
from Products.Localizer.itools.i18n.accept import AcceptLanguage



class TestSimplifiedPayslipReport(ERP5TypeTestCase):
  def getTitle(self):
    return "Simplified Payslip Report"

  def beforeTearDown(self):
    test_pay_sheet_transaction = self.portal.accounting_module.test_pay_sheet_transaction
    test_pay_sheet_transaction.setStartDate(DateTime("2018/01/01"))
    for change_id in ['5','7','11','14']:
      test_pay_sheet_transaction[change_id].edit(
        group_by_report_section=1)
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
    image1 = Image.open(cStringIO.StringIO(image_data_1))
    image2 = Image.open(cStringIO.StringIO(image_data_2))

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

  def convertToPng(self, img_data):
    bmp_file = Image.open(io.BytesIO(img_data))
    img_buff = cStringIO.StringIO()
    bmp_file.save(img_buff, format='PNG', optimize=True, quality=75)
    img_data = img_buff.getvalue()
    return ''.join(['data:image/png;base64,', base64.encodestring(img_data)])

  def assertImageRenderingEquals(self, test_image_data, expected_image_data, message="Images rendering differs", max_rms=10.0):
    rms = self.computeImageRenderingRootMeanSquare(test_image_data, expected_image_data)
    if rms <= max_rms:
      return
    raise AssertionError("%(message)s\nComparing rendered image:\n%(base64_1)s\nWith expected image:\n%(base64_2)s\nRMS: %(rms)s > %(max_rms)s\nAssertionError: %(message)s" % {
      "message": message,
      "base64_1": self.convertToPng(test_image_data),
      "base64_2": self.convertToPng(expected_image_data),
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
    "total_pay_by_employer": 9854.25,
    "total_contribution_relief": 468.88
    }
    payslip_content = test_pay_sheet_transaction.PaySheetTransaction_getPayslipData()
    for key, value in expected_payslip_content.iteritems():
      self.assertEquals(value, payslip_content[key])

    expected_non_contribution_dict_list= [
      {'title': 'AMOUNT NON SUBJECT TO CONTRIBUTION', 'base': 0, 'employee_price': 0, 'employee_total_price': 0, 'employer_price': 0, 'employer_total_price': 0},
      {'title': 'Remboursement transport en commun', 'base': 14.0, 'employee_price': 1.0, 'employee_total_price': 14.0, 'employer_price': None, 'employer_total_price': None},
      {'title': 'Plvt cheques vacances', 'base': -44.0, 'employee_price': 1.0, 'employee_total_price': -44.0, 'employer_price': None, 'employer_total_price': None},
      {'title': 'Remboursement internet', 'base': 0.0, 'employee_price': None, 'employee_total_price': None, 'employer_price': None, 'employer_total_price': None},
      {'title': 'Tickets restaurant', 'base': -3.2, 'employee_price': 4.0, 'employee_total_price': -12.8, 'employer_price': 4.0, 'employer_total_price': -19.2},
      {'title': 'TOTAL AMOUNTS NON SUBJECT TO CONTRIBUTIONS', 'base': 0, 'employee_price': 0, 'employee_total_price': -42.8, 'employer_price': 0, 'employer_total_price': -19.2}
    ]

    non_contribution_dict_list = payslip_content['non_contribution_dict_list']
    self.assertEquals(len(non_contribution_dict_list), len(expected_non_contribution_dict_list))
    for index in  range(len(expected_non_contribution_dict_list)):
      expected_value_dict = expected_non_contribution_dict_list[index]
      value_dict = non_contribution_dict_list[index]
      for key, value in expected_value_dict.iteritems():
        self.assertEquals(value_dict[key], value)

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
      {'title': 'FAMILY-SOCAL SECURITY', 'base': 2250.0, 'employee_price': 0, 'employee_total_price': 0, 'employer_price': -0.0345, 'employer_total_price': -77.63},
      {'title': 'UNEMPLOYMENT INSURANCE', 'base': 2250.0, 'employee_price': -0.02424, 'employee_total_price': -54.54, 'employer_price': -0.04336, 'employer_total_price': -97.56},
      {'title': 'OTHER EMPLOYER CONTRIBUTIONS', 'base': 94.91, 'employee_price': 0, 'employee_total_price': 0, 'employer_price': -0.08, 'employer_total_price': -7.59},
      {'title': 'OTHER EMPLOYER CONTRIBUTIONS', 'base': 2250.0, 'employee_price': 0, 'employee_total_price': 0, 'employer_price': -0.024, 'employer_total_price': -54.0},
      {'title': 'CSG NON TAXABLE TO INCOME TAX', 'base': 0, 'employee_price': 0, 'employee_total_price': 0, 'employer_price': 0, 'employer_total_price': 0},
      {'title': 'CSG non deductible', 'base': 2305.53, 'employee_price': -0.029, 'employee_total_price': -66.86, 'employer_price': None, 'employer_total_price': None},
      {'title': 'CSG/CRDS TAXABLE TO INCOME TAX', 'base': 0, 'employee_price': 0, 'employee_total_price': 0, 'employer_price': 0, 'employer_total_price': 0},
      {'title': 'CSG/CRDS imposible a impot sur le  revenu', 'base': 2305.53, 'employee_price': -0.029, 'employee_total_price': -66.86, 'employer_price': None, 'employer_total_price': None},
      {'title': 'CONTRIBUTION RELIEF', 'base': 468.88, 'employee_price': 0, 'employee_total_price': 0, 'employer_price': 1.0, 'employer_total_price': 468.88},
      {'title': 'TOTAL CONTRIBUTIONS', 'base': 0, 'employee_price': 0, 'employee_total_price': -499.87, 'employer_price': 0, 'employer_total_price': -585.05}
    ]

    contribution_dict_list = payslip_content['contribution_dict_list']
    self.assertEquals(len(contribution_dict_list), len(expected_contribution_dict_list))
    for index in  range(len(expected_contribution_dict_list)):
      expected_value_dict = expected_contribution_dict_list[index]
      value_dict = contribution_dict_list[index]
      for key, value in expected_value_dict.iteritems():
        self.assertAlmostEquals(value_dict[key], value)

    test_pay_sheet_transaction.setStartDate(DateTime("2020/01/01"))
    self.tic()
    self.assertEqual(test_pay_sheet_transaction.PaySheetTransaction_getPayslipData()['amount_of_remuneration_evolution'], 2250 * 0.0315 - 2305.53 * 0.017)
    # OTHER EMPLOYER CONTRIBUTIONS
    change_id_list = ['5','7','11','14']
    for change_id in change_id_list:
      test_pay_sheet_transaction[change_id].edit(
        group_by_report_section=0)
    self.tic()
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
      {'title': 'FAMILY-SOCAL SECURITY', 'base': 2250.0, 'employee_price': 0, 'employee_total_price': 0, 'employer_price': -0.0345, 'employer_total_price': -77.63},
      {'title': 'UNEMPLOYMENT INSURANCE', 'base': 2250.0, 'employee_price': -0.02424, 'employee_total_price': -54.54, 'employer_price': -0.04336, 'employer_total_price': -97.56},
      {'title': 'OTHER EMPLOYER CONTRIBUTIONS', 'base': 0, 'employee_price': 0, 'employee_total_price': 0, 'employer_price': 0, 'employer_total_price': 0},
      {'title': 'aide au logement', 'base': 2250.0, 'employee_price': None, 'employee_total_price': None, 'employer_price': -0.001, 'employer_total_price': -2.25},
      {'title': 'Journee de solidarite', 'base': 2250.0, 'employee_price': None, 'employee_total_price': None, 'employer_price': -0.003, 'employer_total_price': -6.75},
      {'title': 'Versement au transport', 'base': 2250.0, 'employee_price': None, 'employee_total_price': None, 'employer_price': -0.02, 'employer_total_price': -45.0},
      {'title': 'Taxe Prevoyance', 'base': 94.91, 'employee_price': None, 'employee_total_price': None, 'employer_price': -0.08, 'employer_total_price': -7.59},
      {'title': 'CSG NON TAXABLE TO INCOME TAX', 'base': 0, 'employee_price': 0, 'employee_total_price': 0, 'employer_price': 0, 'employer_total_price': 0},
      {'title': 'CSG non deductible', 'base': 2305.53, 'employee_price': -0.029, 'employee_total_price': -66.86, 'employer_price': None, 'employer_total_price': None},
      {'title': 'CSG/CRDS TAXABLE TO INCOME TAX', 'base': 0, 'employee_price': 0, 'employee_total_price': 0, 'employer_price': 0, 'employer_total_price': 0},
      {'title': 'CSG/CRDS imposible a impot sur le  revenu', 'base': 2305.53, 'employee_price': -0.029, 'employee_total_price': -66.86, 'employer_price': None, 'employer_total_price': None},
      {'title': 'CONTRIBUTION RELIEF', 'base': 468.88, 'employee_price': 0, 'employee_total_price': 0, 'employer_price': 1.0, 'employer_total_price': 468.88},
      {'title': 'TOTAL CONTRIBUTIONS', 'base': 0, 'employee_price': 0, 'employee_total_price': -499.87, 'employer_price': 0, 'employer_total_price': -585.05}
    ]
    contribution_dict_list = test_pay_sheet_transaction.PaySheetTransaction_getPayslipData()['contribution_dict_list']
    self.assertEquals(len(contribution_dict_list), len(expected_contribution_dict_list))
    for index in  range(len(expected_contribution_dict_list)):
      expected_value_dict = expected_contribution_dict_list[index]
      value_dict = contribution_dict_list[index]
      for key, value in expected_value_dict.iteritems():
        self.assertAlmostEquals(value_dict[key], value)

  def test_02_payslip_view(self):
    test_pay_sheet_transaction = self.portal.accounting_module.test_pay_sheet_transaction
    expected_image = self.portal.image_module.pay_sheet_transaction_expected_image
    image_source_pdf_doc = self.portal.document_module.pay_sheet_transaction_image_source_pdf_doc
    self.app.REQUEST["AcceptLanguage"] = AcceptLanguage()
    self.app.REQUEST["AcceptLanguage"].set("*", 0)
    pdf_data = test_pay_sheet_transaction.PaySheetTransaction_printPayslipReport(format="pdf")
    image_source_pdf_doc.setData(pdf_data)
    self.tic()
    _, bmp = image_source_pdf_doc.convert("bmp", frame=0)
    self.assertImageRenderingEquals(str(bmp), str(expected_image.getData()))
