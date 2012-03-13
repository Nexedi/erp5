##############################################################################
#
# Copyright (c) 2011 Nexedi SARL and Contributors. All Rights Reserved.
#                     Rafael Monnerat <rafael@nexedi.com>
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

class TestZeleniumRunMyDocSample(ERP5TypeFunctionalTestCase):
  """
    Simple Test to assure that ERP5TypeFunctionalTestCase can pull code from a 
    URL and to test if ERP5 can provide approppriate code.

    The url should provide an equivalent Zope Page template used by Zelenium.

    TestPage_viewSeleniumTest is a perfect way to extract test from a Test Page,
    but the usage of Test Page is not mandatory, any valid Selenium Test in HTML 
    can be used.
  """
  foreground = 0
  run_only = "tutorial_zuite"
  remote_code_url_list = [
     "https://www.tiolive.com/nexedi/test_page_module/14/TestPage_viewSeleniumTest",
     # Warning, the URLs bellow use cache and be delayed to
     # be updated ( and produce inconsistent results).
     "http://www.erp5.com/test_page_module/14/TestPage_viewSeleniumTest",
     "http://www.erp5.com/developer-Test.Page.Sample/TestPage_viewSeleniumTest",]

  def getBusinessTemplateList(self):
    """
      Return the list of business templates.
    """
    return ('erp5_core_proxy_field_legacy', 'erp5_full_text_myisam_catalog',
            'erp5_base', 'erp5_ui_test_core')

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestZeleniumRunMyDocSample))
  return suite
