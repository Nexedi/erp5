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

from Products.ERP5Type.tests.testFunctionalStandaloneUserTutorial import \
        BASE_REMOTE_SELENIUM_TEST_URL_LIST

class TestZeleniumConfiguratorStandard(ERP5TypeFunctionalTestCase):
  run_only = "configurator_standard_zuite"

  remote_code_url_list = [
     "http://www.erp5.com/user-Howto.Configure.ERP5.for.SMB.With.Configurator/TestPage_viewSeleniumTest"
     ] + BASE_REMOTE_SELENIUM_TEST_URL_LIST

  def afterSetUp(self):
     self.setupAutomaticBusinessTemplateRepository()
     print self.portal.portal_templates.getRepositoryList()
     ERP5TypeFunctionalTestCase.afterSetUp(self)

  def getBusinessTemplateList(self):
    """
      Return the list of business templates.
    """
    return ('erp5_core_proxy_field_legacy', 'erp5_full_text_myisam_catalog',
            'erp5_base', 'erp5_workflow', 
            'erp5_configurator', 'erp5_configurator_standard',
            # Test suite
           'erp5_ui_test_core', 'erp5_configurator_standard_ui_test',
           'erp5_user_tutorial_ui_test'
           )

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestZeleniumConfiguratorStandard))
  return suite
