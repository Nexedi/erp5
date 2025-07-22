##############################################################################
#
# Copyright (c) 2011 Nexedi SA and Contributors. All Rights Reserved.
#                     Rafael Monnerat <rafael@nexedi.com>
#
# This program is free software: you can Use, Study, Modify and Redistribute
# it under the terms of the GNU General Public License version 3, or (at your
# option) any later version, as published by the Free Software Foundation.
#
# You can also Link and Combine this program with other software covered by
# the terms of any of the Free Software licenses or any of the Open Source
# Initiative approved licenses and Convey the resulting work. Corresponding
# source of such a combination shall include the source code for all other
# software used.
#
# This program is distributed WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See COPYING file for full licensing terms.
# See https://www.nexedi.com/licensing for rationale and options.
#
##############################################################################

import unittest
from Products.ERP5Type.tests.ERP5TypeFunctionalTestCase import \
        ERP5TypeFunctionalTestCase

class TestZeleniumRunTutorialTests(ERP5TypeFunctionalTestCase):
  """
    Simple Test to assure that ERP5TypeFunctionalTestCase can pull code from a
    URL and to test if ERP5 can provide approppriate code.

    The url should provide an equivalent Zope Page template used by Zelenium.

    TestPage_viewSeleniumTest is a perfect way to extract test from a Test Page,
    but the usage of Test Page is not mandatory, any valid Selenium Test in HTML
    can be used.
  """
  foregroun = 0
  run_only = "tutorial_zuite"

  def afterSetUp(self):
    url_list = []
    for x in self.portal.test_page_module.objectValues():
      if "wendelin" in x.getId():
        url_list.append("test_page_module/"+x.getId())
    self.remote_code_url_list = url_list
    ERP5TypeFunctionalTestCase.afterSetUp(self)


  def getBusinessTemplateList(self):
    """
      Return the list of business templates.
    """
    return ('erp5_wendelin', 'erp5_core_proxy_field_legacy', 'erp5_full_text_mroonga_catalog',
            'erp5_base', 'erp5_ui_test_core','erp5_web', 'erp5_ingestion',
            'erp5_simulation', 'erp5_accounting',
            'erp5_jquery', 'erp5_dms', 'erp5_jquery_ui', 'erp5_web',
            'erp5_slideshow_style', 'erp5_knowledge_pad', 'erp5_run_my_doc',
            'erp5_user_tutorial_ui_test', 'erp5_user_tutorial','erp5_wendelin_tutorial_ui_test','erp5_wendelin_data_lake_ui')

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestZeleniumRunTutorialTests))
  return suite
