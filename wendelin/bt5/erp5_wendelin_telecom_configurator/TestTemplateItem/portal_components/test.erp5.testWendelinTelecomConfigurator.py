##############################################################################
#
# Copyright (c) 2002-2024 Nexedi SA and Contributors. All Rights Reserved.
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
import random
import transaction

from Products.ERP5Type.tests.SecurityTestCase import SecurityTestCase
from Products.ERP5Type.tests.utils import DummyMailHost
from Products.ERP5Type.Utils import convertToUpperCase
from AccessControl.SecurityManagement import getSecurityManager, setSecurityManager

class TestWendelinTelecomConfigurator(SecurityTestCase):

  abort_transaction = 0

  def clearCache(self):
    self.portal.portal_caches.clearAllCache()
    self.portal.portal_workflow.refreshWorklistCache()

  def createAlarmStep(self):
    def makeCallAlarm(alarm):
      def callAlarm(*args, **kwargs):
        sm = getSecurityManager()
        self.login()
        try:
          alarm.activeSense(params=kwargs)
          self.commit()
        finally:
          setSecurityManager(sm)

      return callAlarm
    for alarm in self.portal.portal_alarms.contentValues():
      if alarm.isEnabled():
        setattr(self, 'stepCall' + convertToUpperCase(alarm.getId()) \
          + 'Alarm', makeCallAlarm(alarm))

  def setupPortalAlarms(self):
    if not self.portal.portal_alarms.isSubscribed():
      self.portal.portal_alarms.subscribe()
    self.assertTrue(self.portal.portal_alarms.isSubscribed())

  def beforeTearDown(self):
    self.tearDownPersistentDummyMailHost()
    if self.abort_transaction:
      transaction.abort()

  def setUpConfiguratorOnce(self):
    self.commit()
    self.portal.portal_templates.updateRepositoryBusinessTemplateList(
      repository_list=self.portal.portal_templates.getRepositoryList()
    )
    self.commit()
    self.launchConfigurator()

  def afterSetUp(self):
    self.login()
    self.createAlarmStep()

    # Execute the business configuration if not installed
    business_configuration = self.getBusinessConfiguration()
    if (business_configuration.getSimulationState() != 'installed'):
      self.portal.portal_caches.erp5_site_global_id = '%s' % random.random()
      self.portal.portal_caches._p_changed = 1
      self.commit()
      self.portal.portal_caches.updateCache()

      self.bootstrapSite()
      self.commit()

  def tearDownPersistentDummyMailHost(self):
    if 'MailHost' in self.portal.objectIds():
      self.portal.manage_delObjects(['MailHost'])
    self.portal.manage_addProduct['MailHost'].manage_addMailHost('MailHost')
    self.commit()

  def setUpPersistentDummyMailHost(self):
    if 'MailHost' in self.portal.objectIds():
      self.portal.manage_delObjects(['MailHost'])
    self.portal._setObject('MailHost', DummyMailHost('MailHost'))

    self.portal.email_from_address = 'paul.graydon@nexedi.com'
    self.portal.email_to_address = 'paul.graydon@nexedi.com'

  def getBusinessConfiguration(self):
    return self.portal.business_configuration_module["wendelin_telecom_configuration"]

  def launchConfigurator(self):
    self.logMessage('Wendelin Telecom launchConfigurator')
    self.login()
    # Create new Configuration
    business_configuration = self.getBusinessConfiguration()

    response_dict = {}
    configurator_options = {}

    while response_dict.get("command", "next") != "install":
      response_dict = self.portal.portal_configurator._next(
        business_configuration, configurator_options
    )

    self.tic()
    self.portal.portal_configurator.startInstallation(
      business_configuration,
      REQUEST=self.portal.REQUEST
    )

  def bootstrapSite(self):
    self.logMessage('Wendelin Telecom bootstrapSite')
    self.setupPortalAlarms()

    self.clearCache()
    self.tic()
    self.setUpConfiguratorOnce()
    self.tic()

  def getBusinessTemplateList(self):
    """
    Install the business templates.
    """
    return ['wendelin_telecom_configurator']

  def testConfiguredBusinessTemplateList(self):
    """
    Check that the list of installed Business Templates is correct.
    """

    expected_business_template_list = [
      'erp5_code_mirror',
      'erp5_mysql_innodb_catalog',
      'erp5_pdm',
      'erp5_svg_editor',
      'erp5_jquery_plugin_mbmenu',
      'erp5_notebook',
      'erp5_base',
      'erp5_xhtml_style',
      'erp5_knowledge_pad',
      'erp5_jquery_ui',
      'erp5_property_sheets',
      'erp5_web_renderjs_ui',
      'erp5_dms',
      'erp5_jquery',
      'erp5_ingestion_mysql_innodb_catalog',
      'erp5_ingestion',
      'erp5_forge',
      'erp5_jquery_plugin_elastic',
      'erp5_core_proxy_field_legacy',
      'erp5_jquery_sheet_editor',
      'erp5_big_file',
      'erp5_jquery_plugin_colorpicker',
      'erp5_web',
      'erp5_project',
      'erp5_administration',
      'erp5_jquery_plugin_sheet',
      'erp5_json_type',
      'erp5_core',
      'erp5_font',
      'erp5_configurator',
      'erp5_hal_json_style',
      'erp5_web_service',
      'erp5_trade',
      'erp5_wendelin_category',
      'erp5_accounting',
      'erp5_full_text_mroonga_catalog',
      'erp5_oauth2_resource',
      'erp5_wendelin',
      'erp5_jquery_plugin_jqchart',
      'erp5_simulation',
      'erp5_crm',
      'erp5_credential',
      'erp5_data_notebook',
      'erp5_wendelin_telecom_configurator',
      'erp5_wendelin_telecom_base',
      'erp5_wendelin_telecom_web',
      'erp5_wendelin_telecom_security'
    ]

    self.assertSameSet(
      expected_business_template_list,
      self.portal.portal_templates.getInstalledBusinessTemplateTitleList()
    )

  def testPreferences(self):
    default_site_preference = getattr(
      self.portal.portal_preferences,
      'default_site_preference',
      None
    )
    self.assertEqual(default_site_preference.getPreferenceState(), 'global')
    self.assertEqual(
      self.portal.portal_preferences.getPreferredDataProductIndividualVariationBaseCategoryList(),
      ['variation']
    )
    self.assertEqual(
      self.portal.portal_preferences.getPreferredEnableDataAnalysisSharing(),
      0
    )
