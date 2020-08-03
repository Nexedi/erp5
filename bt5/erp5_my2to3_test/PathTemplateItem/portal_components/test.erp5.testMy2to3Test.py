##############################################################################
#
# Copyright (c) 2002-2020 Nexedi SA and Contributors. All Rights Reserved.
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


class TestMy2to3Test(ERP5TypeTestCase):
  def getBusinessTemplateList(self):
    return ('erp5_my2to3',)

  def afterSetUp(self):
    self.my2to3_test_module = m = self.portal.getDefaultModule(portal_type='my2to3 Test')
    self.assertIsNotNone(m)

  def test_script(self):
    self.my2to3_test_module.script()

  def test_page_template(self):
    self.my2to3_test_module.page_template()

  def test_external_method(self):
    self.my2to3_test_module.external_method()


1 / 2