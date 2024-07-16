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


import uuid
from DateTime import DateTime
from Products.ERP5Type.tests.utils import createZODBPythonScript
from erp5.component.module.ConfiguratorTestMixin import \
                                             TestLiveConfiguratorWorkflowMixin

from Products.ERP5 import tests as test_folder

class TestConfiguratorItem(TestLiveConfiguratorWorkflowMixin):
  """
    Test the Configurator Tool
  """

  def getBusinessTemplateList(self):
    return ('erp5_core_proxy_field_legacy',
            'erp5_full_text_mroonga_catalog',
            'erp5_base',
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
    item.fixConsistency()
    self.tic()

    organisation = self.portal.portal_catalog.getResultValue(
                       portal_type="Organisation",
                       title = title)

    self.assertNotEqual(organisation, None)

    self.assertEqual(group_id, organisation.getGroup())
    self.assertEqual(kw['title'], organisation.getTitle())
    self.assertEqual(kw['corporate_name'], organisation.getCorporateName())
    self.assertEqual(kw['default_address_city'],
                      organisation.getDefaultAddressCity())
    self.assertEqual(kw['default_email_text'],
                      organisation.getDefaultEmailText())
    self.assertEqual(kw['default_telephone_text'],
                      organisation.getDefaultTelephoneText())
    self.assertEqual(kw['default_address_zip_code'],
                      organisation.getDefaultAddressZipCode())
    self.assertEqual(kw['default_address_region'],
                      organisation.getDefaultAddressRegion())

    self.assertEqual(kw['default_address_street_address'],
                      organisation.getDefaultAddressStreetAddress())

    self.assertEqual('main', organisation.getSite())
    self.assertEqual('validated', organisation.getValidationState())


  def testCategoryConfiguratorItem(self):
    """ Test Category Configurator Item """
    configuration_save = self.createConfigurationSave()

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
    item0.fixConsistency()
    self.tic()

    category_0 = getattr(self.portal.portal_categories.group, category_id_0, None)
    self.assertNotEqual(category_0, None)
    self.assertEqual(category_0.getTitle(), "title_%s" % category_id_0)

    category_1 = getattr(self.portal.portal_categories.group, category_id_1, None)
    self.assertEqual(category_1, None)

    item1.fixConsistency()
    self.tic()

    category_1 = getattr(self.portal.portal_categories.group, category_id_1, None)
    self.assertNotEqual(category_1, None)
    self.assertEqual(category_1.getTitle(), "title_%s" % category_id_1)

    # recreate category_1 with new title

    item2 = configuration_save.addConfigurationItem(
                                        "Category Configurator Item",
                                        category_root='group',
                                        object_id=category_id_1,
                                        title="new_title_%s" % category_id_1)

    item2.fixConsistency()
    self.tic()

    category_1 = getattr(self.portal.portal_categories.group,
                         category_id_1, None)
    self.assertNotEqual(category_1, None)
    self.assertEqual(category_1.getTitle(), "new_title_%s" % category_id_1)

  def testCurrencyConfiguratorItem(self):
    """ Test Category Configurator Item """
    configuration_save = self.createConfigurationSave()

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

    item_eur.fixConsistency()
    self.tic()

    eur = getattr(self.portal.currency_module, eur_currency_id , None)
    self.assertNotEqual(eur, None)
    self.assertEqual(eur.getTitle(), eur_currency_title)

    brl = getattr(self.portal.currency_module, brl_currency_id , None)
    self.assertEqual(brl, None)

    item_brl.fixConsistency()
    self.tic()

    brl = getattr(self.portal.currency_module, brl_currency_id , None)
    self.assertNotEqual(brl, None)
    self.assertEqual(brl.getTitle(), brl_currency_title)

    # Build several times to not break portal.

    item_brl.fixConsistency()
    self.tic()
    item_brl.fixConsistency()
    self.tic()

  def testSecurityCategoryMappingConfiguratorItem(self):
    """ Test Security Category Mapping Configurator Item
        XXX This test and the Security Category Mapping should be improved to
            allow provide the name of skin folder and the script/categories to
            be used for the script oucome. For now it does the minimum.
    """
    configuration_save = self.createConfigurationSave()

    expect_script_outcome = (
           ('ERP5Type_getSecurityCategoryFromAssignmentStrict', ['function']),
           ('ERP5Type_getSecurityCategoryFromAssignmentStrict', ['follow_up']),
           ('ERP5Type_getSecurityCategoryFromAssignmentStrict', ['function', 'follow_up']),
           ('ERP5Type_getSecurityCategoryFromAssignmentStrict', ['group']),
           ('ERP5Type_getSecurityCategoryRoot', ['group']),)


    item = configuration_save.addConfigurationItem(
                  "Security Category Mapping Configurator Item")

    self.tic()
    item.fixConsistency()
    self.tic()

    # XXX Skin folder should be part of configuration and not always custom
    security_script = getattr(self.portal.portal_skins.custom,
                              "ERP5Type_getSecurityCategoryMapping", None)

    self.assertNotEqual(None, security_script)
    self.assertEqual(security_script(), expect_script_outcome)

  def testAccountConfiguratorItem(self):
    """ Test Account Configurator Item """
    configuration_save = self.createConfigurationSave()
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
    item.fixConsistency()
    self.tic()

    account = getattr(account_module, account_dict['account_id'], None)
    self.assertNotEqual(account, None)
    self.assertEqual(account.getTitle(), account_dict['title'])
    self.assertEqual(account.getGap(), account_dict['gap'])
    self.assertEqual(account.getFinancialSection(),
                      account_dict['financial_section'])
    self.assertEqual(account.getAccountType(),
                      account_dict['account_type'])

    # Update Account dict and try to create again the same account,
    # the account should be only updated instead a new account be created.
    account_dict['title'] = 'Clientes'
    previous_gap = account_dict['gap']
    account_dict['gap'] = 'br/pcg/1/1.1/1.1.2'

    item = configuration_save.addConfigurationItem(
                  "Account Configurator Item", **account_dict)

    self.tic()
    item.fixConsistency()
    self.tic()

    same_account = getattr(account_module, account_dict['account_id'], None)
    self.assertEqual(account, same_account)
    self.assertEqual(account.getTitle(), account_dict['title'])
    self.assertSameSet(account.getGapList(), [previous_gap,
                                              account_dict['gap']])
    self.assertEqual(account.getFinancialSection(),
                      account_dict['financial_section'])
    self.assertEqual(account.getAccountType(),
                      account_dict['account_type'])

  def testAlarmConfiguratorItem(self):
    """ Test Alarm Configurator Item """
    configuration_save = self.createConfigurationSave()

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
    item.fixConsistency()
    self.tic()

    alarm = getattr(self.portal.portal_alarms, "my_test_alarm", None)
    self.assertNotEqual(None, alarm)

    self.assertEqual(alarm.getEnabled(), True)
    self.assertEqual(alarm.getTitle(), "My Test Alarm")
    self.assertEqual(alarm.getPeriodicityMinuteFrequency(),
                      property_map["periodicity_minute_frequency"])
    self.assertEqual(alarm.getPeriodicityMonthList(),
                      property_map["periodicity_month_list"])
    self.assertEqual(alarm.getPeriodicityMonthDayList(),
                      property_map["periodicity_month_day_list"])
    self.assertEqual(alarm.getPeriodicityHourList(),
                      property_map["periodicity_hour_list"])
    self.assertEqual(alarm.getPeriodicityHourList(),
                      property_map["periodicity_hour_list"])
    self.assertEqual(alarm.getActiveSenseMethodId(),
                      property_map["active_sense_method_id"])
    self.assertNotEqual(alarm.getPeriodicityStartDate(), None)
    self.assertTrue(alarm.getPeriodicityStartDate() < DateTime())
    alarm.activeSense()
    self.tic()
    self.assertEqual(alarm.getEnabled(), 0)

  def testPortalTypeRolesSpreadsheetConfiguratorItem(self):
    """ Test Portal Type Roles Configurator Item """
    configuration_save = self.createConfigurationSave()
    category_tool = self.portal.portal_categories

    test_folder_path = '/'.join(test_folder.__file__.split('/')[:-1])

    with open(
      "%s/test_data/test_standard_portal_type_roles.ods" % test_folder_path, "rb") as f:
      data = f.read()

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
    item.fixConsistency()
    self.tic()

    role_list = [i for i in person_type.objectValues(
                 portal_type="Role Information")
                if i.getTitle() == "TestRole_Person"]

    self.assertEqual(len(role_list), 1)

    self.assertEqual(role_list[0].getDescription(),
                      "Configured by ERP5 Configurator")

    self.assertEqual(role_list[0].getRoleNameList(),
                      ['Auditor', 'Author', 'Assignee'])

    self.assertEqual(role_list[0].getRoleCategoryList(),
                      ['group/my_group',])


    role_list = [i for i in person_module_type.objectValues(
                 portal_type="Role Information")
                if i.getTitle() == "TestRole_PersonModule"]

    self.assertEqual(len(role_list), 1)

    self.assertEqual(role_list[0].getDescription(),
                      "Configured by ERP5 Configurator")

    self.assertEqual(role_list[0].getRoleNameList(),
                      ['Auditor', 'Author'])

    self.assertEqual(role_list[0].getRoleCategoryList(),
                      ['group/my_group',])


  def testCategoriesSpreadsheetConfiguratorItem(self):
    """ Test Portal Type Roles Configurator Item """
    configuration_save = self.createConfigurationSave()
    category_tool = self.portal.portal_categories

    test_folder_path = '/'.join(test_folder.__file__.split('/')[:-1])

    with open("%s/test_data/test_standard_categories.ods" \
               % test_folder_path, "rb") as f:
      data = f.read()

    item = configuration_save.addConfigurationItem(
      "Categories Spreadsheet Configurator Item",
      configuration_spreadsheet_data = data)

    self.tic()
    item.fixConsistency()
    self.tic()

    base_category_list = ["group", "site", "business_application",
                          "function", "region"]

    for base_category_id in base_category_list:
      # Check first Level
      base_category = getattr(category_tool, base_category_id)
      my_test = getattr(base_category, "my_test", None)
      self.assertNotEqual(my_test, None)
      self.assertEqual(my_test.getTitle(), "TEST")
      self.assertEqual(my_test.getDescription(), "TEST")
      self.assertEqual(my_test.getCodification(), "TEST")
      self.assertEqual(my_test.getIntIndex(), 1)
      # Check Second level
      my_test = getattr(my_test, "my_test", None)
      self.assertNotEqual(my_test, None)
      self.assertEqual(my_test.getTitle(), "TEST")
      self.assertEqual(my_test.getDescription(), "TEST")
      self.assertEqual(my_test.getCodification(), "TEST")
      self.assertEqual(my_test.getIntIndex(), 2)

      # Check Thrid level
      my_test = getattr(my_test, "my_test", None)
      self.assertNotEqual(my_test, None)
      self.assertEqual(my_test.getTitle(), "TEST")
      self.assertEqual(my_test.getDescription(), "TEST")
      self.assertEqual(my_test.getCodification(), "TEST")
      self.assertEqual(my_test.getIntIndex(), 3)

  def testRuleConfiguratorItem(self):
    """ Test Rules Configurator Item """
    configuration_save = self.createConfigurationSave()
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
    self.assertRaises(ValueError, item.fixConsistency)

    rule_reference = "testing_configurator_rule_%s" % self.newUniqueUID()
    item = configuration_save.addConfigurationItem(
      "Rule Configurator Item",
      reference = rule_reference,
      id = "new_delivery_simulation_rule",
      trade_phase_list = ['testing/order'])

    self.tic()
    item.fixConsistency()
    self.tic()

    rule_list = rule_tool.searchFolder(
          portal_type=self.portal.getPortalRuleTypeList(),
          validation_state="validated", reference=rule_reference)

    self.assertEqual(len(rule_list), 1)
    self.assertEqual(['testing/order'], rule_list[0].getTradePhaseList())

  def testBusinessProcessConfiguratorItem(self):
    configuration_save = self.createConfigurationSave()

    test_folder_path = '/'.join(test_folder.__file__.split('/')[:-1])

    with open("%s/test_data/test_standard_business_process.ods" \
               % test_folder_path, "rb") as f:
      data = f.read()

    reference = "testing_business_process_%s" % self.newUniqueUID()
    item = configuration_save.addConfigurationItem(
      "Business Process Configurator Item",
      configuration_spreadsheet_data = data,
      reference = reference)

    self.tic()
    item.fixConsistency()
    self.tic()

    business_process = self.portal.portal_catalog.getResultValue(
          portal_type="Business Process",
          reference=reference)

    self.assertNotEqual(business_process, None)

    order_path = getattr(business_process, "order_path", None)
    self.assertNotEqual(order_path, None)
    self.assertEqual(order_path.getEfficiency(), 1.0)
    self.assertEqual(order_path.getTradePhase(), 'trade/order')
    self.assertEqual(order_path.getTradeDate(), 'trade_phase/trade/order')
    self.assertEqual(order_path.getTestMethodId(), None)

    delivery_path = getattr(business_process, "delivery_path", None)
    self.assertNotEqual(delivery_path, None)
    self.assertEqual(delivery_path.getEfficiency(), 1.0)
    self.assertEqual(delivery_path.getTradePhase(), 'trade/delivery')
    self.assertEqual(delivery_path.getTradeDate(), 'trade_phase/trade/order')
    self.assertEqual(delivery_path.getTestMethodId(), None)

    invoicing_path = getattr(business_process, "invoicing_path", None)
    self.assertNotEqual(invoicing_path, None)
    self.assertEqual(invoicing_path.getEfficiency(), 1.0)
    self.assertEqual(invoicing_path.getTradePhase(), 'trade/invoicing')
    self.assertEqual(invoicing_path.getTradeDate(), 'trade_phase/trade/delivery')
    self.assertEqual(invoicing_path.getTestMethodId(), None)
    self.assertEqual(invoicing_path.getMembershipCriterionBaseCategoryList(), [])
    self.assertEqual(invoicing_path.getMembershipCriterionCategoryList(), [])

    accounting_debit_path = getattr(business_process, "accounting_debit_path", None)
    self.assertNotEqual(accounting_debit_path, None)
    self.assertEqual(accounting_debit_path.getEfficiency(), 1.0)
    self.assertEqual(accounting_debit_path.getTradePhase(), 'trade/accounting')
    self.assertEqual(accounting_debit_path.getTradeDate(), 'trade_phase/trade/invoicing')
    self.assertEqual(accounting_debit_path.getTestMethodId(), "isAccountingMovementType")
    self.assertEqual(
        accounting_debit_path.getMembershipCriterionBaseCategoryList(),
        ['trade_phase'])
    self.assertEqual(
        accounting_debit_path.getMembershipCriterionCategoryList(),
        ['trade_phase/trade/invoicing', 'trade_phase/trade/delivery',])

    accounting_credit_path = getattr(business_process, "accounting_credit_path", None)
    self.assertNotEqual(accounting_credit_path, None)
    self.assertEqual(accounting_credit_path.getEfficiency(), -1.0)
    self.assertEqual(accounting_credit_path.getTradePhase(), 'trade/accounting')
    self.assertEqual(accounting_credit_path.getTradeDate(), 'trade_phase/trade/invoicing')
    self.assertEqual(accounting_credit_path.getTestMethodId(), "isAccountingMovementType")
    self.assertEqual(
        accounting_credit_path.getMembershipCriterionBaseCategoryList(),
        ['trade_phase'])
    self.assertEqual(
        accounting_credit_path.getMembershipCriterionCategoryList(),
        ['trade_phase/trade/delivery',])

    order_link = getattr(business_process, "order_link", None)
    self.assertNotEqual(order_link, None)
    #self.assertTrue(order_link.getDeliverable())
    self.assertEqual(order_link.getSuccessor(), "trade_state/trade/ordered")
    self.assertEqual(order_link.getPredecessor(),None)
    self.assertEqual(order_link.getCompletedStateList(),["confirmed"])
    self.assertEqual(order_link.getFrozenState(), None)
    self.assertEqual(order_link.getDeliveryBuilder(), None)
    self.assertEqual(order_link.getTradePhase(),'trade/order')

    deliver_link = getattr(business_process, "deliver_link", None)
    self.assertNotEqual(deliver_link, None)
    #self.assertTrue(deliver_link.getDeliverable())
    self.assertEqual(deliver_link.getSuccessor(),"trade_state/trade/delivered")
    self.assertEqual(deliver_link.getPredecessor(),"trade_state/trade/ordered")
    self.assertEqual(deliver_link.getCompletedStateList(),['delivered','started','stopped'])
    self.assertEqual(deliver_link.getFrozenStateList(),['delivered','stopped'])
    self.assertEqual(deliver_link.getTradePhase(),'trade/delivery')

    self.assertEqual(deliver_link.getDeliveryBuilderList(),
           ["portal_deliveries/sale_packing_list_builder",
            "portal_deliveries/internal_packing_list_builder",
            "portal_deliveries/purchase_packing_list_builder"])

    invoice_link = getattr(business_process, "invoice_link", None)
    self.assertNotEqual(invoice_link, None)
    #self.assertFalse(invoice_link.getDeliverable())
    self.assertEqual(invoice_link.getSuccessor(),"trade_state/trade/invoiced")
    self.assertEqual(invoice_link.getPredecessor(),"trade_state/trade/delivered")
    self.assertEqual(invoice_link.getCompletedStateList(),
                        ['confirmed','delivered','started','stopped'])
    self.assertEqual(invoice_link.getFrozenStateList(),['delivered','stopped'])
    self.assertEqual(invoice_link.getTradePhase(),'trade/invoicing')

    self.assertEqual(invoice_link.getDeliveryBuilderList(),
           ["portal_deliveries/purchase_invoice_builder",
            "portal_deliveries/purchase_invoice_transaction_trade_model_builder",
            "portal_deliveries/sale_invoice_builder",
            "portal_deliveries/sale_invoice_transaction_trade_model_builder"])

    account_link = getattr(business_process, "account_link", None)
    self.assertNotEqual(account_link, None)
    #self.assertFalse(account_link.getDeliverable())
    self.assertEqual(account_link.getSuccessor(),"trade_state/trade/accounted")
    self.assertEqual(account_link.getPredecessor(),"trade_state/trade/invoiced")
    self.assertEqual(account_link.getCompletedStateList(),['delivered','started','stopped'])
    self.assertEqual(account_link.getFrozenStateList(),['delivered','stopped'])
    self.assertEqual(account_link.getTradePhase(), 'trade/accounting')

    self.assertSameSet(account_link.getDeliveryBuilderList(),
           ["portal_deliveries/purchase_invoice_transaction_builder",
            "portal_deliveries/sale_invoice_transaction_builder"])

    pay_link = getattr(business_process, "pay_link", None)
    self.assertNotEqual(pay_link, None)
    #self.assertFalse(pay_link.getDeliverable())
    self.assertEqual(pay_link.getTradePhase(), 'trade/payment')
    self.assertEqual(pay_link.getSuccessor(), None)
    self.assertEqual(pay_link.getPredecessor(),"trade_state/trade/accounted")
    self.assertEqual(pay_link.getCompletedState(), None)
    self.assertEqual(pay_link.getFrozenState(), None)

    self.assertEqual(pay_link.getDeliveryBuilderList(),
           ["portal_deliveries/payment_transaction_builder"])

  def test_configurator_item_mixin(self):
    """ConfiguratorItemMixin is available for TTW definition of portal types.
    """
    self.assertIn(
        'ConfiguratorItemMixin',
        self.portal.portal_types.newContent(
            portal_type='Base Type',
            temp_object=True).getMixinTypeList())

