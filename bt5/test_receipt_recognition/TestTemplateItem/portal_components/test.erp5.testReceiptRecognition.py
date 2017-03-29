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
    result = self.portal.find_receipt_value(data.getData())
    return result

  def test_functionnality(self):
    """
    Functionnality test: test if the value of the image is recognized
    """
    self.assertEquals(self._run_recognition("1"), 28.0)
    self.assertEquals(self._run_recognition("2"), 311.35)
    # The following image should contain the value "28" but fail due to
    # its bad quality
    self.assertEquals(self._run_recognition("3"), 24.09)
    self.assertEquals(self._run_recognition("4"), 7.8)
    self.assertEquals(self._run_recognition("5"), 5.85)
    # This image should contain 5.85, but the module fail to recognize
    # the keyword "EUR" in the line.
    self.assertEquals(self._run_recognition("6"), 5.55)
    self.assertEquals(self._run_recognition("7"), 21.27)
    self.assertEquals(self._run_recognition("8"), 6.8)
    # This receipt was folded multiple time and is filled with un-clearable
    # noise.
    with self.assertRaises(ValueError):
      self._run_recognition("9")

  def test_create_object(self):
    """
    Test creation of receipt object and call of the action function
    """
    source = self.portal.image_module["1"]
    receipt = self.portal.receipt_recognition_module.newContent(
      id="0",
      title="test",
      source_value=source
    )
    receipt.ReceiptConversion_convertImage(batch_mode=True)
    self.assertEquals(receipt.total, 28.0)

