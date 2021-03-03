##############################################################################
#
# Copyright (c) 2011 Nexedi SARL and Contributors. All Rights Reserved.
#                     Kazuhiko <kazuhiko@nexedi.com>
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

import random
import unittest

from Products.ERP5Type.tests.ERP5TypeFunctionalTestCase import \
        ERP5TypeFunctionalTestCase

class TestZeleniumStandaloneUserTutorial(ERP5TypeFunctionalTestCase):
  foreground = 0
  run_only = "user_tutorial_zuite"

  def afterSetUp(self):
    url_list = []
    for x in self.portal.test_page_module.objectValues():
      if "user" in x.getId():
        url_list.append("test_page_module/"+x.getId())
    self.remote_code_url_list = url_list
    # Execute the business configuration if not installed
    business_configuration = self.getBusinessConfiguration()
    if (business_configuration.getSimulationState() != 'installed'):
      self.portal.portal_caches.erp5_site_global_id = '%s' % random.random()
      self.portal.portal_caches._p_changed = 1
      self.commit()
      self.portal.portal_caches.updateCache()

      self.bootstrapSite()
      self.commit()

    ERP5TypeFunctionalTestCase.afterSetUp(self)

  def bootstrapSite(self):
    self.logMessage('OSOE Development bootstrapSite')

    self.clearCache()
    self.tic()
    self.setUpConfiguratorOnce()
    self.tic()

  def setUpConfiguratorOnce(self):
    self.commit()
    self.portal.portal_templates.updateRepositoryBusinessTemplateList(
       repository_list=self.portal.portal_templates.getRepositoryList())
    self.commit()
    self.launchConfigurator()

  def launchConfigurator(self):
    self.logMessage('OSOE Access Page launchConfigurator')
    self.login()
    # Create new Configuration
    business_configuration  = self.getBusinessConfiguration()

    response_dict = {}
    while response_dict.get("command", "next") != "install":
      response_dict = self.portal.portal_configurator._next(
                            business_configuration, {})

    self.tic()
    self.portal.portal_configurator.startInstallation(
                 business_configuration,REQUEST=self.portal.REQUEST)

  def getBusinessConfiguration(self):
    return self.portal.business_configuration_module[\
                          "default_standard_configuration"]

  def getBusinessTemplateList(self):
    """
      Return the list of business templates.
    """
    return ('erp5_core_proxy_field_legacy', 'erp5_full_text_mroonga_catalog',
            'erp5_base', 'erp5_ui_test_core',
            'erp5_dhtml_style',
            'erp5_jquery', 'erp5_jquery_ui',
            'erp5_knowledge_pad', 'erp5_pdm',
            'erp5_simulation', 'erp5_trade', 'erp5_ooo_import',
            'erp5_accounting', 'erp5_invoicing',
            'erp5_simplified_invoicing', 'erp5_project',
            'erp5_simulation',
            'erp5_configurator_standard_solver',
            'erp5_configurator_standard_trade_template',
            'erp5_configurator_standard_accounting_template',
            'erp5_configurator_standard_invoicing_template',
            'erp5_simulation_test',
            'erp5_ingestion', 'erp5_ingestion_mysql_innodb_catalog',
            'erp5_web', 'erp5_dms', 'erp5_credential',
            'erp5_rss_style', 'erp5_discussion',
            'erp5_l10n_fr', 'erp5_crm', 'erp5_forge',
            'erp5_run_my_doc',
            'erp5_osoe_web_renderjs_ui',
            'erp5_web_renderjs_ui_test_core',
            'erp5_user_tutorial_ui_test',
            'erp5_user_tutorial',
           )

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestZeleniumStandaloneUserTutorial))
  return suite