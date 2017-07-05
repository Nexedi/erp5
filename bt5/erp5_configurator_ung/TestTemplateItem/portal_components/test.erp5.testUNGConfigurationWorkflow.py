##############################################################################
# Copyright (c) 2011 Nexedi SA and Contributors. All Rights Reserved.
#           Gabriel M. Monnerat <gabriel@tiolive.com>
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

from Products.ERP5Type.tests.ERP5TypeTestCase import _getConversionServerUrl
from Products.ERP5Type.tests.Sequence import SequenceList
from Products.ERP5Configurator.tests.ConfiguratorTestMixin import \
                                             TestLiveConfiguratorWorkflowMixin

class TestUNGConfiguratorWorkflowMixin(TestLiveConfiguratorWorkflowMixin):
  """
    Test UNG Configuration Workflow Mixin.
  """

  standard_bt5_list = ('erp5_ingestion_mysql_innodb_catalog',
                       'erp5_simulation',
                       'erp5_dhtml_style',
                       'erp5_jquery',
                       'erp5_jquery_ui',
                       'erp5_web',
                       'erp5_ingestion',
                       'erp5_dms',
                       'erp5_crm',
                       'erp5_knowledge_pad',
                       'erp5_jquery_plugin_spinbtn',
                       'erp5_jquery_plugin_jgraduate',
                       'erp5_jquery_plugin_svgicon',
                       'erp5_jquery_plugin_hotkey',
                       'erp5_jquery_plugin_jquerybbq',
                       'erp5_jquery_plugin_svg_editor',
                       'erp5_jquery_plugin_sheet',
                       'erp5_jquery_plugin_mbmenu',
                       'erp5_jquery_plugin_jqchart',
                       'erp5_jquery_plugin_colorpicker',
                       'erp5_jquery_plugin_elastic',
                       'erp5_jquery_plugin_wdcalendar',
                       'erp5_jquery_sheet_editor',
                       'erp5_xinha_editor',
                       'erp5_svg_editor',
                       'erp5_email_reader',
                       'erp5_web_ung_core',
                       'erp5_web_ung_theme',
                       'erp5_web_ung_role')

  DEFAULT_SEQUENCE_LIST = """
     stepCreateBusinessConfiguration
     stepSetUNGWorkflow
     stepConfiguratorNext
     stepTic
     stepCheckBT5ConfiguratorItem
     stepCheckConfigureOrganisationForm
     stepSetupOrganisationConfiguratorItem
     stepConfiguratorNext
     stepTic
     stepCheckConfigureUserAccountNumberForm
     stepCheckOrganisationConfiguratorItem
     stepSetupUserAccountNumberThree
     stepConfiguratorNext
     stepTic
     stepCheckConfigureMultipleUserAccountForm
     stepSetupMultipleUserAccountThree
     stepConfiguratorNext
     stepTic
     stepCheckConfigurePreferenceForm
     stepCheckMultipleUserAccountThree%(country)s
     stepSetupPreferenceConfiguration%(country)s
     stepConfiguratorNext
     stepTic
     stepCheckConfigureInstallationForm
     stepSetupInstallConfiguration
     stepConfiguratorNext
     stepTic
     stepCheckInstallConfiguration
     stepStartConfigurationInstallation
     stepTic
     stepCheckUNGWebSiteAfterInstallation
     stepCheckSystemPreferenceAfterInstallation
     stepCheckSitePreferenceAfterInstallation
     stepCheckWebSiteRoles
     stepCheckKnowledgePadRole
     stepCheckCreateNewEvent
  """

  def stepCreateBusinessConfiguration(self, sequence=None, sequence_list=None, **kw):
    """ Create one Business Configuration """
    module = self.portal.business_configuration_module
    business_configuration = module.newContent(
                               portal_type="Business Configuration",
                               title='Test Configurator UNG Workflow')
    next_dict = {}
    sequence.edit(business_configuration=business_configuration,
                  next_dict=next_dict)

  def stepSetUNGWorkflow(self, sequence=None, sequence_list=None, **kw):
    """ Set UNG Workflow into Business Configuration """
    business_configuration = sequence.get("business_configuration")
    self.setBusinessConfigurationWorkflow(business_configuration,
                                   "workflow_module/ung_configuration_workflow")

  def stepSetupOrganisationConfiguratorItem(self, sequence=None, sequence_list=None, **kw):
    """ Create one Organisation with Basic information """
    next_dict = dict(
        field_your_title='My Organisation',
        field_your_default_email_text='me@example.com',
        field_your_default_telephone_text='01234567890',
        field_your_default_address_street_address='.',
        field_your_default_address_zip_code='59000')
    sequence.edit(next_dict=next_dict)


  def stepCheckOrganisationConfiguratorItem(self, sequence=None, sequence_list=None, **kw):
    """ Check if organisation was created fine """
    business_configuration = sequence.get("business_configuration")
    organisation_config_save = business_configuration['3']
    self.assertEqual(organisation_config_save.getTitle(),
                      "My Organisation")
    self.assertEqual(1, len(organisation_config_save.contentValues()))
    organisation_config_item = organisation_config_save['1']
    self.assertEqual(organisation_config_item.getPortalType(),
                      'Organisation Configurator Item')
    self.assertEqual(organisation_config_item.getDefaultEmailText(),
                      'me@example.com')

  def stepSetupUserAccountNumberThree(self, sequence=None, sequence_list=None, **kw):
    """ Create one more user account """
    next_dict = dict(field_your_user_number="3")
    sequence.edit(next_dict=next_dict)

  def _stepSetupMultipleUserAccountThree(self, sequence, user_list):
    """ Generic step to create multiple user account """
    next_dict = {}
    for user in user_list:
      for k, v in user.items():
        next_dict.setdefault(k, []).append(v)
    sequence.edit(next_dict=next_dict)

  def stepCheckConfigurePreferenceForm(self, sequence=None, sequence_list=None, **kw):
    """ Check the preference form """
    response_dict = sequence.get("response_dict")
    if 'command' in response_dict:
      self.assertEqual('show', response_dict['command'])
    self.assertEqual('Previous', response_dict['previous'])
    self.assertEqual('Configure ERP5 Preferences', response_dict['next'])
    self.assertCurrentStep('UNG Preferences', response_dict)

  def stepSetupPreferenceConfigurationBrazil(self, sequence=None, sequence_list=None, **kw):
    """ Setup the Brazil preference configuration """
    next_dict = dict(field_your_preferred_date_order='dmy',
                     field_your_default_available_language='pt-BR',
                     field_your_preferred_event_sender_email="test@test.com",
                     default_field_your_lang=1)
    sequence.edit(next_dict=next_dict)

  def stepSetupPreferenceConfigurationFrance(self, sequence=None, sequence_list=None, **kw):
    """ Setup the France preference configuration """
    next_dict = dict(field_your_preferred_date_order='ymd',
                     field_your_default_available_language='fr',
                     field_your_preferred_event_sender_email="test@test.com",
                     default_field_your_lang=1)
    sequence.edit(next_dict=next_dict)

  def stepCheckMultipleUserAccountThreeBrazil(self, sequence=None, sequence_list=None, **kw):
     """ Check if the users were created correctly """
     business_configuration = sequence.get("business_configuration")
     person_config_save = business_configuration["5"]
     person_config_item = person_config_save["1"]
     self.assertEqual(person_config_item.getReference(), "person_creator")
     person_config_item = person_config_save["2"]
     self.assertEqual(person_config_item.getReference(), "person_assignee")
     person_config_item = person_config_save["3"]
     self.assertEqual(person_config_item.getReference(), "person_assignor")

  def stepCheckMultipleUserAccountThreeFrance(self, sequence=None, sequence_list=None, **kw):
     """ Check if the users were created correctly """
     business_configuration = sequence.get("business_configuration")
     person_config_save = business_configuration["5"]
     person_config_item = person_config_save["1"]
     self.assertEqual(person_config_item.getReference(), "french_creator")
     person_config_item = person_config_save["2"]
     self.assertEqual(person_config_item.getReference(), "french_assignee")
     person_config_item = person_config_save["3"]
     self.assertEqual(person_config_item.getReference(), "french_assignor")

  def stepCheckConfigureInstallationForm(self, sequence=None, sequence_list=None, **kw):
    """ Check the installation form """
    response_dict = sequence.get("response_dict")
    self.assertEqual('show', response_dict['command'])

  def stepCheckSystemPreferenceAfterInstallation(self, sequence=None, sequence_list=None, **kw):
    """ Check System Preference"""
    system_preference = self.getDefaultSystemPreference()
    self.assertEqual(system_preference.getPreferredDocumentConversionServerUrl(),
                     _getConversionServerUrl())

  def stepCheckSitePreferenceAfterInstallation(self, sequence=None, sequence_list=None, **kw):
    """ Check Site Preference"""
    preference = self.portal.portal_preferences.ung_preference
    self.assertEqual(preference.getPreferenceState(), "global")
  
  def _stepCheckWebSiteRoles(self):
    """ Check permission of Web Site with normal user """
    self.changeSkin("UNGDoc")
    self.portal.web_page_module.ERP5Site_createNewWebDocument("web_page_template")
    self.tic()
    self.changeSkin("UNGDoc")
    result_list = self.portal.web_site_module.ung.WebSection_getWebPageObjectList()
    self.assertEqual(len(result_list), 1)
    self.assertEqual(result_list[0].getTitle(), "Web Page")
    new_object = self.portal.web_page_module.newContent(portal_type="Web Page")
    new_object.edit(title="New")
    new_object = self.portal.web_page_module.newContent(portal_type="Web Table")
    new_object.edit(title="New")
    new_object = self.portal.web_page_module.newContent(portal_type="Web Illustration")
    new_object.edit(title="New")
    self.tic()
    kw = {"portal_type": "Web Page", "title": "New"}
    self.changeSkin("UNGDoc")
    result_list = self.portal.web_site_module.ung.WebSection_getWebPageObjectList(**kw)
    self.assertEqual(len(result_list), 1)
    self.assertEqual(result_list[0].getPortalType(), "Web Page")
    kw["portal_type"] = "Web Illustration"
    self.changeSkin("UNGDoc")
    result_list = self.portal.web_site_module.ung.WebSection_getWebPageObjectList(**kw)
    self.assertEqual(len(result_list), 1)
    self.assertEqual(result_list[0].getPortalType(), "Web Illustration")
    kw["portal_type"] = "Web Table"
    self.changeSkin("UNGDoc")
    result_list = self.portal.web_site_module.ung.WebSection_getWebPageObjectList(**kw)
    self.assertEqual(len(result_list), 1)
    self.assertEqual(result_list[0].getPortalType(), "Web Table")

  def _stepCheckKnowledgePadRole(self):
    """ Check if Knowledge Pad is configured correctly """
    pad = self.portal.knowledge_pad_module.newContent(portal_type="Knowledge Pad")
    pad.edit(publication_section_value=self.portal.web_site_module.ung)
    pad.visible()
    self.tic()
    gadget = self.portal.portal_gadgets.searchFolder()[0]
    gadget_id = gadget.getId()
    self.changeSkin("UNGDoc")
    self.portal.web_site_module.ung.WebSection_addGadgetList(gadget_id)
    self.tic()
    box_list = pad.contentValues()
    self.assertEqual(len(box_list), 1)
    knowledge_box = box_list[0]
    self.assertEqual(pad.getPublicationSection(), 'web_site_module/ung')
    self.assertTrue(knowledge_box.getSpecialiseValue().getId() == gadget_id)

  def _stepCheckCreateNewEvent(self):
    """ """
    portal = self.portal
    event_dict = dict(portal_type="Note",
                      title="Buy Phone",
                      event_text_content="testUNG Sample",
                      start_date_hour=11,
                      start_date_minute=12,
                      start_date_day=12,
                      start_date_month=02,
                      start_date_year=2011,
                      stop_date_hour=12,
                      stop_date_minute=12,
                      stop_date_day=13,
                      stop_date_month=02,
                      stop_date_year=2011)
    portal.REQUEST.form.update(event_dict)
    self.changeSkin("UNGDoc")
    portal.event_module.EventModule_createNewEvent()
    self.tic()
    event = portal.portal_catalog.getResultValue(portal_type="Note")
    self.assertEqual(event.getDescription(), "testUNG Sample")
    start_date = event.getStartDate()
    self.assertEqual(start_date.month(), 2)
    self.assertEqual(start_date.minute(), 12)
 

class TestUNGConfiguratorWorkflowFranceLanguage(TestUNGConfiguratorWorkflowMixin):
  """
    Test UNG Configuration Workflow
  """

  def test_ung_workflow_france(self):
    """ Test the ung workflow with french language """
    sequence_list = SequenceList()
    sequence_string = self.DEFAULT_SEQUENCE_LIST % dict(country='France')
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def stepSetupMultipleUserAccountThree(self, sequence=None, sequence_list=None, **kw):
    """ Create multiple user account """
    user_list = [
      dict(
        field_your_first_name='Person',
        field_your_last_name='Creator',
        field_your_reference="french_creator",
        field_your_password='person_creator',
        field_your_password_confirm='person_creator',
        field_your_default_email_text='test@test.com',
        field_your_default_telephone_text='',
      ), dict(
        field_your_first_name='Person',
        field_your_last_name='Assignee',
        field_your_reference="french_assignee",
        field_your_password='person_assignee',
        field_your_password_confirm='person_assignee',
        field_your_default_email_text='test@test.com',
        field_your_default_telephone_text='',
      ), dict(
        field_your_first_name='Person',
        field_your_last_name='Assignor',
        field_your_reference="french_assignor",
        field_your_password='person_assignor',
        field_your_password_confirm='person_assignor',
        field_your_default_email_text='test@test.com',
        field_your_default_telephone_text='',
      ),
    ]
    self._stepSetupMultipleUserAccountThree(sequence, user_list)

  def stepSetupWebSiteConfiguration(self, sequence=None, sequence_list=None, **kw):
    """ Setup Web Site """
    next_dict = dict(your_default_available_language="fr")
    sequence.edit(next_dict=next_dict)

  def stepCheckUNGWebSiteAfterInstallation(self, sequence=None, sequence_list=None, **kw):
    """ Check if UNG Web Site is published and your language"""
    ung_web_site = self.portal.web_site_module.ung
    portal_catalog = self.portal.portal_catalog
    self.assertEqual(ung_web_site.getValidationState(),
                      "published")
    self.assertEqual(ung_web_site.getDefaultAvailableLanguage(),
                      "fr")
    person = portal_catalog.getResultValue(portal_type="Person",
                                           reference="french_creator")
    self.assertEqual(person.getValidationState(), 'validated')
    self.assertEqual(person.getFirstName(), 'Person')
    self.assertEqual(person.getLastName(), 'Creator')
    assignment = person.contentValues(portal_type="Assignment")[0]
    self.assertEqual(assignment.getValidationState(), "open")
    self.assertEqual(assignment.getFunction(), "ung_user")
    person = portal_catalog.getResultValue(portal_type="Person",
                                           reference="french_assignee")
    self.assertEqual(person.getValidationState(), 'validated')
    self.assertEqual(person.getFirstName(), 'Person')
    self.assertEqual(person.getLastName(), 'Assignee')
    assignment = person.contentValues(portal_type="Assignment")[0]
    self.assertEqual(assignment.getValidationState(), "open")
    self.assertEqual(assignment.getFunction(), "ung_user")
    person = portal_catalog.getResultValue(portal_type="Person",
                                           reference="french_assignor")
    self.assertEqual(person.getValidationState(), 'validated')
    self.assertEqual(person.getFirstName(), 'Person')
    self.assertEqual(person.getLastName(), 'Assignor')
    assignment = person.contentValues(portal_type="Assignment")[0]
    self.assertEqual(assignment.getValidationState(), "open")
    self.assertEqual(assignment.getFunction(), "ung_user")

  def stepCheckWebSiteRoles(self, sequence=None, sequence_list=None, **kw):
    """ Check permission of Web Site with normal user """
    self.loginByUserName("french_assignor")
    self._stepCheckWebSiteRoles()

  def stepCheckKnowledgePadRole(self, sequence=None, sequence_list=None, **kw):
    self.loginByUserName("french_creator")
    self._stepCheckKnowledgePadRole()

  def stepCheckCreateNewEvent(self, sequence=None, sequence_list=None, **kw):
    self.loginByUserName("french_assignee")
    self._stepCheckCreateNewEvent()


class TestUNGConfiguratorWorkflowBrazilLanguage(TestUNGConfiguratorWorkflowMixin):
  """
    Test UNG Configuration Workflow
  """

  def test_ung_workflow_brazil(self):
    """ Test the ung workflow with brazilian language """
    sequence_list = SequenceList()
    sequence_string = self.DEFAULT_SEQUENCE_LIST % dict(country='Brazil')
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def stepSetupWebSiteConfiguration(self, sequence=None, sequence_list=None, **kw):
    """ Setup Web Site """
    next_dict = dict(your_default_available_language="pt-BR")
    sequence.edit(next_dict=next_dict)

  def stepSetupMultipleUserAccountThree(self, sequence=None, sequence_list=None, **kw):
    """ Create multiple user account """
    user_list = [
      dict(
        field_your_first_name='Person',
        field_your_last_name='Creator',
        field_your_reference="person_creator",
        field_your_password='person_creator',
        field_your_password_confirm='person_creator',
        field_your_default_email_text='test@test.com',
        field_your_default_telephone_text='',
      ), dict(
        field_your_first_name='Person',
        field_your_last_name='Assignee',
        field_your_reference="person_assignee",
        field_your_password='person_assignee',
        field_your_password_confirm='person_assignee',
        field_your_default_email_text='test@test.com',
        field_your_default_telephone_text='',
      ), dict(
        field_your_first_name='Person',
        field_your_last_name='Assignor',
        field_your_reference="person_assignor",
        field_your_password='person_assignor',
        field_your_password_confirm='person_assignor',
        field_your_default_email_text='test@test.com',
        field_your_default_telephone_text='',
      ),
    ]
    self._stepSetupMultipleUserAccountThree(sequence, user_list)

  def stepCheckUNGWebSiteAfterInstallation(self, sequence=None, sequence_list=None, **kw):
    """ Check if UNG Web Site is published and your language """
    ung_web_site = self.portal.web_site_module.ung
    portal_catalog = self.portal.portal_catalog
    self.assertEqual(ung_web_site.getValidationState(),
                      "published")
    self.assertEqual(ung_web_site.getDefaultAvailableLanguage(),
                      "pt-BR")
    person = portal_catalog.getResultValue(portal_type="Person",
                                           reference="person_creator")
    self.assertEqual(person.getValidationState(), 'validated')
    self.assertEqual(person.getFirstName(), 'Person')
    self.assertEqual(person.getLastName(), 'Creator')
    assignment = person.contentValues(portal_type="Assignment")[0]
    self.assertEqual(assignment.getValidationState(), "open")
    self.assertEqual(assignment.getFunction(), "ung_user")
    person = portal_catalog.getResultValue(portal_type="Person",
                                           reference="person_assignee")
    self.assertEqual(person.getValidationState(), 'validated')
    self.assertEqual(person.getFirstName(), 'Person')
    self.assertEqual(person.getLastName(), 'Assignee')
    assignment = person.contentValues(portal_type="Assignment")[0]
    self.assertEqual(assignment.getValidationState(), "open")
    self.assertEqual(assignment.getFunction(), "ung_user")
    person = portal_catalog.getResultValue(portal_type="Person",
                                           reference="person_assignor")
    self.assertEqual(person.getValidationState(), 'validated')
    self.assertEqual(person.getFirstName(), 'Person')
    self.assertEqual(person.getLastName(), 'Assignor')
    assignment = person.contentValues(portal_type="Assignment")[0]
    self.assertEqual(assignment.getValidationState(), "open")
    self.assertEqual(assignment.getFunction(), "ung_user")

  def stepCheckWebSiteRoles(self, sequence=None, sequence_list=None, **kw):
    """ Check permission of Web Site with normal user """
    self.loginByUserName("person_assignor")
    self._stepCheckWebSiteRoles()

  def stepCheckKnowledgePadRole(self, sequence=None, sequence_list=None, **kw):
    self.loginByUserName("person_creator")
    self._stepCheckKnowledgePadRole()

  def stepCheckCreateNewEvent(self, sequence=None, sequence_list=None, **kw):
    self.loginByUserName("person_assignee")
    self._stepCheckCreateNewEvent()
