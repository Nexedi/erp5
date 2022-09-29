##############################################################################
# Copyright (c) 2011 Nexedi SA and Contributors. All Rights Reserved.
#           Gabriel M. Monnerat <gabriel@tiolive.com>
#           Xavier Hardy <xavier.hardy@tiolive.com>
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

from Products.ERP5Type.tests.ERP5TypeTestCase import _getConversionServerUrlList
from Products.ERP5Type.tests.Sequence import SequenceList
from erp5.component.module.ConfiguratorTestMixin import \
                                             TestLiveConfiguratorWorkflowMixin

class TestRunMyDocsConfiguratorWorkflowMixin(TestLiveConfiguratorWorkflowMixin):
  """
    Test RunMyDocs Configuration Workflow Mixin.
  """

  standard_bt5_list = ('erp5_jquery',
                         'erp5_web',
                         'erp5_ingestion_mysql_innodb_catalog',
                         'erp5_ingestion',
                         'erp5_ui_test_core',
                         'erp5_dms',
                         'erp5_jquery_ui',
                         'erp5_slideshow_style',
                         'erp5_knowledge_pad',
                         'erp5_run_my_doc',
                         'erp5_run_my_doc_role')

  DEFAULT_SEQUENCE_LIST = """
     stepCreateBusinessConfiguration
     stepSetRunMyDocsWorkflow
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
     stepCheckSystemPreferenceAfterInstallation
     stepCheckKnowledgePadRole
  """

  def stepCreateBusinessConfiguration(self, sequence=None, sequence_list=None, **kw):
    """ Create one Business Configuration """
    module = self.portal.business_configuration_module
    business_configuration = module.newContent(
                               portal_type="Business Configuration",
                               title='Test Configurator RunMyDocs Workflow')
    next_dict = {}
    sequence.edit(business_configuration=business_configuration,
                  next_dict=next_dict)

  def stepSetRunMyDocsWorkflow(self, sequence=None, sequence_list=None, **kw):
    """ Set RunMyDocs Workflow into Business Configuration """
    business_configuration = sequence.get("business_configuration")
    self.setBusinessConfigurationWorkflow(business_configuration,
                                   "portal_workflow/run_my_doc_configuration_workflow")

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
    """ Check the multiple user account form """
    response_dict = sequence.get("response_dict")
    if 'command' in response_dict:
      self.assertEqual('show', response_dict['command'])
    self.assertEqual('Previous', response_dict['previous'])
    self.assertEqual('Configure ERP5 Preferences', response_dict['next'])
    self.assertCurrentStep('RunMyDoc Preferences', response_dict)

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

  def stepCheckSystemPreferenceAfterInstallation(self, sequence=None, sequence_list=None, **kw):
    """ Check System Preference"""
    system_preference = self.getDefaultSystemPreference()
    self.assertEqual(system_preference.getPreferredDocumentConversionServerUrlList(),
                     _getConversionServerUrlList())

  def _stepCheckKnowledgePadRole(self):
    """ Check if Knowledge Pad is configured correctly """
    self.portal.ERP5Site_createDefaultKnowledgePadListForUser()
    self.tic()
    current_user = self.portal.portal_membership.getAuthenticatedMember().getIdOrUserName()
    pad = self.portal.portal_catalog.getResultValue(portal_type="Knowledge Pad",
                                             owner=current_user)
    gadget_uid = self.portal.portal_gadgets.test_wizard_gadget.getUid()
    self.portal.KnowledgePad_addBoxList(uids=[gadget_uid],
                                        active_pad_relative_url=pad.getRelativeUrl())
    self.tic()
    self.assertEqual(len(pad.contentValues()), 1)
    box = pad.contentValues()[0]
    self.assertEqual(box.getValidationState(), 'visible')
    self.assertEqual(box.getSpecialise(), 'portal_gadgets/test_wizard_gadget')

class TestRunMyDocsConfiguratorWorkflowFranceLanguage(TestRunMyDocsConfiguratorWorkflowMixin):
  """
    Test RunMyDocs Configuration Workflow
  """

  def test_run_my_docs_workflow_france(self):
    """ Test the RunMyDocs workflow with french language """
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

  def stepCheckKnowledgePadRole(self, sequence=None, sequence_list=None, **kw):
    self.loginByUserName("french_creator")
    self._stepCheckKnowledgePadRole()



class TestRunMyDocsConfiguratorWorkflowBrazilLanguage(TestRunMyDocsConfiguratorWorkflowMixin):
  """
    Test RunMyDocs Configuration Workflow
  """

  def test_run_my_docs_workflow_brazil(self):
    """ Test the RunMyDocs workflow with brazilian language """
    sequence_list = SequenceList()
    sequence_string = self.DEFAULT_SEQUENCE_LIST % dict(country='Brazil')
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

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

  def stepCheckKnowledgePadRole(self, sequence=None, sequence_list=None, **kw):
    self.loginByUserName("person_creator")
    self._stepCheckKnowledgePadRole()
