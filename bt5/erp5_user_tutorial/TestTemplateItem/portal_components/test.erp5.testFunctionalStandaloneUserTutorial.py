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
  configuration_info = {
    "Configure Organisation": {
      'field_your_title': 'SpaceZ',
      'field_your_default_email_text': 'john@spacez.com',
      'field_your_default_telephone_text': '0123456789',
      'field_your_default_address_street_address': 'Rue de JeanBart',
      'field_your_default_address_zip_code': '59000',
      'field_your_default_address_city': 'Lille',
      'field_your_default_address_region': 'europe/western_europe/france',
    },
    "Configure user accounts number": {
      'field_your_company_employees_number': "1",
    },
    "Configure user accounts": {
      'field_your_first_name': "John",
      'field_your_last_name': "Doe",
      'field_your_reference': "user",
      'field_your_password': "1234",
      'field_your_password_confirm': "1234",
      'field_your_default_email_text': "abc@nexedi.com",
      'field_your_function': "project/developer" ,
    },
    "Configure accounting": {
      'field_your_period_title': "2021",
      'subfield_field_your_period_start_date_year': "2021",
      'subfield_field_your_period_start_date_month': "01",
      'subfield_field_your_period_start_date_day': "01",
      'subfield_field_your_period_stop_date_year': "2021",
      'subfield_field_your_period_stop_date_month': "12",
      'subfield_field_your_period_stop_date_day': "31",
      'field_your_accounting_plan': "fr",
    },
    "Configure ERP5 Preferences": {
      'field_your_lang': "erp5_l10n_fr",
      'field_your_price_currency': "EUR;0.01;Euro",
      'field_your_preferred_date_order': "dmy",
      'default_field_your_lang': "1",
    }
  }

  def clearCache(self):
    self.portal.portal_caches.clearAllCache()
    self.portal.portal_workflow.refreshWorklistCache()

  def afterSetUp(self):
    url_list = []
    for x in self.portal.test_page_module.objectValues():
      if "user" in x.getId():
        url_list.append("test_page_module/"+x.getId())
    self.remote_code_url_list = url_list
    ERP5TypeFunctionalTestCase.afterSetUp(self)

   # Execute the business configuration if not installed
    business_configuration = self.getBusinessConfiguration()
    if (business_configuration.getSimulationState() != 'installed'):
      self.portal.portal_caches.erp5_site_global_id = '%s' % random.random()
      self.portal.portal_caches._p_changed = 1
      self.commit()
      self.portal.portal_caches.updateCache()

      self.bootstrapSite()
      self.commit()


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
    previous_title = None
    while response_dict.get("command", "next") != "install":
      title = response_dict.get("next", "")
      if title == previous_title:
        # transition = business_configuration.getNextTransition()
        # form = getattr(business_configuration, transition.getTransitionFormId())
        # raise NotImplementedError(form(), response_dict)
        break
      previous_title = title
      kw = self.configuration_info.get(title, {})
      response_dict = self.portal.portal_configurator._next(
                            business_configuration, kw)

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
    return ('erp5_configurator', )

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestZeleniumStandaloneUserTutorial))
  return suite