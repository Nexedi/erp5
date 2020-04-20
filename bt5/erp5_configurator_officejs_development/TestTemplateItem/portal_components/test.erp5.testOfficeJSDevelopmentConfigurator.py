# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2020 Nexedi SA and Contributors. All Rights Reserved.
#
##############################################################################

import random
import transaction
import unittest
from Products.ERP5Type.tests.SecurityTestCase import SecurityTestCase
from Products.ERP5Type.tests.utils import DummyMailHost
from Products.ERP5Type.Utils import convertToUpperCase
from AccessControl.SecurityManagement import getSecurityManager, \
    setSecurityManager
from App.config import getConfiguration


class TestSlapOSConfigurator(SecurityTestCase):

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
                          "officejs_development_configuration_workflow"]

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
      'erp5_configurator_officejs_development'
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

  def testConfiguredConversionServer(self):
    """ Make sure Conversion Server (Cloudooo) is
        well configured """
    # set preference
    preference_tool = self.portal.portal_preferences
    conversion_url = "https://cloudooo.erp5.net/"
    self.assertEqual(preference_tool.getPreferredDocumentConversionServerUrl(), conversion_url)

  def notestModuleHasIdGeneratorByDay(self):
    """ Ensure the Constraint sets appropriate id generator on all modules.
    """
    module_list = [module.getId() for module in self.portal.objectValues() 
                     if getattr(module, "getIdGenerator", None) is not None and \
                                        module.getIdGenerator() == "_generatePerDayId"]
    self.assertSameSet(module_list,
                [
       'access_token_module',
       'account_module',
       'accounting_module',
       'bug_module',
       'business_configuration_module',
       'business_process_module',
       'campaign_module',
       'component_module',
       'computer_model_module',
       'computer_module',
       'computer_network_module',
       'consumption_document_module',
       'credential_recovery_module',
       'credential_request_module',
       'credential_update_module',
       'currency_module',
       'cloud_contract_module',
       'data_set_module',
       'delivery_node_module',
       'document_ingestion_module',
       'document_module',
       'event_module',
       'external_source_module',
       'glossary_module',
       'hosting_subscription_module',
       'image_module',
       'implicit_item_movement_module',
       'internal_order_module',
       'internal_packing_list_module',
       'internal_supply_module',
       'internal_trade_condition_module',
       'inventory_module',
       'item_module',
       'knowledge_pad_module',
       'meeting_module',
       'notification_message_module',
       'open_internal_order_module',
       'open_purchase_order_module',
       'open_sale_order_module',
       'organisation_module',
       'person_module',
       'portal_activities',
       'portal_simulation',
       'product_module',
       'project_module',
       'purchase_order_module',
       'purchase_packing_list_module',
       'purchase_supply_module',
       'purchase_trade_condition_module',
       'quantity_unit_conversion_module',
       'query_module',
       'regularisation_request_module',
       'requirement_module',
       'returned_purchase_order_module',
       'returned_purchase_packing_list_module',
       'returned_sale_order_module',
       'returned_sale_packing_list_module',
       'sale_opportunity_module',
       'sale_order_module',
       'sale_packing_list_module',
       'sale_supply_module',
       'sale_trade_condition_module',
       'service_module',
       'service_report_module',
       'software_installation_module',
       'software_instance_module',
       'software_licence_module',
       'software_product_module',
       'software_publication_module',
       'software_release_module',
       'subscription_condition_module',
       'subscription_request_module',
       'support_request_module',
       'system_event_module',
       'task_module',
       'task_report_module',
       'transformation_module',
       'trial_condition_module',
       'trial_request_module',
       'upgrade_decision_module',
       'web_page_module',
       'web_site_module',
       'workflow_module',
     ])


  def testConfiguredBusinessTemplateList(self):
    """ Make sure Installed business Templates are
        what it is expected.  """

    expected_business_template_list = [
      'erp5_accounting',
      'erp5_base',
      'erp5_configurator',
      'erp5_content_translation',
      'erp5_core',
      'erp5_core_proxy_field_legacy',
      'erp5_credential',
      'erp5_crm',
      'erp5_dms',
      'erp5_font',
      'erp5_full_text_mroonga_catalog',
      'erp5_hal_json_style',
      'erp5_ingestion',
      'erp5_ingestion_mysql_innodb_catalog',
      'erp5_jquery',
      'erp5_jquery_plugin_colorpicker',
      'erp5_jquery_plugin_elastic',
      'erp5_jquery_plugin_jqchart',
      'erp5_jquery_plugin_mbmenu',
      'erp5_jquery_plugin_sheet',
      'erp5_jquery_sheet_editor',
      'erp5_jquery_ui',
      'erp5_knowledge_pad',
      'erp5_l10n_fa',
      'erp5_mysql_innodb_catalog',
      'erp5_officejs_appstore_base',
      'erp5_officejs_appstore_website',
      'erp5_pdm',
      'erp5_property_sheets',
      'erp5_simulation',
      'erp5_software_pdm',
      'erp5_svg_editor',
      'erp5_trade',
      'erp5_upgrader',
      'erp5_web',
      'erp5_web_renderjs_ui',
      'erp5_workflow',
      'erp5_xhtml_style',
      'officejs_appstore_configurator',
      'officejs_base',
      'officejs_credential',
      'officejs_meta',
      'officejs_security',
      'officejs_upgrader',
      # test bt5
      'erp5_forge',
      'erp5_ui_test',
      'erp5_ui_test_core',
      'officejs_test'
    ]
    self.assertSameSet(expected_business_template_list,
      self.portal.portal_templates.getInstalledBusinessTemplateTitleList())
