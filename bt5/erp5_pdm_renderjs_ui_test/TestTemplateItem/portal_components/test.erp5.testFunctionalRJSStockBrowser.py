##############################################################################
#
# Copyright (c) 2018 Nexedi SARL and Contributors. All Rights Reserved.
#                    Ayush Tiwari <ayush.tiwari@nexedi.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import unittest

from Products.ERP5Type.tests.ERP5TypeFunctionalTestCase import \
        ERP5TypeFunctionalTestCase

class TestRenderJSUIStockBrowser(ERP5TypeFunctionalTestCase):
  foreground = 0
  run_only = "renderjs_ui_stock_browser_zuite"

  def getBusinessTemplateList(self):
    """
      Return the list of business templates.
    """
    return (
      'erp5_pdm_renderjs_ui_test',
      'erp5_pdm_ui_test',
      'erp5_pdm',
      'erp5_web_renderjs_ui',
      'erp5_web_renderjs_ui_test',
      'erp5_ui_test_core',
      'erp5_test_result',
      'erp5_configurator_standard_trade_template',
    )

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestRenderJSUIStockBrowser))
  return suite
