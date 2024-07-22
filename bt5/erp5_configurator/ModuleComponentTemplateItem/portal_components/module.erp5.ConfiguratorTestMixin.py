##############################################################################
# coding: utf-8
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
from AccessControl import Unauthorized
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.SecurityTestCase import SecurityTestCase
from AccessControl.SecurityManagement import newSecurityManager

class TestLiveConfiguratorWorkflowMixin(SecurityTestCase):
  """
    Configurator Mixin Class
  """
  # The list of standard business templates that the configurator should force
  # to install
  expected_bt5_list = ('erp5_simulation',
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
                       'erp5_invoicing',
                       'erp5_configurator_standard_solver',
                       'erp5_configurator_standard_trade_template',
                       'erp5_configurator_standard_accounting_template',
                       'erp5_configurator_standard_invoicing_template',
                       'erp5_trade_knowledge_pad',
                       'erp5_crm_knowledge_pad',
                       'erp5_simplified_invoicing',
                       'erp5_ods_style',
                       'erp5_odt_style',
                       'erp5_ooo_import')

  standard_bt5_list = ('erp5_dhtml_style',
                         'erp5_jquery_ui',
                         'erp5_ingestion_mysql_innodb_catalog',
                         'erp5_dms',
                         'erp5_accounting',
                         'erp5_crm',
                         'erp5_graph_editor',
                         'erp5_simplified_invoicing',
                         'erp5_trade_knowledge_pad',
                         'erp5_crm_knowledge_pad',
                         'erp5_configurator_standard_solver',
                         'erp5_configurator_standard_trade_template',
                         'erp5_configurator_standard_accounting_template',
                         'erp5_configurator_standard_invoicing_template',
                         'erp5_ods_style',
                         'erp5_odt_style',
                         'erp5_ooo_import',
                         'erp5_osoe_web_renderjs_ui',
)

  def getBusinessTemplateList(self):
    return ('erp5_core_proxy_field_legacy',
        'erp5_full_text_mroonga_catalog',
        'erp5_base',
        'erp5_configurator',
        'erp5_configurator_standard',)

  def stepLogin(self, quiet=0, run=1, **kw):
    uf = self.getPortal().acl_users
    uf._doAddUser('test_configurator_user', '',
                              ['Manager', 'Assignee', 'Assignor',
                               'Associate', 'Auditor', 'Author'], [])
    user = uf.getUserById('test_configurator_user').__of__(uf)
    newSecurityManager(None, user)

  def afterSetUp(self):
    self.stepLogin()
    self.loginByUserName(user_name='test_configurator_user')
    # XXX (lucas): The request is not clean between tests.
    # So, we need to force the test to use a clean REQUEST
    # Otherwise the next test will fail trying to validate the form,
    # because the REQUEST has data from the previous step/test.
    if getattr(self.app.REQUEST, 'default_other', None) is None:
      self.app.REQUEST.default_other = self.app.REQUEST.other.copy()
    else:
      self.stepCleanUpRequest()

    self.restricted_security = 0
    self.setupAutomaticBusinessTemplateRepository(
                 searchable_business_template_list=["erp5_core", "erp5_base"])

    # it is required by SecurityTestCase
    self.workflow_tool = self.portal.portal_workflow
    self.portal.portal_activities.unsubscribe()

  def beforeTearDown(self):
    self.portal.portal_activities.subscribe()
    ERP5TypeTestCase.beforeTearDown(self)

  def setBusinessConfigurationWorkflow(self, business_configuration, workflow):
    """ Set configurator workflow """
    business_configuration.setResource(workflow)

  def assertCurrentStep(self, step_title, server_response):
    """ Checks the current step title. """
    self.assertTrue(
      '<h2>%s</h2>' % step_title in server_response['data'],
      'Unable to guess current step title (expected:%s) in: \n%s' %
      (step_title, server_response))

  ### STEPS

  def stepCleanUpRequest(self, sequence=None, sequence_list=None, **kw):
    """ Restore clean up the request """
    self.app.REQUEST.other = self.app.REQUEST.default_other.copy()

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

  def stepCheckBT5ConfiguratorItem(self, sequence=None, sequence_list=None, **kw):
    """ Check if the Configuration Item list is correct """
    business_configuration = sequence.get("business_configuration")
    # second one: install some standard business templates
    standard_bt5_config_save = business_configuration['1']
    self.assertEqual(
      set(self.standard_bt5_list),
      {x.bt5_id for x in standard_bt5_config_save.contentValues()})

    # third one: we create a business template to store customer configuration
    custom_bt5_config_save = business_configuration['2']
    custom_bt5_config_item = custom_bt5_config_save['1']
    self.assertEqual(custom_bt5_config_item.getPortalType(),
                      'Customer BT5 Configurator Item')
    self.assertEqual(custom_bt5_config_item.bt5_title,
          '_'.join(business_configuration.getTitle().strip().lower().split()))

  def stepCheckConfigureOrganisationForm(self, sequence=None, sequence_list=None, **kw):
    """ Check if Confire Organisation step was showed """
    response_dict = sequence.get("response_dict")
    if 'command' in response_dict:
      self.assertEqual('show', response_dict['command'])
    self.assertEqual('Configure Organisation', response_dict['next'])
    self.assertCurrentStep('Your organisation', response_dict)

  def stepSetupOrganisationConfiguratorItem(self, sequence=None, sequence_list=None, **kw):
    """ Create one Organisation """
    default_address_city = sequence.get('organisation_default_address_city')
    default_address_region = sequence.get('organisation_default_address_region')
    next_dict = dict(
        field_your_title='My Organisation',
        field_your_default_email_text='me@example.com',
        field_your_default_telephone_text='01234567890',
        field_your_default_address_street_address='.',
        field_your_default_address_zip_code='59000',
        field_your_default_address_city=default_address_city,
        field_your_default_address_region=default_address_region)
    next_dict.update(**kw)
    sequence.edit(next_dict=next_dict)

  def stepCheckConfigureUserAccountNumberForm(self, sequence=None, sequence_list=None, **kw):
    """ Check if Configure Organisation step was showed """
    response_dict = sequence.get("response_dict")
    if 'command' in response_dict:
      self.assertEqual('show', response_dict['command'])
    self.assertEqual('Configure user accounts number', response_dict['next'])
    self.assertEqual('Previous', response_dict['previous'])
    self.assertCurrentStep('Number of user accounts', response_dict)

  def stepSetupUserAccounNumberSix(self, sequence=None, sequence_list=None, **kw):
    """ Create one more user account """
    next_dict = dict(
          field_your_company_employees_number=self.company_employees_number)
    sequence.edit(next_dict=next_dict)

  def stepCheckConfigureMultipleUserAccountForm(self, sequence=None, sequence_list=None, **kw):
    """ Check the multiple user account form """
    response_dict = sequence.get("response_dict")
    if 'command' in response_dict:
      self.assertEqual('show', response_dict['command'])
    self.assertEqual('Previous', response_dict['previous'])
    self.assertEqual('Configure user accounts', response_dict['next'])
    self.assertCurrentStep('User accounts configuration', response_dict)

  def stepSetupMultipleUserAccountSix(self, sequence=None, sequence_list=None, **kw):
    """ Create multiple user account """
    next_dict = {}
    for user in self.user_list:
      for k, v in user.items():
        next_dict.setdefault(k, []).append(v)
    sequence.edit(next_dict=next_dict)

  def _getUserIdList(self, login_list):
    user_id_dict = {
      x['login']: x['id'] for x in self.portal.acl_users.searchUsers(
        login=login_list,
        exact_match=True,
      )
    }
    self.assertSameSet(user_id_dict, login_list)
    return user_id_dict.values()


  def stepCheckMultiplePersonConfigurationItem(self, sequence=None, sequence_list=None, **kw):
    """
      Check if multiple Person Configuration Item of the Business
      Configuration have been created successfully.
    """
    business_configuration = sequence.get("business_configuration")
    self.assertEqual(int(self.company_employees_number),
                          business_configuration.getGlobalConfigurationAttr(
                                                 "company_employees_number"))

    configuration_save_list = business_configuration.contentValues(
                                             portal_type='Configuration Save')
    person_business_configuration_save = None
    for configuration_save in configuration_save_list:
      person_item_list = configuration_save.contentValues(
                                 portal_type='Person Configurator Item')
      if person_item_list:
        person_business_configuration_save = configuration_save
        break


    self.assertEqual(int(self.company_employees_number),
        len(person_business_configuration_save.contentValues()))
    return person_business_configuration_save

  def stepCheckConfigureAccountingForm(self, sequence=None, sequence_list=None, **kw):
    """ Check the accounting form configuration. """
    response_dict = sequence.get("response_dict")
    if 'command' in response_dict:
      self.assertEqual('show', response_dict['command'])
    self.assertEqual('Previous', response_dict['previous'])
    self.assertEqual('Configure accounting', response_dict['next'])
    self.assertCurrentStep('Accounting', response_dict)

  def stepSetupAccountingConfiguration(self, sequence=None, sequence_list=None, **kw):
    """ Setup up the accounting configuration """
    accounting_plan=sequence.get('configuration_accounting_plan')
    next_dict = dict(field_your_accounting_plan=accounting_plan,
                subfield_field_your_period_start_date_year='2008',
                subfield_field_your_period_start_date_month='01',
                subfield_field_your_period_start_date_day='01',
                subfield_field_your_period_stop_date_year='2008',
                subfield_field_your_period_stop_date_month='12',
                subfield_field_your_period_stop_date_day='31',
                field_your_period_title='2008'
           )
    sequence.edit(next_dict=next_dict)

  def stepCheckConfigurePreferenceForm(self, sequence=None, sequence_list=None, **kw):
    """ Check the preference form """
    response_dict = sequence.get("response_dict")
    if 'command' in response_dict:
      self.assertEqual('show', response_dict['command'])
    self.assertEqual('Previous', response_dict['previous'])
    self.assertEqual('Configure ERP5 Preferences', response_dict['next'])
    self.assertCurrentStep('Application preferences', response_dict)

  def _stepCheckAccountingConfigurationItemList(self, business_configuration,
                                                      bt5_id,
                                                      accounting_transaction_gap,
                                                      gap):
    """ Check the French accounting configuration item list """
    # 1. the localization business template
    accounting_business_configuration_save = business_configuration.\
                      contentValues(portal_types='Configuration Save')[-1]
    bt5_business_configuration_item =\
          accounting_business_configuration_save['1']
    self.assertEqual('Standard BT5 Configurator Item',
            bt5_business_configuration_item.getPortalType())
    self.assertEqual(bt5_id, bt5_business_configuration_item.bt5_id)

    # 2. a preference
    preference_buisiness_configurator_item_list =\
       accounting_business_configuration_save.contentValues(
           portal_type='Preference Configurator Item')
    self.assertEqual(1, len(preference_buisiness_configurator_item_list))
    preference_buisiness_configurator_item = \
        preference_buisiness_configurator_item_list[0]
    self.assertEqual(accounting_transaction_gap,
           preference_buisiness_configurator_item.getProperty(
              'preferred_accounting_transaction_gap'))
    self.assertEqual(self.preference_group,
           preference_buisiness_configurator_item.getProperty(
              'preferred_accounting_transaction_section_category'))

    # 3. some pre-configured accounts
    account_business_configuration_item =\
          accounting_business_configuration_save['2']
    self.assertEqual('Account Configurator Item',
            account_business_configuration_item.getPortalType())
    self.assertEqual('capital',
        getattr(account_business_configuration_item, 'account_id', 'not set'))
    self.assertEqual('equity',
            account_business_configuration_item.getAccountType())
    self.assertEqual(gap, account_business_configuration_item.getGap())
    self.assertEqual('equity/share_capital',
            account_business_configuration_item.getFinancialSection())

    # title is translated here
    title = account_business_configuration_item.getTitle()
    self.assertIn(title, ('Capital', 'Gezeichnetes Kapital', 'Уставный капитал'))

    # 4. An accounting period configuration item
    accounting_period_configuration_item = \
        accounting_business_configuration_save['14']
    # this ['14'] will break when we'll add more accounts
    self.assertEqual('Accounting Period Configurator Item',
        accounting_period_configuration_item.getPortalType())

    self.assertEqual(DateTime(2008, 1, 1),
        accounting_period_configuration_item.getStartDate())
    self.assertEqual(DateTime(2008, 12, 31),
        accounting_period_configuration_item.getStopDate())
    self.assertEqual('2008',
        accounting_period_configuration_item.getShortTitle())

  def stepCheckAccountingConfigurationItemListFrance(self, sequence=None, sequence_list=None, **kw):
    """ Check the French accounting configuration item """
    self._stepCheckAccountingConfigurationItemList(
                business_configuration=sequence.get("business_configuration"),
                bt5_id='erp5_accounting_l10n_fr',
                accounting_transaction_gap='gap/fr/pcg',
                gap='fr/pcg/1/10/101')

  def stepCheckAccountingConfigurationItemListGermany(self, sequence=None, sequence_list=None, **kw):
    """ Check the German accounting configuration item """
    self._stepCheckAccountingConfigurationItemList(
                business_configuration=sequence.get("business_configuration"),
                bt5_id='erp5_accounting_l10n_de_skr04',
                accounting_transaction_gap='gap/de/skr04',
                gap='de/skr04/3/1/2/1/1')

  def stepCheckAccountingConfigurationItemListBrazil(self, sequence=None, sequence_list=None, **kw):
    """ Check the Brazilian accounting configuration item """
    self._stepCheckAccountingConfigurationItemList(
                business_configuration=sequence.get("business_configuration"),
                bt5_id='erp5_accounting_l10n_br_extend',
                accounting_transaction_gap='gap/br/pcg',
                gap='br/pcg/2/2.4/2.4.1/2.4.1.01')

  def stepCheckAccountingConfigurationItemListRussia(self, sequence=None, sequence_list=None, **kw):
    """ Check the Russian accounting configuration item """
    self._stepCheckAccountingConfigurationItemList(
                business_configuration=sequence.get("business_configuration"),
                bt5_id='erp5_accounting_l10n_ru',
                accounting_transaction_gap='gap/ru/ru2000',
                gap='ru/ru2000/80')

  def stepSetupPreferenceConfiguration(self, sequence=None, sequence_list=None, **kw):
    """ Setup the preference configuration """

    lang = sequence.get('configuration_lang')
    price_currency = sequence.get('configuration_price_currency')
    next_dict = dict(field_your_price_currency=price_currency,
                field_your_preferred_date_order='dmy',
                field_your_lang=lang,
                default_field_your_lang=1,)

    currency_id = sequence.get('configuration_currency_reference')
    sequence.edit(next_dict=next_dict, currency_id=currency_id)

  def stepCheckPreferenceConfigurationItemList(self, sequence=None, sequence_list=None, **kw):
    """
      Check the creation of:
      - Currency Configurator Item
      - Service Configurator Item
      - System Preference Configurator Item
      - Standard BT5 Configurator Item
    """
    currency_title = sequence.get('configuration_currency_title')
    currency_reference = sequence.get('configuration_currency_reference')
    bt5_id = sequence.get('configuration_lang')
    business_configuration = sequence.get("business_configuration")

    # this created a currency
    preferences_business_configuration_save = business_configuration.\
                      contentValues(portal_types='Configuration Save')[-1]

    currency_business_configuration_item =\
          preferences_business_configuration_save['1']
    self.assertEqual('Currency Configurator Item',
          currency_business_configuration_item.getPortalType())
    self.assertEqual(currency_title,
          currency_business_configuration_item.getTitle())
    self.assertEqual(0.01,
          currency_business_configuration_item.getBaseUnitQuantity())
    self.assertEqual(currency_reference,
          currency_business_configuration_item.getReference())
    # some services
    # TODO
    service_business_configuration_item =\
          preferences_business_configuration_save['2']
    self.assertEqual('Service Configurator Item',
                     service_business_configuration_item.getPortalType())
    # and a preference
    preference_business_configuration_item =\
          preferences_business_configuration_save['3']
    self.assertEqual('Preference Configurator Item',
        preference_business_configuration_item.getPortalType())
    # that uses the currency
    self.assertEqual('currency_module/%s' % currency_reference,
        preference_business_configuration_item.getProperty(
             'preferred_accounting_transaction_currency'))

    # system preferences
    system_pref_configurator_item =\
        preferences_business_configuration_save['4']
    self.assertEqual('System Preference Configurator Item',
        system_pref_configurator_item.getPortalType())

    # a standard bt5 for localisation
    bt5_business_configuration_item =\
          preferences_business_configuration_save['5']
    self.assertEqual('Standard BT5 Configurator Item',
            bt5_business_configuration_item.getPortalType())
    self.assertEqual(bt5_id,
            bt5_business_configuration_item.bt5_id)

  def stepCheckConfigureInstallationForm(self, sequence=None, sequence_list=None, **kw):
    """ Check the installation form """
    response_dict = sequence.get("response_dict")
    # configuration is finished. We are at the Install state.
    self.assertEqual('show', response_dict['command'])
    self.assertEqual('Previous', response_dict['previous'])
    self.assertEqual('Install', response_dict['next'])

    self.assertCurrentStep('Download', response_dict)

  def stepSetupInstallConfiguration(self, sequence=None, sequence_list=None, **kw):
    """ Install the Configuration """
    sequence.edit(next_dict={})

  def stepCheckInstallConfiguration(self, sequence=None, sequence_list=None, **kw):
    """ Check the installation of the configuration """
    response_dict = sequence.get("response_dict")
    self.assertEqual('install', response_dict['command'])

  def _stepCheckInstanceIsConfigured(self, business_configuration, bt5_tuple):
    """ Check if the instance is configured with proper business templates """
    # XXX FIXME (lucas): it should be a property of business configuration
    bc_id = '_'.join(business_configuration.getTitle().strip().lower().split())

    # check if bt5 are installed.
    bt5_title_list = self.portal.portal_templates.getInstalledBusinessTemplateTitleList()
    expected_list = self.expected_bt5_list + bt5_tuple
    self.assertEqual([i for i in expected_list if i not in bt5_title_list], [])

    self.assertNotIn(bc_id, bt5_title_list)

    bt = business_configuration.getSpecialiseValue(portal_type="Business Template")
    self.assertEqual(bc_id, bt.getTitle())
    self.assertEqual(bt.getInstallationState(), 'not_installed')

  def stepCheckConfiguredInstancePreference(self, sequence=None,  sequence_list=None, **kw):
    """ Check if the configured instance  has appropriate configuration"""

  def stepCheckInstanceIsConfiguredFrance(self, sequence=None,  sequence_list=None, **kw):
    """ Check if the instance is configured with French business templates """
    self._stepCheckInstanceIsConfigured(
                business_configuration=sequence.get('business_configuration'),
                bt5_tuple=('erp5_accounting_l10n_fr', 'erp5_l10n_fr',))

  def stepCheckInstanceIsConfiguredGermany(self, sequence=None,  sequence_list=None, **kw):
    """ Check if the instance is configured with German business templates """
    self._stepCheckInstanceIsConfigured(
                business_configuration=sequence.get('business_configuration'),
                bt5_tuple=('erp5_accounting_l10n_de_skr04', 'erp5_l10n_de',))

  def stepCheckInstanceIsConfiguredBrazil(self, sequence=None,  sequence_list=None, **kw):
    """ Check if the instance is configured with Brazilian business templates """
    self._stepCheckInstanceIsConfigured(
             business_configuration=sequence.get('business_configuration'),
             bt5_tuple=('erp5_accounting_l10n_br_extend', 'erp5_l10n_pt-BR',))

  def stepCheckInstanceIsConfiguredRussia(self, sequence=None,  sequence_list=None, **kw):
    """ Check if the instance is configured with Russian business templates """
    self._stepCheckInstanceIsConfigured(
             business_configuration=sequence.get('business_configuration'),
             bt5_tuple=('erp5_accounting_l10n_ru', 'erp5_l10n_ru',))

  def stepStartConfigurationInstallation(self, sequence=None, sequence_list=None, **kw):
    """ Starts the installation """
    business_configuration = sequence.get("business_configuration")
    self.portal.portal_configurator.startInstallation(
         business_configuration, REQUEST=self.portal.REQUEST)


  ###################################
  ## Test Configurator Security
  ###################################
  def stepViewAddGadget(self, sequence=None, sequence_list=None, **kw):
    """
       Test if gadget system is working.
    """
    for user_id in self._getUserIdList(self.all_username_list):
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
    for user_id in self._getUserIdList(self.all_username_list):
      self.failUnlessUserCanViewDocument(user_id, self.portal.event_module)
      self.failUnlessUserCanAccessDocument(user_id, self.portal.event_module)

  def stepAddEvent(self, sequence=None, sequence_list=None, **kw):
    """ Everybody can add events. """
    for user_id in self._getUserIdList(self.all_username_list):
      self.failUnlessUserCanAddDocument(user_id, self.portal.event_module)
      for event_type in ('Visit', 'Web Message', 'Letter', 'Note',
                         'Phone Call', 'Mail Message', 'Fax Message'):
        self._loginAsUser(user_id)
        event = self.portal.event_module.newContent(portal_type=event_type)
        self.failUnlessUserCanViewDocument(user_id, event)
        self.failUnlessUserCanAccessDocument(user_id, event)

  def stepSentEventWorkflow(self, sequence=None, sequence_list=None, **kw):
    for event_type in ('Visit', 'Web Message', 'Letter', 'Note',
                       'Phone Call', 'Mail Message', 'Fax Message'):
      event = self.portal.event_module.newContent(portal_type=event_type)
      # in draft state, we can view & modify
      for user_id in self._getUserIdList(self.all_username_list):
        self.failUnlessUserCanAccessDocument(user_id, event)
        self.failUnlessUserCanViewDocument(user_id, event)
        self.failUnlessUserCanModifyDocument(user_id, event)

      # everybody can cancel from draft
      for user_id in self._getUserIdList(self.all_username_list):
        self.failUnlessUserCanPassWorkflowTransition(
                    user_id, 'cancel_action', event)

      # everybody can plan
      for user_id in self._getUserIdList(self.all_username_list):
        self.failUnlessUserCanPassWorkflowTransition(
                    user_id, 'plan_action', event)

      event.plan()
      self.assertEqual('planned', event.getSimulationState())

      # everybody can confirm or send a planned event
      for user_id in self._getUserIdList(self.all_username_list):
        self.failUnlessUserCanPassWorkflowTransition(
                    user_id, 'confirm_action', event)
        self.failUnlessUserCanPassWorkflowTransition(
                    user_id, 'start_action', event)

      event.start()
      self.assertEqual('started', event.getSimulationState())

      # everybody can deliver a sent event
      for user_id in self._getUserIdList(self.all_username_list):
        self.failUnlessUserCanPassWorkflowTransition(
                    user_id, 'deliver_action', event)
      event.deliver()
      self.assertEqual('delivered', event.getSimulationState())

  ## Accounts {{{
  def stepViewAccountModule(self, sequence=None, sequence_list=None, **kw):
    """ everybody can view and access account module. """
    for user_id in self._getUserIdList(self.all_username_list):
      self.failUnlessUserCanViewDocument(user_id,
                              self.portal.account_module)
      self.failUnlessUserCanAccessDocument(user_id,
                              self.portal.account_module)

  def stepAddAccountModule(self, sequence=None, sequence_list=None, **kw):
    """ only accountants can add accounts. """
    for user_id in self._getUserIdList(self.accountant_username_list):
      self.failUnlessUserCanAddDocument(user_id,
                    self.portal.account_module)
    if self.restricted_security:
      for user_id in self._getUserIdList(self.all_username_list - self.accountant_username_list):
        self.failIfUserCanAddDocument(user_id,
                      self.portal.account_module)

  def stepViewAccount(self, sequence=None, sequence_list=None, **kw):
    account = self.portal.account_module.newContent(
        portal_type='Account',
        account_type='expense',
    )
    # in draft state,
    self.assertEqual('draft', account.getValidationState())
    # everybody can see
    for user_id in self._getUserIdList(self.all_username_list):
      self.failUnlessUserCanViewDocument(user_id, account)
      self.failUnlessUserCanAccessDocument(user_id, account)

    # only accountants can modify
    for user_id in self._getUserIdList(self.accountant_username_list):
      self.failUnlessUserCanModifyDocument(user_id, account)
    if self.restricted_security:
      for user_id in self._getUserIdList(self.all_username_list - self.accountant_username_list):
        self.failIfUserCanModifyDocument(user_id, account)

    # only accountants can validate
    for user_id in self._getUserIdList(self.accountant_username_list):
      self.failUnlessUserCanPassWorkflowTransition(
                  user_id, 'validate_action', account)
    if self.restricted_security:
      for user_id in self._getUserIdList(self.all_username_list - self.accountant_username_list):
        self.failIfUserCanPassWorkflowTransition(
                    user_id, 'validate_action', account)

    account.validate()
    self.assertEqual('validated', account.getValidationState())
    # in validated state, every body can view, but *nobody* can modify
    for user_id in self._getUserIdList(self.all_username_list):
      self.failUnlessUserCanViewDocument(user_id, account)
      self.failUnlessUserCanAccessDocument(user_id, account)
      self.failIfUserCanModifyDocument(user_id, account)

    # only accountants can invalidate
    for user_id in self._getUserIdList(self.accountant_username_list):
      self.failUnlessUserCanPassWorkflowTransition(
                  user_id, 'invalidate_action', account)
    if self.restricted_security:
      for user_id in self._getUserIdList(self.all_username_list - self.accountant_username_list):
        self.failIfUserCanPassWorkflowTransition(
                  user_id, 'invalidate_action', account)

    account.invalidate()
    self.assertEqual('invalidated', account.getValidationState())
    # back in invalidated state, everybody can view
    for user_id in self._getUserIdList(self.all_username_list):
      self.failUnlessUserCanViewDocument(user_id, account)
      self.failUnlessUserCanAccessDocument(user_id, account)
    # only accountants can modify
    for user_id in self._getUserIdList(self.accountant_username_list):
      self.failUnlessUserCanModifyDocument(user_id, account)
    if self.restricted_security:
      for user_id in self._getUserIdList(self.all_username_list - self.accountant_username_list):
        self.failIfUserCanModifyDocument(user_id, account)

    account.delete()
    # nobody can view delete object, but we can still access, for safety
    for user_id in self._getUserIdList(self.all_username_list):
      self.failIfUserCanViewDocument(user_id, account)

  def stepCopyPasteAccount(self, sequence=None, sequence_list=None, **kw):
    # tests copy / pasting accounts from account module
    account = self.portal.account_module.newContent(
        portal_type='Account',
        account_type='expense',
    )
    # in draft state,
    self.assertEqual('draft', account.getValidationState())

    # everybody can see
    for user_id in self._getUserIdList(self.all_username_list):
      self.failUnlessUserCanViewDocument(user_id, account)
      self.failUnlessUserCanAccessDocument(user_id, account)

  def stepViewEntityModules(self, sequence=None, sequence_list=None, **kw):
    # Everybody can view entities.
    for user_id in self._getUserIdList(self.all_username_list):
      for module in [self.portal.person_module,
                     self.portal.organisation_module]:
        self.failUnlessUserCanViewDocument(user_id, module)
        self.failUnlessUserCanAccessDocument(user_id, module)

  def stepAddEntityModules(self, sequence=None, sequence_list=None, **kw):
    # Everybody can add entities.
    for user_id in self._getUserIdList(self.all_username_list):
      for module in [self.portal.person_module,
                     self.portal.organisation_module]:
        self.failUnlessUserCanAddDocument(user_id, module)

  def stepCopyAndPastePerson(self, sequence=None, sequence_list=None, **kw):
    # copy & paste in person module
    person = self.portal.person_module.newContent(
                                    portal_type='Person')

    for user_id in self._getUserIdList(self.all_username_list):
      self._loginAsUser(user_id)
      person.Base_createCloneDocument()

  def stepCopyAndPasteOrganisation(self, sequence=None, sequence_list=None, **kw):
    # copy & paste in organisation module
    organisation = self.portal.organisation_module.newContent(
                                    portal_type='Organisation')
    for user_id in self._getUserIdList(self.all_username_list):
      self._loginAsUser(user_id)
      organisation.Base_createCloneDocument()

  def stepEntityWorkflow(self, sequence=None, sequence_list=None, **kw):
    for module in [self.portal.person_module,
                   self.portal.organisation_module]:
      entity = module.newContent()
      # in draft state, we can view, modify & add
      for user_id in self._getUserIdList(self.all_username_list):
        self.failUnlessUserCanAccessDocument(user_id, entity)
        self.failUnlessUserCanViewDocument(user_id, entity)
        self.failUnlessUserCanModifyDocument(user_id, entity)
        self.failUnlessUserCanAddDocument(user_id, entity)

      # everybody can validate
      for user_id in self._getUserIdList(self.all_username_list):
        self.failUnlessUserCanPassWorkflowTransition(
                    user_id, 'validate_action', entity)
      entity.validate()
      self.assertEqual('validated', entity.getValidationState())

      # in validated state, we can still modify
      for user_id in self._getUserIdList(self.all_username_list):
        self.failUnlessUserCanAccessDocument(user_id, entity)
        self.failUnlessUserCanViewDocument(user_id, entity)
        self.failUnlessUserCanModifyDocument(user_id, entity)
        self.failUnlessUserCanAddDocument(user_id, entity)

      # and invalidate
      for user_id in self._getUserIdList(self.all_username_list):
        self.failUnlessUserCanPassWorkflowTransition(
                    user_id, 'invalidate_action', entity)

  def stepViewCreatedPersons(self, sequence=None, sequence_list=None, **kw):
    self.loginByUserName(user_name='test_configurator_user')
    business_configuration = sequence.get('business_configuration')
    person_list = self.getBusinessConfigurationObjectList(business_configuration, 'Person')
    self.assertNotEqual(0, len(person_list))

    for entity in person_list:
      for user_id in self._getUserIdList(self.all_username_list):
        self.failUnlessUserCanAccessDocument(user_id, entity)
        self.failUnlessUserCanViewDocument(user_id, entity)

  def stepViewCreatedOrganisations(self, sequence=None, sequence_list=None, **kw):
    self.loginByUserName(user_name='test_configurator_user')
    business_configuration = sequence.get('business_configuration')
    organisation_list = self.getBusinessConfigurationObjectList(business_configuration, 'Organisation')
    self.assertNotEqual(0, len(organisation_list))

    for entity in organisation_list:
      for user_id in self._getUserIdList(self.all_username_list):
        self.failUnlessUserCanAccessDocument(user_id, entity)
        self.failUnlessUserCanViewDocument(user_id, entity)

  def stepViewCreatedAssignemnts(self, sequence=None, sequence_list=None, **kw):
    self.loginByUserName(user_name='test_configurator_user')
    business_configuration = sequence.get('business_configuration')
    person_list = self.getBusinessConfigurationObjectList(business_configuration, 'Person')
    self.assertNotEqual(0, len(person_list))

    for person in person_list:
      found_one = 0
      for assignment in person.contentValues(portal_type='Assignment'):
        found_one = 1
        for user_id in self._getUserIdList(self.all_username_list):
          self.failUnlessUserCanAccessDocument(user_id, assignment)
          self.failUnlessUserCanViewDocument(user_id, assignment)
      self.assertTrue(found_one, 'No assignment found in %s' % person)

  # }}}

  ## Accounting Periods {{{
  def stepAddAccoutingPeriod(self, sequence=None, sequence_list=None, **kw):
    # Everybody can add accounting periods.
    organisation = self.portal.organisation_module.newContent(
                          portal_type='Organisation')
    for user_id in self._getUserIdList(self.all_username_list):
      self._loginAsUser(user_id)
      self.assertIn('Accounting Period',
            organisation.getVisibleAllowedContentTypeList())

  def stepValidatedAccountingPeriods(self, sequence=None, sequence_list=None, **kw):

    currency_id = sequence.get("currency_id")
    currency_value = getattr(self.portal.currency_module, currency_id)

    organisation = self.portal.organisation_module.newContent(
                          portal_type='Organisation',
                          price_currency_value=currency_value,
                          group='my_group')
    accounting_period = organisation.newContent(
                          portal_type='Accounting Period',
                          start_date=DateTime(2001, 1, 1),
                          stop_date=DateTime(2002, 12, 31))
    self.assertEqual(accounting_period.getSimulationState(), 'draft')

    # accountants can modify the period
    for user_id in self._getUserIdList(self.accountant_username_list):
      self.failUnlessUserCanModifyDocument(user_id, accounting_period)
    # accountants can cancel the period
    for user_id in self._getUserIdList(self.accountant_username_list):
      self.failUnlessUserCanPassWorkflowTransition(
          user_id, 'cancel_action', accounting_period)
    # accountants can start the period
    for user_id in self._getUserIdList(self.accountant_username_list):
      self.failUnlessUserCanPassWorkflowTransition(
          user_id, 'start_action', accounting_period)

    # once the period is started, nobody can modify
    accounting_period.start()
    self.assertEqual('started', accounting_period.getSimulationState())
    for user_id in self._getUserIdList(self.accountant_username_list):
      self.failIfUserCanModifyDocument(user_id, accounting_period)
    # accountants can still cancel the period
    for user_id in self._getUserIdList(self.accountant_username_list):
      self.failUnlessUserCanPassWorkflowTransition(
          user_id, 'cancel_action', accounting_period)
    # accountants can stop the period
    for user_id in self._getUserIdList(self.accountant_username_list):
      self.failUnlessUserCanPassWorkflowTransition(
          user_id, 'stop_action', accounting_period)
    # and reopen it
    accounting_period.stop()
    self.assertEqual('stopped', accounting_period.getSimulationState())
    for user_id in self._getUserIdList(self.accountant_username_list):
      self.failUnlessUserCanPassWorkflowTransition(
          user_id, 'restart_action', accounting_period)
    # but only accounting manager can close it
    accounting_manager_id, = self._getUserIdList([self.accounting_manager_reference])
    self.failUnlessUserCanPassWorkflowTransition(
          accounting_manager_id, 'deliver_action', accounting_period)
    if self.restricted_security:
      accounting_agent_id, = self._getUserIdList([self.accounting_agent_reference])
      self.failIfUserCanPassWorkflowTransition(
          accounting_agent_id, 'deliver_action', accounting_period)

  # }}}

  ## Payment Nodes (Bank Account & Credit Cards) {{{
  def stepViewBankAccount(self, sequence=None, sequence_list=None, **kw):
    # Everybody can view bank accounts.
    entity = self.portal.organisation_module.newContent(
                                               portal_type='Organisation')
    bank_account = entity.newContent(portal_type='Bank Account')
    # everybody can view in draft ...
    self.assertEqual('draft', bank_account.getValidationState())
    for user_id in self._getUserIdList(self.all_username_list):
      self.failUnlessUserCanViewDocument(user_id, bank_account)
      self.failUnlessUserCanAccessDocument(user_id, bank_account)
    # ... and validated states
    bank_account.validate()
    self.assertEqual('validated', bank_account.getValidationState())
    for user_id in self._getUserIdList(self.all_username_list):
      self.failUnlessUserCanViewDocument(user_id, bank_account)
      self.failUnlessUserCanAccessDocument(user_id, bank_account)

  def stepViewCreditCard(self, sequence=None, sequence_list=None, **kw):
    # Everybody can view credit cards
    entity = self.portal.organisation_module.newContent(
                                               portal_type='Organisation')
    ext_payment = entity.newContent(portal_type='Credit Card')
    # every body can view in draft ...
    self.assertEqual('draft', ext_payment.getValidationState())
    for user_id in self._getUserIdList(self.all_username_list):
      self.failUnlessUserCanViewDocument(user_id, ext_payment)
      self.failUnlessUserCanAccessDocument(user_id, ext_payment)
    # ... and validated states
    ext_payment.validate()
    self.assertEqual('validated', ext_payment.getValidationState())
    for user_id in self._getUserIdList(self.all_username_list):
      self.failUnlessUserCanViewDocument(user_id, ext_payment)
      self.failUnlessUserCanAccessDocument(user_id, ext_payment)

  def stepValidateAndModifyBankAccount(self, sequence=None, sequence_list=None, **kw):
    # Every body can modify Bank Accounts
    entity = self.portal.organisation_module.newContent(
                                               portal_type='Organisation')
    bank_account = entity.newContent(portal_type='Bank Account')
    # draft
    for user_id in self._getUserIdList(self.all_username_list):
      self.failUnlessUserCanModifyDocument(user_id, bank_account)
    for user_id in self._getUserIdList(self.all_username_list):
      self.failUnlessUserCanPassWorkflowTransition(user_id,
                'validate_action', bank_account)
    # validated
    bank_account.validate()
    self.assertEqual('validated', bank_account.getValidationState())
    for user_id in self._getUserIdList(self.all_username_list):
      self.failUnlessUserCanModifyDocument(user_id, bank_account)
    for user_id in self._getUserIdList(self.all_username_list):
      self.failUnlessUserCanPassWorkflowTransition(user_id,
                'invalidate_action', bank_account)
    # invalidated
    bank_account.invalidate()
    self.assertEqual('invalidated', bank_account.getValidationState())
    for user_id in self._getUserIdList(self.all_username_list):
      self.failUnlessUserCanModifyDocument(user_id, bank_account)
    for user_id in self._getUserIdList(self.all_username_list):
      self.failUnlessUserCanPassWorkflowTransition(user_id,
                'validate_action', bank_account)

  def stepValidateAndModifyCreditCard(self, sequence=None, sequence_list=None, **kw):
    # Every body can modify Credit Card
    entity = self.portal.organisation_module.newContent(
                                               portal_type='Organisation')
    credit_card = entity.newContent(portal_type='Credit Card')
    # draft
    for user_id in self._getUserIdList(self.all_username_list):
      self.failUnlessUserCanModifyDocument(user_id, credit_card)
    for user_id in self._getUserIdList(self.all_username_list):
      self.failUnlessUserCanPassWorkflowTransition(user_id,
                'validate_action', credit_card)
    # validated
    credit_card.validate()
    self.assertEqual('validated', credit_card.getValidationState())
    for user_id in self._getUserIdList(self.all_username_list):
      self.failUnlessUserCanModifyDocument(user_id, credit_card)
    for user_id in self._getUserIdList(self.all_username_list):
      self.failUnlessUserCanPassWorkflowTransition(user_id,
                'invalidate_action', credit_card)
    # invalidated
    credit_card.invalidate()
    self.assertEqual('invalidated', credit_card.getValidationState())
    for user_id in self._getUserIdList(self.all_username_list):
      self.failUnlessUserCanModifyDocument(user_id, credit_card)
    for user_id in self._getUserIdList(self.all_username_list):
      self.failUnlessUserCanPassWorkflowTransition(user_id,
                'validate_action', credit_card)

  def stepAddPaymentNodeInPerson(self, sequence=None, sequence_list=None, **kw):
    person = self.portal.person_module.newContent(portal_type='Person')
    for user_id in self._getUserIdList(self.all_username_list):
      self._loginAsUser(user_id)
      self.failUnlessUserCanAddDocument(user_id, person)
      self.assertIn('Bank Account',
                    person.getVisibleAllowedContentTypeList())
      self.assertIn('Credit Card',
                    person.getVisibleAllowedContentTypeList())
    # when the entity is validated, we can still add some payment nodes
    person.validate()
    self.portal.portal_caches.clearAllCache()
    for user_id in self._getUserIdList(self.all_username_list):
      self._loginAsUser(user_id)
      self.failUnlessUserCanAddDocument(user_id, person)
      self.assertIn('Bank Account',
                    person.getVisibleAllowedContentTypeList())
      self.assertIn('Credit Card',
                    person.getVisibleAllowedContentTypeList())

  def stepAddPaymentNodeInOrganisation(self, sequence=None, sequence_list=None, **kw):
    org = self.portal.organisation_module.newContent(
                                    portal_type='Organisation')
    for user_id in self._getUserIdList(self.all_username_list):
      self._loginAsUser(user_id)
      self.failUnlessUserCanAddDocument(user_id, org)
      self.assertIn('Bank Account',
                    org.getVisibleAllowedContentTypeList())
      self.assertIn('Credit Card',
                    org.getVisibleAllowedContentTypeList())
    # when the entity is validated, we can still add some payment nodes
    org.validate()
    self.portal.portal_caches.clearAllCache()
    for user_id in self._getUserIdList(self.all_username_list):
      self._loginAsUser(user_id)
      self.failUnlessUserCanAddDocument(user_id, org)
      self.assertIn('Bank Account',
                    org.getVisibleAllowedContentTypeList())
      self.assertIn('Credit Card',
                    org.getVisibleAllowedContentTypeList())

  def stepCopyAndPasteBankAccountInPerson(self, sequence=None, sequence_list=None, **kw):
    # everybody can cp bank accounts in persons
    person = self.portal.organisation_module.newContent(
                                    portal_type='Organisation')
    bank_account = person.newContent(
                              portal_type='Bank Account')
    for user_id in self._getUserIdList(self.all_username_list):
      self._loginAsUser(user_id)
      bank_account.Base_createCloneDocument()

  def stepCopyAndPasteBankAccountInOrganisation(self, sequence=None, sequence_list=None, **kw):
    # everybody can cp bank accounts in organisation
    organisation = self.portal.organisation_module.newContent(
                                    portal_type='Organisation')
    bank_account = organisation.newContent(
                              portal_type='Bank Account')
    for user_id in self._getUserIdList(self.all_username_list):
      self._loginAsUser(user_id)
      bank_account.Base_createCloneDocument()

  # }}}

  ## Accounting Module {{{
  def stepViewAccountingTransactionModule(self, sequence=None, sequence_list=None, **kw):
    for user_id in self._getUserIdList(self.all_username_list):
      self.failUnlessUserCanViewDocument(user_id,
              self.portal.accounting_module)
      self.failUnlessUserCanAccessDocument(user_id,
              self.portal.accounting_module)

  def stepAddAccountingTransactionModule(self, sequence=None, sequence_list=None, **kw):
    # Anyone can adds accounting transactions
    for user_id in self._getUserIdList(self.all_username_list):
      self.failUnlessUserCanAddDocument(user_id,
              self.portal.accounting_module)

  def stepCopyAndPasteAccountingTransactions(self, sequence=None, sequence_list=None, **kw):
    # Anyone can copy and paste accounting transaction.
    for portal_type in self._getAccountingTransactionTypeList():
      if portal_type != 'Balance Transaction':
        transaction = self.portal.accounting_module.newContent(
                                        portal_type=portal_type)
        for user_id in self._getUserIdList(self.all_username_list):
          self._loginAsUser(user_id)
          transaction.Base_createCloneDocument()

  def _getAccountingTransactionTypeList(self):
    module = self.portal.accounting_module
    return [ti for ti in module.getVisibleAllowedContentTypeList()
               if ti not in ('Balance Transaction', )]

  def stepAccountingTransaction(self, sequence=None, sequence_list=None, **kw):
    transaction = self.portal.accounting_module.newContent(
                      portal_type='Accounting Transaction',
                      start_date=DateTime(2001, 1, 1),
                      stop_date=DateTime(2001, 1, 1))
    self.assertEqual('draft', transaction.getSimulationState())
    for user_id in self._getUserIdList(self.all_username_list):
      self.assertUserCanViewDocument(user_id, transaction)
      self.assertUserCanAccessDocument(user_id, transaction)
    if self.restricted_security:
      for user_id in self._getUserIdList(self.all_username_list - self.accountant_username_list):
        self.failIfUserCanModifyDocument(user_id, transaction)
    for user_id in self._getUserIdList(self.accountant_username_list):
      self.failUnlessUserCanModifyDocument(user_id, transaction)
      self.failUnlessUserCanAddDocument(user_id, transaction)
    if self.restricted_security:
      for user_id in self._getUserIdList(self.all_username_list - self.accountant_username_list):
        self.failIfUserCanPassWorkflowTransition(user_id,
                                                 'cancel_action',
                                                 transaction)
        self.failIfUserCanPassWorkflowTransition(user_id,
                                                 'plan_action',
                                                 transaction)
        self.failIfUserCanPassWorkflowTransition(user_id,
                                                 'confirm_action',
                                                 transaction)
        self.failIfUserCanPassWorkflowTransition(user_id,
                                                 'start_action',
                                                 transaction)
        self.failIfUserCanPassWorkflowTransition(user_id,
                                                 'stop_action',
                                                 transaction)
    for user_id in self._getUserIdList(self.accountant_username_list):
      self.failUnlessUserCanPassWorkflowTransition(user_id,
                                               'cancel_action',
                                               transaction)
      self.failUnlessUserCanPassWorkflowTransition(user_id,
                                               'plan_action',
                                               transaction)
      self.failUnlessUserCanPassWorkflowTransition(user_id,
                                               'confirm_action',
                                               transaction)
      self.failUnlessUserCanPassWorkflowTransition(user_id,
                                               'stop_action',
                                               transaction)
      # TODO
      ### self.failUnlessUserCanPassWorkflowTransition(user_id,
      ###                                          'delete_action',
      ###                                          transaction)

    # (skip some states)
    transaction.start()
    self.assertEqual('started', transaction.getSimulationState())
    self.tic()

    for user_id in self._getUserIdList(self.all_username_list):
      # everybody can view
      self.assertUserCanViewDocument(user_id, transaction)
      self.assertUserCanAccessDocument(user_id, transaction)

    # only accountant can modify
    if self.restricted_security:
      for user_id in  self._getUserIdList(self.all_username_list - self.accountant_username_list):
        self.failIfUserCanModifyDocument(user_id, transaction)
        self.failIfUserCanAddDocument(user_id, transaction)

    if self.restricted_security:
      # only accountant can "stop"
      for user_id in self._getUserIdList(self.all_username_list - self.accountant_username_list):
        self.failIfUserCanPassWorkflowTransition(user_id,
                                                 'stop_action',
                                                 transaction)
        self.failIfUserCanPassWorkflowTransition(user_id,
                                                 'deliver_action',
                                                 transaction)
    for user_id in self._getUserIdList(self.accountant_username_list):
      self.failUnlessUserCanPassWorkflowTransition(user_id,
                                               'stop_action',
                                               transaction)

    transaction.stop()
    self.assertEqual('stopped', transaction.getSimulationState())
    for user_id in self._getUserIdList(self.all_username_list):
      # everybody can view
      self.assertUserCanViewDocument(user_id, transaction)
      self.assertUserCanAccessDocument(user_id, transaction)
      # nobody can modify
      self.failIfUserCanModifyDocument(user_id, transaction)
      self.failIfUserCanAddDocument(user_id, transaction)

    if self.restricted_security:
      for user_id in self._getUserIdList(self.all_username_list - self.accountant_username_list):
        self.failIfUserCanPassWorkflowTransition(user_id,
                                                 'restart_action',
                                                 transaction)
        self.failIfUserCanPassWorkflowTransition(user_id,
                                                 'deliver_action',
                                                 transaction)
        self.failIfUserCanPassWorkflowTransition(user_id,
                                                 'cancel_action',
                                                 transaction)

    for user_id in self._getUserIdList(self.accountant_username_list):
      self.failUnlessUserCanPassWorkflowTransition(user_id,
                                               'restart_action',
                                               transaction)
    # in started state, we can modify again, and go back to stopped state
    transaction.restart()
    self.assertEqual('started', transaction.getSimulationState())
    self.tic()

    for user_id in self._getUserIdList(self.accountant_username_list):
      self.failUnlessUserCanModifyDocument(user_id, transaction)
      self.failUnlessUserCanPassWorkflowTransition(user_id,
                                                  'stop_action',
                                                  transaction)

    # go back to stopped state
    transaction.stop()
    self.assertEqual('stopped', transaction.getSimulationState())

    # only accounting_manager can validate
    accounting_manager_id, = self._getUserIdList([self.accounting_manager_reference])
    self.failUnlessUserCanPassWorkflowTransition(accounting_manager_id,
                                            'deliver_action',
                                             transaction)
    if self.restricted_security:
      accounting_agent_id, = self._getUserIdList([self.accounting_agent_reference])
      self.failIfUserCanPassWorkflowTransition(accounting_agent_id,
                                              'deliver_action',
                                               transaction)

  def stepSaleInvoiceTransaction(self, sequence=None, sequence_list=None, **kw):
    transaction = self.portal.accounting_module.newContent(
                      portal_type='Sale Invoice Transaction',
                      start_date=DateTime(2001, 1, 1),
                      stop_date=DateTime(2001, 1, 1))
    self.assertEqual('draft', transaction.getSimulationState())
    for user_id in self._getUserIdList(self.all_username_list):
      self.assertUserCanViewDocument(user_id, transaction)
      self.assertUserCanAccessDocument(user_id, transaction)
    if self.restricted_security:
      for user_id in self._getUserIdList(self.all_username_list - self.accountant_username_list):
        self.failIfUserCanModifyDocument(user_id, transaction)
    for user_id in self._getUserIdList(self.accountant_username_list):
      self.failUnlessUserCanModifyDocument(user_id, transaction)
      self.failUnlessUserCanAddDocument(user_id, transaction)
    if self.restricted_security:
      for user_id in self._getUserIdList(self.all_username_list - self.accountant_username_list -
                       self.sales_and_purchase_username_list):
        self.failIfUserCanPassWorkflowTransition(user_id,
                                                 'cancel_action',
                                                 transaction)
        self.failIfUserCanPassWorkflowTransition(user_id,
                                                 'plan_action',
                                                 transaction)
        self.failIfUserCanPassWorkflowTransition(user_id,
                                                 'confirm_action',
                                                 transaction)
        self.failIfUserCanPassWorkflowTransition(user_id,
                                                 'stop_action',
                                                 transaction)

    for user_id in self._getUserIdList(self.sales_and_purchase_username_list):
      self.failUnlessUserCanPassWorkflowTransition(user_id,
                                                   'cancel_action',
                                                    transaction)
      self.failUnlessUserCanPassWorkflowTransition(user_id,
                                                   'plan_action',
                                                    transaction)
      self.failUnlessUserCanPassWorkflowTransition(user_id,
                                                   'confirm_action',
                                                    transaction)

    for user_id in self._getUserIdList(self.accountant_username_list):
      self.failUnlessUserCanPassWorkflowTransition(user_id,
                                               'cancel_action',
                                               transaction)
      self.failUnlessUserCanPassWorkflowTransition(user_id,
                                               'plan_action',
                                               transaction)
      self.failUnlessUserCanPassWorkflowTransition(user_id,
                                               'confirm_action',
                                               transaction)
      self.failUnlessUserCanPassWorkflowTransition(user_id,
                                               'stop_action',
                                               transaction)
      # TODO
      ### self.failUnlessUserCanPassWorkflowTransition(user_id,
      ###                                          'delete_action',
      ###                                          transaction)

    # (skip some states)
    transaction.start()
    self.assertEqual('started', transaction.getSimulationState())
    self.tic()

    for user_id in self._getUserIdList(self.all_username_list):
      # everybody can view
      self.assertUserCanViewDocument(user_id, transaction)
      self.assertUserCanAccessDocument(user_id, transaction)

    # only accountant can modify
    if self.restricted_security:
      for user_id in self._getUserIdList(self.all_username_list - self.accountant_username_list):
        self.failIfUserCanModifyDocument(user_id, transaction)
        self.failIfUserCanAddDocument(user_id, transaction)

    if self.restricted_security:
      # only accountant can "stop"
      for user_id in self._getUserIdList(self.all_username_list - self.accountant_username_list):
        self.failIfUserCanPassWorkflowTransition(user_id,
                                                 'stop_action',
                                                 transaction)
        self.failIfUserCanPassWorkflowTransition(user_id,
                                                 'deliver_action',
                                                 transaction)
    for user_id in self._getUserIdList(self.accountant_username_list):
      self.failUnlessUserCanPassWorkflowTransition(user_id,
                                               'stop_action',
                                               transaction)

    transaction.stop()
    self.assertEqual('stopped', transaction.getSimulationState())
    for user_id in self._getUserIdList(self.all_username_list):
      # everybody can view
      self.assertUserCanViewDocument(user_id, transaction)
      self.assertUserCanAccessDocument(user_id, transaction)
      # nobody can modify
      self.failIfUserCanModifyDocument(user_id, transaction)
      self.failIfUserCanAddDocument(user_id, transaction)

    if self.restricted_security:
      for user_id in self._getUserIdList(self.all_username_list - self.accountant_username_list):
        self.failIfUserCanPassWorkflowTransition(user_id,
                                                 'restart_action',
                                                 transaction)
        self.failIfUserCanPassWorkflowTransition(user_id,
                                                 'deliver_action',
                                                 transaction)
        self.failIfUserCanPassWorkflowTransition(user_id,
                                                 'cancel_action',
                                                 transaction)

    for user_id in self._getUserIdList(self.accountant_username_list):
      self.failUnlessUserCanPassWorkflowTransition(user_id,
                                               'restart_action',
                                               transaction)
    # in started state, we can modify again, and go back to stopped state
    transaction.restart()
    self.assertEqual('started', transaction.getSimulationState())
    self.tic()

    for user_id in self._getUserIdList(self.accountant_username_list):
      self.failUnlessUserCanModifyDocument(user_id, transaction)
      self.failUnlessUserCanPassWorkflowTransition(user_id,
                                                  'stop_action',
                                                  transaction)

    # go back to stopped state
    transaction.stop()
    self.assertEqual('stopped', transaction.getSimulationState())

    # only accounting_manager can validate
    accounting_manager_id, = self._getUserIdList([self.accounting_manager_reference])
    self.failUnlessUserCanPassWorkflowTransition(accounting_manager_id,
                                            'deliver_action',
                                             transaction)
    if self.restricted_security:
      accounting_agent_id, = self._getUserIdList([self.accounting_agent_reference])
      self.failIfUserCanPassWorkflowTransition(accounting_agent_id,
                                              'deliver_action',
                                               transaction)


  def stepPurchaseInvoiceTransaction(self, sequence=None, sequence_list=None, **kw):
    transaction = self.portal.accounting_module.newContent(
                      portal_type='Purchase Invoice Transaction',
                      start_date=DateTime(2001, 1, 1),
                      stop_date=DateTime(2001, 1, 1))
    self.assertEqual('draft', transaction.getSimulationState())
    for user_id in self._getUserIdList(self.all_username_list):
      self.assertUserCanViewDocument(user_id, transaction)
      self.assertUserCanAccessDocument(user_id, transaction)
    if self.restricted_security:
      for user_id in self._getUserIdList(self.all_username_list - self.accountant_username_list):
        self.failIfUserCanModifyDocument(user_id, transaction)
    for user_id in self._getUserIdList(self.accountant_username_list):
      self.failUnlessUserCanModifyDocument(user_id, transaction)
      self.failUnlessUserCanAddDocument(user_id, transaction)
    if self.restricted_security:
      for user_id in self._getUserIdList(self.all_username_list - self.accountant_username_list -
                       self.sales_and_purchase_username_list):
        self.failIfUserCanPassWorkflowTransition(user_id,
                                                 'cancel_action',
                                                 transaction)
        self.failIfUserCanPassWorkflowTransition(user_id,
                                                 'plan_action',
                                                 transaction)
        self.failIfUserCanPassWorkflowTransition(user_id,
                                                 'confirm_action',
                                                 transaction)
        self.failIfUserCanPassWorkflowTransition(user_id,
                                                 'stop_action',
                                                 transaction)

    for user_id in self._getUserIdList(self.sales_and_purchase_username_list):
      self.failUnlessUserCanPassWorkflowTransition(user_id,
                                                   'cancel_action',
                                                    transaction)
      self.failUnlessUserCanPassWorkflowTransition(user_id,
                                                   'plan_action',
                                                    transaction)
      self.failUnlessUserCanPassWorkflowTransition(user_id,
                                                   'confirm_action',
                                                    transaction)
      # XXX would require to go to confirmed state first
      # self.failIfUserCanPassWorkflowTransition(user_id,
      #                                         'start_action',
      #                                         transaction)


    for user_id in self._getUserIdList(self.accountant_username_list):
      self.failUnlessUserCanPassWorkflowTransition(user_id,
                                               'cancel_action',
                                               transaction)
      self.failUnlessUserCanPassWorkflowTransition(user_id,
                                               'plan_action',
                                               transaction)
      self.failUnlessUserCanPassWorkflowTransition(user_id,
                                               'confirm_action',
                                               transaction)
      self.failUnlessUserCanPassWorkflowTransition(user_id,
                                               'stop_action',
                                               transaction)
      # TODO
      ### self.failUnlessUserCanPassWorkflowTransition(user_id,
      ###                                          'delete_action',
      ###                                          transaction)

    # (skip some states)
    transaction.start()
    self.assertEqual('started', transaction.getSimulationState())
    self.tic()

    for user_id in self._getUserIdList(self.all_username_list):
      # everybody can view
      self.assertUserCanViewDocument(user_id, transaction)
      self.assertUserCanAccessDocument(user_id, transaction)

    # only accountant can modify
    if self.restricted_security:
      for user_id in self._getUserIdList(self.all_username_list - self.accountant_username_list):
        self.failIfUserCanModifyDocument(user_id, transaction)
        self.failIfUserCanAddDocument(user_id, transaction)

    if self.restricted_security:
      # only accountant can "stop"
      for user_id in self._getUserIdList(self.all_username_list - self.accountant_username_list):
        self.failIfUserCanPassWorkflowTransition(user_id,
                                                 'stop_action',
                                                 transaction)
        self.failIfUserCanPassWorkflowTransition(user_id,
                                                 'deliver_action',
                                                 transaction)
    for user_id in self._getUserIdList(self.accountant_username_list):
      self.failUnlessUserCanPassWorkflowTransition(user_id,
                                               'stop_action',
                                               transaction)

    transaction.stop()
    self.assertEqual('stopped', transaction.getSimulationState())
    for user_id in self._getUserIdList(self.all_username_list):
      # everybody can view
      self.assertUserCanViewDocument(user_id, transaction)
      self.assertUserCanAccessDocument(user_id, transaction)
      # nobody can modify
      self.failIfUserCanModifyDocument(user_id, transaction)
      self.failIfUserCanAddDocument(user_id, transaction)

    if self.restricted_security:
      for user_id in self._getUserIdList(self.all_username_list - self.accountant_username_list):
        self.failIfUserCanPassWorkflowTransition(user_id,
                                                 'restart_action',
                                                 transaction)
        self.failIfUserCanPassWorkflowTransition(user_id,
                                                 'deliver_action',
                                                 transaction)
        self.failIfUserCanPassWorkflowTransition(user_id,
                                                 'cancel_action',
                                                 transaction)

    for user_id in self._getUserIdList(self.accountant_username_list):
      self.failUnlessUserCanPassWorkflowTransition(user_id,
                                               'restart_action',
                                               transaction)
    # in started state, we can modify again, and go back to stopped state
    transaction.restart()
    self.assertEqual('started', transaction.getSimulationState())
    self.tic()

    for user_id in self._getUserIdList(self.accountant_username_list):
      self.failUnlessUserCanModifyDocument(user_id, transaction)
      self.failUnlessUserCanPassWorkflowTransition(user_id,
                                                  'stop_action',
                                                  transaction)

    # go back to stopped state
    transaction.stop()
    self.assertEqual('stopped', transaction.getSimulationState())

    # only accounting_manager can validate
    accounting_manager_id, = self._getUserIdList([self.accounting_manager_reference])
    self.failUnlessUserCanPassWorkflowTransition(accounting_manager_id,
                                            'deliver_action',
                                             transaction)
    if self.restricted_security:
      accounting_agent_id, = self._getUserIdList([self.accounting_agent_reference])
      self.failIfUserCanPassWorkflowTransition(accounting_agent_id,
                                              'deliver_action',
                                               transaction)

  def stepPaymentTransaction(self, sequence=None, sequence_list=None, **kw):
    transaction = self.portal.accounting_module.newContent(
                      portal_type='Payment Transaction',
                      start_date=DateTime(2001, 1, 1),
                      stop_date=DateTime(2001, 1, 1))
    self.assertEqual('draft', transaction.getSimulationState())
    for user_id in self._getUserIdList(self.all_username_list):
      self.assertUserCanViewDocument(user_id, transaction)
      self.assertUserCanAccessDocument(user_id, transaction)
    if self.restricted_security:
      for user_id in self._getUserIdList(self.all_username_list - self.accountant_username_list):
        self.failIfUserCanModifyDocument(user_id, transaction)
    for user_id in self._getUserIdList(self.accountant_username_list):
      self.failUnlessUserCanModifyDocument(user_id, transaction)
      self.failUnlessUserCanAddDocument(user_id, transaction)
    if self.restricted_security:
      for user_id in self._getUserIdList(self.all_username_list - self.accountant_username_list):
        self.failIfUserCanPassWorkflowTransition(user_id,
                                                 'cancel_action',
                                                 transaction)
        self.failIfUserCanPassWorkflowTransition(user_id,
                                                 'plan_action',
                                                 transaction)
        self.failIfUserCanPassWorkflowTransition(user_id,
                                                 'confirm_action',
                                                 transaction)
        self.failIfUserCanPassWorkflowTransition(user_id,
                                                 'start_action',
                                                 transaction)
        self.failIfUserCanPassWorkflowTransition(user_id,
                                                 'stop_action',
                                                 transaction)
    for user_id in self._getUserIdList(self.accountant_username_list):
      self.failUnlessUserCanPassWorkflowTransition(user_id,
                                               'cancel_action',
                                               transaction)
      self.failUnlessUserCanPassWorkflowTransition(user_id,
                                               'plan_action',
                                               transaction)
      self.failUnlessUserCanPassWorkflowTransition(user_id,
                                               'confirm_action',
                                               transaction)
      self.failUnlessUserCanPassWorkflowTransition(user_id,
                                               'stop_action',
                                               transaction)
      # TODO
      ### self.failUnlessUserCanPassWorkflowTransition(user_id,
      ###                                          'delete_action',
      ###                                          transaction)

    # (skip some states)
    transaction.start()
    self.assertEqual('started', transaction.getSimulationState())
    self.tic()

    for user_id in self._getUserIdList(self.all_username_list):
      # everybody can view
      self.assertUserCanViewDocument(user_id, transaction)
      self.assertUserCanAccessDocument(user_id, transaction)

    # only accountant can modify
    if self.restricted_security:
      for user_id in self._getUserIdList(self.all_username_list - self.accountant_username_list):
        self.failIfUserCanModifyDocument(user_id, transaction)
        self.failIfUserCanAddDocument(user_id, transaction)

    # only accountant can "stop"
    if self.restricted_security:
      for user_id in self._getUserIdList(self.all_username_list - self.accountant_username_list):
        self.failIfUserCanPassWorkflowTransition(user_id,
                                                 'stop_action',
                                                 transaction)
        self.failIfUserCanPassWorkflowTransition(user_id,
                                                 'deliver_action',
                                                 transaction)
    for user_id in self._getUserIdList(self.accountant_username_list):
      self.failUnlessUserCanPassWorkflowTransition(user_id,
                                               'stop_action',
                                               transaction)

    transaction.stop()
    self.assertEqual('stopped', transaction.getSimulationState())
    for user_id in self._getUserIdList(self.all_username_list):
      # everybody can view
      self.assertUserCanViewDocument(user_id, transaction)
      self.assertUserCanAccessDocument(user_id, transaction)
      # nobody can modify
      self.failIfUserCanModifyDocument(user_id, transaction)
      self.failIfUserCanAddDocument(user_id, transaction)

    if self.restricted_security:
      for user_id in self._getUserIdList(self.all_username_list - self.accountant_username_list):
        self.failIfUserCanPassWorkflowTransition(user_id,
                                                 'restart_action',
                                                 transaction)
        self.failIfUserCanPassWorkflowTransition(user_id,
                                                 'deliver_action',
                                                 transaction)
        self.failIfUserCanPassWorkflowTransition(user_id,
                                                 'cancel_action',
                                                 transaction)

    for user_id in self._getUserIdList(self.accountant_username_list):
      self.failUnlessUserCanPassWorkflowTransition(user_id,
                                               'restart_action',
                                               transaction)
    # in started state, we can modify again, and go back to stopped state
    transaction.restart()
    self.assertEqual('started', transaction.getSimulationState())
    self.tic()

    for user_id in self._getUserIdList(self.accountant_username_list):
      self.failUnlessUserCanModifyDocument(user_id, transaction)
      self.failUnlessUserCanPassWorkflowTransition(user_id,
                                                  'stop_action',
                                                  transaction)

    # go back to stopped state
    transaction.stop()
    self.assertEqual('stopped', transaction.getSimulationState())

    # only accounting_manager can validate
    accounting_manager_id, = self._getUserIdList([self.accounting_manager_reference])
    self.failUnlessUserCanPassWorkflowTransition(accounting_manager_id,
                                            'deliver_action',
                                             transaction)
    if self.restricted_security:
      accounting_agent_id, = self._getUserIdList([self.accounting_agent_reference])
      self.failIfUserCanPassWorkflowTransition(accounting_agent_id,
                                              'deliver_action',
                                               transaction)

  def stepBalanceTransaction(self, sequence=None, sequence_list=None, **kw):
    # Balance Transaction must be viewable by users (creation & validation is
    # done from unrestricted code, so no problem)
    balance_transaction = self.portal.accounting_module.newContent(
                      portal_type='Balance Transaction')
    for user_id in self._getUserIdList(self.all_username_list):
      self.assertUserCanViewDocument(user_id, balance_transaction)
      self.assertUserCanAccessDocument(user_id, balance_transaction)

  def stepAccountingTransaction_getCausalityGroupedAccountingTransactionList(
      self, sequence=None, sequence_list=None, **kw):
    accounting_manager_id, = self._getUserIdList([self.accounting_manager_reference])
    self._loginAsUser(accounting_manager_id)
    accounting_transaction_x_related_to_a = self.portal.\
                                    accounting_module.newContent(
                                    portal_type='Accounting Transaction',
                                    start_date=DateTime(2010, 6, 1),
                                    stop_date=DateTime(2010, 6, 1))

    accounting_transaction_y_related_to_a = self.portal.\
                                    accounting_module.newContent(
                                    portal_type='Accounting Transaction',
                                    start_date=DateTime(2010, 6, 1),
                                    stop_date=DateTime(2010, 6, 1))

    accounting_transaction_a = self.portal.accounting_module.newContent(
                                    portal_type='Accounting Transaction',
                                    start_date=DateTime(2010, 6, 1),
                                    stop_date=DateTime(2010, 6, 1))

    accounting_transaction_b = self.portal.accounting_module.newContent(
                                    portal_type='Accounting Transaction',
                                    start_date=DateTime(2010, 6, 1),
                                    stop_date=DateTime(2010, 6, 1))

    accounting_transaction_c = self.portal.accounting_module.newContent(
                                   portal_type='Accounting Transaction',
                                   start_date=DateTime(2010, 6, 1),
                                   stop_date=DateTime(2010, 6, 1))

    accounting_transaction_x_related_to_a.setCausalityValue(\
                                                   accounting_transaction_a)

    accounting_transaction_y_related_to_a.setCausalityValue(\
                                                   accounting_transaction_a)


    accounting_transaction_a.setCausalityValueList([accounting_transaction_b,
                                                    accounting_transaction_c])
    self.tic()

    accounting_transaction_list = accounting_transaction_a.\
          AccountingTransaction_getCausalityGroupedAccountingTransactionList()

    self.assertEqual(5, len(accounting_transaction_list))

    self.assertIn(accounting_transaction_a, accounting_transaction_list)
    self.assertIn(accounting_transaction_b, accounting_transaction_list)
    self.assertIn(accounting_transaction_c, accounting_transaction_list)
    self.assertIn(accounting_transaction_x_related_to_a, \
                                                accounting_transaction_list)
    self.assertIn(accounting_transaction_y_related_to_a, \
                                                accounting_transaction_list)

    accounting_transaction_x_related_to_a.delete()
    accounting_transaction_y_related_to_a.cancel()
    self.tic()

    accounting_transaction_list = accounting_transaction_a.\
          AccountingTransaction_getCausalityGroupedAccountingTransactionList()

    self.assertEqual(3, len(accounting_transaction_list))

    self.assertNotIn(accounting_transaction_x_related_to_a, \
                                                accounting_transaction_list)
    self.assertNotIn(accounting_transaction_y_related_to_a, \
                                                accounting_transaction_list)

  # }}}

  ## Assignments / Login and Password {{{
  def stepAddAssignments(self, sequence=None, sequence_list=None, **kw):
    # for now, anybody can add assignements
    person = self.portal.person_module.newContent(portal_type='Person')
    for user_id in self._getUserIdList(self.all_username_list):
      self._loginAsUser(user_id)
      self.assertIn('Assignment',
                  person.getVisibleAllowedContentTypeList())
      self.failUnlessUserCanAddDocument(user_id, person)

  def stepAssignmentTI(self, sequence=None, sequence_list=None, **kw):
    ti = self.getTypesTool().getTypeInfo('Assignment')
    self.assertNotEqual(None, ti)
    # Acquire local roles on Assignment ? no
    self.assertFalse(ti.getProperty('type_acquire_local_role', 1))

  def stepEditAssignments(self, sequence=None, sequence_list=None, **kw):
    # everybody can open assignments in express
    person = self.portal.person_module.newContent(portal_type='Person')
    assignment = person.newContent(portal_type='Assignment')
    for user_id in self._getUserIdList(self.all_username_list):
      self.failUnlessUserCanModifyDocument(user_id, assignment)
      self.failUnlessUserCanPassWorkflowTransition(user_id,
                                                   'open_action',
                                                   assignment)
  # }}}

  # {{{ Trade
  def stepViewAcessAddPurchaseTradeCondition(self, sequence=None, sequence_list=None, **kw):
    module = self.portal.purchase_trade_condition_module
    for user_id in self._getUserIdList(self.all_username_list):
      self.assertUserCanViewDocument(user_id, module)
      self.assertUserCanAccessDocument(user_id, module)
    for user_id in self._getUserIdList(self.sales_and_purchase_username_list):
      self.assertUserCanAddDocument(user_id, module)
      self._loginAsUser(user_id)
      tc = module.newContent(portal_type='Purchase Trade Condition')
      self.assertUserCanViewDocument(user_id, tc)
      self.failUnlessUserCanPassWorkflowTransition(
                    user_id, 'validate_action', tc)
      self.portal.portal_workflow.doActionFor(tc, 'validate_action')
      self.failUnlessUserCanPassWorkflowTransition(
                    user_id, 'invalidate_action', tc)

  def stepViewAccessAddSaleTradeCondition(self, sequence=None, sequence_list=None, **kw):
    module = self.portal.sale_trade_condition_module
    for user_id in self._getUserIdList(self.all_username_list):
      self.assertUserCanViewDocument(user_id, module)
      self.assertUserCanAccessDocument(user_id, module)
    for user_id in self._getUserIdList(self.sales_and_purchase_username_list):
      self.assertUserCanAddDocument(user_id, module)
      self._loginAsUser(user_id)
      tc = module.newContent(portal_type='Sale Trade Condition')
      self.assertUserCanViewDocument(user_id, tc)
      self.failUnlessUserCanPassWorkflowTransition(
                    user_id, 'validate_action', tc)
      self.portal.portal_workflow.doActionFor(tc, 'validate_action')
      self.failUnlessUserCanPassWorkflowTransition(
                    user_id, 'invalidate_action', tc)

  def stepViewAccessAddSaleOrder(self, sequence=None, sequence_list=None, **kw):
    module = self.portal.sale_order_module
    for user_id in self._getUserIdList(self.all_username_list):
      self.assertUserCanViewDocument(user_id, module)
      self.assertUserCanAccessDocument(user_id, module)
    for user_id in self._getUserIdList(self.sales_and_purchase_username_list):
      self.assertUserCanAddDocument(user_id, module)
      self._loginAsUser(user_id)
      order = module.newContent(portal_type='Sale Order')
      self.assertUserCanViewDocument(user_id, order)
      self.failUnlessUserCanPassWorkflowTransition(
                    user_id, 'plan_action', order)
      self.failUnlessUserCanPassWorkflowTransition(
                    user_id, 'confirm_action', order)
      self.failUnlessUserCanPassWorkflowTransition(
                    user_id, 'cancel_action', order)

      order.confirm()
      self.assertEqual('confirmed', order.getSimulationState())
      self.assertUserCanViewDocument(user_id, order)
      self.failIfUserCanModifyDocument(user_id, order)


  def stepViewAccessAddSalePackingList(self, sequence=None, sequence_list=None, **kw):
    module = self.portal.sale_packing_list_module
    for user_id in self._getUserIdList(self.all_username_list):
      self.assertUserCanViewDocument(user_id, module)
      self.assertUserCanAccessDocument(user_id, module)
    for user_id in self._getUserIdList(self.sales_and_purchase_username_list):
      self.assertUserCanAddDocument(user_id, module)
      self._loginAsUser(user_id)
      pl = module.newContent(portal_type='Sale Packing List')
      self.assertUserCanViewDocument(user_id, pl)
      self.failUnlessUserCanPassWorkflowTransition(
                    user_id, 'confirm_action', pl)

  def stepViewAccessPurchaseOrder(self, sequence=None, sequence_list=None, **kw):
    module = self.portal.purchase_order_module
    for user_id in self._getUserIdList(self.all_username_list):
      self.assertUserCanViewDocument(user_id, module)
      self.assertUserCanAccessDocument(user_id, module)
    for user_id in self._getUserIdList(self.sales_and_purchase_username_list):
      self.assertUserCanAddDocument(user_id, module)
      self._loginAsUser(user_id)
      order = module.newContent(portal_type='Purchase Order')
      self.assertUserCanViewDocument(user_id, order)
      self.failUnlessUserCanPassWorkflowTransition(
                    user_id, 'plan_action', order)
      self.failUnlessUserCanPassWorkflowTransition(
                    user_id, 'confirm_action', order)
      self.failUnlessUserCanPassWorkflowTransition(
                    user_id, 'cancel_action', order)

      order.confirm()
      self.assertEqual('confirmed', order.getSimulationState())
      self.assertUserCanViewDocument(user_id, order)
      self.failIfUserCanModifyDocument(user_id, order)

  def stepPurchasePackingList(self, sequence=None, sequence_list=None, **kw):
    module = self.portal.purchase_packing_list_module
    for user_id in self._getUserIdList(self.all_username_list):
      self.assertUserCanViewDocument(user_id, module)
      self.assertUserCanAccessDocument(user_id, module)
    for user_id in self._getUserIdList(self.sales_and_purchase_username_list):
      self.assertUserCanAddDocument(user_id, module)
      self._loginAsUser(user_id)
      pl = module.newContent(portal_type='Purchase Packing List')
      self.assertUserCanViewDocument(user_id, pl)
      self.failUnlessUserCanPassWorkflowTransition(
                    user_id, 'confirm_action', pl)

  # }}}
  # web
  def stepWebSiteModule(self, sequence=None, sequence_list=None, **kw):
    """Anonymous should not be able to access web_site_module."""
    web_site_module = self.portal.web_site_module
    checkPermission = self.portal.portal_membership.checkPermission
    # switch to Anonymous user
    self.logout()
    self.assertEqual(None, checkPermission('View', web_site_module))
    self.assertEqual(None, checkPermission('Access Contents Information',web_site_module))
    self.assertRaises(Unauthorized,  web_site_module)

  # DMS
  def stepPortalContributionsTool(self, sequence=None, sequence_list=None, **kw):
    """
      TioLive user should be able to contribute from this tool
      (i.e. has Manage portal content).
    """
    portal_contributions = self.portal.portal_contributions
    checkPermission = self.portal.portal_membership.checkPermission
    for user_id in self._getUserIdList(self.all_username_list):
      self._loginAsUser(user_id)
      self.assertEqual(True,  \
                        checkPermission('Modify portal content', portal_contributions))
