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

class TestZeleniumConfiguratorStandard(ERP5TypeFunctionalTestCase):
  run_only = "configurator_standard_zuite"
  base_remote_code_url = [
     "http://www.erp5.com/user-Howto.Create.Person-TESTONLY/TestPage_viewSeleniumTest",
     "http://www.erp5.com/user-Howto.Create.Organisations-TESTONLY/TestPage_viewSeleniumTest",
     "http://www.erp5.com/user-Howto.Link.Persons.and.Organisations-TESTONLY/TestPage_viewSeleniumTest",
     "http://www.erp5.com/user-Howto.Create.Campaigns-TESTONLY/TestPage_viewSeleniumTest",
     "http://www.erp5.com/user-Howto.Create.Outgoing.Events-TESTONLY/TestPage_viewSeleniumTest",
     "http://www.erp5.com/user-Howto.Post.Outgoing.Events-TESTONLY/TestPage_viewSeleniumTest",
     # Chapter 17 is missing here
     "http://www.erp5.com/user-Howto.Process.Incoming.Events-TESTONLY/TestPage_viewSeleniumTest",
     # Products test bellow
     "http://www.erp5.com/user-Howto.Create.and.Manage.Products-TESTONLY/TestPage_viewSeleniumTest",
     # The test bellow should be splited because it handle several tutorials at
     # once which is what it is wanted.
     "http://www.erp5.com/user-Howto.Create.Sale.Orders-TESTONLY/TestPage_viewSeleniumTest",
     # Additional Tests not yet related to any previous tutorial
     "http://www.erp5.com/user-HowTo.Use.FullText.Search-TESTONLY/TestPage_viewSeleniumTest",
     "http://www.erp5.com/user-HowTo.Change.Language-TESTONLY/TestPage_viewSeleniumTest"
  ]

  remote_code_url_list = [
     "http://www.erp5.com/user-Howto.Configure.ERP5.for.SMB.With.Configurator/TestPage_viewSeleniumTest"
     ] + base_remote_code_url

  def afterSetUp(self):
     # information to know if a business template is a standard business
     # template or a custom one
     public_bt5_repository_list = ['http://www.erp5.org/dists/snapshot/bt5/']
     template_list = self._getBTPathAndIdList(["erp5_base"])
     if len(template_list) > 0:
       bt5_repository_path = "/".join(template_list[0][0].split("/")[:-1])
       try:
         self.portal.portal_templates.updateRepositoryBusinessTemplateList(
                [bt5_repository_path], None)
       except (RuntimeError, IOError):
         # If bt5 repository is not a repository use public one.
         self.portal.portal_templates.updateRepositoryBusinessTemplateList(
                                   public_bt5_repository_list)
     else:
       self.portal.portal_templates.updateRepositoryBusinessTemplateList(
                                     public_bt5_repository_list)
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
