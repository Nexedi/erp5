# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2020 Nexedi SA and Contributors. All Rights Reserved.
#
##############################################################################

import random
import transaction
from Products.ERP5Type.tests.SecurityTestCase import SecurityTestCase
from Products.ERP5Type.tests.utils import DummyMailHost
from Products.ERP5Type.Utils import convertToUpperCase
from AccessControl.SecurityManagement import getSecurityManager, \
    setSecurityManager

class TestOfficeJSSDKConfigurator(SecurityTestCase):

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
    self.deSetUpPersistentDummyMailHost()
    if self.abort_transaction:
      transaction.abort()

  def getUserFolder(self):
    """
    Return the user folder
    """
    return getattr(self.getPortal(), 'acl_users', None)

  def setUpConfiguratorOnce(self):
    self.commit()
    self.portal.portal_templates.updateRepositoryBusinessTemplateList(
       repository_list=self.portal.portal_templates.getRepositoryList())
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

  def deSetUpPersistentDummyMailHost(self):
    if 'MailHost' in self.portal.objectIds():
      self.portal.manage_delObjects(['MailHost'])
    self.portal.manage_addProduct['MailHost'].manage_addMailHost('MailHost')
    self.commit()

  def setUpPersistentDummyMailHost(self):
    if 'MailHost' in self.portal.objectIds():
      self.portal.manage_delObjects(['MailHost'])
    self.portal._setObject('MailHost', DummyMailHost('MailHost'))

    self.portal.email_from_address = 'romain@nexedi.com'
    self.portal.email_to_address = 'romain@nexedi.com'

  def getBusinessConfiguration(self):
    return self.portal.business_configuration_module[\
                          "default_officejs_sdk_configuration"]

  def launchConfigurator(self):
    self.logMessage('OfficeJS Development launchConfigurator')
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

  def bootstrapSite(self):
    self.logMessage('OfficeJS Development bootstrapSite')
    self.setupPortalAlarms()

    self.clearCache()
    self.tic()
    self.setUpConfiguratorOnce()
    self.tic()

  def getBusinessTemplateList(self):
    """
    Install the business templates.
    """
    return [
      'erp5_configurator'
    ]

  def testConfiguredShacacheWebSite(self):
    """ Make sure Shacache WebSite is setuped by Alarm
        case we trust on promise outcome."""
    self.assertEqual(self.portal.web_site_module.checkConsistency(), [])

  def testConfiguredCacheViaConstraint(self):
    """ Make sure Volitile and Persistent Cache was configured well,
        invoking the consistency to check """
    self.assertEqual(self.portal.portal_memcached.checkConsistency(), [])

  def testConfiguredConversionServerViaConstraint(self):
    """ Make sure Conversion Server was configured well,
        invoking checkConsistency """
    self.assertEqual(self.portal.portal_preferences.checkConsistency(), [])

  def testConfiguredTemplateToolViaConstraint(self):
    """ Make sure Template Tool Repositories was configured well,
        invoking checkConsistency """
    self.assertEqual(
        [ i for i in self.portal.portal_templates.checkConsistency()
                     if "(reinstall)" not in i.message], [])

  def testConfiguredVolatileCache(self):
    """  Make sure Memcached is configured
    """
    from Products.ERP5Type.tests.ERP5TypeTestCase import \
                                         _getVolatileMemcachedServerDict

    memcached_tool = self.getPortal().portal_memcached
    connection_dict = _getVolatileMemcachedServerDict()
    url_string = 'erp5-memcached-volatile:%(port)s' % connection_dict
    self.assertEqual(memcached_tool.default_memcached_plugin.getUrlString(),
                      url_string)

  def testConfiguredPersistentCache(self):
    """ Make sure Kumofs is configured
    """
    from Products.ERP5Type.tests.ERP5TypeTestCase import\
            _getPersistentMemcachedServerDict
    memcached_tool = self.getPortal().portal_memcached
    connection_dict = _getPersistentMemcachedServerDict()
    url_string = 'erp5-memcached-persistent:%(port)s' % connection_dict
    self.assertEqual(memcached_tool.persistent_memcached_plugin.getUrlString(),
                      url_string)

  # XXX The configurator doesn't setup cloudooo
  # def testConfiguredConversionServer(self):
  #   """ Make sure Conversion Server (Cloudooo) is
  #       well configured """
  #   # set preference
  #   preference_tool = self.portal.portal_preferences
  #   conversion_url = "https://cloudooo.erp5.net/"
  #   self.assertEqual(preference_tool.getPreferredDocumentConversionServerUrl(), conversion_url)

  def testConfiguredBusinessTemplateList(self):
    """ Make sure Installed business Templates are
        what it is expected.  """

    expected_business_template_list = self.portal.getCoreBusinessTemplateList() + [
      'erp5_accounting',
      'erp5_administration',
      'erp5_base',
      'erp5_calendar',
      'erp5_code_mirror',
      'erp5_configurator',
      'erp5_configurator_standard',
      'erp5_core_proxy_field_legacy',
      'erp5_crm',
      'erp5_dms',
      'erp5_dms_ui_test',
      'erp5_font',
      'erp5_forge',
      'erp5_full_text_mroonga_catalog',
      'erp5_gadget_interface_validator',
      'erp5_hal_json_style',
      'erp5_hr',
      'erp5_ingestion',
      'erp5_ingestion_mysql_innodb_catalog',
      'erp5_jexcel_editor',
      'erp5_jquery',
      'erp5_jquery_plugin_colorpicker',
      'erp5_jquery_plugin_elastic',
      'erp5_jquery_plugin_jqchart',
      'erp5_jquery_plugin_mbmenu',
      'erp5_jquery_plugin_sheet',
      'erp5_jquery_sheet_editor',
      'erp5_jquery_sheet_js_editor',
      'erp5_jquery_ui',
      'erp5_knowledge_pad',
      'erp5_l10n_fa',
      'erp5_minipaint',
      'erp5_monaco_editor',
      'erp5_multimedia',
      'erp5_notebook',
      'erp5_officejs',
      'erp5_officejs_connector',
      'erp5_officejs_jquery_app',
      'erp5_officejs_ooffice',
      'erp5_officejs_ui_test',
      'erp5_only_office',
      'erp5_pdm',
      'erp5_project',
      'erp5_run_my_doc',
      'erp5_simulation',
      'erp5_slideshow_style',
      'erp5_smart_assistant',
      'erp5_svg_editor',
      'erp5_test_result',
      'erp5_trade',
      'erp5_travel_expense',
      'erp5_ui_test',
      'erp5_ui_test_core',
      'erp5_ui_test_data',
      'erp5_upgrader',
      'erp5_upgrader_officejs_sdk',
      'erp5_web',
      'erp5_web_renderjs_ui',
      'erp5_web_renderjs_ui_test',
      'erp5_web_renderjs_ui_test_core',
      'erp5_web_service',
      'officejs_todomvc'
    ]
    self.assertSameSet(expected_business_template_list,
      self.portal.portal_templates.getInstalledBusinessTemplateTitleList())
