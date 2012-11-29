##############################################################################
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#                     Rafael Monnerat <rafael@nexedi.com>
#                     Ivan Tyagov <ivan@nexedi.com>
#                     Lucas Carvalho <lucas@nexedi.com>
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


import os
from DateTime import DateTime
from Products.ERP5Type.tests.Sequence import SequenceList
from Products.ERP5Type.tests.backportUnittest import expectedFailure
from Products.ERP5Type.tests.runUnitTest import tests_home
from Products.ERP5Type.tests.utils import FileUpload
from Products.ERP5Configurator.tests.ConfiguratorTestMixin import \
                                             TestLiveConfiguratorWorkflowMixin

class StandardConfigurationMixin(TestLiveConfiguratorWorkflowMixin):
  """
    Mixin for shared methods between Consulting and Standard Configurator
    Workflow.
  """
  AFTER_CONFIGURATION_SEQUENCE = '''
      stepCheckValidAccountList
      stepCheckAccountReference
      stepCheckValidPersonList
      stepCheckPersonInformationList
      stepCheckValidOrganisationList
      stepCheckValidCurrencyList
      stepCheckAlarmList
      stepCheckPublicGadgetList
      stepCheckPreferenceList
      stepCheckModulesBusinessApplication
      stepCheckBaseCategoryList
      stepCheckOrganisationSite
      stepCheckAccountingPeriod
      stepCheckRuleValidation
      stepCheckBusinessProcess
      stepCheckSolver
      stepCheckSaleTradeCondition
      stepCheckPurchaseTradeCondition
      stepCheckSaleOrderSimulation
      '''

  SECURITY_CONFIGURATION_SEQUENCE = """
      stepTic
      stepViewAddGadget
      stepViewEventModule
      stepAddEvent
      stepSentEventWorkflow
      stepViewAccountModule
      stepAddAccountModule
      stepViewAccount
      stepCopyPasteAccount
      stepViewEntityModules
      stepAddEntityModules
      stepCopyAndPastePerson
      stepCopyAndPasteOrganisation
      stepEntityWorkflow
      stepViewCreatedPersons
      stepViewCreatedOrganisations
      stepViewCreatedAssignemnts
      stepAddAccoutingPeriod
      stepValidatedAccountingPeriods
      stepViewBankAccount
      stepViewCreditCard
      stepValidateAndModifyBankAccount
      stepValidateAndModifyCreditCard
      stepAddPaymentNodeInPerson
      stepAddPaymentNodeInOrganisation
      stepCopyAndPasteBankAccountInPerson
      stepCopyAndPasteBankAccountInOrganisation
      stepViewAccountingTransactionModule
      stepAddAccountingTransactionModule
      stepCopyAndPasteAccountingTransactions
      stepTic
      stepAccountingTransaction
      stepTic
      stepSaleInvoiceTransaction
      stepTic
      stepPurchaseInvoiceTransaction
      stepTic
      stepPaymentTransaction
      stepTic
      stepBalanceTransaction
      stepTic
      stepAccountingTransaction_getCausalityGroupedAccountingTransactionList
      stepAddAssignments
      stepAssignmentTI
      stepEditAssignments
      stepViewAcessAddPurchaseTradeCondition
      stepViewAccessAddSaleTradeCondition
      stepViewAccessAddSaleOrder
      stepViewAccessAddSalePackingList
      stepViewAccessPurchaseOrder
      stepPurchasePackingList
      stepWebSiteModule
      stepPortalContributionsTool
      stepConfiguredPropertySheets
      """
  def stepSetFranceCase(self, sequence=None, sequence_list=None, **kw):
    """ Check if configuration key was created fine """
    sequence.edit(configuration_currency_reference='EUR',
                  configuration_gap = 'gap/fr/pcg',
                  configuration_accounting_plan='fr',
                  configuration_currency_title = 'Euro',
                  configuration_lang = 'erp5_l10n_fr',
                  configuration_price_currency = 'EUR;0.01;Euro',
                  organisation_default_address_city='LILLE',
                  organisation_default_address_region='europe/western_europe/france')

  def stepSetBrazilCase(self, sequence=None, sequence_list=None, **kw):
    """ Check if configuration key was created fine """
    sequence.edit(configuration_currency_reference='BRL',
                  configuration_gap = 'gap/br/pcg',
                  configuration_accounting_plan='br',
                  configuration_lang = 'erp5_l10n_pt-BR',
                  configuration_currency_title = 'Brazilian Real',
                  configuration_price_currency = 'BRL;0.01;Brazilian Real',
                  organisation_default_address_city='CAMPOS',
                  organisation_default_address_region='americas/south_america/brazil')

  def stepSetRussiaCase(self, sequence=None, sequence_list=None, **kw):
    """ Check if configuration key was created fine """

    sequence.edit(configuration_currency_reference='BYR',
                  configuration_gap = 'gap/ru/ru2000',
                  configuration_accounting_plan='ru',
                  configuration_price_currency = 'BYR;0.01;Belarusian Rouble',
                  configuration_lang = 'erp5_l10n_ru',
                  configuration_currency_title = 'Belarusian Rouble',
                  organisation_default_address_city='MOSCOW',
                  organisation_default_address_region='europe/eastern_europe/russian_federation')


  def getBusinessConfigurationObjectList(self, business_configuration,
                                               portal_type):
    """
      It returns a list of object filtered by portal_type.
      This list should be created based on the paths into specialise value
      of the business configuration.
    """
    object_list = []
    bt5_obj = business_configuration.getSpecialiseValue()
    for path in bt5_obj.getTemplatePathList():
      obj = self.portal.restrictedTraverse(path, None)
      if obj is not None and hasattr(obj, 'getPortalType'):
        if obj.getPortalType() == portal_type:
          object_list.append(obj)
    return object_list

  def stepCheckValidPersonList(self, sequence=None, sequence_list=None, **kw):
    """
      Check if after the configuration the Person objects are validated.
      The Assignments must be opened and valid.
    """
    business_configuration = sequence.get("business_configuration")
    person_list = self.getBusinessConfigurationObjectList(business_configuration, 'Person')
    self.assertNotEquals(len(person_list), 0)
    for person in person_list:
      self.assertEquals('validated', person.getValidationState())
      person.Base_checkConsistency()
      assignment_list = person.contentValues(portal_type='Assignment')
      self.assertNotEquals(len(assignment_list), 0)
      for assignment in assignment_list:
        self.assertEquals('open', assignment.getValidationState())
        self.assertNotEquals(None, assignment.getStartDate())
        self.assertNotEquals(None, assignment.getStopDate())
        self.assertEquals(assignment.getGroup(), "my_group")
        assignment.Base_checkConsistency()

  def stepCheckPersonInformationList(self, sequence=None, sequence_list=None, **kw):
    """
      Check created person informations.
    """
    business_configuration = sequence.get("business_configuration")
    person_list = self.getBusinessConfigurationObjectList(business_configuration, 'Person')
    self.assertEquals(len(person_list), len(self.user_list))
    for person in person_list:
      user_info = None
      for user_dict in self.user_list:
        if user_dict["field_your_reference"] == person.getReference():
          user_info = user_dict
          break

      self.assertNotEquals(user_info, None)
      self.assertEquals(user_info["field_your_first_name"],
                        person.getFirstName())
      self.assertEquals(user_info["field_your_last_name"],
                        person.getLastName())
      self.assertNotEquals(person.getPassword(), None)
      self.assertEquals(user_info["field_your_function"],
                        person.getFunction())
      self.assertEquals(user_info["field_your_default_email_text"],
                        person.getDefaultEmailText())
      self.assertEquals(user_info["field_your_default_telephone_text"],
                        person.getDefaultTelephoneText())

      assignment_list = person.contentValues(portal_type='Assignment')
      self.assertEquals(len(assignment_list), 1)
      self.assertEquals('my_group', assignment_list[0].getGroup())

  def stepCheckValidOrganisationList(self, sequence=None, sequence_list=None, **kw):
    """
      Check if after the configuration the Organisation objects are validated.
    """
    business_configuration = sequence.get("business_configuration")
    organisation_list = self.getBusinessConfigurationObjectList(business_configuration, 'Organisation')
    self.assertNotEquals(len(organisation_list), 0)
    organisation = organisation_list[0]
    self.assertEquals('validated', organisation.getValidationState())
    organisation.Base_checkConsistency()

  def stepCheckBaseCategoryList(self, sequence=None, sequence_list=None, **kw):
    """
       Tests that common base categories are not overwritten by configurator
       We use role as an example
    """
    role = self.portal.portal_categories.role
    self.assertEquals('Role', role.getTitle())
    self.assertEquals(['subordination'], role.getAcquisitionBaseCategoryList())
    self.assertEquals(['default_career'], role.getAcquisitionObjectIdList())
    # ... this is enough to proove it has not been erased by an empty one

  def stepCheckOrganisationSite(self, sequence=None, sequence_list=None, **kw):
    """
      Check if organisation is on the main site (for stock browser)
    """
    business_configuration = sequence.get('business_configuration')
    organisation_list = self.getBusinessConfigurationObjectList(business_configuration, 'Organisation')
    self.assertNotEquals(len(organisation_list), 0)

    self.assertEquals(self.portal.portal_categories.site.main,
                      organisation_list[0].getSiteValue())


  def stepSetConfiguratorWorkflow(self, sequence=None, sequence_list=None, **kw):
    """ Set Consulting Workflow into Business Configuration """
    business_configuration = sequence.get("business_configuration")
    self.setBusinessConfigurationWorkflow(business_configuration,
                                   self.CONFIGURATION_WORKFLOW)

  def stepCreateBusinessConfiguration(self,  sequence=None, sequence_list=None, **kw):
    """ Create one Business Configuration """
    module = self.portal.business_configuration_module
    business_configuration = module.newContent(
                               portal_type="Business Configuration",
                               title=self.getTitle())
    next_dict = {}
    sequence.edit(business_configuration=business_configuration, 
                  next_dict=next_dict)

  def stepCheckValidCurrencyList(self, sequence=None, sequence_list=None, **kw):
    """
      Check if after configuration the Currency objects are validated.
    """
    business_configuration = sequence.get("business_configuration")
    currency_list = self.getBusinessConfigurationObjectList(business_configuration, 'Currency')
    self.assertNotEquals(len(currency_list), 0)
    for currency in currency_list:
      self.assertEquals('validated', currency.getValidationState())
      currency.Base_checkConsistency()

  def stepCheckAlarmList(self, sequence=None, sequence_list=None, **kw):
    """
      Check if after configuration the Alarms objects are enabled.
    """
    business_configuration = sequence.get("business_configuration")
    alarm_list = self.getBusinessConfigurationObjectList(business_configuration, 'Alarm')
    self.assertEquals(len(alarm_list), 2)
    for alarm in alarm_list:
      self.failUnless(alarm.getPeriodicityStartDate() < DateTime())
      self.assertNotEquals(alarm.getPeriodicityStartDate(), None)
      self.assertEquals(alarm.getPeriodicityMinuteFrequency(), 5)
      self.assertEquals(alarm.getEnabled(), True)
      self.assertNotEquals(alarm.getActiveSenseMethodId(), None)

  def stepCheckPublicGadgetList(self, sequence=None, sequence_list=None, **kw):
    """
     Assert all gadgets are publics.
    """
    business_configuration = sequence.get("business_configuration")
    gadget_list = self.getBusinessConfigurationObjectList(business_configuration, 'Gadget')
    for gadget in gadget_list:
      self.assertEquals('public', gadget.getValidationState(),
                        "%s is not public but %s" % (gadget.getRelativeUrl(),
                                                     gadget.getValidationState()))
      gadget.Base_checkConsistency()

  def stepCheckPreferenceList(self, sequence=None, sequence_list=None, **kw):
    """
      Assert all the Peference properties.
    """
    preference_tool = self.portal.portal_preferences
    business_configuration = sequence.get("business_configuration")
    bt5_object = business_configuration.getSpecialiseValue()
    preference_list = bt5_object.getTemplatePreferenceList()
    self.assertEquals(len(preference_list), 2)

    for preference in preference_list:
      self.assertEquals(preference_tool[preference].getPreferenceState(),
                        'global')

    organisation_list = self.getBusinessConfigurationObjectList(business_configuration,
                                                                'Organisation')
    self.assertNotEquals(len(organisation_list), 0)
    organisation_id = organisation_list[0].getId()

    # ui
    # The default preferences are not disabled anymore, there is no reason to
    # assert such properties.
    #self.assertEquals('dmy', preference_tool.getPreferredDateOrder())
    #self.assertTrue(preference_tool.getPreferredHtmlStyleAccessTab())
    self.assertEquals('ODT', preference_tool.getPreferredReportStyle())
    self.assertEquals('pdf', preference_tool.getPreferredReportFormat())
    self.assertEquals(10, preference_tool.getPreferredMoneyQuantityFieldWidth())

    currency_reference = sequence.get('configuration_currency_reference')
    self.assertEquals('currency_module/%s' % currency_reference,
                     preference_tool.getPreferredAccountingTransactionCurrency())
    self.assertEquals(sequence.get('configuration_gap') ,
                      preference_tool.getPreferredAccountingTransactionGap())


    # on Business Configuration
    #self.assertEquals('localhost', preference_tool.getPreferredOoodocServerAddress())
    #self.assertEquals(8011, preference_tool.getPreferredOoodocServerPortNumber())

    # accounting
    self.assertEquals('group/my_group',
                  preference_tool.getPreferredAccountingTransactionSectionCategory())
    self.assertEquals('organisation_module/%s' % organisation_id,
                      preference_tool.getPreferredAccountingTransactionSourceSection())
    self.assertEquals(preference_tool.getPreferredSectionCategory(),
                      'group/my_group')
    self.assertEquals('organisation_module/%s' % organisation_id,
                      preference_tool.getPreferredSection())
    self.assertSameSet(['delivered', 'stopped'],
                  preference_tool.getPreferredAccountingTransactionSimulationStateList())

    # trade
    self.assertEquals(['supplier'], preference_tool.getPreferredSupplierRoleList())
    self.assertEquals(['client'], preference_tool.getPreferredClientRoleList())
    self.assertEquals(['trade/sale'], preference_tool.getPreferredSaleUseList())
    self.assertEquals(['trade/purchase'], preference_tool.getPreferredPurchaseUseList())
    self.assertEquals(['trade/container'], preference_tool.getPreferredPackingUseList())
    self.assertEquals(['trade/tax'], preference_tool.getPreferredTaxUseList())

  def stepCheckModulesBusinessApplication(self, sequence=None, sequence_list=None, **kw):
    """
      Test modules business application.
    """
    ba = self.portal.portal_categories.business_application
    self.assertEquals('Base',
        self.portal.organisation_module.getBusinessApplicationTitle())
    self.assertEquals('Base',
        self.portal.person_module.getBusinessApplicationTitle())
    self.assertEquals('Base',
        self.portal.currency_module.getBusinessApplicationTitle())
    self.assertEquals(set([self.portal.organisation_module,
                       self.portal.person_module,
                       self.portal.currency_module,
                       ba.base]),
         set(ba.base.getBusinessApplicationRelatedValueList()))

    self.assertEquals('CRM',
        self.portal.campaign_module.getBusinessApplicationTitle())
    self.assertEquals('CRM',
        self.portal.event_module.getBusinessApplicationTitle())
    self.assertEquals('CRM',
        self.portal.sale_opportunity_module.getBusinessApplicationTitle())
    self.assertEquals('CRM',
        self.portal.meeting_module.getBusinessApplicationTitle())
    self.assertEquals('CRM',
        self.portal.support_request_module.getBusinessApplicationTitle())
    self.assertEquals(set([self.portal.campaign_module,
                       self.portal.event_module,
                       self.portal.sale_opportunity_module,
                       self.portal.meeting_module,
                       self.portal.support_request_module,
                       ba.crm]),
         set(ba.crm.getBusinessApplicationRelatedValueList()))

    self.assertEquals('Accounting',
        self.portal.account_module.getBusinessApplicationTitle())
    self.assertEquals('Accounting',
        self.portal.accounting_module.getBusinessApplicationTitle())
    self.assertEquals(set([self.portal.account_module,
                       self.portal.accounting_module,
                       ba.accounting]),
         set(ba.accounting.getBusinessApplicationRelatedValueList()))

    self.assertEquals('Trade',
        self.portal.sale_order_module.getBusinessApplicationTitle())
    self.assertEquals('Trade',
        self.portal.purchase_order_module.getBusinessApplicationTitle())
    self.assertEquals('Trade',
        self.portal.sale_trade_condition_module.getBusinessApplicationTitle())
    self.assertEquals('Trade',
        self.portal.purchase_trade_condition_module.getBusinessApplicationTitle())
    self.assertEquals('Trade',
        self.portal.sale_packing_list_module.getBusinessApplicationTitle())
    self.assertEquals('Trade',
        self.portal.purchase_packing_list_module.getBusinessApplicationTitle())
    self.assertEquals('Trade',
        self.portal.inventory_module.getBusinessApplicationTitle())
    self.assertEquals('Trade',
        self.portal.internal_packing_list_module.getBusinessApplicationTitle())
    self.assertEquals('Trade',
        self.portal.returned_sale_packing_list_module.getBusinessApplicationTitle())
    self.assertEquals(set([self.portal.sale_order_module,
                       self.portal.purchase_order_module,
                       self.portal.sale_trade_condition_module,
                       self.portal.purchase_trade_condition_module,
                       self.portal.sale_packing_list_module,
                       self.portal.purchase_packing_list_module,
                       self.portal.internal_packing_list_module,
                       self.portal.returned_sale_packing_list_module,
                       self.portal.inventory_module,
                       ba.trade]),
         set(ba.trade.getBusinessApplicationRelatedValueList()))

    self.assertEquals('PDM',
        self.portal.service_module.getBusinessApplicationTitle())
    self.assertEquals('PDM',
        self.portal.product_module.getBusinessApplicationTitle())
    self.assertEquals('PDM',
        self.portal.component_module.getBusinessApplicationTitle())
    self.assertEquals('PDM',
        self.portal.transformation_module.getBusinessApplicationTitle())
    self.assertEquals('PDM',
        self.portal.sale_supply_module.getBusinessApplicationTitle())
    self.assertEquals('PDM',
        self.portal.purchase_supply_module.getBusinessApplicationTitle())
    self.assertEquals(set([self.portal.service_module,
                       self.portal.product_module,
                       self.portal.component_module,
                       self.portal.transformation_module,
                       self.portal.sale_supply_module,
                       self.portal.purchase_supply_module,
                       ba.pdm]),
         set(ba.pdm.getBusinessApplicationRelatedValueList()))

  def stepCheckValidAccountList(self, sequence=None, sequence_list=None, **kw):
    """
      Check is the Account documents are validated
    """
    business_configuration = sequence.get("business_configuration")
    account_list = self.getBusinessConfigurationObjectList(business_configuration, 'Account')
    self.assertNotEquals(len(account_list), 0)
    for account in account_list:
      self.assertEquals('validated', account.getValidationState())
      # all accounts have a financial section set correctly
      self.assertNotEquals(None, account.getFinancialSectionValue())
      # all accounts have a gap correctly
      self.assertNotEquals(None, account.getGapValue())
      account.Base_checkConsistency()

  def stepCheckAccountReference(self, sequence=None, sequence_list=None, **kw):
    """
     Accounts are exported with the same ID that the one in the spreadsheet
    """
    # XXX FIXME (Lucas): this is not possible yet, because the Account does not have
    # the id set like that, we probably gonna use reference.
    return
    account_id_list = [
      'capital', 'profit_loss', 'equipments',
      'inventories', 'bank', 'receivable',
      'payable', 'refundable_vat', 'coll_vat',
      'purchase', 'sales']
    for account_id in account_id_list:
      account = self.portal.account_module._getOb(account_id)
      self.assertNotEquals(account, None,
                     "%s account is not Found." % account_id)

  def stepCheckSolver(self, sequence=None, sequence_list=None, **kw):
    """
      Check if Solver objects have been created.
    """
    # XXX FIXME Make sure we verify if the default set of solvers
    # are present on the portal.
    return

  def stepCheckRuleValidation(self, sequence=None, sequence_list=None, **kw):
    """
      Check if rule are cloned and validated.
    """
    business_configuration = sequence.get('business_configuration')
    for rule_template_id in [
                          "new_order_root_simulation_rule",
                          "new_delivery_simulation_rule",
                          "new_trade_model_simulation_rule",
                          "new_accounting_transaction_root_simulation_rule",
                          "new_invoice_transaction_simulation_rule",
                          "new_payment_simulation_rule",
                          "new_invoice_root_simulation_rule",
                          "new_delivery_root_simulation_rule",
                          "new_invoice_simulation_rule"]:

      rule_template = getattr(self.portal.portal_rules, rule_template_id, None)
      self.assertNotEquals(rule_template, None)
      rule_list = self.portal.portal_rules.searchFolder(
                        reference=rule_template.getReference(),
                        title=rule_template.getTitle(),
                        validation_stade="validated")

      self.assertTrue(len(rule_list) > 0)
      self.assertEquals(int(rule_template.getVersion(0)) + 1,
                        int(rule_list[-1].getVersion(0)))

      result = self.getBusinessConfigurationObjectList(business_configuration,
                                                 rule_template.getPortalType())
      self.assertNotEquals(0, len(result))
      # one rule with same reference must exist.
      self.assertTrue(len([i for i in result \
                   if i.getReference() == rule_template.getReference()]) == 1)

  def stepCheckBusinessProcess(self, sequence=None, sequence_list=None, **kw):
    """
      Check if there is a Business Process on the site.
    """
    business_configuration = sequence.get('business_configuration')
    business_process_list = \
              self.getBusinessConfigurationObjectList(business_configuration,
                                                           'Business Process')
    self.assertEquals(len(business_process_list), 1)

    business_process = business_process_list[0]
    self.assertEquals("default_erp5_business_process",
                      business_process.getReference())

    self.assertEquals("Default Trade Business Process",
                      business_process.getTitle())

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
    self.assertEquals(accounting_credit_path.getSource(), "account_module/receivable")

    accounting_debit_path = getattr(business_process, "accounting_debit_path", None)
    self.assertNotEquals(accounting_debit_path, None)
    self.assertEquals(accounting_debit_path.getEfficiency(), 1.0)
    self.assertEquals(accounting_debit_path.getTradePhase(), 'trade/accounting')
    self.assertEquals(accounting_debit_path.getTradeDate(), 'trade_phase/trade/invoicing')
    self.assertEquals(accounting_debit_path.getSource(), "account_module/sales")

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

  def stepCheckAccountingPeriod(self, sequence=None, sequence_list=None, **kw):
    """
      The configurator prepared an accounting period for 2008, make
      sure it's openned and have correct parameters.
    """
    business_configuration = sequence.get('business_configuration')
    organisation_list = self.getBusinessConfigurationObjectList(business_configuration, 'Organisation')
    self.assertNotEquals(len(organisation_list), 0)

    organisation = organisation_list[0]
    period_list = organisation.contentValues(portal_type='Accounting Period')
    self.assertEquals(1, len(period_list))
    period = period_list[0]
    self.assertEquals('started', period.getSimulationState())
    self.assertEquals(DateTime(2008, 1, 1), period.getStartDate())
    self.assertEquals(DateTime(2008, 12, 31), period.getStopDate())
    self.assertEquals('2008', period.getShortTitle())

    # security on this period has been initialised
    for username in self.accountant_username_list:
      self.failUnlessUserCanPassWorkflowTransition(
          username, 'cancel_action', period)

  def stepCheckSaleTradeCondition(self, sequence=None, sequence_list=None, **kw):
    """
      Check if Sale Trade Condition object has been created.
    """
    business_configuration = sequence.get('business_configuration')
    sale_trade_condition_list = \
                self.getBusinessConfigurationObjectList(business_configuration,
                                                        'Sale Trade Condition')
    self.assertEquals(len(sale_trade_condition_list), 1)
    sale_trade_condition = sale_trade_condition_list[0]

    self.assertEquals("General Sale Trade Condition",
                                              sale_trade_condition.getTitle())
    self.assertEquals("STC-General", sale_trade_condition.getReference())

    self.assertNotEquals(None, sale_trade_condition.getEffectiveDate())
    self.assertNotEquals(None, sale_trade_condition.getExpirationDate())

    # Check relation with Business Process
    business_process_list = \
              self.getBusinessConfigurationObjectList(business_configuration,
                                                           'Business Process')
    self.assertEquals(len(business_process_list), 1)

    business_process = business_process_list[0]
    self.assertEquals(business_process,
                      sale_trade_condition.getSpecialiseValue())

    # Check relation with Organisation
    organisation_list = \
                self.getBusinessConfigurationObjectList(business_configuration,
                                                                'Organisation')
    organisation = organisation_list[0]

    self.assertEquals(organisation, sale_trade_condition.getSourceValue())
    self.assertEquals(organisation,
                      sale_trade_condition.getSourceSectionValue())

    # Check relation with Currency
    currency_list = \
                self.getBusinessConfigurationObjectList(business_configuration,
                                                                    'Currency')
    currency = currency_list[0]
    self.assertEquals(currency.getRelativeUrl(),
                      sale_trade_condition.getPriceCurrency())

  def stepCheckPurchaseTradeCondition(self, sequence=None, sequence_list=None, **kw):
    """
      Check if Purchase Trade Condition object has been created.
    """
    business_configuration = sequence.get('business_configuration')
    purchase_trade_condition_list = \
                self.getBusinessConfigurationObjectList(business_configuration,
                                                        'Purchase Trade Condition')
    self.assertEquals(len(purchase_trade_condition_list), 1)
    purchase_trade_condition = purchase_trade_condition_list[0]

    self.assertEquals("General Purchase Trade Condition",
                                              purchase_trade_condition.getTitle())
    self.assertEquals("PTC-General", purchase_trade_condition.getReference())

    self.assertNotEquals(None, purchase_trade_condition.getEffectiveDate())
    self.assertNotEquals(None, purchase_trade_condition.getExpirationDate())

    # Check relation with Business Process
    business_process_list = \
              self.getBusinessConfigurationObjectList(business_configuration,
                                                           'Business Process')
    self.assertEquals(len(business_process_list), 1)

    business_process = business_process_list[0]
    self.assertEquals(business_process,
                      purchase_trade_condition.getSpecialiseValue())

    # Check relation with Organisation
    organisation_list = \
                self.getBusinessConfigurationObjectList(business_configuration,
                                                                'Organisation')
    organisation = organisation_list[0]

    self.assertEquals(organisation,
                      purchase_trade_condition.getDestinationValue())
    self.assertEquals(organisation,
                      purchase_trade_condition.getDestinationSectionValue())

    # Check relation with Currency
    currency_list = \
                self.getBusinessConfigurationObjectList(business_configuration,
                                                                    'Currency')
    currency = currency_list[0]
    self.assertEquals(currency.getRelativeUrl(),
                      purchase_trade_condition.getPriceCurrency())

  @expectedFailure
  def stepCheckQuantityConversion(self, sequence=None, sequence_list=None, **kw):
    resource = self.portal.product_module.newContent(
                      portal_type='Product',
                      quantity_unit_list=('mass/gram',
                                          'mass/kilogram'),)
    node = self.portal.organisation_module.newContent(
                      portal_type='Organisation')
    delivery = self.portal.purchase_packing_list_module.newContent(
                      portal_type='Purchase Packing List',
                      start_date='2010-01-26',
                      price_currency='currency_module/EUR',
                      destination_value=node,
                      destination_section_value=node)
    delivery.newContent(portal_type='Purchase Packing List Line',
                        resource_value=resource,
                        quantity=10,
                        quantity_unit='mass/gram')
    delivery.newContent(portal_type='Purchase Packing List Line',
                        resource_value=resource,
                        quantity=3,
                        quantity_unit='mass/kilogram')
    delivery.confirm()
    delivery.start()
    delivery.stop()
    self.tic()

    # inventories of that resource are index in grams
    self.assertEquals(3010,
        self.portal.portal_simulation.getCurrentInventory(
          resource_uid=resource.getUid(),
          node_uid=node.getUid()))

    # converted inventory also works
    self.assertEquals(3.01,
        self.portal.portal_simulation.getCurrentInventory(
          quantity_unit='mass/kilogram',
          resource_uid=resource.getUid(),
          node_uid=node.getUid()))

  def stepConfiguredPropertySheets(self, sequence=None, sequence_list=None, **kw):
    """
      Configurator can configure some PropertySheets.
    """
    portal = self.portal
    purchase_order = portal.portal_types['Purchase Order']
    purchase_order_line = portal.portal_types['Purchase Order Line']
    sale_order = portal.portal_types['Sale Order']
    sale_order_line = portal.portal_types['Sale Order Line']
    inventory = portal.portal_types['Inventory']
    sale_packing_list = portal.portal_types['Sale Packing List']
    sale_packing_list_line = portal.portal_types['Sale Packing List Line']
    self.assertEquals(True,
                      'TradeOrderLine' in sale_packing_list_line.getTypePropertySheetList())
    self.assertEquals(True,
                      'TradeOrder' in purchase_order.getTypePropertySheetList())
    self.assertEquals(True,
                      'TradeOrderLine' in purchase_order_line.getTypePropertySheetList())
    self.assertEquals(True,
                      'TradeOrder' in sale_order.getTypePropertySheetList())
    self.assertEquals(True,
                      'TradeOrderLine' in sale_order_line.getTypePropertySheetList())
    self.assertEquals(True,
                      'InventoryConstraint' in inventory.getTypePropertySheetList())


  def stepCheckSaleOrderSimulation(self, sequence=None, sequence_list=None, **kw):
    """
      After the configuration we need to make sure that Simulation for
      Sale Order is working as expected.
    """
    # stepCreateSaleOrders
    portal = self.getPortal()
    module = portal.sale_order_module
    business_configuration = sequence.get('business_configuration')
    sale_trade_condition = \
                self.getBusinessConfigurationObjectList(business_configuration,
                                                     'Sale Trade Condition')[0]
    # Check relation with Business Process
    business_process_list = \
              self.getBusinessConfigurationObjectList(business_configuration,
                                                           'Business Process')
    self.assertEquals(len(business_process_list), 1)

    business_process = business_process_list[0]
    destination_decision = portal.portal_catalog.getResultValue(
                                       portal_type='Person',
                                       reference=self.sales_manager_reference)
    destination_administration = portal.portal_catalog.getResultValue(
                                     portal_type='Person',
                                     reference=self.purchase_manager_reference)
    resource = portal.product_module.newContent(portal_type='Product',
                                quantity_unit='unit/piece',
                                individual_variation_base_category='variation',
                                base_contribution='base_amount/taxable')
    self.tic()
    resource.validate()
    self.tic()

    start_date = sale_trade_condition.getEffectiveDate() + 1
    stop_date = sale_trade_condition.getExpirationDate() - 1
    order = module.newContent(
       portal_type='Sale Order',
       specialise=(sale_trade_condition.getRelativeUrl(),),
       destination_decision=destination_decision.getRelativeUrl(),
       destination_administration=destination_administration.getRelativeUrl(),
       start_date=start_date,
       stop_date=stop_date)
    self.tic()

    # Set the rest through the trade condition.
    order.SaleOrder_applySaleTradeCondition()
    self.tic()

    order.newContent(portal_type='Sale Order Line',
                     resource=resource.getRelativeUrl(),
                     quantity=1.0)
    self.tic()

    # stepPlanSaleOrders
    self.assertEquals(order.getSimulationState(), 'draft')
    order.plan()
    self.tic()
    self.assertEquals(order.getSimulationState(), 'planned')

    # stepOrderSaleOrders
    order.order()
    self.tic()
    self.assertEquals(order.getSimulationState(), 'ordered')

    # stepConfirmSaleOrders
    order.confirm()
    self.tic()
    self.assertEquals(order.getSimulationState(), 'confirmed')

    # stepCheckSaleOrderSimulation
    causality_list = order.getCausalityRelatedValueList(portal_type='Applied Rule')
    self.assertEquals(len(causality_list), 1)
    applied_rule = causality_list[0]
    self.assertEquals(applied_rule.getPortalType(), 'Applied Rule')
    rule = applied_rule.getSpecialiseValue()
    self.assertNotEquals(rule, None)
    self.assertEquals(rule.getReference(), 'default_order_rule')
    self.assertEquals(applied_rule.objectCount(), 1)

    simulation_movement = applied_rule.objectValues()[0]
    self.assertEquals(simulation_movement.getPortalType(),
                                                      'Simulation Movement')
    self.assertEquals(simulation_movement.getQuantity(), 1.0)
    self.assertEquals(simulation_movement.getResourceValue(), resource)

    self.assertNotEquals(simulation_movement.getCausality(), None)
    self.assertEquals(simulation_movement.getDestinationDecisionValue(),
                                                       destination_decision)
    self.assertEquals(simulation_movement.getDestinationAdministrationValue(),
                                                 destination_administration)


class TestConsultingConfiguratorWorkflow(StandardConfigurationMixin):
  """
    Test Live Consulting Configuration Workflow
  """

  CONFIGURATION_WORKFLOW = 'workflow_module/erp5_consulting_workflow'

  DEFAULT_SEQUENCE_LIST = """
      stepSet%(country)sCase
      stepCreateBusinessConfiguration
      stepTic
      stepSetConfiguratorWorkflow
      stepTic
      stepConfiguratorNext
      stepTic
      stepCheckBT5ConfiguratorItem
      stepCheckConfigureCategoriesForm
      stepSetupCategoriesConfiguratorItem
      stepConfiguratorNext
      stepTic
      stepCheckConfigureRolesForm
      stepCheckCategoriesConfiguratorItem
      stepSetupRolesConfiguratorItem
      stepConfiguratorNext
      stepTic
      stepCheckConfigureOrganisationForm
      stepSetupOrganisationConfiguratorItem
      stepConfiguratorNext
      stepTic
      stepCheckConfigureUserAccountNumberForm
      stepCheckOrganisationConfiguratorItem
      stepSetupUserAccounNumberSix
      stepConfiguratorNext
      stepTic
      stepCheckConfigureMultipleUserAccountForm
      stepSetupMultipleUserAccountSix
      stepConfiguratorNext
      stepTic
      stepCheckConfigureAccountingForm
      stepCheckMultiplePersonConfigurationItem
      stepSetupAccountingConfiguration
      stepConfiguratorNext
      stepTic
      stepCheckConfigurePreferenceForm
      stepCheckAccountingConfigurationItemList%(country)s
      stepSetupPreferenceConfiguration
      stepConfiguratorNext
      stepTic
      stepCheckPreferenceConfigurationItemList
      stepCheckConfigureInstallationForm
      stepSetupInstallConfiguration
      stepConfiguratorNext
      stepTic
      stepCheckInstallConfiguration
      stepStartConfigurationInstallation
      stepTic
      stepCheckInstanceIsConfigured%(country)s
      """

  def uploadFile(self, file_id):
    file_obj = getattr(self.portal, file_id)
    file_path = tests_home + '/%s' % file_id
    temp_file = open(file_path, 'w+b')
    try:
      temp_file.write(str(file_obj))
    finally:
      temp_file.close()

    return (file_path, FileUpload(file_path, file_id))

  def afterSetUp(self):
    TestLiveConfiguratorWorkflowMixin.afterSetUp(self)
    categories_file_id = 'standard_category.ods'
    self.categories_file_path, self.categories_file_upload = \
                                           self.uploadFile(categories_file_id)

    roles_file_id = 'standard_portal_types_roles.ods'
    self.roles_file_path, self.roles_file_upload = \
                                           self.uploadFile(roles_file_id)
    # set the company employees number
    self.company_employees_number = '3'

    newId = self.portal.portal_ids.generateNewId
    id_group ='testConfiguratorConsultingWorkflow'
    self.person_creator_reference = 'person_creator_%s' % newId(id_group)
    self.person_assignee_reference = 'person_assignee_%s' % newId(id_group)
    self.person_assignor_reference = 'person_assignor_%s' % newId(id_group)


    self.accountant_username_list = (self.person_creator_reference,
                                     self.person_assignee_reference,
                                     self.person_assignor_reference)

    self.sales_manager_reference = self.person_assignee_reference
    self.purchase_manager_reference = self.person_assignee_reference
    self.accounting_agent_reference = self.person_assignee_reference
    self.accounting_manager_reference = self.person_assignee_reference
    self.warehouse_agent_reference = self.person_assignee_reference
    self.simple_user_reference = self.person_assignee_reference

    self.sales_and_purchase_username_list = (self.sales_manager_reference,
                                             self.purchase_manager_reference,)
    self.warehouse_username_list = (self.warehouse_agent_reference,)
    self.simple_username_list = (self.simple_user_reference,)


    self.all_username_list = self.accountant_username_list

    # set the user list
    self.user_list = [
      dict(
        field_your_first_name='Person',
        field_your_last_name='Creator',
        field_your_reference=self.person_creator_reference,
        field_your_password='person_creator',
        field_your_password_confirm='person_creator',
        field_your_function='hr/manager',
        field_your_default_email_text='person_creator@example.com',
        field_your_default_telephone_text='',
      ), dict(
        field_your_first_name='Person',
        field_your_last_name='Assignee',
        field_your_reference=self.person_assignee_reference,
        field_your_password='person_assignee',
        field_your_password_confirm='person_assignee',
        field_your_function='af/accounting/manager',
        field_your_default_email_text='person_assignee@example.com',
        field_your_default_telephone_text='',
      ), dict(
        field_your_first_name='Person',
        field_your_last_name='Assignor',
        field_your_reference=self.person_assignor_reference,
        field_your_password='person_assignor',
        field_your_password_confirm='person_assignor',
        field_your_function='sales/manager',
        field_your_default_email_text='person_assignor@example.com',
        field_your_default_telephone_text='',
      ),
    ]

    # set preference group
    self.preference_group = 'group/my_group'

  def beforeTearDown(self):
    os.remove(self.categories_file_path)
    os.remove(self.roles_file_path)

  def stepCheckConfigureCategoriesForm(self, sequence=None, sequence_list=None, **kw):
    """ Check if Confire Categories step was showed """
    response_dict = sequence.get("response_dict")
    if 'command' in response_dict:
      self.assertEquals('show', response_dict['command'])
    self.assertEquals(None, response_dict['previous'])
    self.assertEquals('Configure Categories', response_dict['next'])
    self.assertCurrentStep('Your Categories', response_dict)

  def stepSetupCategoriesConfiguratorItem(self, sequence=None, sequence_list=None, **kw):
    """ Load the categories """
    next_dict = dict(field_your_configuration_spreadsheet=self.categories_file_upload)
    next_dict.update(**kw)
    sequence.edit(next_dict=next_dict)

  def stepCheckConfigureRolesForm(self, sequence=None, sequence_list=None, **kw):
    """ Check if Configure Roles step was showed """
    response_dict = sequence.get("response_dict")
    if 'command' in response_dict:
      self.assertEquals('show', response_dict['command'])
    self.assertEquals('Configure Roles', response_dict['next'])
    self.assertEquals('Previous', response_dict['previous'])
    self.assertCurrentStep('Your roles settings', response_dict)

  def stepCheckCategoriesConfiguratorItem(self, sequence=None, sequence_list=None, **kw):
    """ Checki if categories was created """
    business_configuration = sequence.get("business_configuration")
    # this created a categories spreadsheet confiurator item
    categories_spreadsheet_configuration_save = business_configuration['3']
    categories_spreadsheet_configuration_item =\
          categories_spreadsheet_configuration_save['1']
    self.assertEquals('Categories Spreadsheet Configurator Item',
          categories_spreadsheet_configuration_item.getPortalType())

    spreadsheet = categories_spreadsheet_configuration_item\
                    .getConfigurationSpreadsheet()
    self.assertNotEquals(None, spreadsheet)
    self.assertEquals('Embedded File', spreadsheet.getPortalType())
    self.failUnless(spreadsheet.hasData())

  def stepSetupRolesConfiguratorItem(self, sequence=None, sequence_list=None, **kw):
    """ Load the Roles """
    next_dict = dict(field_your_portal_type_roles_spreadsheet=self.roles_file_upload)
    next_dict.update(**kw)
    sequence.edit(next_dict=next_dict)

  def stepCheckConfigureOrganisationForm(self, sequence=None, sequence_list=None, **kw):
    """ Check if Confire Organisation step was showed """
    response_dict = sequence.get("response_dict")
    TestLiveConfiguratorWorkflowMixin.stepCheckConfigureOrganisationForm(
                         self, sequence, sequence_list, **kw)
    self.assertEquals('Previous', response_dict['previous'])

  def stepSetupOrganisationConfiguratorItem(self, sequence=None, sequence_list=None, **kw):
    """ Create one Organisation with French information """
    TestLiveConfiguratorWorkflowMixin.stepSetupOrganisationConfiguratorItem(
        self,
        sequence=sequence,
        sequence_list=sequence_list,
        field_your_group='my_group')

  def stepCheckOrganisationConfiguratorItem(self, sequence=None, sequence_list=None, **kw):
    """ Check if organisation was created fine """
    business_configuration = sequence.get("business_configuration")
    # last one: a step for what the client selected
    organisation_config_save = business_configuration['5']
    self.assertEquals(1, len(organisation_config_save.contentValues()))
    # first item: configuration of our organisation
    organisation_config_item = organisation_config_save['1']
    self.assertEquals(organisation_config_item.getPortalType(),
                      'Organisation Configurator Item')
    # this organisation configurator items contains all properties that the
    # orgnanisation will have.
    self.assertEquals(organisation_config_item.getDefaultAddressCity(),
                      'LILLE')
    self.assertEquals(organisation_config_item.getDefaultAddressRegion(),
                      'europe/western_europe/france')
    self.assertEquals(organisation_config_item.getDefaultEmailText(),
                      'me@example.com')
    self.assertEquals('01234567890',
        organisation_config_item.getDefaultTelephoneTelephoneNumber())

    configuration_save_list = business_configuration.contentValues(
                                             portal_type="Configuration Save")
    self.assertEquals(5, len(configuration_save_list))

    link_list = business_configuration.contentValues(portal_type="Link")
    self.assertEquals(0, len(link_list))

  def stepCheckMultiplePersonConfigurationItem(self, sequence=None, sequence_list=None, **kw):
    """
      Check if multiple Person Configuration Item of the Business
      Configuration have been created successfully.
    """
    person_business_configuration_save = TestLiveConfiguratorWorkflowMixin.\
              stepCheckMultiplePersonConfigurationItem(
                                  self, sequence, sequence_list, **kw)

    person_business_configuration_item =\
          person_business_configuration_save['1']
    self.assertEquals('Person Configurator Item',
            person_business_configuration_item.getPortalType())
    self.assertEquals('Person',
            person_business_configuration_item.getFirstName())
    self.assertEquals('Creator',
            person_business_configuration_item.getLastName())
    self.assertEquals(self.person_creator_reference,
            person_business_configuration_item.getReference())
    self.assertEquals('person_creator',
            person_business_configuration_item.getPassword())
    self.assertEquals('hr/manager',
            person_business_configuration_item.getFunction())

    person_business_configuration_item =\
          person_business_configuration_save['2']
    self.assertEquals('Person Configurator Item',
            person_business_configuration_item.getPortalType())
    self.assertEquals('Person',
            person_business_configuration_item.getFirstName())
    self.assertEquals('Assignee',
            person_business_configuration_item.getLastName())
    self.assertEquals(self.person_assignee_reference,
            person_business_configuration_item.getReference())
    self.assertEquals('person_assignee',
            person_business_configuration_item.getPassword())
    self.assertEquals('af/accounting/manager',
            person_business_configuration_item.getFunction())

    person_business_configuration_item =\
          person_business_configuration_save['3']
    self.assertEquals('Person Configurator Item',
            person_business_configuration_item.getPortalType())
    self.assertEquals('Person',
            person_business_configuration_item.getFirstName())
    self.assertEquals('Assignor',
            person_business_configuration_item.getLastName())
    self.assertEquals(self.person_assignor_reference,
            person_business_configuration_item.getReference())
    self.assertEquals('person_assignor',
            person_business_configuration_item.getPassword())
    self.assertEquals('sales/manager',
            person_business_configuration_item.getFunction())

  def test_consulting_workflow(self):
    """ Test the consulting workflow configuration"""
    sequence_list = SequenceList()
    sequence_string = \
      self.DEFAULT_SEQUENCE_LIST % dict(country='France') + \
      self.AFTER_CONFIGURATION_SEQUENCE + \
      self.SECURITY_CONFIGURATION_SEQUENCE

    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

class TestStandardConfiguratorWorkflow(StandardConfigurationMixin):
  """
    Test Live Standard Configuration Workflow.
  """
  CONFIGURATION_WORKFLOW = 'workflow_module/erp5_standard_workflow'

  DEFAULT_SEQUENCE_LIST = """
      stepSet%(country)sCase
      stepCreateBusinessConfiguration
      stepTic
      stepSetConfiguratorWorkflow
      stepTic
      stepConfiguratorNext
      stepTic
      stepCheckBT5ConfiguratorItem
      stepCheckConfigureOrganisationForm
      stepSetupOrganisationConfiguratorItem
      stepConfiguratorNext
      stepTic
      stepCheckConfigureUserAccountNumberForm
      stepCheckOrganisationConfiguratorItem
      stepSetupUserAccounNumberSix
      stepConfiguratorNext
      stepTic
      stepCheckConfigureMultipleUserAccountForm
      stepSetupMultipleUserAccountSix
      stepConfiguratorNext
      stepTic
      stepCheckConfigureAccountingForm
      stepCheckMultiplePersonConfigurationItem
      stepSetupAccountingConfiguration
      stepConfiguratorNext
      stepTic
      stepCheckConfigurePreferenceForm
      stepCheckAccountingConfigurationItemList%(country)s
      stepSetupPreferenceConfiguration
      stepConfiguratorNext
      stepTic
      stepCheckConfigureInstallationForm
      stepCheckPreferenceConfigurationItemList
      stepSetupInstallConfiguration
      stepConfiguratorNext
      stepTic
      stepCheckInstallConfiguration
      stepStartConfigurationInstallation
      stepTic
      stepCheckInstanceIsConfigured%(country)s
      """ + \
      StandardConfigurationMixin.AFTER_CONFIGURATION_SEQUENCE + \
      StandardConfigurationMixin.SECURITY_CONFIGURATION_SEQUENCE

  def afterSetUp(self):
    TestLiveConfiguratorWorkflowMixin.afterSetUp(self)
    newId = self.portal.portal_ids.generateNewId
    id_group ='testConfiguratorStandardWorkflow'

    self.sales_manager_reference = 'sales_manager_%s' % newId(id_group)
    self.purchase_manager_reference = 'purchase_manager_%s' % newId(id_group)
    self.accounting_agent_reference = 'accounting_agent_%s' % newId(id_group)
    self.accounting_manager_reference = 'accounting_manager_%s' % newId(id_group)
    self.warehouse_agent_reference = 'warehouse_agent_%s' % newId(id_group)
    self.simple_user_reference = 'simple_user_%s' % newId(id_group)

    self.accountant_username_list = (self.accounting_agent_reference,
                                     self.accounting_manager_reference,)
    self.all_username_list = (self.sales_manager_reference,
                              self.purchase_manager_reference,
                              self.accounting_agent_reference,
                              self.accounting_manager_reference,
                              self.warehouse_agent_reference,
                              self.simple_user_reference,)
    self.sales_and_purchase_username_list = (self.sales_manager_reference,
                                             self.purchase_manager_reference,)
    self.warehouse_username_list = (self.warehouse_agent_reference,)
    self.simple_username_list = (self.simple_user_reference,)

    # set the company employees number
    self.company_employees_number = '6'

    # create our 6 users:
    self.user_list = [
      dict(
                # A sales manager
        field_your_first_name='Sales',
        field_your_last_name='Manager',
        field_your_reference=self.sales_manager_reference,
        field_your_password='sales_manager',
        field_your_password_confirm='sales_manager',
        field_your_function='sales/manager',
        field_your_default_email_text='sales_manager@example.com',
        field_your_default_telephone_text='',
      ), dict(
                # A purchase manager
        field_your_first_name='Purchase',
        field_your_last_name='Manager',
        field_your_reference=self.purchase_manager_reference,
        field_your_password='purchase_manager',
        field_your_password_confirm='purchase_manager',
        field_your_function='purchase/manager',
        field_your_default_email_text='purchase_manager@example.com',
        field_your_default_telephone_text='',
      ), dict(
                # An Accounting agent
        field_your_first_name='Accounting',
        field_your_last_name='Agent',
        field_your_reference=self.accounting_agent_reference,
        field_your_password='accounting_agent',
        field_your_password_confirm='accounting_agent',
        field_your_function='af/accounting/agent',
        field_your_default_email_text='accounting_agent@example.com',
        field_your_default_telephone_text='',
      ), dict(
                # An Accounting Manager
        field_your_first_name='Accounting',
        field_your_last_name='Manager',
        field_your_reference=self.accounting_manager_reference,
        field_your_password='accounting_manager',
        field_your_password_confirm='accounting_manager',
        field_your_function='af/accounting/manager',
        field_your_default_email_text='accounting_manager@example.com',
        field_your_default_telephone_text='',
      ), dict(
                # A Warehouse Agent
        field_your_first_name='Warehouse',
        field_your_last_name='Agent',
        field_your_reference=self.warehouse_agent_reference,
        field_your_password='warehouse_agent',
        field_your_password_confirm='warehouse_agent',
        field_your_function='warehouse/agent',
        field_your_default_email_text='warehouse_agent@example.com',
        field_your_default_telephone_text='',
      ), dict(
          # A Simple user without meaningfull function ( hr / manager)
        field_your_first_name='Simple',
        field_your_last_name='User',
        field_your_reference=self.simple_user_reference,
        field_your_password='simple_user',
        field_your_password_confirm='simple_user',
        field_your_function='hr/manager',
        field_your_default_email_text='simple_user@example.com',
        field_your_default_telephone_text='',
      ),
    ]
    # set preference group
    self.preference_group = 'group/my_group'

  def stepCheckConfigureOrganisationForm(self, sequence=None, sequence_list=None, **kw):
    """ Check if Confire Organisation step was showed """
    response_dict = sequence.get("response_dict")
    TestLiveConfiguratorWorkflowMixin.stepCheckConfigureOrganisationForm(
                         self, sequence, sequence_list, **kw)
    self.assertEquals(None, response_dict['previous'])

  def stepCheckOrganisationConfiguratorItem(self, sequence=None, sequence_list=None, **kw):
    """ Check if configuration key was created fine """
    business_configuration = sequence.get('business_configuration')
    default_address_city = sequence.get('organisation_default_address_city')
    default_address_region = sequence.get('organisation_default_address_region')

    # last one: a step for what the client selected
    organisation_config_save = business_configuration['5']
    self.assertEquals(2, len(organisation_config_save.contentValues()))
    # first item: configuration of our organisation
    organisation_config_item = organisation_config_save['1']
    self.assertEquals(organisation_config_item.getPortalType(),
                      'Organisation Configurator Item')
    # this organisation configurator items contains all properties that the
    # orgnanisation will have.
    self.assertEquals(organisation_config_item.getDefaultAddressCity(),
                      default_address_city)
    self.assertEquals(organisation_config_item.getDefaultAddressRegion(),
                      default_address_region)
    self.assertEquals(organisation_config_item.getDefaultEmailText(),
                      'me@example.com')
    self.assertEquals('01234567890',
        organisation_config_item.getDefaultTelephoneTelephoneNumber())

    # we also create a category for our group
    category_config_item = organisation_config_save['2']
    self.assertEquals(category_config_item.getPortalType(),
                      'Category Configurator Item')
    self.assertEquals(category_config_item.getTitle(),
                      'My Organisation')

    self.assertEquals(5, len(business_configuration.contentValues(portal_type="Configuration Save")))
    self.assertEquals(0, len(business_configuration.contentValues(portal_type="Link")))

  def stepCheckMultiplePersonConfigurationItem(self, sequence=None, sequence_list=None, **kw):
    """
      Check if multiple Person Configuration Item of the Business
      Configuration have been created successfully.
    """
    person_business_configuration_save = TestLiveConfiguratorWorkflowMixin.\
              stepCheckMultiplePersonConfigurationItem(
                                  self, sequence, sequence_list, **kw)

    person_business_configuration_item =\
          person_business_configuration_save['1']
    self.assertEquals('Person Configurator Item',
            person_business_configuration_item.getPortalType())
    self.assertEquals('Sales',
            person_business_configuration_item.getFirstName())
    self.assertEquals('Manager',
            person_business_configuration_item.getLastName())
    self.assertEquals(self.sales_manager_reference,
            person_business_configuration_item.getReference())
    self.assertEquals('sales_manager',
            person_business_configuration_item.getPassword())
    self.assertEquals('sales/manager',
            person_business_configuration_item.getFunction())

    # ...
    person_business_configuration_item =\
          person_business_configuration_save['3']
    self.assertEquals('Person Configurator Item',
            person_business_configuration_item.getPortalType())
    self.assertEquals('Accounting',
            person_business_configuration_item.getFirstName())
    self.assertEquals('Agent',
            person_business_configuration_item.getLastName())
    self.assertEquals(self.accounting_agent_reference,
            person_business_configuration_item.getReference())
    self.assertEquals('accounting_agent',
            person_business_configuration_item.getPassword())
    self.assertEquals('af/accounting/agent',
            person_business_configuration_item.getFunction())

  ##########################################
  def test_standard_workflow_france(self):
    """ Test the standard workflow with french configuration"""
    sequence_list = SequenceList()
    sequence_string = self.DEFAULT_SEQUENCE_LIST % dict(country='France')
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_standard_workflow_brazil(self):
    """ Test the standard workflow with brazilian configuration """
    sequence_list = SequenceList()
    sequence_string = self.DEFAULT_SEQUENCE_LIST % dict(country='Brazil')
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_standard_workflow_russia(self):
    """ Test the standard workflow with russian configuration """
    sequence_list = SequenceList()
    sequence_string = self.DEFAULT_SEQUENCE_LIST % dict(country='Russia')
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_standard_workflow_brazil_with_previous(self):
    """ This time we must simulate the previous buttom """
    sequence_list = SequenceList()
    sequence_string = """
      stepSetBrazilCase
      stepCreateBusinessConfiguration
      stepTic
      stepSetConfiguratorWorkflow
      stepTic
      stepConfiguratorNext
      stepTic
      stepCheckBT5ConfiguratorItem
      stepCheckConfigureOrganisationForm
      stepSetupOrganisationConfiguratorItem
      stepConfiguratorNext
      stepTic
      stepCheckConfigureUserAccountNumberForm
      stepCheckOrganisationConfiguratorItem
    """
    # check previous to organisation form and go back to
    # User Account Number Form to setup the number of user
    sequence_string += """
      stepConfiguratorPrevious
      stepCheckConfigureOrganisationForm
      stepConfiguratorNext
      stepCheckConfigureUserAccountNumberForm
      stepSetupUserAccounNumberSix
      stepConfiguratorNext
      stepTic
      stepCheckConfigureMultipleUserAccountForm
    """
    # check previous to user account number form
    sequence_string += """
      stepConfiguratorPrevious
      stepCheckConfigureUserAccountNumberForm
    """
    # check previous to organisation form
    sequence_string += """
      stepConfiguratorPrevious
      stepCheckConfigureOrganisationForm
      stepSetupOrganisationConfiguratorItem
    """
    # go next to user account number form
    sequence_string += """
      stepConfiguratorNext
      stepCheckConfigureUserAccountNumberForm
      stepSetupUserAccounNumberSix
    """
    # go next to Multiple User Account Form
    sequence_string += """
      stepConfiguratorNext
      stepCheckConfigureMultipleUserAccountForm
      stepSetupMultipleUserAccountSix
      stepConfiguratorNext
      stepTic
      stepCheckMultiplePersonConfigurationItem
      stepCheckConfigureAccountingForm
      stepSetupAccountingConfiguration
      stepConfiguratorNext
      stepTic
      stepCheckAccountingConfigurationItemListBrazil
      stepCheckConfigurePreferenceForm
    """
    # check previous until organisation form
    # and go back to Configure Preference form
    sequence_string += """
      stepConfiguratorPrevious
      stepCheckConfigureAccountingForm
      stepConfiguratorPrevious
      stepCheckConfigureMultipleUserAccountForm
      stepConfiguratorPrevious
      stepCheckConfigureUserAccountNumberForm
      stepConfiguratorPrevious
      stepCleanUpRequest
      stepCheckConfigureOrganisationForm
      stepSetupOrganisationConfiguratorItem
      stepConfiguratorNext
      stepCheckConfigureUserAccountNumberForm
      stepSetupUserAccounNumberSix
      stepConfiguratorNext
      stepCheckConfigureMultipleUserAccountForm
      stepSetupMultipleUserAccountSix
      stepConfiguratorNext
      stepCheckConfigureAccountingForm
      stepSetupAccountingConfiguration
      stepConfiguratorNext
      stepTic
      stepCheckConfigurePreferenceForm
    """
    # check next Configure Installation form
    sequence_string += """
      stepSetupPreferenceConfiguration
      stepConfiguratorNext
      stepTic
      stepCheckPreferenceConfigurationItemList
      stepCheckConfigureInstallationForm
      stepSetupInstallConfiguration
      stepConfiguratorNext
      stepCheckInstallConfiguration
      stepTic
      stepStartConfigurationInstallation
      stepTic
      stepCheckInstanceIsConfiguredBrazil
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

#  def exportConfiguratorBusinessTemplate(self):
#    """ """
#    # we save this configuration business template for another test
#    outfile_path = os.path.join(os.environ['INSTANCE_HOME'],
#                        'configurator_express_configuration.bt5')
#    outfile = file(outfile_path, 'w')
#    try:
#      outfile.write(server_response['filedata'][-1])
#      print 'Saved generated business template as', outfile_path
#    finally:
#      outfile.close()

import unittest
def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestConsultingConfiguratorWorkflow))
  suite.addTest(unittest.makeSuite(TestStandardConfiguratorWorkflow))
  return suite
