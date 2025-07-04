##############################################################################
#
# Copyright (c) 2002-2025 Nexedi KK and Contributors. All Rights Reserved.
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

class TestQuantityUnitConversion(ERP5TypeTestCase):
  """
  Make sure that all business templates for this test are reindexed
  properly while setting up an erp5 site, and as a result, this test
  can run.
  """

  def getBusinessTemplateList(self):
    return ('erp5_pdm',)

  def testQuantityUnitConversion(self):
    measure = self.portal.product_module.test_quantity_unit_unit_piece['1']
    self.assertEqual(measure.getConvertedQuantity(variation_list=('packing_form/case',)), 20)
