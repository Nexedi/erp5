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


from DateTime import DateTime
from Products.ERP5Type.tests.Sequence import SequenceList
from Products.ERP5Type.tests.ERP5TypeLiveTestCase import ERP5TypeLiveTestCase
from Products.ERP5Type.tests.SecurityTestCase import SecurityTestCase
from Products.ERP5Type.tests.backportUnittest import expectedFailure
from AccessControl import Unauthorized
from zLOG import LOG

class TestLiveStandardConfiguratorWorkflow(ERP5TypeLiveTestCase, SecurityTestCase):
  """
    Test Live Standard Configuration Workflow.
  """
  # The list of standard business templates that the configurator should force
  # to install
  standard_bt5_list = ('erp5_configurator_standard_categories',)

  DEFAULT_SEQUENCE_LIST = """
      stepCreateBusinessConfiguration 
      stepTic
      stepSetStandardWorkflow
      stepTic
      stepConfiguratorNext
      stepTic
      stepCheckBT5ConfiguratorItem
      stepCheckConfigureOrganisationForm
      stepSetupOrganisationConfiguratorItem%(country)s
      stepConfiguratorNext
      stepTic
      stepCheckConfigureUserAccountNumberForm
      stepCheckOrganisationConfiguratorItem%(country)s
      stepSetupUserAccounNumberSix
      stepConfiguratorNext
      stepTic
      stepCheckConfigureMultipleUserAccountForm
      stepSetupMultipleUserAccountSix
      stepConfiguratorNext
      stepTic
      stepCheckMultiplePersonConfigurationItem
      stepCheckConfigureAccountingForm
      stepSetupAccountingConfiguration%(country)s
      stepConfiguratorNext
      stepTic
      stepCheckAccountingConfigurationItemList%(country)s
      stepCheckConfigurePreferenceForm
      stepSetupPreferenceConfiguration%(country)s
      stepConfiguratorNext
      stepTic
      stepCheckPreferenceConfigurationItemList%(country)s
      stepCheckConfigureInstallationForm
      stepSetupInstallConfiguration
      stepConfiguratorNext
      stepCheckInstallConfiguration
      stepTic
      stepStartConfigurationInstallation
      stepTic
      stepCheckInstanceIsConfigured%(country)s
  """

  def afterSetUp(self):
    newId = self.portal.portal_ids.generateNewId
    id_group ='testConfiguratorStandardWorkflow'

    self.login(user_name='test_configurator_user')
    # XXX (lucas): The request is not clean between tests.
    # So, we need to force the test to use a clean REQUEST
    # Otherwise the next test will fail trying to validate the form,
    # because the REQUEST has data from the previous step/test.
    if getattr(self.app.REQUEST, 'default_other', None) is None:
      self.app.REQUEST.default_other = self.app.REQUEST.other.copy()
    else:
      self.stepCleanUpRequest()

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

    self.restricted_security = 0

    # information to know if a business template is a standard business
    # template or a custom one
    self.portal.portal_templates.updateRepositoryBusinessTemplateList(
                           ['http://www.erp5.org/dists/snapshot/bt5/'])

    # it is required by SecurityTestCase
    self.workflow_tool = self.portal.portal_workflow

  def stepCleanUpRequest(self, sequence=None, sequence_list=None, **kw):
    """ Restore clean up the request """
    self.app.REQUEST.other = self.app.REQUEST.default_other.copy()

  def stepCreateBusinessConfiguration(self,  sequence=None, sequence_list=None, **kw):
    """ Create one Business Configuration """
    module = self.portal.business_configuration_module
    business_configuration = module.newContent(
                               portal_type="Business Configuration",
                               title='Test Configurator Standard Workflow')
    next_dict = {}
    sequence.edit(business_configuration=business_configuration, 
                  next_dict=next_dict)

  def stepSetStandardWorkflow(self, sequence=None, sequence_list=None, **kw):
    """ Set Standard Workflow into Business Configuration """
    business_configuration = sequence.get("business_configuration")
    business_configuration.setResource("workflow_module/erp5_standard_workflow")

  # utility methods for things that are likely to change in the future
  def assertCurrentStep(self, step_title, server_response):
    """ Checks the current step title. """
    self.assertTrue(
      '<h2>%s</h2>' % step_title in server_response['data'],
      'Unable to guess current step title (expected:%s) in: \n%s' %
      (step_title, server_response))

  def stepConfiguratorNext(self, sequence=None, sequence_list=None, **kw):
    """ Go Next into Configuration """
    business_configuration = sequence.get("business_configuration")
    next_dict = sequence.get("next_dict")
    response_dict = self.portal.portal_configurator._next(
                            business_configuration, next_dict)
    sequence.edit(response_dict=response_dict)
    
  def stepConfiguratorPrevious(self, sequence=None, sequence_list=None, **kw):
    """ Go to the previous form. """
    business_configuration = sequence.get("business_configuration")
    next_dict = sequence.get("next_dict")
    response_dict = self.portal.portal_configurator._previous(
                            business_configuration, next_dict)
    sequence.edit(response_dict=response_dict)

  def stepCheckConfigureOrganisationForm(self, sequence=None, sequence_list=None, **kw):
    """ Check if Confire Organisation step was showed """
    response_dict = sequence.get("response_dict")
    if 'command' in response_dict:
      self.assertEquals('show', response_dict['command'])
    self.assertEquals(None, response_dict['previous'])
    self.assertEquals('Configure organisation', response_dict['next'])
    self.assertCurrentStep('Your organisation', response_dict)

  def _stepSetupOrganisationConfiguratorItem(self, sequence=None, sequence_list=None, **kw):
    """ Create one Organisation """
    next_dict = dict(
        field_your_title='My Organisation',
        field_your_default_email_text='me@example.com',
        field_your_default_telephone_text='01234567890',
        field_your_default_address_street_address='.',
        field_your_default_address_zip_code='59000')
    next_dict.update(**kw)
    sequence.edit(next_dict=next_dict)

  def stepSetupOrganisationConfiguratorItemFrance(self, sequence=None, sequence_list=None, **kw):
    """ Create one Organisation with French information """
    self._stepSetupOrganisationConfiguratorItem(
        sequence=sequence,
        sequence_list=sequence_list,
        field_your_default_address_city='LILLE',
        field_your_default_address_region='europe/western_europe/france')

  def stepSetupOrganisationConfiguratorItemBrazil(self, sequence=None, sequence_list=None, **kw):
    """ Create one Organisation with Brazilian information"""
    self._stepSetupOrganisationConfiguratorItem(
        sequence=sequence,
        sequence_list=sequence_list,
        field_your_default_address_city='CAMPOS',
        field_your_default_address_region='americas/south_america/brazil')

  def stepCheckConfigureUserAccountNumberForm(self, sequence=None, sequence_list=None, **kw):
    """ Check if Configure Organisation step was showed """
    response_dict = sequence.get("response_dict")
    if 'command' in response_dict:
      self.assertEquals('show', response_dict['command'])
    #import pdb; pdb.set_trace()
    self.assertEquals('Configure user accounts number', response_dict['next'])
    self.assertEquals('Previous', response_dict['previous'])
    self.assertCurrentStep('Number of user accounts', response_dict)

  def stepCheckBT5ConfiguratorItem(self, sequence=None, sequence_list=None, **kw):
    """ Check if the Configuration Item list is correct """
    business_configuration = sequence.get("business_configuration")
    # second one: install some standard business templates
    standard_bt5_config_save = business_configuration['1']
    self.assertEquals(len(self.standard_bt5_list),
          len(standard_bt5_config_save.contentValues(
                  portal_type='Standard BT5 Configurator Item')))
    self.assertEquals(
      set(self.standard_bt5_list),
      set([x.bt5_id for x in standard_bt5_config_save.contentValues()]))

    # third one: we create a business template to store customer configuration
    custom_bt5_config_save = business_configuration['2']
    custom_bt5_config_item = custom_bt5_config_save['1']
    self.assertEquals(custom_bt5_config_item.getPortalType(),
                      'Customer BT5 Configurator Item')

    self.assertEquals(custom_bt5_config_item.bt5_id,
          '_'.join(business_configuration.getTitle().strip().lower().split()))

  def _stepCheckOrganisationConfiguratorItem(self, business_configuration,
                                                   default_address_city,
                                                   default_address_region):
    """ Check if configuration key was created fine """
    # last one: a step for what the client selected
    organisation_config_save = business_configuration['3']
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

    self.assertEquals(3, len(business_configuration.contentValues(portal_type="Configuration Save")))
    self.assertEquals(0, len(business_configuration.contentValues(portal_type="Link")))

  def stepCheckOrganisationConfiguratorItemFrance(self, sequence=None, sequence_list=None, **kw):
    """ Check if configuration key was created fine """
    self._stepCheckOrganisationConfiguratorItem(
                business_configuration=sequence.get('business_configuration'),
                default_address_city='LILLE',
                default_address_region='europe/western_europe/france')

  def stepCheckOrganisationConfiguratorItemBrazil(self, sequence=None, sequence_list=None, **kw):
    """ Check if configuration key was created fine """
    self._stepCheckOrganisationConfiguratorItem(
                business_configuration=sequence.get('business_configuration'),
                default_address_city='CAMPOS',
                default_address_region='americas/south_america/brazil')

  def stepSetupUserAccounNumberSix(self, sequence=None, sequence_list=None, **kw):
    """ Create one more user account """
    next_dict = dict(field_your_company_employees_number='6', )
    sequence.edit(next_dict=next_dict)

  def stepCheckConfigureMultipleUserAccountForm(self, sequence=None, sequence_list=None, **kw):
    """ Check the multiple user account form """
    response_dict = sequence.get("response_dict")
    if 'command' in response_dict:
      self.assertEquals('show', response_dict['command'])
    self.assertEquals('Previous', response_dict['previous'])
    self.assertEquals('Configure user accounts', response_dict['next'])
    self.assertCurrentStep('User accounts configuration', response_dict)

  def stepSetupMultipleUserAccountSix(self, sequence=None, sequence_list=None, **kw):
    """ Create multiple user account """
    # create our 6 users:
    user_list = [
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
    next_dict = {}
    for user in user_list:
      for k, v in user.items():
        next_dict.setdefault(k, []).append(v)
    sequence.edit(next_dict=next_dict)

  def stepCheckMultiplePersonConfigurationItem(self, sequence=None, sequence_list=None, **kw):
    """ 
      Check if multiple Person Configuration Item of the Business
      Configuration have been created successfully.
    """
    business_configuration = sequence.get("business_configuration")

    person_number_business_configuration_save = business_configuration['4']
    self.assertEquals(6,
        person_number_business_configuration_save.company_employees_number)
    self.assertEquals(0,
        len(person_number_business_configuration_save.contentValues()))
    person_business_configuration_save = business_configuration['5']
    self.assertEquals(6, # we have 6 users
        len(person_business_configuration_save.contentValues()))
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

  def stepCheckConfigureAccountingForm(self, sequence=None, sequence_list=None, **kw):
    """ Check the accounting form configuration. """
    response_dict = sequence.get("response_dict")
    if 'command' in response_dict:
      self.assertEquals('show', response_dict['command']) 
    self.assertEquals('Previous', response_dict['previous'])
    self.assertEquals('Configure accounting', response_dict['next'])
    self.assertCurrentStep('Accounting', response_dict)

  def _stepSetupAccountingConfiguration(self, accounting_plan):
    """ Setup up the accounting configuration """
    return dict(field_your_accounting_plan=accounting_plan,
                subfield_field_your_period_start_date_year='2008',
                subfield_field_your_period_start_date_month='01',
                subfield_field_your_period_start_date_day='01',
                subfield_field_your_period_stop_date_year='2008',
                subfield_field_your_period_stop_date_month='12',
                subfield_field_your_period_stop_date_day='31',
                field_your_period_title='2008',
           )


  def stepSetupAccountingConfigurationFrance(self, sequence=None, sequence_list=None, **kw):
    """ Setup up the French accounting configuration """
    next_dict = self._stepSetupAccountingConfiguration(accounting_plan='fr')
    sequence.edit(next_dict=next_dict)

  def stepSetupAccountingConfigurationBrazil(self, sequence=None, sequence_list=None, **kw):
    """ Setup up the Brazilian accounting configuration """
    next_dict = self._stepSetupAccountingConfiguration(accounting_plan='br')
    sequence.edit(next_dict=next_dict)

  def stepCheckConfigurePreferenceForm(self, sequence=None, sequence_list=None, **kw):
    """ Check the preference form """
    response_dict = sequence.get("response_dict")
    if 'command' in response_dict:
      self.assertEquals('show', response_dict['command'])
    self.assertEquals('Previous', response_dict['previous'])
    self.assertEquals('Configure preferences', response_dict['next'])
    self.assertCurrentStep('Application preferences', response_dict)

  def _stepSetupPreferenceConfiguration(self, price_currency, lang):
    """ Setup the preference configuration """
    return dict(field_your_price_currency=price_currency,
                field_your_preferred_date_order='dmy',
                field_your_lang=lang,
                default_field_your_lang=1
           )


  def stepSetupPreferenceConfigurationFrance(self, sequence=None, sequence_list=None, **kw):
    """ Setup the French preference configuration """
    next_dict = self._stepSetupPreferenceConfiguration(
                                               price_currency='EUR;0.01;Euro',
                                               lang='erp5_l10n_fr',
                )
    sequence.edit(next_dict=next_dict)

  def stepSetupPreferenceConfigurationBrazil(self, sequence=None, sequence_list=None, **kw):
    """ Setup the Brazil preference configuration """
    next_dict = self._stepSetupPreferenceConfiguration(
                                      price_currency='BRL;0.01;Brazilian Real',
                                      lang='erp5_l10n_pt-BR',
                )
    sequence.edit(next_dict=next_dict)

  def _stepCheckAccountingConfigurationItemList(self, business_configuration,
                                                      bt5_id,
                                                      accounting_transaction_gap,
                                                      gap):
    """ Check the French accounting configuration item list """
    # 1. the localization business template
    accounting_business_configuration_save = business_configuration['6']
    bt5_business_configuration_item =\
          accounting_business_configuration_save['1']
    self.assertEquals('Standard BT5 Configurator Item',
            bt5_business_configuration_item.getPortalType())
    self.assertEquals(bt5_id, bt5_business_configuration_item.bt5_id)

    # 2. a preference
    preference_buisiness_configurator_item_list =\
       accounting_business_configuration_save.contentValues(
           portal_type='Preference Configurator Item')
    self.assertEquals(1, len(preference_buisiness_configurator_item_list))
    preference_buisiness_configurator_item = \
        preference_buisiness_configurator_item_list[0]
    self.assertEquals(accounting_transaction_gap,
           preference_buisiness_configurator_item.getProperty(
              'preferred_accounting_transaction_gap'))
    self.assertEquals('group/my_group',
           preference_buisiness_configurator_item.getProperty(
              'preferred_accounting_transaction_section_category'))
    
    # 3. some pre-configured accounts
    account_business_configuration_item =\
          accounting_business_configuration_save['2']
    self.assertEquals('Account Configurator Item',
            account_business_configuration_item.getPortalType())
    self.assertEquals('capital',
        getattr(account_business_configuration_item, 'account_id', 'not set'))
    self.assertEquals('equity',
            account_business_configuration_item.getAccountType())
    self.assertEquals(gap, account_business_configuration_item.getGap())
    self.assertEquals('equity/share_capital',
            account_business_configuration_item.getFinancialSection())

    # title is translated here
    self.assertEquals('Capital',
            account_business_configuration_item.getTitle())

    # 4. An accounting period configuration item
    accounting_period_configuration_item = \
        accounting_business_configuration_save['14']
    # this ['14'] will break when we'll add more accounts
    self.assertEquals('Accounting Period Configurator Item',
        accounting_period_configuration_item.getPortalType())
    
    self.assertEquals(DateTime(2008, 1, 1),
        accounting_period_configuration_item.getStartDate())
    self.assertEquals(DateTime(2008, 12, 31),
        accounting_period_configuration_item.getStopDate())
    self.assertEquals('2008',
        accounting_period_configuration_item.getShortTitle())

  def stepCheckAccountingConfigurationItemListFrance(self, sequence=None, sequence_list=None, **kw):
    """ """
    self._stepCheckAccountingConfigurationItemList(
                business_configuration=sequence.get("business_configuration"),
                bt5_id='erp5_accounting_l10n_fr',
                accounting_transaction_gap='gap/fr/pcg',
                gap='fr/pcg/1/10/101')

  def stepCheckAccountingConfigurationItemListBrazil(self, sequence=None, sequence_list=None, **kw):
    """ """
    self._stepCheckAccountingConfigurationItemList(
                business_configuration=sequence.get("business_configuration"),
                bt5_id='erp5_accounting_l10n_br_extend',
                accounting_transaction_gap='gap/br/pcg',
                gap='br/pcg/2/2.4/2.4.1/2.4.1.01')

  def _stepCheckPreferenceConfigurationItemList(self, business_configuration,
                                                      currency_title,
                                                      currency_reference,
                                                      bt5_id):
    """
      Check the creation of:
      - Currency Configurator Item
      - Service Configurator Item
      - System Preference Configurator Item
      - Standard BT5 Configurator Item
    """
    # this created a currency
    preferences_business_configuration_save = business_configuration['7']
    currency_business_configuration_item =\
          preferences_business_configuration_save['1']
    self.assertEquals('Currency Configurator Item',
          currency_business_configuration_item.getPortalType())
    self.assertEquals(currency_title,
          currency_business_configuration_item.getTitle())
    self.assertEquals(0.01,
          currency_business_configuration_item.getBaseUnitQuantity())
    self.assertEquals(currency_reference,
          currency_business_configuration_item.getReference())
    # some services
    # TODO
    service_business_configuration_item =\
          preferences_business_configuration_save['2']
    self.assertEquals('Service Configurator Item',
                     service_business_configuration_item.getPortalType())
    # and a preference
    preference_business_configuration_item =\
          preferences_business_configuration_save['3']
    self.assertEquals('Preference Configurator Item',
        preference_business_configuration_item.getPortalType())
    # that uses the currency
    self.assertEquals('currency_module/%s' % currency_reference,
        preference_business_configuration_item.getProperty(
             'preferred_accounting_transaction_currency'))

    # system preferences
    system_pref_configurator_item =\
        preferences_business_configuration_save['4']
    self.assertEquals('System Preference Configurator Item',
        system_pref_configurator_item.getPortalType())

    # a standard bt5 for localisation
    bt5_business_configuration_item =\
          preferences_business_configuration_save['5']
    self.assertEquals('Standard BT5 Configurator Item',
            bt5_business_configuration_item.getPortalType())
    self.assertEquals(bt5_id,
            bt5_business_configuration_item.bt5_id)

  def stepCheckPreferenceConfigurationItemListFrance(self, sequence=None, sequence_list=None, **kw):
    """
      Check the creation of:
      - Currency Configurator Item
      - Service Configurator Item
      - System Preference Configurator Item
      - Standard BT5 Configurator Item
    """
    self._stepCheckPreferenceConfigurationItemList(
                business_configuration=sequence.get("business_configuration"),
                currency_title='Euro',
                currency_reference='EUR',
                bt5_id='erp5_l10n_fr')

  def stepCheckPreferenceConfigurationItemListBrazil(self, sequence=None, sequence_list=None, **kw):
    """
      Check the creation of:
      - Currency Configurator Item
      - Service Configurator Item
      - System Preference Configurator Item
      - Standard BT5 Configurator Item
    """
    self._stepCheckPreferenceConfigurationItemList(
                business_configuration=sequence.get("business_configuration"),
                currency_title='Brazilian Real',
                currency_reference='BRL',
                bt5_id='erp5_l10n_pt-BR')

  def stepCheckConfigureInstallationForm(self, sequence=None, sequence_list=None, **kw):
    """ Check the installation form """
    response_dict = sequence.get("response_dict")
    # configuration is finished. We are at the Install state.
    self.assertEquals('show', response_dict['command'])
    self.assertEquals('Previous', response_dict['previous'])
    self.assertEquals('Install', response_dict['next'])

    self.assertCurrentStep('TioLive installation', response_dict)

  def stepSetupInstallConfiguration(self, sequence=None, sequence_list=None, **kw):
    """ Install the Configuration """
    next_dict = {}
    sequence.edit(next_dict=next_dict)

  def stepCheckInstallConfiguration(self, sequence=None, sequence_list=None, **kw):
    """ Check the installation of the configuration """
    response_dict = sequence.get("response_dict")
    self.assertEquals('install', response_dict['command'])

  def _stepCheckInstanceIsConfigured(self, business_configuration, bt5_tuple):
    """ Check if the instance is configured with proper business templates """
    # XXX FIXME (lucas): it should be a property of business configuration
    bc_id = '_'.join(business_configuration.getTitle().strip().lower().split())

    # check if bt5 are installed.
    bt5_title_list = self.portal.portal_templates.getInstalledBusinessTemplateTitleList()
    expected_list = self.standard_bt5_list + bt5_tuple
    self.assertEquals([i for i in expected_list if i not in bt5_title_list], [])

    self.assertTrue(bc_id in bt5_title_list)

    # check for links
    link_list = business_configuration.searchFolder(portal_type="Link")
    # XXX FIXME Too poor check, it should verify if links are correnct.
    self.assertEquals(2, len(link_list))

    # check for links
    file_list = business_configuration.searchFolder(portal_type="File")
    # XXX FIXME Too poor check, it should verify if file are correnct.
    self.assertEquals(2, len(file_list))
    file_title_list = ('%s_copy.bt5' % self.standard_bt5_list[0],
                       '%s' % bc_id,)
    self.assertSameSet(file_title_list, [f.getTitle() for f in file_list])

  def stepCheckInstanceIsConfiguredFrance(self, sequence=None,  sequence_list=None, **kw):
    """ Check if the instance is configured with French business templates """
    self._stepCheckInstanceIsConfigured(
                business_configuration=sequence.get('business_configuration'),
                bt5_tuple=('erp5_accounting_l10n_fr', 'erp5_l10n_fr',))

  def stepCheckInstanceIsConfiguredBrazil(self, sequence=None,  sequence_list=None, **kw):
    """ Check if the instance is configured with Brazil business templates """
    self._stepCheckInstanceIsConfigured(
             business_configuration=sequence.get('business_configuration'),
             bt5_tuple=('erp5_accounting_l10n_br_extend', 'erp5_l10n_pt-BR',))

  def stepStartConfigurationInstallation(self, sequence=None, sequence_list=None, **kw):
    """ Starts the installation """
    business_configuration = sequence.get("business_configuration")
    self.portal.portal_configurator.startInstallation(
         business_configuration, REQUEST=self.portal.REQUEST)

  ##########################################
  # testExpressConfigurationInstance
  #########################################
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
      self.assertNotEquals(len(assignment_list), assignment_list)
      for assignment in assignment_list:
        self.assertEquals('open', assignment.getValidationState())
        self.assertNotEquals(None, assignment.getStartDate())
        self.assertNotEquals(None, assignment.getStopDate())
        self.assertTrue(assignment.getStopDate() > assignment.getStartDate())
        assignment.Base_checkConsistency()

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

  def stepCheckValidCurrencyList(self, sequence=None, sequence_list=None, **kw):
    """
      Check if after configuration the Currency objects are validated.
    """
    business_configuration = sequence.get("business_configuration")
    currency_list = self.getBusinessConfigurationObjectList(business_configuration, 'Currency')
    self.assertNotEquals(len(currency_list), 0)
    for currency in currency_list:
      # XXX FIXME: should the currency be validated by After Configuration Script?
      # On tiolive it is not validated, is there any reason?
      # self.assertEquals('validated', currency.getValidationState())
      currency.Base_checkConsistency()

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
    pref = self.portal.portal_preferences
    business_configuration = sequence.get("business_configuration")
    bt5_object = business_configuration.getSpecialiseValue()
    preference_list = bt5_object.getTemplatePreferenceList()
    self.assertEquals(len(preference_list), 2)

    organisation_list = self.getBusinessConfigurationObjectList(business_configuration, 'Organisation')
    self.assertNotEquals(len(organisation_list), 0)
    organisation_id = organisation_list[0].getId()

    # ui
    self.assertEquals('dmy', pref.getPreferredDateOrder())
    self.assertEquals('ODT', pref.getPreferredReportStyle())
    self.assertEquals('pdf', pref.getPreferredReportFormat())
    self.assertEquals(10, pref.getPreferredMoneyQuantityFieldWidth())
    # XXX FIXME (lucas): oood and oood port should be defined
    # on Business Configuration
    self.assertEquals('oood', pref.getPreferredOoodocServerAddress())
    self.assertEquals(8008, pref.getPreferredOoodocServerPortNumber())

    # accounting
    self.assertEquals('currency_module/EUR',
                      pref.getPreferredAccountingTransactionCurrency())
    self.assertEquals('gap/fr/pcg',
                      pref.getPreferredAccountingTransactionGap())
    self.assertEquals('group/my_group', 
                  pref.getPreferredAccountingTransactionSectionCategory())
    self.assertEquals('organisation_module/%s' % organisation_id,
                      pref.getPreferredAccountingTransactionSourceSection())
    self.assertEquals(pref.getPreferredSectionCategory(),
                      'group/my_group')
    self.assertEquals('organisation_module/%s' % organisation_id,
                      pref.getPreferredSection())
    self.assertEquals(['delivered', 'stopped'],
                  pref.getPreferredAccountingTransactionSimulationStateList())

    # trade
    self.assertEquals(['supplier'], pref.getPreferredSupplierRoleList())
    self.assertEquals(['client'], pref.getPreferredClientRoleList())
    self.assertEquals(['trade/sale'], pref.getPreferredSaleUseList())
    self.assertEquals(['trade/purchase'], pref.getPreferredPurchaseUseList())
    self.assertEquals(['trade/container'], pref.getPreferredPackingUseList())

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
    self.assertEquals('Trade',
        self.portal.discount_module.getBusinessApplicationTitle())
    self.assertEquals('Trade',
        self.portal.tax_module.getBusinessApplicationTitle())
    self.assertEquals(set([self.portal.sale_order_module,
                       self.portal.purchase_order_module,
                       self.portal.sale_trade_condition_module,
                       self.portal.purchase_trade_condition_module,
                       self.portal.sale_packing_list_module,
                       self.portal.purchase_packing_list_module,
                       self.portal.internal_packing_list_module,
                       self.portal.returned_sale_packing_list_module,
                       self.portal.inventory_module,
                       self.portal.discount_module,
                       self.portal.tax_module,
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

  def stepCheckRuleValidation(self, sequence=None, sequence_list=None, **kw):
    """
      Check if rule are validated 
    """
    business_configuration = sequence.get('business_configuration')
    rule_dict = self.portal.ERPSite_getConfiguratorSimulationRuleDict()
    self.assertEquals(9, len(rule_dict))
    for value in rule_dict.itervalues():
      portal_type = value.get('portal_type')
      result = self.getBusinessConfigurationObjectList(business_configuration, portal_type)
      self.assertNotEquals(0, len(result))
      for rule in result:
        self.assertEquals('validated', rule.getValidationState())

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
    get_transaction().commit()
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

  ###################################
  ## Test Configurator Security
  ###################################
  def stepViewAddGadget(self, sequence=None, sequence_list=None, **kw):
    """
       Test if gadget system is working.
    """
    for user_id in self.all_username_list:
      self._loginAsUser(user_id)
      knowledge_pad_module = self.portal.knowledge_pad_module
      knowledge_pad = knowledge_pad_module.newContent(portal_type='Knowledge Pad')
      self.failUnlessUserCanViewDocument(user_id, knowledge_pad)
      self.failUnlessUserCanAccessDocument(user_id, knowledge_pad)
      # only in visible state we can add Gadgets (i.e. Knowledge Boxes)
      knowledge_pad.visible()
      knowledge_box = knowledge_pad.newContent(portal_type='Knowledge Box')
      self.failUnlessUserCanViewDocument(user_id, knowledge_box)
      self.failUnlessUserCanAccessDocument(user_id, knowledge_box)

  def stepViewEventModule(self, sequence=None, sequence_list=None, **kw):
    """ Everybody can view events. """
    for username in self.all_username_list:
      self.failUnlessUserCanViewDocument(username, self.portal.event_module)
      self.failUnlessUserCanAccessDocument(username, self.portal.event_module)

  def stepAddEvent(self, sequence=None, sequence_list=None, **kw):
    """ Everybody can add events. """
    for username in self.all_username_list:
      self.failUnlessUserCanAddDocument(username, self.portal.event_module)
      for event_type in ('Visit', 'Web Message', 'Letter', 'Note',
                         'Phone Call', 'Mail Message', 'Fax Message'):
        self._loginAsUser(username)
        event = self.portal.event_module.newContent(portal_type=event_type)
        self.failUnlessUserCanViewDocument(username, event)
        self.failUnlessUserCanAccessDocument(username, event)

  def stepSentEventWorkflow(self, sequence=None, sequence_list=None, **kw):
    for event_type in ('Visit', 'Web Message', 'Letter', 'Note',
                       'Phone Call', 'Mail Message', 'Fax Message'):
      event = self.portal.event_module.newContent(portal_type=event_type)
      # in draft state, we can view & modify
      for username in self.all_username_list:
        self.failUnlessUserCanAccessDocument(username, event)
        self.failUnlessUserCanViewDocument(username, event)
        self.failUnlessUserCanModifyDocument(username, event)

      # everybody can cancel from draft
      for username in self.all_username_list:
        self.failUnlessUserCanPassWorkflowTransition(
                    username, 'cancel_action', event)

      # everybody can submit
      for username in self.all_username_list:
        self.failUnlessUserCanPassWorkflowTransition(
                    username, 'plan_action', event)

      event.plan()
      self.assertEquals('planned', event.getSimulationState())

      # everybody can request or post a submitted event
      for username in self.all_username_list:
        self.failUnlessUserCanPassWorkflowTransition(
                    username, 'order_action', event)
        self.failUnlessUserCanPassWorkflowTransition(
                    username, 'start_action', event)

      event.start()
      self.assertEquals('started', event.getSimulationState())

      # everybody can deliver a posted event
      for username in self.all_username_list:
        self.failUnlessUserCanPassWorkflowTransition(
                    username, 'deliver_action', event)
      event.deliver()
      self.assertEquals('delivered', event.getSimulationState())

  ## Accounts {{{
  def stepViewAccountModule(self, sequence=None, sequence_list=None, **kw):
    """ everybody can view and access account module. """
    for username in self.all_username_list:
      self.failUnlessUserCanViewDocument(username,
                              self.portal.account_module)
      self.failUnlessUserCanAccessDocument(username,
                              self.portal.account_module)

  def stepAddAccountModule(self, sequence=None, sequence_list=None, **kw):
    """ only accountants can add accounts. """
    for username in self.accountant_username_list:
      self.failUnlessUserCanAddDocument(username,
                    self.portal.account_module)
    if self.restricted_security:
      for username in (self.all_username_list - self.accountant_username_list):
        self.failIfUserCanAddDocument(username,
                      self.portal.account_module)

  def stepViewAccount(self, sequence=None, sequence_list=None, **kw):
    account = self.portal.account_module.newContent(
                                      portal_type='Account')
    # in draft state,
    self.assertEquals('draft', account.getValidationState())
    # everybody can see
    for username in self.all_username_list:
      self.failUnlessUserCanViewDocument(username, account)
      self.failUnlessUserCanAccessDocument(username, account)

    # only accountants can modify
    for username in self.accountant_username_list:
      self.failUnlessUserCanModifyDocument(username, account)
    if self.restricted_security:
      for username in (self.all_username_list - self.accountant_username_list):
        self.failIfUserCanModifyDocument(username, account)

    # only accountants can validate
    for username in self.accountant_username_list:
      self.failUnlessUserCanPassWorkflowTransition(
                  username, 'validate_action', account)
    if self.restricted_security:
      for username in (self.all_username_list - self.accountant_username_list):
        self.failIfUserCanPassWorkflowTransition(
                    username, 'validate_action', account)

    account.validate()
    self.assertEquals('validated', account.getValidationState())
    # in validated state, every body can view, but *nobody* can modify
    for username in self.all_username_list:
      self.failUnlessUserCanViewDocument(username, account)
      self.failUnlessUserCanAccessDocument(username, account)
      self.failIfUserCanModifyDocument(username, account)

    # only accountants can invalidate
    for username in self.accountant_username_list:
      self.failUnlessUserCanPassWorkflowTransition(
                  username, 'invalidate_action', account)
    if self.restricted_security:
      for username in (self.all_username_list - self.accountant_username_list):
        self.failIfUserCanPassWorkflowTransition(
                  username, 'invalidate_action', account)

    account.invalidate()
    self.assertEquals('invalidated', account.getValidationState())
    # back in invalidated state, everybody can view
    for username in self.all_username_list:
      self.failUnlessUserCanViewDocument(username, account)
      self.failUnlessUserCanAccessDocument(username, account)
    # only accountants can modify
    for username in self.accountant_username_list:
      self.failUnlessUserCanModifyDocument(username, account)
    if self.restricted_security:
      for username in (self.all_username_list - self.accountant_username_list):
        self.failIfUserCanModifyDocument(username, account)

    account.delete()
    # nobody can view delete object, but we can still access, for safety
    for username in self.all_username_list:
      self.failIfUserCanViewDocument(username, account)

  def stepCopyPasteAccount(self, sequence=None, sequence_list=None, **kw):
    # tests copy / pasting accounts from account module
    account = self.portal.account_module.newContent(
                                      portal_type='Account')
    # in draft state,
    self.assertEquals('draft', account.getValidationState())

    # everybody can see
    for username in self.all_username_list:
      self.failUnlessUserCanViewDocument(username, account)
      self.failUnlessUserCanAccessDocument(username, account)

  def stepViewEntityModules(self, sequence=None, sequence_list=None, **kw):
    # Everybody can view entities.
    for username in self.all_username_list:
      for module in [self.portal.person_module,
                     self.portal.organisation_module]:
        self.failUnlessUserCanViewDocument(username, module)
        self.failUnlessUserCanAccessDocument(username, module)

  def stepAddEntityModules(self, sequence=None, sequence_list=None, **kw):
    # Everybody can add entities.
    for username in self.all_username_list:
      for module in [self.portal.person_module,
                     self.portal.organisation_module]:
        self.failUnlessUserCanAddDocument(username, module)

  def stepCopyAndPastePerson(self, sequence=None, sequence_list=None, **kw):
    # copy & paste in person module
    person = self.portal.person_module.newContent(
                                    portal_type='Person')

    for username in self.all_username_list:
      self._loginAsUser(username)
      person.Base_createCloneDocument()

  def stepCopyAndPasteOrganisation(self, sequence=None, sequence_list=None, **kw):
    # copy & paste in organisation module
    organisation = self.portal.organisation_module.newContent(
                                    portal_type='Organisation')
    for username in self.all_username_list:
      self._loginAsUser(username)
      organisation.Base_createCloneDocument()

  def stepEntityWorkflow(self, sequence=None, sequence_list=None, **kw):
    for module in [self.portal.person_module,
                   self.portal.organisation_module]:
      entity = module.newContent()
      # in draft state, we can view, modify & add
      for username in self.all_username_list:
        self.failUnlessUserCanAccessDocument(username, entity)
        self.failUnlessUserCanViewDocument(username, entity)
        self.failUnlessUserCanModifyDocument(username, entity)
        self.failUnlessUserCanAddDocument(username, entity)

      # everybody can validate
      for username in self.all_username_list:
        self.failUnlessUserCanPassWorkflowTransition(
                    username, 'validate_action', entity)
      entity.validate()
      self.assertEquals('validated', entity.getValidationState())

      # in validated state, we can still modify
      for username in self.all_username_list:
        self.failUnlessUserCanAccessDocument(username, entity)
        self.failUnlessUserCanViewDocument(username, entity)
        self.failUnlessUserCanModifyDocument(username, entity)
        self.failUnlessUserCanAddDocument(username, entity)

      # and invalidate
      for username in self.all_username_list:
        self.failUnlessUserCanPassWorkflowTransition(
                    username, 'invalidate_action', entity)

  def stepViewCreatedPersons(self, sequence=None, sequence_list=None, **kw):
    self.login(user_name='test_configurator_user')
    business_configuration = sequence.get('business_configuration')
    person_list = self.getBusinessConfigurationObjectList(business_configuration, 'Person')
    self.assertNotEquals(0, len(person_list))

    for entity in person_list:
      for username in self.all_username_list:
        self.failUnlessUserCanAccessDocument(username, entity)
        self.failUnlessUserCanViewDocument(username, entity)

  def stepViewCreatedOrganisations(self, sequence=None, sequence_list=None, **kw):
    self.login(user_name='test_configurator_user')
    business_configuration = sequence.get('business_configuration')
    organisation_list = self.getBusinessConfigurationObjectList(business_configuration, 'Organisation')
    self.assertNotEquals(0, len(organisation_list))

    for entity in organisation_list:
      for username in self.all_username_list:
        self.failUnlessUserCanAccessDocument(username, entity)
        self.failUnlessUserCanViewDocument(username, entity)

  def stepViewCreatedAssignemnts(self, sequence=None, sequence_list=None, **kw):
    self.login(user_name='test_configurator_user')
    business_configuration = sequence.get('business_configuration')
    person_list = self.getBusinessConfigurationObjectList(business_configuration, 'Person')
    self.assertNotEquals(0, len(person_list))

    for person in person_list:
      found_one = 0
      for assignment in person.contentValues(portal_type='Assignment'):
        found_one = 1
        for username in self.all_username_list:
          self.failUnlessUserCanAccessDocument(username, assignment)
          self.failUnlessUserCanViewDocument(username, assignment)
      self.assertTrue(found_one, 'No assignment found in %s' % person)

  # }}}

  ## Accounting Periods {{{
  def stepAddAccoutingPeriod(self, sequence=None, sequence_list=None, **kw):
    # Everybody can add accounting periods.
    organisation = self.portal.organisation_module.newContent(
                          portal_type='Organisation')
    for username in self.all_username_list:
      self._loginAsUser(username)
      self.assertTrue('Accounting Period' in
            organisation.getVisibleAllowedContentTypeList())

  def stepValidatedAccountingPeriods(self, sequence=None, sequence_list=None, **kw):
    organisation = self.portal.organisation_module.newContent(
                          portal_type='Organisation')
    accounting_period = organisation.newContent(
                          portal_type='Accounting Period',
                          start_date=DateTime(2001, 01, 01),
                          stop_date=DateTime(2002, 12, 31))
    self.assertEquals(accounting_period.getSimulationState(), 'draft')

    # accountants can modify the period
    for username in self.accountant_username_list:
      self.failUnlessUserCanModifyDocument(username, accounting_period)
    # accountants can cancel the period
    for username in self.accountant_username_list:
      self.failUnlessUserCanPassWorkflowTransition(
          username, 'cancel_action', accounting_period)
    # accountants can start the period
    for username in self.accountant_username_list:
      self.failUnlessUserCanPassWorkflowTransition(
          username, 'start_action', accounting_period)

    # once the period is started, nobody can modify
    accounting_period.start()
    self.assertEquals('started', accounting_period.getSimulationState())
    for username in self.accountant_username_list:
      self.failIfUserCanModifyDocument(username, accounting_period)
    # accountants can still cancel the period
    for username in self.accountant_username_list:
      self.failUnlessUserCanPassWorkflowTransition(
          username, 'cancel_action', accounting_period)
    # accountants can stop the period
    for username in self.accountant_username_list:
      self.failUnlessUserCanPassWorkflowTransition(
          username, 'stop_action', accounting_period)
    # and reopen it
    accounting_period.stop()
    self.assertEquals('stopped', accounting_period.getSimulationState())
    for username in self.accountant_username_list:
      self.failUnlessUserCanPassWorkflowTransition(
          username, 'restart_action', accounting_period)
    # but only accounting manager can close it
    self.failUnlessUserCanPassWorkflowTransition(
          self.accounting_manager_reference, 'deliver_action', accounting_period)
    if self.restricted_security:
      self.failIfUserCanPassWorkflowTransition(
          self.accounting_agent_reference, 'deliver_action', accounting_period)

  # }}}

  ## Payment Nodes (Bank Account & Credit Cards) {{{
  def stepViewBankAccount(self, sequence=None, sequence_list=None, **kw):
    # Everybody can view bank accounts.
    entity = self.portal.organisation_module.newContent(
                                               portal_type='Organisation')
    bank_account = entity.newContent(portal_type='Bank Account')
    # everybody can view in draft ...
    self.assertEquals('draft', bank_account.getValidationState())
    for username in self.all_username_list:
      self.failUnlessUserCanViewDocument(username, bank_account)
      self.failUnlessUserCanAccessDocument(username, bank_account)
    # ... and validated states
    bank_account.validate()
    self.assertEquals('validated', bank_account.getValidationState())
    for username in self.all_username_list:
      self.failUnlessUserCanViewDocument(username, bank_account)
      self.failUnlessUserCanAccessDocument(username, bank_account)

  def stepViewCreditCard(self, sequence=None, sequence_list=None, **kw):
    # Everybody can view credit cards
    entity = self.portal.organisation_module.newContent(
                                               portal_type='Organisation')
    ext_payment = entity.newContent(portal_type='Credit Card')
    # every body can view in draft ...
    self.assertEquals('draft', ext_payment.getValidationState())
    for username in self.all_username_list:
      self.failUnlessUserCanViewDocument(username, ext_payment)
      self.failUnlessUserCanAccessDocument(username, ext_payment)
    # ... and validated states
    ext_payment.validate()
    self.assertEquals('validated', ext_payment.getValidationState())
    for username in self.all_username_list:
      self.failUnlessUserCanViewDocument(username, ext_payment)
      self.failUnlessUserCanAccessDocument(username, ext_payment)

  def stepValidateAndModifyBankAccount(self, sequence=None, sequence_list=None, **kw):
    # Every body can modify Bank Accounts
    entity = self.portal.organisation_module.newContent(
                                               portal_type='Organisation')
    bank_account = entity.newContent(portal_type='Bank Account')
    # draft
    for username in self.all_username_list:
      self.failUnlessUserCanModifyDocument(username, bank_account)
    for username in self.all_username_list:
      self.failUnlessUserCanPassWorkflowTransition(username,
                'validate_action', bank_account)
    # validated
    bank_account.validate()
    self.assertEquals('validated', bank_account.getValidationState())
    for username in self.all_username_list:
      self.failUnlessUserCanModifyDocument(username, bank_account)
    for username in self.all_username_list:
      self.failUnlessUserCanPassWorkflowTransition(username,
                'invalidate_action', bank_account)
    # invalidated
    bank_account.invalidate()
    self.assertEquals('invalidated', bank_account.getValidationState())
    for username in self.all_username_list:
      self.failUnlessUserCanModifyDocument(username, bank_account)
    for username in self.all_username_list:
      self.failUnlessUserCanPassWorkflowTransition(username,
                'validate_action', bank_account)

  def stepValidateAndModifyCreditCard(self, sequence=None, sequence_list=None, **kw):
    # Every body can modify Credit Card
    entity = self.portal.organisation_module.newContent(
                                               portal_type='Organisation')
    credit_card = entity.newContent(portal_type='Credit Card')
    # draft
    for username in self.all_username_list:
      self.failUnlessUserCanModifyDocument(username, credit_card)
    for username in self.all_username_list:
      self.failUnlessUserCanPassWorkflowTransition(username,
                'validate_action', credit_card)
    # validated
    credit_card.validate()
    self.assertEquals('validated', credit_card.getValidationState())
    for username in self.all_username_list:
      self.failUnlessUserCanModifyDocument(username, credit_card)
    for username in self.all_username_list:
      self.failUnlessUserCanPassWorkflowTransition(username,
                'invalidate_action', credit_card)
    # invalidated
    credit_card.invalidate()
    self.assertEquals('invalidated', credit_card.getValidationState())
    for username in self.all_username_list:
      self.failUnlessUserCanModifyDocument(username, credit_card)
    for username in self.all_username_list:
      self.failUnlessUserCanPassWorkflowTransition(username,
                'validate_action', credit_card)

  def stepAddPaymentNodeInPerson(self, sequence=None, sequence_list=None, **kw):
    person = self.portal.person_module.newContent(portal_type='Person')
    for username in self.all_username_list:
      self._loginAsUser(username)
      self.failUnlessUserCanAddDocument(username, person)
      self.failUnless('Bank Account' in
                    person.getVisibleAllowedContentTypeList())
      self.failUnless('Credit Card' in
                    person.getVisibleAllowedContentTypeList())
    # when the entity is validated, we can still add some payment nodes
    person.validate()
    self.portal.portal_caches.clearAllCache()
    for username in self.all_username_list:
      self._loginAsUser(username)
      self.failUnlessUserCanAddDocument(username, person)
      self.failUnless('Bank Account' in
                    person.getVisibleAllowedContentTypeList())
      self.failUnless('Credit Card' in
                    person.getVisibleAllowedContentTypeList())

  def stepAddPaymentNodeInOrganisation(self, sequence=None, sequence_list=None, **kw):
    org = self.portal.organisation_module.newContent(
                                    portal_type='Organisation')
    for username in self.all_username_list:
      self._loginAsUser(username)
      self.failUnlessUserCanAddDocument(username, org)
      self.failUnless('Bank Account' in
                    org.getVisibleAllowedContentTypeList())
      self.failUnless('Credit Card' in
                    org.getVisibleAllowedContentTypeList())
    # when the entity is validated, we can still add some payment nodes
    org.validate()
    self.portal.portal_caches.clearAllCache()
    for username in self.all_username_list:
      self._loginAsUser(username)
      self.failUnlessUserCanAddDocument(username, org)
      self.failUnless('Bank Account' in
                    org.getVisibleAllowedContentTypeList())
      self.failUnless('Credit Card' in
                    org.getVisibleAllowedContentTypeList())

  def stepCopyAndPasteBankAccountInPerson(self, sequence=None, sequence_list=None, **kw):
    # everybody can cp bank accounts in persons
    person = self.portal.organisation_module.newContent(
                                    portal_type='Organisation')
    bank_account = person.newContent(
                              portal_type='Bank Account')
    for username in self.all_username_list:
      self._loginAsUser(username)
      bank_account.Base_createCloneDocument()

  def stepCopyAndPasteBankAccountInOrganisation(self, sequence=None, sequence_list=None, **kw):
    # everybody can cp bank accounts in organisation
    organisation = self.portal.organisation_module.newContent(
                                    portal_type='Organisation')
    bank_account = organisation.newContent(
                              portal_type='Bank Account')
    for username in self.all_username_list:
      self._loginAsUser(username)
      bank_account.Base_createCloneDocument()

  # }}}

  ## Accounting Module {{{
  def stepViewAccountingTransactionModule(self, sequence=None, sequence_list=None, **kw):
    for username in self.all_username_list:
      self.failUnlessUserCanViewDocument(username,
              self.portal.accounting_module)
      self.failUnlessUserCanAccessDocument(username,
              self.portal.accounting_module)

  def stepAddAccountingTransactionModule(self, sequence=None, sequence_list=None, **kw):
    # Anyone can adds accounting transactions
    for username in self.all_username_list:
      self.failUnlessUserCanAddDocument(username,
              self.portal.accounting_module)

  def stepCopyAndPasteAccountingTransactions(self, sequence=None, sequence_list=None, **kw):
    # Anyone can copy and paste accounting transaction.
    for portal_type in self._getAccountingTransactionTypeList():
      if portal_type != 'Balance Transaction':
        transaction = self.portal.accounting_module.newContent(
                                        portal_type=portal_type)
        for username in self.all_username_list:
          self._loginAsUser(username)
          transaction.Base_createCloneDocument()

  def _getAccountingTransactionTypeList(self):
    module = self.portal.accounting_module
    return [ti for ti in module.getVisibleAllowedContentTypeList()
               if ti not in ('Balance Transaction', )]

  def stepAccountingTransaction(self, sequence=None, sequence_list=None, **kw):
    transaction = self.portal.accounting_module.newContent(
                      portal_type='Accounting Transaction',
                      start_date=DateTime(2001, 01, 01),
                      stop_date=DateTime(2001, 01, 01))
    self.assertEquals('draft', transaction.getSimulationState())
    for username in self.all_username_list:
      self.assertUserCanViewDocument(username, transaction)
      self.assertUserCanAccessDocument(username, transaction)
    if self.restricted_security:
      for username in (self.all_username_list - self.accountant_username_list):
        self.failIfUserCanModifyDocument(username, transaction)
    for username in self.accountant_username_list:
      self.failUnlessUserCanModifyDocument(username, transaction)
      self.failUnlessUserCanAddDocument(username, transaction)
    if self.restricted_security:
      for username in (self.all_username_list - self.accountant_username_list):
        self.failIfUserCanPassWorkflowTransition(username,
                                                 'cancel_action',
                                                 transaction)
        self.failIfUserCanPassWorkflowTransition(username,
                                                 'plan_action',
                                                 transaction)
        self.failIfUserCanPassWorkflowTransition(username,
                                                 'confirm_action',
                                                 transaction)
        self.failIfUserCanPassWorkflowTransition(username,
                                                 'start_action',
                                                 transaction)
        self.failIfUserCanPassWorkflowTransition(username,
                                                 'stop_action',
                                                 transaction)
    for username in self.accountant_username_list:
      self.failUnlessUserCanPassWorkflowTransition(username,
                                               'cancel_action',
                                               transaction)
      self.failUnlessUserCanPassWorkflowTransition(username,
                                               'plan_action',
                                               transaction)
      self.failUnlessUserCanPassWorkflowTransition(username,
                                               'confirm_action',
                                               transaction)
      self.failUnlessUserCanPassWorkflowTransition(username,
                                               'stop_action',
                                               transaction)
      # TODO
      ### self.failUnlessUserCanPassWorkflowTransition(username,
      ###                                          'delete_action',
      ###                                          transaction)

    # (skip some states)
    transaction.start()
    self.assertEquals('started', transaction.getSimulationState())
    self.stepTic()

    for username in self.all_username_list:
      # everybody can view
      self.assertUserCanViewDocument(username, transaction)
      self.assertUserCanAccessDocument(username, transaction)

    # only accountant can modify
    if self.restricted_security:
      for username in  (self.all_username_list - self.accountant_username_list):
        self.failIfUserCanModifyDocument(username, transaction)
        self.failIfUserCanAddDocument(username, transaction)

    if self.restricted_security:
      # only accountant can "stop"
      for username in (self.all_username_list - self.accountant_username_list):
        self.failIfUserCanPassWorkflowTransition(username,
                                                 'stop_action',
                                                 transaction)
        self.failIfUserCanPassWorkflowTransition(username,
                                                 'deliver_action',
                                                 transaction)
    for username in self.accountant_username_list:
      self.failUnlessUserCanPassWorkflowTransition(username,
                                               'stop_action',
                                               transaction)

    transaction.stop()
    self.assertEquals('stopped', transaction.getSimulationState())
    for username in self.all_username_list:
      # everybody can view
      self.assertUserCanViewDocument(username, transaction)
      self.assertUserCanAccessDocument(username, transaction)
      # nobody can modify
      self.failIfUserCanModifyDocument(username, transaction)
      self.failIfUserCanAddDocument(username, transaction)

    if self.restricted_security:
      for username in (self.all_username_list - self.accountant_username_list):
        self.failIfUserCanPassWorkflowTransition(username,
                                                 'restart_action',
                                                 transaction)
        self.failIfUserCanPassWorkflowTransition(username,
                                                 'deliver_action',
                                                 transaction)
        self.failIfUserCanPassWorkflowTransition(username,
                                                 'cancel_action',
                                                 transaction)

    for username in self.accountant_username_list:
      self.failUnlessUserCanPassWorkflowTransition(username,
                                               'restart_action',
                                               transaction)
    # in started state, we can modify again, and go back to stopped state
    transaction.restart()
    self.assertEquals('started', transaction.getSimulationState())
    self.stepTic()

    for username in self.accountant_username_list:
      self.failUnlessUserCanModifyDocument(username, transaction)
      self.failUnlessUserCanPassWorkflowTransition(username,
                                                  'stop_action',
                                                  transaction)

    # go back to stopped state
    transaction.stop()
    self.assertEquals('stopped', transaction.getSimulationState())

    # only accounting_manager can validate
    self.failUnlessUserCanPassWorkflowTransition(self.accounting_manager_reference,
                                            'deliver_action',
                                             transaction)
    if self.restricted_security:
      self.failIfUserCanPassWorkflowTransition(self.accounting_agent_reference,
                                              'deliver_action',
                                               transaction)

  def stepSaleInvoiceTransaction(self, sequence=None, sequence_list=None, **kw):
    transaction = self.portal.accounting_module.newContent(
                      portal_type='Sale Invoice Transaction',
                      start_date=DateTime(2001, 01, 01),
                      stop_date=DateTime(2001, 01, 01))
    self.assertEquals('draft', transaction.getSimulationState())
    for username in self.all_username_list:
      self.assertUserCanViewDocument(username, transaction)
      self.assertUserCanAccessDocument(username, transaction)
    if self.restricted_security:
      for username in (self.all_username_list - self.accountant_username_list):
        self.failIfUserCanModifyDocument(username, transaction)
    for username in self.accountant_username_list:
      self.failUnlessUserCanModifyDocument(username, transaction)
      self.failUnlessUserCanAddDocument(username, transaction)
    if self.restricted_security:
      for username in (self.all_username_list - self.accountant_username_list -
                       sales_and_purchase_username_list):
        self.failIfUserCanPassWorkflowTransition(username,
                                                 'cancel_action',
                                                 transaction)
        self.failIfUserCanPassWorkflowTransition(username,
                                                 'plan_action',
                                                 transaction)
        self.failIfUserCanPassWorkflowTransition(username,
                                                 'confirm_action',
                                                 transaction)
        self.failIfUserCanPassWorkflowTransition(username,
                                                 'stop_action',
                                                 transaction)

    for username in self.sales_and_purchase_username_list:
      self.failUnlessUserCanPassWorkflowTransition(username,
                                                   'cancel_action',
                                                    transaction)
      self.failUnlessUserCanPassWorkflowTransition(username,
                                                   'plan_action',
                                                    transaction)
      self.failUnlessUserCanPassWorkflowTransition(username,
                                                   'confirm_action',
                                                    transaction)

    for username in self.accountant_username_list:
      self.failUnlessUserCanPassWorkflowTransition(username,
                                               'cancel_action',
                                               transaction)
      self.failUnlessUserCanPassWorkflowTransition(username,
                                               'plan_action',
                                               transaction)
      self.failUnlessUserCanPassWorkflowTransition(username,
                                               'confirm_action',
                                               transaction)
      self.failUnlessUserCanPassWorkflowTransition(username,
                                               'stop_action',
                                               transaction)
      # TODO
      ### self.failUnlessUserCanPassWorkflowTransition(username,
      ###                                          'delete_action',
      ###                                          transaction)

    # (skip some states)
    transaction.start()
    self.assertEquals('started', transaction.getSimulationState())
    self.stepTic()

    for username in self.all_username_list:
      # everybody can view
      self.assertUserCanViewDocument(username, transaction)
      self.assertUserCanAccessDocument(username, transaction)

    # only accountant can modify
    if self.restricted_security:
      for username in (self.all_username_list - self.accountant_username_list):
        self.failIfUserCanModifyDocument(username, transaction)
        self.failIfUserCanAddDocument(username, transaction)

    if self.restricted_security:
      # only accountant can "stop"
      for username in (self.all_username_list - self.accountant_username_list):
        self.failIfUserCanPassWorkflowTransition(username,
                                                 'stop_action',
                                                 transaction)
        self.failIfUserCanPassWorkflowTransition(username,
                                                 'deliver_action',
                                                 transaction)
    for username in self.accountant_username_list:
      self.failUnlessUserCanPassWorkflowTransition(username,
                                               'stop_action',
                                               transaction)

    transaction.stop()
    self.assertEquals('stopped', transaction.getSimulationState())
    for username in self.all_username_list:
      # everybody can view
      self.assertUserCanViewDocument(username, transaction)
      self.assertUserCanAccessDocument(username, transaction)
      # nobody can modify
      self.failIfUserCanModifyDocument(username, transaction)
      self.failIfUserCanAddDocument(username, transaction)

    if self.restricted_security:
      for username in (self.all_username_list - self.accountant_username_list):
        self.failIfUserCanPassWorkflowTransition(username,
                                                 'restart_action',
                                                 transaction)
        self.failIfUserCanPassWorkflowTransition(username,
                                                 'deliver_action',
                                                 transaction)
        self.failIfUserCanPassWorkflowTransition(username,
                                                 'cancel_action',
                                                 transaction)

    for username in self.accountant_username_list:
      self.failUnlessUserCanPassWorkflowTransition(username,
                                               'restart_action',
                                               transaction)
    # in started state, we can modify again, and go back to stopped state
    transaction.restart()
    self.assertEquals('started', transaction.getSimulationState())
    self.stepTic()

    for username in self.accountant_username_list:
      self.failUnlessUserCanModifyDocument(username, transaction)
      self.failUnlessUserCanPassWorkflowTransition(username,
                                                  'stop_action',
                                                  transaction)

    # go back to stopped state
    transaction.stop()
    self.assertEquals('stopped', transaction.getSimulationState())

    # only accounting_manager can validate
    self.failUnlessUserCanPassWorkflowTransition(self.accounting_manager_reference,
                                            'deliver_action',
                                             transaction)
    if self.restricted_security:
      self.failIfUserCanPassWorkflowTransition(self.accounting_agent_reference,
                                              'deliver_action',
                                               transaction)


  def stepPurchaseInvoiceTransaction(self, sequence=None, sequence_list=None, **kw):
    transaction = self.portal.accounting_module.newContent(
                      portal_type='Purchase Invoice Transaction',
                      start_date=DateTime(2001, 01, 01),
                      stop_date=DateTime(2001, 01, 01))
    self.assertEquals('draft', transaction.getSimulationState())
    for username in self.all_username_list:
      self.assertUserCanViewDocument(username, transaction)
      self.assertUserCanAccessDocument(username, transaction)
    if self.restricted_security:
      for username in (self.all_username_list - self.accountant_username_list):
        self.failIfUserCanModifyDocument(username, transaction)
    for username in self.accountant_username_list:
      self.failUnlessUserCanModifyDocument(username, transaction)
      self.failUnlessUserCanAddDocument(username, transaction)
    if self.restricted_security:
      for username in (self.all_username_list - self.accountant_username_list -
                       sales_and_purchase_username_list):
        self.failIfUserCanPassWorkflowTransition(username,
                                                 'cancel_action',
                                                 transaction)
        self.failIfUserCanPassWorkflowTransition(username,
                                                 'plan_action',
                                                 transaction)
        self.failIfUserCanPassWorkflowTransition(username,
                                                 'confirm_action',
                                                 transaction)
        self.failIfUserCanPassWorkflowTransition(username,
                                                 'stop_action',
                                                 transaction)

    for username in self.sales_and_purchase_username_list:
      self.failUnlessUserCanPassWorkflowTransition(username,
                                                   'cancel_action',
                                                    transaction)
      self.failUnlessUserCanPassWorkflowTransition(username,
                                                   'plan_action',
                                                    transaction)
      self.failUnlessUserCanPassWorkflowTransition(username,
                                                   'confirm_action',
                                                    transaction)
      # XXX would require to go to confirmed state first
      # self.failIfUserCanPassWorkflowTransition(username,
      #                                         'start_action',
      #                                         transaction)


    for username in self.accountant_username_list:
      self.failUnlessUserCanPassWorkflowTransition(username,
                                               'cancel_action',
                                               transaction)
      self.failUnlessUserCanPassWorkflowTransition(username,
                                               'plan_action',
                                               transaction)
      self.failUnlessUserCanPassWorkflowTransition(username,
                                               'confirm_action',
                                               transaction)
      self.failUnlessUserCanPassWorkflowTransition(username,
                                               'stop_action',
                                               transaction)
      # TODO
      ### self.failUnlessUserCanPassWorkflowTransition(username,
      ###                                          'delete_action',
      ###                                          transaction)

    # (skip some states)
    transaction.start()
    self.assertEquals('started', transaction.getSimulationState())
    self.stepTic()

    for username in self.all_username_list:
      # everybody can view
      self.assertUserCanViewDocument(username, transaction)
      self.assertUserCanAccessDocument(username, transaction)

    # only accountant can modify
    if self.restricted_security:
      for username in (self.all_username_list - self.accountant_username_list):
        self.failIfUserCanModifyDocument(username, transaction)
        self.failIfUserCanAddDocument(username, transaction)

    if self.restricted_security:
      # only accountant can "stop"
      for username in (self.all_username_list - self.accountant_username_list):
        self.failIfUserCanPassWorkflowTransition(username,
                                                 'stop_action',
                                                 transaction)
        self.failIfUserCanPassWorkflowTransition(username,
                                                 'deliver_action',
                                                 transaction)
    for username in self.accountant_username_list:
      self.failUnlessUserCanPassWorkflowTransition(username,
                                               'stop_action',
                                               transaction)

    transaction.stop()
    self.assertEquals('stopped', transaction.getSimulationState())
    for username in self.all_username_list:
      # everybody can view
      self.assertUserCanViewDocument(username, transaction)
      self.assertUserCanAccessDocument(username, transaction)
      # nobody can modify
      self.failIfUserCanModifyDocument(username, transaction)
      self.failIfUserCanAddDocument(username, transaction)

    if self.restricted_security:
      for username in (self.all_username_list - self.accountant_username_list):
        self.failIfUserCanPassWorkflowTransition(username,
                                                 'restart_action',
                                                 transaction)
        self.failIfUserCanPassWorkflowTransition(username,
                                                 'deliver_action',
                                                 transaction)
        self.failIfUserCanPassWorkflowTransition(username,
                                                 'cancel_action',
                                                 transaction)

    for username in self.accountant_username_list:
      self.failUnlessUserCanPassWorkflowTransition(username,
                                               'restart_action',
                                               transaction)
    # in started state, we can modify again, and go back to stopped state
    transaction.restart()
    self.assertEquals('started', transaction.getSimulationState())
    self.stepTic()

    for username in self.accountant_username_list:
      self.failUnlessUserCanModifyDocument(username, transaction)
      self.failUnlessUserCanPassWorkflowTransition(username,
                                                  'stop_action',
                                                  transaction)

    # go back to stopped state
    transaction.stop()
    self.assertEquals('stopped', transaction.getSimulationState())

    # only accounting_manager can validate
    self.failUnlessUserCanPassWorkflowTransition(self.accounting_manager_reference,
                                            'deliver_action',
                                             transaction)
    if self.restricted_security:
      self.failIfUserCanPassWorkflowTransition(self.accounting_agent_reference,
                                              'deliver_action',
                                               transaction)

  def stepPaymentTransaction(self, sequence=None, sequence_list=None, **kw):
    transaction = self.portal.accounting_module.newContent(
                      portal_type='Payment Transaction',
                      start_date=DateTime(2001, 01, 01),
                      stop_date=DateTime(2001, 01, 01))
    self.assertEquals('draft', transaction.getSimulationState())
    for username in self.all_username_list:
      self.assertUserCanViewDocument(username, transaction)
      self.assertUserCanAccessDocument(username, transaction)
    if self.restricted_security:
      for username in (self.all_username_list - self.accountant_username_list):
        self.failIfUserCanModifyDocument(username, transaction)
    for username in self.accountant_username_list:
      self.failUnlessUserCanModifyDocument(username, transaction)
      self.failUnlessUserCanAddDocument(username, transaction)
    if self.restricted_security:
      for username in (self.all_username_list - self.accountant_username_list):
        self.failIfUserCanPassWorkflowTransition(username,
                                                 'cancel_action',
                                                 transaction)
        self.failIfUserCanPassWorkflowTransition(username,
                                                 'plan_action',
                                                 transaction)
        self.failIfUserCanPassWorkflowTransition(username,
                                                 'confirm_action',
                                                 transaction)
        self.failIfUserCanPassWorkflowTransition(username,
                                                 'start_action',
                                                 transaction)
        self.failIfUserCanPassWorkflowTransition(username,
                                                 'stop_action',
                                                 transaction)
    for username in self.accountant_username_list:
      self.failUnlessUserCanPassWorkflowTransition(username,
                                               'cancel_action',
                                               transaction)
      self.failUnlessUserCanPassWorkflowTransition(username,
                                               'plan_action',
                                               transaction)
      self.failUnlessUserCanPassWorkflowTransition(username,
                                               'confirm_action',
                                               transaction)
      self.failUnlessUserCanPassWorkflowTransition(username,
                                               'stop_action',
                                               transaction)
      # TODO
      ### self.failUnlessUserCanPassWorkflowTransition(username,
      ###                                          'delete_action',
      ###                                          transaction)

    # (skip some states)
    transaction.start()
    self.assertEquals('started', transaction.getSimulationState())
    self.stepTic()

    for username in self.all_username_list:
      # everybody can view
      self.assertUserCanViewDocument(username, transaction)
      self.assertUserCanAccessDocument(username, transaction)

    # only accountant can modify
    if self.restricted_security:
      for username in (self.all_username_list - self.accountant_username_list):
        self.failIfUserCanModifyDocument(username, transaction)
        self.failIfUserCanAddDocument(username, transaction)

    # only accountant can "stop"
    if self.restricted_security:
      for username in (self.all_username_list - self.accountant_username_list):
        self.failIfUserCanPassWorkflowTransition(username,
                                                 'stop_action',
                                                 transaction)
        self.failIfUserCanPassWorkflowTransition(username,
                                                 'deliver_action',
                                                 transaction)
    for username in self.accountant_username_list:
      self.failUnlessUserCanPassWorkflowTransition(username,
                                               'stop_action',
                                               transaction)

    transaction.stop()
    self.assertEquals('stopped', transaction.getSimulationState())
    for username in self.all_username_list:
      # everybody can view
      self.assertUserCanViewDocument(username, transaction)
      self.assertUserCanAccessDocument(username, transaction)
      # nobody can modify
      self.failIfUserCanModifyDocument(username, transaction)
      self.failIfUserCanAddDocument(username, transaction)

    if self.restricted_security:
      for username in (self.all_username_list - self.accountant_username_list):
        self.failIfUserCanPassWorkflowTransition(username,
                                                 'restart_action',
                                                 transaction)
        self.failIfUserCanPassWorkflowTransition(username,
                                                 'deliver_action',
                                                 transaction)
        self.failIfUserCanPassWorkflowTransition(username,
                                                 'cancel_action',
                                                 transaction)

    for username in self.accountant_username_list:
      self.failUnlessUserCanPassWorkflowTransition(username,
                                               'restart_action',
                                               transaction)
    # in started state, we can modify again, and go back to stopped state
    transaction.restart()
    self.assertEquals('started', transaction.getSimulationState())
    self.stepTic()

    for username in self.accountant_username_list:
      self.failUnlessUserCanModifyDocument(username, transaction)
      self.failUnlessUserCanPassWorkflowTransition(username,
                                                  'stop_action',
                                                  transaction)

    # go back to stopped state
    transaction.stop()
    self.assertEquals('stopped', transaction.getSimulationState())

    # only accounting_manager can validate
    self.failUnlessUserCanPassWorkflowTransition(self.accounting_manager_reference,
                                            'deliver_action',
                                             transaction)
    if self.restricted_security:
      self.failIfUserCanPassWorkflowTransition(self.accounting_agent_reference,
                                              'deliver_action',
                                               transaction)

  def stepBalanceTransaction(self, sequence=None, sequence_list=None, **kw):
    # Balance Transaction must be viewable by users (creation & validation is
    # done from unrestricted code, so no problem)
    balance_transaction = self.portal.accounting_module.newContent(
                      portal_type='Balance Transaction')
    for username in self.all_username_list:
      self.assertUserCanViewDocument(username, balance_transaction)
      self.assertUserCanAccessDocument(username, balance_transaction)

  def stepAccountingTransaction_getCausalityGroupedAccountingTransactionList(
      self, sequence=None, sequence_list=None, **kw):
    self._loginAsUser(self.accounting_manager_reference)
    accounting_transaction_x_related_to_a = self.portal.\
                                    accounting_module.newContent(
                                    portal_type='Accounting Transaction',
                                    start_date=DateTime(2010, 06, 01),
                                    stop_date=DateTime(2010, 06, 01))

    accounting_transaction_y_related_to_a = self.portal.\
                                    accounting_module.newContent(
                                    portal_type='Accounting Transaction',
                                    start_date=DateTime(2010, 06, 01),
                                    stop_date=DateTime(2010, 06, 01))

    accounting_transaction_a = self.portal.accounting_module.newContent(
                                    portal_type='Accounting Transaction',
                                    start_date=DateTime(2010, 06, 01),
                                    stop_date=DateTime(2010, 06, 01))
  
    accounting_transaction_b = self.portal.accounting_module.newContent(
                                    portal_type='Accounting Transaction',
                                    start_date=DateTime(2010, 06, 01),
                                    stop_date=DateTime(2010, 06, 01))
  
    accounting_transaction_c = self.portal.accounting_module.newContent(
                                   portal_type='Accounting Transaction',
                                   start_date=DateTime(2010, 06, 01),
                                   stop_date=DateTime(2010, 06, 01))
    
    accounting_transaction_x_related_to_a.setCausalityValue(\
                                                   accounting_transaction_a)

    accounting_transaction_y_related_to_a.setCausalityValue(\
                                                   accounting_transaction_a)


    accounting_transaction_a.setCausalityValueList([accounting_transaction_b,
                                                    accounting_transaction_c])
    self.stepTic()
  
    accounting_transaction_list = accounting_transaction_a.\
          AccountingTransaction_getCausalityGroupedAccountingTransactionList()
    
    self.assertEquals(5, len(accounting_transaction_list))
  
    self.assertTrue(accounting_transaction_a in accounting_transaction_list)
    self.assertTrue(accounting_transaction_b in accounting_transaction_list)
    self.assertTrue(accounting_transaction_c in accounting_transaction_list)
    self.assertTrue(accounting_transaction_x_related_to_a in \
                                                accounting_transaction_list)
    self.assertTrue(accounting_transaction_y_related_to_a in \
                                                accounting_transaction_list)
  
    accounting_transaction_x_related_to_a.delete()
    accounting_transaction_y_related_to_a.cancel()
    self.stepTic()
 
    accounting_transaction_list = accounting_transaction_a.\
          AccountingTransaction_getCausalityGroupedAccountingTransactionList()
  
    self.assertEquals(3, len(accounting_transaction_list))
  
    self.assertFalse(accounting_transaction_x_related_to_a in \
                                                accounting_transaction_list)
    self.assertFalse(accounting_transaction_y_related_to_a in \
                                                accounting_transaction_list)

  # }}}

  ## Assignments / Login and Password {{{
  def stepAddAssignments(self, sequence=None, sequence_list=None, **kw):
    # for now, anybody can add assignements
    person = self.portal.person_module.newContent(portal_type='Person')
    for username in self.all_username_list:
      self._loginAsUser(username)
      self.failUnless('Assignment' in
                  person.getVisibleAllowedContentTypeList())
      self.failUnlessUserCanAddDocument(username, person)

  def stepAssignmentTI(self, sequence=None, sequence_list=None, **kw):
    ti = self.getTypesTool().getTypeInfo('Assignment')
    self.assertNotEquals(None, ti)
    # Acquire local roles on Assignment ? no
    self.failIf(ti.getProperty('type_acquire_local_role', 1))

  def stepEditAssignments(self, sequence=None, sequence_list=None, **kw):
    # everybody can open assignments in express
    person = self.portal.person_module.newContent(portal_type='Person')
    assignment = person.newContent(portal_type='Assignment')
    for username in self.all_username_list:
      self.failUnlessUserCanModifyDocument(username, assignment)
      self.failUnlessUserCanPassWorkflowTransition(username,
                                                   'open_action',
                                                   assignment)
  # }}}

  # {{{ Trade
  def stepViewAcessAddPurchaseTradeCondition(self, sequence=None, sequence_list=None, **kw):
    module = self.portal.purchase_trade_condition_module
    for username in self.all_username_list:
      self.assertUserCanViewDocument(username, module)
      self.assertUserCanAccessDocument(username, module)
    for username in self.sales_and_purchase_username_list:
      self.assertUserCanAddDocument(username, module)
      self._loginAsUser(username)
      tc = module.newContent(portal_type='Purchase Trade Condition')
      self.assertUserCanViewDocument(username, tc)
      self.failUnlessUserCanPassWorkflowTransition(
                    username, 'validate_action', tc)
      self.portal.portal_workflow.doActionFor(tc, 'validate_action')
      self.failUnlessUserCanPassWorkflowTransition(
                    username, 'invalidate_action', tc)

  def stepViewAccessAddSaleTradeCondition(self, sequence=None, sequence_list=None, **kw):
    module = self.portal.sale_trade_condition_module
    for username in self.all_username_list:
      self.assertUserCanViewDocument(username, module)
      self.assertUserCanAccessDocument(username, module)
    for username in self.sales_and_purchase_username_list:
      self.assertUserCanAddDocument(username, module)
      self._loginAsUser(username)
      tc = module.newContent(portal_type='Sale Trade Condition')
      self.assertUserCanViewDocument(username, tc)
      self.failUnlessUserCanPassWorkflowTransition(
                    username, 'validate_action', tc)
      self.portal.portal_workflow.doActionFor(tc, 'validate_action')
      self.failUnlessUserCanPassWorkflowTransition(
                    username, 'invalidate_action', tc)

  def stepViewAccessAddSaleOrder(self, sequence=None, sequence_list=None, **kw):
    module = self.portal.sale_order_module
    for username in self.all_username_list:
      self.assertUserCanViewDocument(username, module)
      self.assertUserCanAccessDocument(username, module)
    for username in self.sales_and_purchase_username_list:
      self.assertUserCanAddDocument(username, module)
      self._loginAsUser(username)
      order = module.newContent(portal_type='Sale Order')
      self.assertUserCanViewDocument(username, order)
      self.failUnlessUserCanPassWorkflowTransition(
                    username, 'plan_action', order)
      self.failUnlessUserCanPassWorkflowTransition(
                    username, 'confirm_action', order)
      self.failUnlessUserCanPassWorkflowTransition(
                    username, 'cancel_action', order)

      order.confirm()
      self.assertEquals('confirmed', order.getSimulationState())
      self.assertUserCanViewDocument(username, order)
      self.failIfUserCanModifyDocument(username, order)


  def stepViewAccessAddSalePackingList(self, sequence=None, sequence_list=None, **kw):
    module = self.portal.sale_packing_list_module
    for username in self.all_username_list:
      self.assertUserCanViewDocument(username, module)
      self.assertUserCanAccessDocument(username, module)
    for username in self.sales_and_purchase_username_list:
      self.assertUserCanAddDocument(username, module)
      self._loginAsUser(username)
      pl = module.newContent(portal_type='Sale Packing List')
      self.assertUserCanViewDocument(username, pl)
      self.failUnlessUserCanPassWorkflowTransition(
                    username, 'confirm_action', pl)

  def stepViewAccessPurchaseOrder(self, sequence=None, sequence_list=None, **kw):
    module = self.portal.purchase_order_module
    for username in self.all_username_list:
      self.assertUserCanViewDocument(username, module)
      self.assertUserCanAccessDocument(username, module)
    for username in self.sales_and_purchase_username_list:
      self.assertUserCanAddDocument(username, module)
      self._loginAsUser(username)
      order = module.newContent(portal_type='Purchase Order')
      self.assertUserCanViewDocument(username, order)
      self.failUnlessUserCanPassWorkflowTransition(
                    username, 'plan_action', order)
      self.failUnlessUserCanPassWorkflowTransition(
                    username, 'confirm_action', order)
      self.failUnlessUserCanPassWorkflowTransition(
                    username, 'cancel_action', order)

      order.confirm()
      self.assertEquals('confirmed', order.getSimulationState())
      self.assertUserCanViewDocument(username, order)
      self.failIfUserCanModifyDocument(username, order)

  def stepPurchasePackingList(self, sequence=None, sequence_list=None, **kw):
    module = self.portal.purchase_packing_list_module
    for username in self.all_username_list:
      self.assertUserCanViewDocument(username, module)
      self.assertUserCanAccessDocument(username, module)
    for username in self.sales_and_purchase_username_list:
      self.assertUserCanAddDocument(username, module)
      self._loginAsUser(username)
      pl = module.newContent(portal_type='Purchase Packing List')
      self.assertUserCanViewDocument(username, pl)
      self.failUnlessUserCanPassWorkflowTransition(
                    username, 'confirm_action', pl)

  def stepViewAccessTaxModule(self, sequence=None, sequence_list=None, **kw):
    for username in self.all_username_list:
      self.assertUserCanViewDocument(username, self.portal.tax_module)
      self.assertUserCanAccessDocument(username, self.portal.tax_module)
      self.assertUserCanAddDocument(username, self.portal.tax_module)

  def stepAddTax(self, sequence=None, sequence_list=None, **kw):
    tax = self.portal.tax_module.newContent(portal_type='Tax')
    for username in self.all_username_list:
      self.assertUserCanViewDocument(username, tax)
      self.assertUserCanAccessDocument(username, tax)

  # }}}
  # web
  def stepWebSiteModule(self, sequence=None, sequence_list=None, **kw):
    """Anonymous should not be able to access web_site_module."""
    web_site_module = self.portal.web_site_module
    checkPermission = self.portal.portal_membership.checkPermission
    # switch to Anonymous user
    self.logout()
    self.assertEquals(None, checkPermission('View', web_site_module))
    self.assertEquals(None, checkPermission('Access Contents Information',web_site_module))
    self.assertRaises(Unauthorized,  web_site_module)

  # DMS
  def stepPortalContributionsTool(self, sequence=None, sequence_list=None, **kw):
    """
      TioLive user should be able to contribute from this tool
      (i.e. has Manage portal content).
    """
    portal_contributions = self.portal.portal_contributions
    checkPermission = self.portal.portal_membership.checkPermission
    for username in self.all_username_list:
      self._loginAsUser(username)
      self.assertEquals(True,  \
                        checkPermission('Modify portal content', portal_contributions))

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
                      'TradeOrder' in sale_packing_list.getTypePropertySheetList())
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

  def test_security_standard_workflow_france(self):
    """ Test the after configuration script """
    sequence_list = SequenceList()
    sequence_string =  self.DEFAULT_SEQUENCE_LIST % dict(country='France') + \
      """
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
      stepViewAccessTaxModule
      stepAddTax
      stepWebSiteModule
      stepPortalContributionsTool
      stepConfiguredPropertySheets
      stepPreferredExpressPassword
      """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_after_configuration_standard_workflow_france(self):
    """ Test the after configuration script """
    sequence_list = SequenceList()
    sequence_string =  self.DEFAULT_SEQUENCE_LIST % dict(country='France') + \
      """
      stepCheckValidAccountList
      stepCheckAccountReference
      stepCheckValidPersonList
      stepCheckValidOrganisationList
      stepCheckValidCurrencyList
      stepCheckPublicGadgetList
      stepCheckPreferenceList
      stepCheckModulesBusinessApplication
      stepCheckBaseCategoryList
      stepCheckOrganisationSite
      stepCheckAccountingPeriod
      stepCheckRuleValidation
      """
    # XXX (lucas): expected failure, it must be fixed in ERP5 core.
    sequence_string += """
      stepCheckQuantityConversion
      """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

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

  def test_standard_workflow_brazil_with_previous(self):
    """ This time we must simulate the previous buttom """
    sequence_list = SequenceList()
    sequence_string = """
      stepCreateBusinessConfiguration
      stepTic
      stepSetStandardWorkflow
      stepTic
      stepConfiguratorNext
      stepTic
      stepCheckBT5ConfiguratorItem
      stepCheckConfigureOrganisationForm
      stepSetupOrganisationConfiguratorItemBrazil
      stepConfiguratorNext
      stepTic
      stepCheckConfigureUserAccountNumberForm
      stepCheckOrganisationConfiguratorItemBrazil
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
      stepSetupOrganisationConfiguratorItemBrazil
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
      stepSetupAccountingConfigurationBrazil
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
      stepSetupOrganisationConfiguratorItemBrazil
      stepConfiguratorNext
      stepCheckConfigureUserAccountNumberForm
      stepSetupUserAccounNumberSix
      stepConfiguratorNext
      stepCheckConfigureMultipleUserAccountForm
      stepSetupMultipleUserAccountSix
      stepConfiguratorNext
      stepCheckConfigureAccountingForm
      stepSetupAccountingConfigurationBrazil
      stepConfiguratorNext
      stepTic
      stepCheckConfigurePreferenceForm
    """
    # check next Configure Installation form
    sequence_string += """
      stepSetupPreferenceConfigurationBrazil
      stepConfiguratorNext
      stepTic
      stepCheckPreferenceConfigurationItemListBrazil
      stepCheckConfigureInstallationForm
      stepSetupInstallConfiguration
      stepConfiguratorNext
      stepCheckInstallConfiguration
      stepTic
      stepStartConfigurationInstallation
      stepTic
      stepCheckInstanceIsConfiguredFrance
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
  suite.addTest(unittest.makeSuite(TestConfiguratorStandardWorkflow))
  return suite
