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
from PIL import Image
import StringIO

class Test(ERP5TypeTestCase):
  """
  A Sample Test Class
  """

  def getTitle(self):
    return "testReceiptOrientation"

  def getBusinessTemplateList(self):
    """
    Tuple of Business Templates we need to install
    """
    
    return ('erp5_base', 'erp5_dms', 'nexedi_travel_expense_image_orientation')


  def _run_orientation_detection(self, module_id, expected_rotation):
    original_image_id = module_id + "_to_rotate"
    human_rotated_id = module_id + "_rotated"
    tmp_id = "test_expense_validation_request_invoice_tmp"
    
    data = self.portal.image_module[original_image_id].getData()
    data = StringIO.StringIO(data)
    
    # detect orientation
    rotation = self.portal.Base_detectImageOrientation(data)
    self.assertEqual(rotation, expected_rotation)
    
    # image rotation
    image = Image.open(data).rotate(rotation)
    
    # put orientation
    image_export = StringIO.StringIO()
    image.save(image_export, 'png')
    self.portal.image_module[tmp_id].setData(image_export.getvalue())
    self.tic()
    
    # verify the result
    image_human_rotated = self.portal.image_module[human_rotated_id].getData()

    image_auto_rotated =  self.portal.image_module[tmp_id].getData()
    
    return self.assertEqual(image_human_rotated, image_auto_rotated)

  def test_orientation_1(self) :
    return self._run_orientation_detection("test_expense_validation_request_invoice1", 270)
    
  def test_orientation_2(self) :
    return self._run_orientation_detection("test_expense_validation_request_invoice2", 0)
    
  def test_orientation_3(self) :
    return self._run_orientation_detection("test_expense_validation_request_invoice3", 90)
    
  def test_orientation_4(self) :
    return self._run_orientation_detection("test_expense_validation_request_invoice4", 180)