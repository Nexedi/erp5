##############################################################################
# Copyright (c) 2012 Nexedi SA and Contributors. All Rights Reserved.
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


from AccessControl import Unauthorized
from zLOG import LOG, INFO
import uuid
from DateTime import DateTime
from Products.ERP5Type.tests.utils import createZODBPythonScript
from Products.ERP5Configurator.tests.ConfiguratorTestMixin import \
                                             TestLiveConfiguratorWorkflowMixin

from Products.ERP5Configurator import tests as test_folder

class TestConfiguratorItem(TestLiveConfiguratorWorkflowMixin):
  """
    Test the Configurator Tool
  """

  def getBusinessTemplateList(self):
    return ('erp5_core_proxy_field_legacy',
            'erp5_full_text_myisam_catalog',
            'erp5_base',
            'erp5_workflow',
            'erp5_configurator',
            'erp5_simulation',
            'erp5_pdm',
            'erp5_trade',
            'erp5_accounting',
            'erp5_configurator_standard_trade_template')

  def createConfigurationSave(self):
    """ Create a Business Configuration and a Configuration Save 
    """
    bc = self.portal.business_configuration_module.newContent()
    return bc.newContent(portal_type="Configuration Save")
    

  def newUniqueUID(self):
    """ Return a unique number id"""
    return str(uuid.uuid1())

  def testOrganisationConfiguratorItem(self):
    """
      The Anonymous user can not have access to view the Configurator Tool.
    """
    configuration_save = self.createConfigurationSave()

    group_id = "some_group"

    title = "test_%s" % self.newUniqueUID()
    kw = { 'title': title,
           'corporate_name': "test_corporate_name",
           'default_address_city': 'test_default_address_city',
           'default_email_text': 'test_default@emailtext.com',
           'default_telephone_text': '+55(0)22-123456789',
           'default_address_zip_code': 'test_default_address_zip_code',
           'default_address_region': 'test_default_address_region',
           'default_address_street_address': 'test_default_address_street_address',
         }


    item = configuration_save.addConfigurationItem(  
      "Organisation Configurator Item",
      group=group_id, site='main', **kw)

    self.tic()
    item._build(configuration_save.getParentValue())
    self.tic()

    organisation = self.portal.portal_catalog.getResultValue(
                       portal_type="Organisation", 
                       title = title)

    self.assertNotEquals(organisation, None)
    
    self.assertEquals(group_id, organisation.getGroup())
    self.assertEquals(kw['title'], organisation.getTitle())
    self.assertEquals(kw['corporate_name'], organisation.getCorporateName())
    self.assertEquals(kw['default_address_city'],
                      organisation.getDefaultAddressCity())
    self.assertEquals(kw['default_email_text'],
                      organisation.getDefaultEmailText())
    self.assertEquals(kw['default_telephone_text'],
                      organisation.getDefaultTelephoneText())
    self.assertEquals(kw['default_address_zip_code'],
                      organisation.getDefaultAddressZipCode())
    self.assertEquals(kw['default_address_region'],
                      organisation.getDefaultAddressRegion())

    self.assertEquals(kw['default_address_street_address'],
                      organisation.getDefaultAddressStreetAddress())

    self.assertEquals('main', organisation.getSite())
    self.assertEquals('validated', organisation.getValidationState())


  def testCategoryConfiguratorItem(self):
    """ Test Category Configurator Item """
    configuration_save = self.createConfigurationSave()
    bc = configuration_save.getParentValue()
    
    category_id_0 = "test_category_%s" % self.newUniqueUID()
    item0 = configuration_save.addConfigurationItem(
                                        "Category Configurator Item",
                                        category_root='group',
                                        object_id=category_id_0,
                                        title="title_%s" % category_id_0)

    category_id_1 = "test_category_%s" % self.newUniqueUID()
    item1 = configuration_save.addConfigurationItem(
                                        "Category Configurator Item",
                                        category_root='group',
                                        object_id=category_id_1,
                                        title="title_%s" % category_id_1)

    self.tic()
    item0._build(bc)
    self.tic()

    category_0 = getattr(self.portal.portal_categories.group, category_id_0, None)
    self.assertNotEquals(category_0, None)
    self.assertEquals(category_0.getTitle(), "title_%s" % category_id_0)

    category_1 = getattr(self.portal.portal_categories.group, category_id_1, None)
    self.assertEquals(category_1, None)

    item1._build(bc)
    self.tic()

    category_1 = getattr(self.portal.portal_categories.group, category_id_1, None)
    self.assertNotEquals(category_1, None)
    self.assertEquals(category_1.getTitle(), "title_%s" % category_id_1)

    # recreate category_1 with new title

    item2 = configuration_save.addConfigurationItem(
                                        "Category Configurator Item",
                                        category_root='group',
                                        object_id=category_id_1,
                                        title="new_title_%s" % category_id_1)

    item2._build(bc)
    self.tic()

    category_1 = getattr(self.portal.portal_categories.group, 
                         category_id_1, None)
    self.assertNotEquals(category_1, None)
    self.assertEquals(category_1.getTitle(), "new_title_%s" % category_id_1)

  def testCurrencyConfiguratorItem(self):
    """ Test Category Configurator Item """
    configuration_save = self.createConfigurationSave()
    bc = configuration_save.getParentValue()

    eur_currency_id = "EUR"
    eur_currency_title = "Euro"
    item_eur = configuration_save.addConfigurationItem(
                             "Currency Configurator Item",
                             reference = eur_currency_id,
                             base_unit_quantity = 0.01,
                             title = eur_currency_title,)

    brl_currency_id = "BRL"
    brl_currency_title = "Brazillian Real"
    item_brl = configuration_save.addConfigurationItem(
                             "Currency Configurator Item",
                             reference = brl_currency_id,
                             base_unit_quantity = 0.01,
                             title = brl_currency_title,)

    self.tic()

    item_eur._build(bc)
    self.tic()

    eur = getattr(self.portal.currency_module, eur_currency_id , None)
    self.assertNotEquals(eur, None)
    self.assertEquals(eur.getTitle(), eur_currency_title)

    brl = getattr(self.portal.currency_module, brl_currency_id , None)
    self.assertEquals(brl, None)

    item_brl._build(bc)
    self.tic()

    brl = getattr(self.portal.currency_module, brl_currency_id , None)
    self.assertNotEquals(brl, None)
    self.assertEquals(brl.getTitle(), brl_currency_title)

    # Build several times to not break portal.

    item_brl._build(bc)
    self.tic()
    item_brl._build(bc)
    self.tic()

  def testSecurityCategoryMappingConfiguratorItem(self):
    """ Test Security Category Mapping Configurator Item
        XXX This test and the Security Category Mapping should be improved to
            allow provide the name of skin folder and the script/categories to
            be used for the script oucome. For now it does the minimum.
    """
    configuration_save = self.createConfigurationSave()
    bc = configuration_save.getParentValue()

    expect_script_outcome = (
           ('ERP5Type_getSecurityCategoryFromAssignmentStrict', ['function']),
           ('ERP5Type_getSecurityCategoryFromAssignmentStrict', ['follow_up']),
           ('ERP5Type_getSecurityCategoryFromAssignmentStrict', ['function', 'follow_up']),
           ('ERP5Type_getSecurityCategoryFromAssignmentStrict', ['group']),
           ('ERP5Type_getSecurityCategoryRoot', ['group']),)


    item = configuration_save.addConfigurationItem(
                  "Security Category Mapping Configurator Item")

    self.tic()
    item._build(bc)
    self.tic()

    # XXX Skin folder should be part of configuration and not always custom
    security_script = getattr(self.portal.portal_skins.custom,
                              "ERP5Type_getSecurityCategoryMapping", None)

    self.assertNotEquals(None, security_script)
    self.assertEquals(security_script(), expect_script_outcome)

  def testAccountConfiguratorItem(self):
    """ Test Account Configurator Item """
    configuration_save = self.createConfigurationSave()
    bc = configuration_save.getParentValue()
    account_module = self.portal.account_module

    account_dict = {
             'account_type': 'asset/receivable',
             'account_id': 'receivable',
             'title': 'Customers',
             'gap': 'ias/ifrs/4/41',
             'financial_section': 'asset/current_assets/trade_receivables'}

    item = configuration_save.addConfigurationItem(
                  "Account Configurator Item", **account_dict)

    self.tic()
    item._build(bc)
    self.tic()

    account = getattr(account_module, account_dict['account_id'], None)
    self.assertNotEquals(account, None)
    self.assertEquals(account.getTitle(), account_dict['title'])
    self.assertEquals(account.getGap(), account_dict['gap'])
    self.assertEquals(account.getFinancialSection(),
                      account_dict['financial_section'])
    self.assertEquals(account.getAccountType(),
                      account_dict['account_type'])

    # Update Account dict and try to create again the same account,
    # the account should be only updated instead a new account be created.
    account_dict['title'] = 'Clientes'
    previous_gap = account_dict['gap']
    account_dict['gap'] = 'br/pcg/1/1.1/1.1.2'

    item = configuration_save.addConfigurationItem(
                  "Account Configurator Item", **account_dict)

    self.tic()
    item._build(bc)
    self.tic()

    same_account = getattr(account_module, account_dict['account_id'], None)
    self.assertEquals(account, same_account)
    self.assertEquals(account.getTitle(), account_dict['title'])
    self.assertSameSet(account.getGapList(), [previous_gap,
                                              account_dict['gap']])
    self.assertEquals(account.getFinancialSection(),
                      account_dict['financial_section'])
    self.assertEquals(account.getAccountType(),
                      account_dict['account_type'])

  def testAlarmConfiguratorItem(self):
    """ Test Alarm Configurator Item """
    configuration_save = self.createConfigurationSave()
    bc = configuration_save.getParentValue()

    property_map = {
      "active_sense_method_id" : "Base_setDummy",
      "periodicity_hour_list" : [5, 6],
      "periodicity_minute_list": [30, 31],
      "periodicity_minute_frequency": 5,
      "periodicity_month_list": [1, 2],
      "periodicity_month_day_list": [3, 4],
      "periodicity_week_list": [6, 7],
                        }

    item = configuration_save.addConfigurationItem(
                  "Alarm Configurator Item",
                  id="my_test_alarm",
                  title="My Test Alarm",
                  **property_map)

    createZODBPythonScript(self.getPortal().portal_skins.custom,
                                    property_map["active_sense_method_id"],
                                    "", "context.setEnabled(0)")
    self.tic()
    item._build(bc)
    self.tic()

    alarm = getattr(self.portal.portal_alarms, "my_test_alarm", None)
    self.assertNotEquals(None, alarm)

    self.assertEquals(alarm.getEnabled(), True)
    self.assertEquals(alarm.getTitle(), "My Test Alarm")
    self.assertEquals(alarm.getPeriodicityMinuteFrequency(),
                      property_map["periodicity_minute_frequency"])
    self.assertEquals(alarm.getPeriodicityMonthList(),
                      property_map["periodicity_month_list"])
    self.assertEquals(alarm.getPeriodicityMonthDayList(),
                      property_map["periodicity_month_day_list"])
    self.assertEquals(alarm.getPeriodicityHourList(),
                      property_map["periodicity_hour_list"])
    self.assertEquals(alarm.getPeriodicityHourList(),
                      property_map["periodicity_hour_list"])
    self.assertEquals(alarm.getActiveSenseMethodId(),
                      property_map["active_sense_method_id"])
    self.assertNotEquals(alarm.getPeriodicityStartDate(), None)
    self.failUnless(alarm.getPeriodicityStartDate() < DateTime())
    alarm.activeSense()
    self.tic()
    self.assertEquals(alarm.getEnabled(), 0)

  def testPortalTypeRolesSpreadsheetConfiguratorItem(self):
    """ Test Portal Type Roles Configurator Item """
    configuration_save = self.createConfigurationSave()
    bc = configuration_save.getParentValue()
    category_tool = self.portal.portal_categories

    test_folder_path = '/'.join(test_folder.__file__.split('/')[:-1])

    f = open("%s/test_data/test_standard_portal_type_roles.ods" \
               % test_folder_path, "r")
    try:
      data = f.read()
    finally:
      f.close()

    if getattr(category_tool.group, "my_group", None) is None:
      category_tool.group.newContent(id="my_group")

    item = configuration_save.addConfigurationItem(
      "Portal Type Roles Spreadsheet Configurator Item",
      configuration_spreadsheet_data = data)


    person_type = self.portal.portal_types["Person"]
    person_module_type = self.portal.portal_types["Person Module"]

    role_list = [i for i in person_type.objectValues(
                 portal_type="Role Information")
                 if i.getTitle() == "TestRole_Person"]

    if len(role_list) > 0:
      person_type.manage_delObjects([i.id for i in role_list])

    role_list = [i for i in person_module_type.objectValues(
                 portal_type="Role Information")
                if i.getTitle() == "TestRole_PersonModule"]

    if len(role_list) > 0:
      person_module_type.manage_delObjects([i.id for i in role_list])

    self.tic()
    item._build(bc)
    self.tic()

    role_list = [i for i in person_type.objectValues(
                 portal_type="Role Information") 
                if i.getTitle() == "TestRole_Person"]

    self.assertEquals(len(role_list), 1)

    self.assertEquals(role_list[0].getDescription(), 
                      "Configured by ERP5 Configurator")

    self.assertEquals(role_list[0].getRoleNameList(), 
                      ['Auditor', 'Author', 'Assignee'])

    self.assertEquals(role_list[0].getRoleCategoryList(),
                      ['group/my_group',])


    role_list = [i for i in person_module_type.objectValues(
                 portal_type="Role Information")
                if i.getTitle() == "TestRole_PersonModule"]

    self.assertEquals(len(role_list), 1)

    self.assertEquals(role_list[0].getDescription(),
                      "Configured by ERP5 Configurator")

    self.assertEquals(role_list[0].getRoleNameList(),
                      ['Auditor', 'Author'])

    self.assertEquals(role_list[0].getRoleCategoryList(),
                      ['group/my_group',])


  def testCategoriesSpreadsheetConfiguratorItem(self):
    """ Test Portal Type Roles Configurator Item """
    configuration_save = self.createConfigurationSave()
    bc = configuration_save.getParentValue()
    category_tool = self.portal.portal_categories

    test_folder_path = '/'.join(test_folder.__file__.split('/')[:-1])

    f = open("%s/test_data/test_standard_categories.ods" \
               % test_folder_path, "r")
    try:
      data = f.read()
    finally:
      f.close()

    item = configuration_save.addConfigurationItem(
      "Categories Spreadsheet Configurator Item",
      configuration_spreadsheet_data = data)

    self.tic()
    item._build(bc)
    self.tic()

    base_category_list = ["group", "site", "business_application", 
                          "function", "region"]

    for base_category_id in base_category_list:
      # Check first Level
      base_category = getattr(category_tool, base_category_id)    
      my_test = getattr(base_category, "my_test", None)
      self.assertNotEquals(my_test, None)
      self.assertEquals(my_test.getTitle(), "TEST")
      self.assertEquals(my_test.getDescription(), "TEST")
      self.assertEquals(my_test.getCodification(), "TEST")
      self.assertEquals(my_test.getIntIndex(), 1)
      # Check Second level
      my_test = getattr(my_test, "my_test", None)
      self.assertNotEquals(my_test, None)
      self.assertEquals(my_test.getTitle(), "TEST")
      self.assertEquals(my_test.getDescription(), "TEST")
      self.assertEquals(my_test.getCodification(), "TEST")
      self.assertEquals(my_test.getIntIndex(), 2)

      # Check Thrid level
      my_test = getattr(my_test, "my_test", None)
      self.assertNotEquals(my_test, None)
      self.assertEquals(my_test.getTitle(), "TEST")
      self.assertEquals(my_test.getDescription(), "TEST")
      self.assertEquals(my_test.getCodification(), "TEST")
      self.assertEquals(my_test.getIntIndex(), 3)

  def testRuleConfiguratorItem(self):
    """ Test Rules Configurator Item """
    configuration_save = self.createConfigurationSave()
    bc = configuration_save.getParentValue()
    category_tool = self.portal.portal_categories
    rule_tool = self.portal.portal_rules

    if getattr(category_tool.trade_phase, "testing", None) is None:
      category_tool.trade_phase.newContent(id="testing")

    if getattr(category_tool.trade_phase.testing, "order", None) is None:
      category_tool.trade_phase.testing.newContent(id="order")

    item = configuration_save.addConfigurationItem(
      "Rule Configurator Item",
      reference = "testing_configurator_rule",
      id = "rule_do_not_exist")

    self.tic()
    self.assertRaises(ValueError, item._build, bc)

    rule_reference = "testing_configurator_rule_%s" % self.newUniqueUID()
    item = configuration_save.addConfigurationItem(
      "Rule Configurator Item",
      reference = rule_reference,
      id = "new_delivery_simulation_rule",
      trade_phase_list = ['testing/order'])

    self.tic()
    item._build(bc)
    self.tic()

    template_id = item.getId()
    rule_list = rule_tool.searchFolder(
          portal_type=self.portal.getPortalRuleTypeList(),
          validation_state="validated", reference=rule_reference)

    self.assertEquals(len(rule_list), 1)
    self.assertEquals(['testing/order'], rule_list[0].getTradePhaseList())

  def testBusinessProcessConfiguratorItem(self):
    configuration_save = self.createConfigurationSave()
    bc = configuration_save.getParentValue()
    category_tool = self.portal.portal_categories

    test_folder_path = '/'.join(test_folder.__file__.split('/')[:-1])

    f = open("%s/test_data/test_standard_business_process.ods" \
               % test_folder_path, "r")
    try:
      data = f.read()
    finally:
      f.close()

    reference = "testing_business_process_%s" % self.newUniqueUID()
    item = configuration_save.addConfigurationItem(
      "Business Process Configurator Item",
      configuration_spreadsheet_data = data,
      reference = reference)

    self.tic()
    item._build(bc)
    self.tic()

    business_process = self.portal.portal_catalog.getResultValue(
          portal_type="Business Process",
          reference=reference)

    self.assertNotEquals(business_process, None)

    order_path = getattr(business_process, "order_path", None)
    self.assertNotEquals(order_path, None)
    self.assertEquals(order_path.getEfficiency(), 1.0)
    self.assertEquals(order_path.getTradePhase(), 'trade/order')
    self.assertEquals(order_path.getTradeDate(), 'trade_phase/trade/order')
    self.assertEquals(order_path.getTestMethodId(), None)

    delivery_path = getattr(business_process, "delivery_path", None)
    self.assertNotEquals(delivery_path, None)
    self.assertEquals(delivery_path.getEfficiency(), 1.0)
    self.assertEquals(delivery_path.getTradePhase(), 'trade/delivery')
    self.assertEquals(delivery_path.getTradeDate(), 'trade_phase/trade/order')
    self.assertEquals(delivery_path.getTestMethodId(), None)

    invoicing_path = getattr(business_process, "invoicing_path", None)
    self.assertNotEquals(invoicing_path, None)
    self.assertEquals(invoicing_path.getEfficiency(), 1.0)
    self.assertEquals(invoicing_path.getTradePhase(), 'trade/invoicing')
    self.assertEquals(invoicing_path.getTradeDate(), 'trade_phase/trade/delivery')
    self.assertEquals(invoicing_path.getTestMethodId(), None)

    accounting_credit_path = getattr(business_process, "accounting_credit_path", None)
    self.assertNotEquals(accounting_credit_path, None)
    self.assertEquals(accounting_credit_path.getEfficiency(), -1.0)
    self.assertEquals(accounting_credit_path.getTradePhase(), 'trade/accounting')
    self.assertEquals(accounting_credit_path.getTradeDate(), 'trade_phase/trade/invoicing')
    self.assertEquals(accounting_credit_path.getTestMethodId(), "isAccountingMovementType")

    accounting_debit_path = getattr(business_process, "accounting_debit_path", None)
    self.assertNotEquals(accounting_debit_path, None)
    self.assertEquals(accounting_debit_path.getEfficiency(), 1.0)
    self.assertEquals(accounting_debit_path.getTradePhase(), 'trade/accounting')
    self.assertEquals(accounting_debit_path.getTradeDate(), 'trade_phase/trade/invoicing')
    self.assertEquals(accounting_debit_path.getTestMethodId(), "isAccountingMovementType")

    order_link = getattr(business_process, "order_link", None)
    self.assertNotEquals(order_link, None)
    #self.assertTrue(order_link.getDeliverable())
    self.assertEquals(order_link.getSuccessor(), "trade_state/trade/ordered")
    self.assertEquals(order_link.getPredecessor(),None)
    self.assertEquals(order_link.getCompletedStateList(),["confirmed"])
    self.assertEquals(order_link.getFrozenState(), None)
    self.assertEquals(order_link.getDeliveryBuilder(), None)
    self.assertEquals(order_link.getTradePhase(),'trade/order')

    deliver_link = getattr(business_process, "deliver_link", None)
    self.assertNotEquals(deliver_link, None)
    #self.assertTrue(deliver_link.getDeliverable())
    self.assertEquals(deliver_link.getSuccessor(),"trade_state/trade/delivered")
    self.assertEquals(deliver_link.getPredecessor(),"trade_state/trade/ordered")
    self.assertEquals(deliver_link.getCompletedStateList(),['delivered','started','stopped'])
    self.assertEquals(deliver_link.getFrozenStateList(),['delivered','stopped'])
    self.assertEquals(deliver_link.getTradePhase(),'trade/delivery')

    self.assertEquals(deliver_link.getDeliveryBuilderList(),
           ["portal_deliveries/sale_packing_list_builder",
            "portal_deliveries/internal_packing_list_builder",
            "portal_deliveries/purchase_packing_list_builder"])

    invoice_link = getattr(business_process, "invoice_link", None)
    self.assertNotEquals(invoice_link, None)
    #self.assertFalse(invoice_link.getDeliverable())
    self.assertEquals(invoice_link.getSuccessor(),"trade_state/trade/invoiced")
    self.assertEquals(invoice_link.getPredecessor(),"trade_state/trade/delivered")
    self.assertEquals(invoice_link.getCompletedStateList(),
                        ['confirmed','delivered','started','stopped'])
    self.assertEquals(invoice_link.getFrozenStateList(),['delivered','stopped'])
    self.assertEquals(invoice_link.getTradePhase(),'trade/invoicing')

    self.assertEquals(invoice_link.getDeliveryBuilderList(),
           ["portal_deliveries/purchase_invoice_builder",
            "portal_deliveries/purchase_invoice_transaction_trade_model_builder",
            "portal_deliveries/sale_invoice_builder",
            "portal_deliveries/sale_invoice_transaction_trade_model_builder"])

    account_link = getattr(business_process, "account_link", None)
    self.assertNotEquals(account_link, None)
    #self.assertFalse(account_link.getDeliverable())
    self.assertEquals(account_link.getSuccessor(),"trade_state/trade/accounted")
    self.assertEquals(account_link.getPredecessor(),"trade_state/trade/invoiced")
    self.assertEquals(account_link.getCompletedStateList(),['delivered','started','stopped'])
    self.assertEquals(account_link.getFrozenStateList(),['delivered','stopped'])
    self.assertEquals(account_link.getTradePhase(), 'trade/accounting')

    self.assertSameSet(account_link.getDeliveryBuilderList(),
           ["portal_deliveries/purchase_invoice_transaction_builder",
            "portal_deliveries/sale_invoice_transaction_builder"])

    pay_link = getattr(business_process, "pay_link", None)
    self.assertNotEquals(pay_link, None)
    #self.assertFalse(pay_link.getDeliverable())
    self.assertEquals(pay_link.getTradePhase(), 'trade/payment')
    self.assertEquals(pay_link.getSuccessor(), None)
    self.assertEquals(pay_link.getPredecessor(),"trade_state/trade/accounted")
    self.assertEquals(pay_link.getCompletedState(), None)
    self.assertEquals(pay_link.getFrozenState(), None)

    self.assertEquals(pay_link.getDeliveryBuilderList(),
           ["portal_deliveries/payment_transaction_builder"])

