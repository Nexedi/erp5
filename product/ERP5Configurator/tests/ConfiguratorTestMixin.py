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
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.SecurityTestCase import SecurityTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import  _getConversionServerDict
from AccessControl.SecurityManagement import newSecurityManager

class TestLiveConfiguratorWorkflowMixin(SecurityTestCase):
  """
    Configurator Mixin Class
  """
  # The list of standard business templates that the configurator should force
  # to install
  standard_bt5_list = ('erp5_simulation',
                       'erp5_dhtml_style',
                       'erp5_jquery',
                       'erp5_jquery_ui',
                       'erp5_xhtml_jquery_style',
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
                       'erp5_simplified_invoicing',
                       'erp5_ods_style',
                       'erp5_odt_style',
                       'erp5_ooo_import')

  def getBusinessTemplateList(self):
    return ('erp5_core_proxy_field_legacy',
        'erp5_full_text_myisam_catalog',
        'erp5_base',
        'erp5_workflow',
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
    self.login(user_name='test_configurator_user')
    # XXX (lucas): The request is not clean between tests.
    # So, we need to force the test to use a clean REQUEST
    # Otherwise the next test will fail trying to validate the form,
    # because the REQUEST has data from the previous step/test.
    if getattr(self.app.REQUEST, 'default_other', None) is None:
      self.app.REQUEST.default_other = self.app.REQUEST.other.copy()
    else:
      self.stepCleanUpRequest()

    self.restricted_security = 0
    # information to know if a business template is a standard business
    # template or a custom one
    self.portal.portal_templates.updateRepositoryBusinessTemplateList(
                           ['http://www.erp5.org/dists/snapshot/bt5/'])

    # it is required by SecurityTestCase
    self.workflow_tool = self.portal.portal_workflow
    self.setDefaultSitePreference()
    self.portal.portal_activities.unsubscribe()

  def setDefaultSitePreference(self):
    default_pref = self.portal.portal_preferences.default_site_preference
    conversion_dict = _getConversionServerDict()
    default_pref.setPreferredOoodocServerAddress(conversion_dict['hostname'])
    default_pref.setPreferredOoodocServerPortNumber(conversion_dict['port'])
    if self.portal.portal_workflow.isTransitionPossible(default_pref, 'enable'):
      default_pref.enable()
    return default_pref

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
    self.assertEquals(custom_bt5_config_item.bt5_title,
          '_'.join(business_configuration.getTitle().strip().lower().split()))

  def stepCheckConfigureOrganisationForm(self, sequence=None, sequence_list=None, **kw):
    """ Check if Confire Organisation step was showed """
    response_dict = sequence.get("response_dict")
    if 'command' in response_dict:
      self.assertEquals('show', response_dict['command'])
    self.assertEquals('Configure Organisation', response_dict['next'])
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

  def stepCheckConfigureUserAccountNumberForm(self, sequence=None, sequence_list=None, **kw):
    """ Check if Configure Organisation step was showed """
    response_dict = sequence.get("response_dict")
    if 'command' in response_dict:
      self.assertEquals('show', response_dict['command'])
    self.assertEquals('Configure user accounts number', response_dict['next'])
    self.assertEquals('Previous', response_dict['previous'])
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
      self.assertEquals('show', response_dict['command'])
    self.assertEquals('Previous', response_dict['previous'])
    self.assertEquals('Configure user accounts', response_dict['next'])
    self.assertCurrentStep('User accounts configuration', response_dict)

  def stepSetupMultipleUserAccountSix(self, sequence=None, sequence_list=None, **kw):
    """ Create multiple user account """
    next_dict = {}
    for user in self.user_list:
      for k, v in user.items():
        next_dict.setdefault(k, []).append(v)
    sequence.edit(next_dict=next_dict)

  def stepCheckMultiplePersonConfigurationItem(self, sequence=None, sequence_list=None, **kw):
    """ 
      Check if multiple Person Configuration Item of the Business
      Configuration have been created successfully.
    """
    business_configuration = sequence.get("business_configuration")
    self.assertEquals(int(self.company_employees_number),
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


    self.assertEquals(int(self.company_employees_number),
        len(person_business_configuration_save.contentValues()))
    return person_business_configuration_save

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

  def stepSetupAccountingConfigurationRussia(self, sequence=None, sequence_list=None, **kw):
    """ Setup up the Russian accounting configuration """
    next_dict = self._stepSetupAccountingConfiguration(accounting_plan='ru')
    sequence.edit(next_dict=next_dict)

  def stepCheckConfigurePreferenceForm(self, sequence=None, sequence_list=None, **kw):
    """ Check the preference form """
    response_dict = sequence.get("response_dict")
    if 'command' in response_dict:
      self.assertEquals('show', response_dict['command'])
    self.assertEquals('Previous', response_dict['previous'])
    import pdb;pdb.set_trace()
    self.assertEquals('Configure ERP5 Preferences', response_dict['next'])
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
    self.assertEquals(self.preference_group,
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
    """ Check the French accounting configuration item """
    self._stepCheckAccountingConfigurationItemList(
                business_configuration=sequence.get("business_configuration"),
                bt5_id='erp5_accounting_l10n_fr',
                accounting_transaction_gap='gap/fr/pcg',
                gap='fr/pcg/1/10/101')

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

  def _stepSetupPreferenceConfiguration(self, price_currency, lang):
    """ Setup the preference configuration """
    return dict(field_your_price_currency=price_currency,
                field_your_preferred_date_order='dmy',
                field_your_lang=lang,
                default_field_your_lang=1,)

  def stepSetupPreferenceConfigurationFrance(self, sequence=None, sequence_list=None, **kw):
    """ Setup the French preference configuration """
    next_dict = self._stepSetupPreferenceConfiguration(
                                               price_currency='EUR;0.01;Euro',
                                               lang='erp5_l10n_fr',)
    sequence.edit(next_dict=next_dict)

  def stepSetupPreferenceConfigurationBrazil(self, sequence=None, sequence_list=None, **kw):
    """ Setup the Brazil preference configuration """
    next_dict = self._stepSetupPreferenceConfiguration(
                                      price_currency='BRL;0.01;Brazilian Real',
                                      lang='erp5_l10n_pt-BR',)
    sequence.edit(next_dict=next_dict)

  def stepSetupPreferenceConfigurationRussia(self, sequence=None, sequence_list=None, **kw):
    """ Setup the Russian preference configuration """
    next_dict = self._stepSetupPreferenceConfiguration(
                                      price_currency='BYR;0.01;Belarusian Rouble',
                                      lang='erp5_l10n_ru',)
    sequence.edit(next_dict=next_dict)

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
    preferences_business_configuration_save = business_configuration.\
                      contentValues(portal_types='Configuration Save')[-1]
 
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

  def stepCheckPreferenceConfigurationItemListRussia(self, sequence=None, sequence_list=None, **kw):
    """
      Check the creation of:
      - Currency Configurator Item
      - Service Configurator Item
      - System Preference Configurator Item
      - Standard BT5 Configurator Item
    """
    self._stepCheckPreferenceConfigurationItemList(
                business_configuration=sequence.get("business_configuration"),
                currency_title='Belarusian Rouble',
                currency_reference='BYR',
                bt5_id='erp5_l10n_ru')

  def stepCheckConfigureInstallationForm(self, sequence=None, sequence_list=None, **kw):
    """ Check the installation form """
    response_dict = sequence.get("response_dict")
    # configuration is finished. We are at the Install state.
    self.assertEquals('show', response_dict['command'])
    self.assertEquals('Previous', response_dict['previous'])
    self.assertEquals('Install', response_dict['next'])

    self.assertCurrentStep('ERP5 installation', response_dict)

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

    
    self.assertFalse(bc_id in bt5_title_list)

    bt = business_configuration.getSpecialiseValue(portal_type="Business Template")
    self.assertEquals(bc_id, bt.getTitle())
    self.assertEquals(bt.getInstallationState(), 'not_installed')
    self.assertEquals(bt.getBuildingState(), 'built')


    # check for links
    file_list = business_configuration.searchFolder(portal_type="File")
    self.assertEquals(1, len(file_list))
    self.assertEquals(business_configuration.getSpecialiseTitle(), 
                      file_list[0].getTitle())

    file_title_list = ('%s' % bc_id,)
    self.assertSameSet(file_title_list, [f.getTitle() for f in file_list])

  def stepCheckConfiguredInstancePreference(sequence=None,  sequence_list=None, **kw):
    """ Check if the configured instance  has appropriate configuration"""

  def stepCheckInstanceIsConfiguredFrance(self, sequence=None,  sequence_list=None, **kw):
    """ Check if the instance is configured with French business templates """
    self._stepCheckInstanceIsConfigured(
                business_configuration=sequence.get('business_configuration'),
                bt5_tuple=('erp5_accounting_l10n_fr', 'erp5_l10n_fr',))

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

