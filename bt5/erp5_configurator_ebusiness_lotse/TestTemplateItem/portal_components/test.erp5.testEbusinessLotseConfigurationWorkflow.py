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

from erp5.component.test.testStandardConfigurationWorkflow import \
    StandardConfigurationMixin
from erp5.component.module.ConfiguratorTestMixin import \
                                             TestLiveConfiguratorWorkflowMixin
from Products.ERP5Type.tests.Sequence import SequenceList

class TestEbusinessLotseConfigurationWorkflow(StandardConfigurationMixin):
  """
    Test Live eBusiness Lotse Configuration Workflow
  """

  def getSampleOrganisation(self):
    return self.portal.portal_catalog.getResultValue(portal_type="Organisation",
                                                     title="ISIH GmbH")

  def getSampleBankAccount(self):
    return self.portal.portal_catalog.getResultValue(portal_type="Bank Account",
                                                     title="ISIH Bank")

  def getSampleBusinessProcess(self):
    return self.portal.portal_catalog.getResultValue(
                                      portal_type="Business Process",
                                      reference="default_erp5_business_process")

  def stepCreateBusinessConfiguration(self, sequence=None,\
                   sequence_list=None, **kw):
    """ Create one Business Configuration """
    module = self.portal.business_configuration_module
    business_configuration = module.newContent(
                            portal_type="Business Configuration",
                            title='Test Configurator eBusiness Lotse Workflow')
    next_dict = {}
    sequence.edit(business_configuration=business_configuration,
                  next_dict=next_dict)

  def stepCheckConfigureInstallationForm(self, sequence=None,\
                    sequence_list=None, **kw):
    """ Check the installation form """
    response_dict = sequence.get("response_dict")
    # configuration is finished. We are at the Install state.
    # On eBusiness Lotse, installation is the first slide.
    self.assertEqual('show', response_dict['command'])
    self.assertEqual('Install', response_dict['next'])

  def stepSetEbusinessLotseWorkflow(self, sequence=None, sequence_list=None, **kw):
    """ Set Consulting Workflow into Business Configuration """
    business_configuration = sequence.get("business_configuration")
    self.setBusinessConfigurationWorkflow(business_configuration,
                      "portal_workflow/ebusiness_lotse_configuration_workflow")


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

  def stepCheckPerson(self, sequence=None, sequence_list=None, **kw):
    """ Check if person is created in appropiate state """
    person = self.portal.portal_catalog.getResultValue(portal_type="Person",
    reference="user")

    self.assertNotEquals(person.Person_getAvailableAssignmentValueList(), [])
    self.assertEqual(person.getTitle(), "Herr Admin")
    self.assertEqual(person.getDefaultEmailText(), 'herradmin@isih-gmbh.de')
    self.assertEqual(person.getFunction(), 'company')
    self.assertEqual(person.getValidationState(), "validated")

  def stepCheckOrganisation(self, sequence=None, sequence_list=None, **kw):
    """ Check if organisation is created in appropiate state """
    organisation = self.getSampleOrganisation()

    self.assertEqual(organisation.getTitle(), "ISIH GmbH")
    self.assertEqual(organisation.getDefaultEmailText(), "mail@isih-gmbh.de")
    self.assertEqual(organisation.getDefaultTelephoneText(), "+(0)555-5555")
    self.assertEqual(organisation.getDefaultAddressStreetAddress(), "Musterstr. 1")
    self.assertEqual(organisation.getDefaultAddressZipCode(), "00001")
    self.assertEqual(organisation.getDefaultAddressCity(), "Dresden")
    self.assertEqual(organisation.getDefaultAddressRegion(),
                                               "europe/western_europe/germany")
    self.assertEqual(organisation.getPriceCurrency(), "currency_module/EUR")
    self.assertEqual(organisation.getValidationState(), "validated")

  def stepCheckBankAccount(self, sequence=None, sequence_list=None, **kw):
    """ Check if bank account is created in appropiate state """
    organisation = self.getSampleOrganisation()
    bank_account = self.getSampleBankAccount()

    self.assertEqual(bank_account.aq_parent, organisation)
    self.assertEqual(bank_account.getTitle(), "ISIH Bank")
    self.assertEqual(bank_account.getValidationState(), "validated")

  def stepCheckPurchaseTradeCondition(self, sequence=None, sequence_list=None, **kw):
    """ Check if purchase trade condition is created in appropiate state """
    trade_condition = self.portal.portal_catalog.getResultValue(
                                portal_type="Purchase Trade Condition",
                                reference="PTC-General")
    organisation = self.getSampleOrganisation()
    bank_account = self.getSampleBankAccount()
    business_process = self.getSampleBusinessProcess()

    self.assertEqual(trade_condition.getTitle(), "General Purchase Trade Condition")
    self.assertEqual(trade_condition.getSpecialiseValue(), business_process)
    self.assertEqual(trade_condition.getDestinationValue(), organisation)
    self.assertEqual(trade_condition.getDestinationSectionValue(), organisation)
    self.assertEqual(trade_condition.getDestinationDecisionValue(), organisation)
    self.assertEqual(trade_condition.getDestinationAdministrationValue(), organisation)
    self.assertEqual(trade_condition.getDestinationPaymentValue(), bank_account)
    self.assertEqual(trade_condition.getPriceCurrency(), "currency_module/EUR")
    self.assertEqual(trade_condition.getValidationState(), "validated")

  def stepCheckSaleTradeCondition(self, sequence=None, sequence_list=None, **kw):
    """ Check if sale trade condition is created in appropiate state """
    trade_condition = self.portal.portal_catalog.getResultValue(
                                portal_type="Sale Trade Condition",
                                reference="STC-General")
    organisation = self.getSampleOrganisation()
    bank_account = self.getSampleBankAccount()
    business_process = self.getSampleBusinessProcess()

    self.assertEqual(trade_condition.getTitle(), "General Sale Trade Condition")
    self.assertEqual(trade_condition.getSpecialiseValue(), business_process)
    self.assertEqual(trade_condition.getSourceValue(), organisation)
    self.assertEqual(trade_condition.getSourceSectionValue(), organisation)
    self.assertEqual(trade_condition.getSourceDecisionValue(), organisation)
    self.assertEqual(trade_condition.getSourceAdministrationValue(), organisation)
    self.assertEqual(trade_condition.getSourcePaymentValue(), bank_account)
    self.assertEqual(trade_condition.getPriceCurrency(), "currency_module/EUR")
    self.assertEqual(trade_condition.getValidationState(), "validated")

  ### STEPS
  DEFAULT_SEQUENCE_LIST = """
      stepSetGermanyCase
      stepCreateBusinessConfiguration
      stepTic
      stepSetEbusinessLotseWorkflow
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
      stepCheckPerson
      stepCheckOrganisation
      stepCheckBankAccount
      stepCheckPurchaseTradeCondition
      stepCheckSaleTradeCondition
      """

  def afterSetUp(self):
    TestLiveConfiguratorWorkflowMixin.afterSetUp(self)
    self.all_username_list = ["user"]
    self.accountant_username_list = self.all_username_list
    self.sales_and_purchase_username_list = self.all_username_list
    self.warehouse_username_list = self.all_username_list
    self.simple_username_list = self.all_username_list
    self.preference_group = 'group/my_group'
    self.user_list = [
    dict(
      field_your_first_name='Herr',
      field_your_last_name='Admin',
      field_your_reference='user',
      field_your_password='test',
      field_your_password_confirm='test',
      field_your_function='company',
      field_your_default_email_text='herradmin@isih-gmbh.de',
      field_your_default_telephone_text='',
    )]

  def test_ebusiness_lotse_workflow(self):
    """ Test the consulting workflow configuration"""
    sequence_list = SequenceList()
    sequence_string = self.DEFAULT_SEQUENCE_LIST % dict(country='Germany')
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

import unittest
def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestEbusinessLotseConfigurationWorkflow))
  return suite
