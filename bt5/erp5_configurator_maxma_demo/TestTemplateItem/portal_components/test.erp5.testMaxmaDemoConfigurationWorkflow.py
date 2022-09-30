##############################################################################
# Copyright (c) 2011 Nexedi SA and Contributors. All Rights Reserved.
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

from erp5.component.module.ConfiguratorTestMixin import \
    TestLiveConfiguratorWorkflowMixin
from Products.ERP5Type.tests.Sequence import SequenceList
from unittest import expectedFailure

class TestMaxmaDemoConfiguratorWorkflow(TestLiveConfiguratorWorkflowMixin):
  """
    Configurator Mixin Class
  """
  # The list of standard business templates that the configurator should force
  # to install
  user_reference = "demo"
  standard_bt5_list = ('erp5_simulation',
                       'erp5_dhtml_style',
                       'erp5_jquery',
                       'erp5_jquery_ui',
                       'erp5_ingestion_mysql_innodb_catalog',
                       'erp5_ingestion',
                       'erp5_web',
                       'erp5_dms',
                       'erp5_crm',
                       'erp5_pdm',
                       'erp5_trade',
                       'erp5_knowledge_pad',
                       'erp5_accounting',
                       'erp5_tax_resource',
                       'erp5_discount_resource',
                       'erp5_invoicing',
                       'erp5_configurator_standard_categories',
                       'erp5_trade_knowledge_pad',
                       'erp5_crm_knowledge_pad',
                       'erp5_simulation_test',
                       'erp5_simplified_invoicing',
                       'erp5_ods_style',
                       'erp5_odt_style',
                       'erp5_ooo_import',
                       'erp5_accounting_l10n_fr',
                       'erp5_l10n_fr',
                       'erp5_l10n_pt-BR',
                       'erp5_demo_maxma_rule')

  def stepCreateBusinessConfiguration(self, sequence=None,\
                   sequence_list=None, **kw):
    """ Create one Business Configuration """
    module = self.portal.business_configuration_module
    business_configuration = module.newContent(
                               portal_type="Business Configuration",
                               title='Test Configurator Maxma Demo Workflow')
    next_dict = {}
    sequence.edit(business_configuration=business_configuration,
                  next_dict=next_dict)

  def stepCheckConfigureInstallationForm(self, sequence=None,\
                    sequence_list=None, **kw):
    """ Check the installation form """
    response_dict = sequence.get("response_dict")
    # configuration is finished. We are at the Install state.
    # On maxma demo, installation is the first slide.
    self.assertEqual('show', response_dict['command'])
    self.assertEqual('Install', response_dict['next'])

  def stepSetMaxmaDemoWorkflow(self, sequence=None, sequence_list=None, **kw):
    """ Set Consulting Workflow into Business Configuration """
    business_configuration = sequence.get("business_configuration")
    self.setBusinessConfigurationWorkflow(business_configuration,
                          "portal_workflow/maxma_demo_configuration_workflow")


  def stepViewCreatedPersons(self, sequence=None, sequence_list=None, **kw):
    self.loginByUserName(user_name='test_configurator_user')
    person_list = self.portal.person_module.searchFolder()
    self.assertNotEquals(0, len(person_list))

    for entity in person_list:
      for username in self.all_username_list:
        self.failUnlessUserCanAccessDocument(username, entity)
        self.failUnlessUserCanViewDocument(username, entity)

  def stepViewCreatedOrganisations(self, sequence=None, sequence_list=None, **kw):
    self.loginByUserName(user_name='test_configurator_user')
    organisation_list = self.portal.organisation_module.searchFolder()
    self.assertNotEquals(0, len(organisation_list))

    for entity in organisation_list:
      for username in self.all_username_list:
        self.failUnlessUserCanAccessDocument(username, entity)
        self.failUnlessUserCanViewDocument(username, entity)

  def stepViewCreatedAssignemnts(self, sequence=None, sequence_list=None, **kw):
    self.loginByUserName(user_name='test_configurator_user')
    person_list = self.portal_person_module.searchFolder()
    self.assertNotEquals(0, len(person_list))

    for person in person_list:
      for assignment in person.contentValues(portal_type='Assignment'):
        for username in self.all_username_list:
          self.failUnlessUserCanAccessDocument(username, assignment)
          self.failUnlessUserCanViewDocument(username, assignment)


  def stepCheckMaxmaDemoSampleObjectList(self, sequence=None, sequence_list=None, **kw):
    """ Check if objects are placed into the appropriate state """

    # Check Gadgets
    for gadget in self.portal.portal_gadgets.searchFolder():
      self.assertEqual('public', gadget.getValidationState(),
                        "%s is not public but %s" % (gadget.getRelativeUrl(),
                                                     gadget.getValidationState()))
      gadget.Base_checkConsistency()

    # Check if demo user is working.
    user = self.portal.portal_catalog.getResultValue(portal_type="Person",
    reference=self.user_reference)

    self.assertNotEquals(user.Person_getAvailableAssignmentValueList(), [])
    self.assertEqual(user.getTitle(), "Jack Vale")
    self.assertEqual(user.getValidationState(), "validated")
    self.assertEqual(user.getSubordination(),
                          'organisation_module/myorganisation')
    self.assertEqual(user.getSubordinationTitle(), "Maxma Co")

  ### STEPS
  DEFAULT_SEQUENCE_LIST = """
      stepCreateBusinessConfiguration
      stepTic
      stepSetMaxmaDemoWorkflow
      stepTic
      stepConfiguratorNext
      stepTic
      stepCheckBT5ConfiguratorItem
      stepCheckConfigureInstallationForm
      stepSetupInstallConfiguration
      stepConfiguratorNext
      stepTic
      stepCheckInstallConfiguration
      stepStartConfigurationInstallation
      stepTic
      stepCheckInstanceIsConfigured%(country)s
      stepCheckMaxmaDemoSampleObjectList
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
      """

  # still in developing
  @expectedFailure
  def test_maxma_demo_workflow(self):
    """ Test the consulting workflow configuration"""
    self.all_username_list = ["demo"]
    self.accountant_username_list = self.all_username_list
    self.sales_and_purchase_username_list = self.all_username_list
    self.warehouse_username_list = self.all_username_list
    self.simple_username_list = self.all_username_list
    self.restricted_security = 0
    sequence_list = SequenceList()
    sequence_string = self.DEFAULT_SEQUENCE_LIST % dict(country='France')
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

import unittest
def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestMaxmaDemoConfiguratorWorkflow))
  return suite
