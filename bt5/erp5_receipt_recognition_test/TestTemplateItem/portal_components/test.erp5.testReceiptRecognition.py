##############################################################################
#
# Copyright (c) 2002-2017 Nexedi SA and Contributors. All Rights Reserved.
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

class Test(ERP5TypeTestCase):
  """
  A Sample Test Class
  """

  def getTitle(self):
    return "testReceiptRecognition"

  def getBusinessTemplateList(self):
    """
    Tuple of Business Templates we need to install
    """
    return ('erp5_base', 'erp5_dms', 'erp5_wendelin', 'erp5_receipt_recognition', 'test_receipt_recognition')


  def _run_recognition(self, module_id):
    data = self.portal.image_module[module_id]
    result = self.portal.ReceiptRecognition_getReceiptValue(data.getData())
    return result

  def test_bank_receipt(self):
    """
    This test is successfull. The receipt have a grey text on the whole
    diagonal (name of the bank) but it still works
    """
    self.assertEqual(self._run_recognition("erp5_receipt_recognition_test_image_sample_001"), 28.0)

  def test_distorted_receipt(self):
    """
    This receipt is sghtly curved: the middle is higher than the top and
    bottom
    """
    self.assertEqual(self._run_recognition("erp5_receipt_recognition_test_image_sample_002"), 311.35)

  def test_noisy_image(self):
    """
    The following image should contain the value "28.00" but fail due to
    its base quality.
    """
    self.assertEqual(self._run_recognition("erp5_receipt_recognition_test_image_sample_003"), 24.09)

  def test_cropped_receipt(self):
    """
    This test is successfull. The left and top sid of the receip
    """
    self.assertEqual(self._run_recognition("erp5_receipt_recognition_test_image_sample_004"), 7.8)

  def test_defolded_receipt1(self):
    """
    This test is successfull.
    """
    self.assertEqual(self._run_recognition("erp5_receipt_recognition_test_image_sample_005"), 5.85)

  def test_defolded_receipt2(self):
    """
    This image should contain 5.85, but the module fail to recognize
    the keyword "EUR" in the line.
    """
    self.assertEqual(self._run_recognition("erp5_receipt_recognition_test_image_sample_006"), 5.55)

  def test_monoprix_receipt(self):
    """
    On this receipt, the OCR cannot read the total value because of the
    weird typeset (to do this, we need our own models), but find which
    value was paid with credit card.
    """
    self.assertEqual(self._run_recognition("erp5_receipt_recognition_test_image_sample_007"), 21.27)

  def test_coiled_receipt(self):
    """
    This test is successfull. The receipt is vertically coiled. It leads
    to darker areas in the middle of the receipt that used to break the
    cleaning and segementation.
    """
    self.assertEqual(self._run_recognition("erp5_receipt_recognition_test_image_sample_008"), 6.8)

  def test_failure(self):
    """
    This should fail
    This receipt was folded multiple time and is filled with un-clearable
    noise.
    """
    with self.assertRaises(ValueError):
      self._run_recognition("erp5_receipt_recognition_test_image_sample_009")

  def test_create_object(self):
    """
    Test creation of receipt object and call of the action function
    """
    follow_up = self.portal.image_module["erp5_receipt_recognition_test_image_sample_001"]
    receipt = self.portal.receipt_recognition_module.newContent(
      id="0",
      title="test",
      follow_up_value=follow_up
    )
    receipt.ReceiptRecognition_convertImage(batch_mode=True)
    self.assertEqual(receipt.total, 28.0)

