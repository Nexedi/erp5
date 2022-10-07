##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#          Fabien Morin <fabien@nexedi.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################

import unittest
from Products.ERP5Type.tests.utils import reindex
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import DummyMailHost
from Products.ERP5Type.tests.Sequence import SequenceList
from DateTime import DateTime
import email, re
from email.header import decode_header, make_header
from email.utils import parseaddr
import cgi
import six.moves.urllib.parse

use_verbose_security = 0
if use_verbose_security:
  import AccessControl
  AccessControl.Implementation.setImplementation('python')
  AccessControl.ImplPython.setDefaultBehaviors(
              ownerous=True,
              authenticated=True,
              verbose=True)


class TestERP5Credential(ERP5TypeTestCase):

  def getTitle(self):
    return "ERP5 Credential"

  def getBusinessTemplateList(self):
    return (
      'erp5_full_text_mroonga_catalog',
      'erp5_core_proxy_field_legacy',
      'erp5_base',
      'erp5_jquery',
      'erp5_ingestion_mysql_innodb_catalog',
      'erp5_ingestion',
      'erp5_web',
      'erp5_crm',
      'erp5_credential',
      'erp5_administration')

  def afterSetUp(self):
    """Prepare the test."""
    self.createCategories()
    self.enableAlarm()
    self.validateNotificationMessages()
    # add a dummy mailhost not to send real messages
    if 'MailHost' in self.portal.objectIds():
      self.portal.manage_delObjects(['MailHost'])
    self.portal._setObject('MailHost', DummyMailHost('MailHost'))
    system_preference = self.getPreferenceTool().getActiveSystemPreference()
    if system_preference is None:
      system_preference = self.portal.portal_preferences.newContent(
        portal_type='System Preference')
      system_preference.enable()
    # clear modules if necessary
    module_list = (self.portal.getDefaultModule('Credential Request'),
        self.portal.getDefaultModule('Credential Update'),
        self.portal.getDefaultModule('Credential Recovery'),
        self.portal.getDefaultModule('Person'))
    for module in module_list:
      module.manage_delObjects(list(module.objectIds()))

  @reindex
  def enableAlarm(self):
    """activate the alarm"""
    portal = self.getPortalObject()
    alarm = portal.portal_alarms.accept_submitted_credentials
    if not alarm.isEnabled():
      alarm.setEnabled(True)

  def validateNotificationMessages(self):
    '''validate all notification messages'''
    portal = self.getPortalObject()
    notification_message_module = portal.getDefaultModule('Notification Message')
    for notification_message in notification_message_module.contentValues():
      if notification_message.getValidationState() == 'draft':
        notification_message.validate()

  @reindex
  def createCategories(self):
    """Create the categories for our test. """
    # create categories
    for cat_string in self.getNeededCategoryList():
      base_cat = cat_string.split("/")[0]
      # if base_cat not exist, create it
      if getattr(self.getPortal().portal_categories, base_cat, None) == None:
        self.getPortal().portal_categories.newContent(\
                                          portal_type='Base Category',
                                          id=base_cat)
      base_cat_value = self.getPortal().portal_categories[base_cat]
      for cat in cat_string.split("/")[1:]:
        if not cat in base_cat_value.objectIds():
          base_cat_value = base_cat_value.newContent(
                    portal_type='Category',
                    id=cat,
                    title=cat.replace('_', ' ').title(),)
        else:
          base_cat_value = base_cat_value[cat]
    # check categories have been created
    for cat_string in self.getNeededCategoryList():
      self.assertNotEqual(None,
                self.getCategoryTool().restrictedTraverse(cat_string),
                cat_string)

  def getNeededCategoryList(self):
    """return a list of categories that should be created."""
    return ('role/client/distributor',
            'role/internal',
            'role/media',
            'role/partner',
            'function/member',
            'function/manager',
            'function/agent',
            'site/dakar',
            'site/paris',
            'site/tokyo',
            'region/europe/fr',
           )

  def beforeTearDown(self):
    self.login()
    self.resetCredentialSystemPreference()
    self.tic()
    self.logout()

  def resetCredentialSystemPreference(self):
    self.login()
    preference = self._getPreference()
    preference.edit(preferred_credential_request_automatic_approval=False,
                    preferred_credential_recovery_automatic_approval=False,
                    preferred_organisation_credential_update_automatic_approval=False,
                    preferred_person_credential_update_automatic_approval=False,
                    preferred_credential_alarm_automatic_call=False,
                    preferred_subscription_assignment_category_list=[],
                    preferred_credential_contract_document_reference=None)
    self._enablePreference()

  # Copied from bt5/erp5_egov/TestTemplateItem/testEGovMixin.py
  def decode_email(self, file_):
    # Prepare result
    theMail = {
      'attachment_list': [],
      'body': '',
      # Place all the email header in the headers dictionary in theMail
      'headers': {}
    }
    # Get Message
    msg = email.message_from_string(file_)
    # Back up original file
    theMail['__original__'] = file_
    # Recode headers to UTF-8 if needed
    for key, value in msg.items():
      decoded_value_list = decode_header(value)
      unicode_value = make_header(decoded_value_list)
      new_value = unicode_value.__unicode__().encode('utf-8')
      theMail['headers'][key.lower()] = new_value
    # Filter mail addresses
    for header in ('resent-to', 'resent-from', 'resent-cc', 'resent-sender',
                   'to', 'from', 'cc', 'sender', 'reply-to'):
      header_field = theMail['headers'].get(header)
      if header_field:
        theMail['headers'][header] = parseaddr(header_field)[1]
    # Get attachments
    body_found = 0
    for part in msg.walk():
      content_type = part.get_content_type()
      file_name = part.get_filename()
      # multipart/* are just containers
      # XXX Check if data is None ?
      if content_type.startswith('multipart'):
        continue
      # message/rfc822 contains attached email message
      # next 'part' will be the message itself
      # so we ignore this one to avoid doubling
      elif content_type == 'message/rfc822':
        continue
      elif content_type in ("text/plain", "text/html"):
        charset = part.get_content_charset()
        payload = part.get_payload(decode=True)
        #LOG('CMFMailIn -> ',0,'charset: %s, payload: %s' % (charset,payload))
        if charset:
          payload = unicode(payload, charset).encode('utf-8')
        if body_found:
          # Keep the content type
          theMail['attachment_list'].append((file_name,
                                             content_type, payload))
        else:
          theMail['body'] = payload
          body_found = 1
      else:
        payload = part.get_payload(decode=True)
        # Keep the content type
        theMail['attachment_list'].append((file_name, content_type,
                                           payload))
    return theMail

  def _getPreference(self):
    portal_preferences = self.getPreferenceTool()
    preference = getattr(portal_preferences, 'test_site_preference', None)
    if preference is None:
      preference = portal_preferences.newContent(portal_type='System Preference',
                                title='Default Site Preference',
                                id='test_site_preference')
    return preference

  def _enablePreference(self):
    preference = self._getPreference()
    if preference.getPreferenceState() == 'disabled':
      preference.enable()

  def _disablePreference(self):
    preference = self._getPreference()
    if preference.getPreferenceState() in ('enabled', 'global'):
      preference.disable()

  def stepSetCredentialRequestAutomaticApprovalPreferences(self, sequence=None):
    self.login()
    preference = self._getPreference()
    automatic_call = sequence.get("automatic_call", True)
    preference.edit(preferred_credential_request_automatic_approval=True,
                    preferred_credential_alarm_automatic_call=automatic_call)
    self._enablePreference()
    self.tic()
    self.logout()

  def stepSetCredentialAssignmentPropertyList(self, sequence=None):
    if sequence is None:
      sequence = {}
    category_list = sequence.get("category_list",
        ["role/internal", "function/member"])
    self.login()
    preference = self._getPreference()
    preference.edit(preferred_subscription_assignment_category_list=category_list)
    self._enablePreference()
    self.tic()
    self.logout()

  def stepSetCredentialAssignmentDurationProperty(self, sequence=None):
    if sequence is None:
      sequence = {}
    assignment_duration = sequence.get("assignment_duration",
        20)
    self.login()
    preference = self._getPreference()
    preference.edit(preferred_credential_assignment_duration=assignment_duration)
    self._enablePreference()
    self.tic()
    self.logout()

  def stepSetOrganisationCredentialUpdateAutomaticApprovalPreferences(self,
      sequence=None, sequence_list=None, **kw):
    self.login()
    preference = self._getPreference()
    preference.edit(preferred_organisation_credential_update_automatic_approval=True)
    self._enablePreference()
    self.tic()
    self.logout()

  def stepSetCredentialRecoveryAutomaticApprovalPreferences(self, sequence=None,
      sequence_list=None, **kw):
    self.login()
    preference = self._getPreference()
    preference.edit(preferred_credential_recovery_automatic_approval=True)
    self._enablePreference()
    self.tic()
    self.logout()

  def stepSetPersonCredentialUpdateAutomaticApprovalPreferences(self, sequence=None,
      sequence_list=None, **kw):
    self.login()
    preference = self._getPreference()
    preference.edit(preferred_person_credential_update_automatic_approval=True)
    self._enablePreference()
    self.tic()
    self.logout()

  def stepCheckAssignmentAfterActiveLogin(self, sequence):
    portal_catalog = self.portal.portal_catalog
    reference = sequence["reference"]
    assignment_function = sequence["assignment_function"]
    assignment_role = sequence["assignment_role"]
    credential_request = portal_catalog.getResultValue(
        portal_type="Credential Request", reference=reference)
    mail_message = portal_catalog.getResultValue(portal_type="Mail Message",
        default_follow_up_uid=credential_request.getUid())
    self.tic()
    self.logout()
    self.portal.ERP5Site_activeLogin(mail_message.getReference())
    self.login()
    self.tic()
    person = self.portal.acl_users.getUser(reference).getUserValue()
    assignment_list = person.objectValues(portal_type="Assignment")
    self.assertEqual(len(assignment_list), 1)
    assignment = assignment_list[0]
    self.assertEqual(assignment.getFunction(), assignment_function)
    self.assertEqual(assignment.getRole(), assignment_role)
    
  def stepCheckAssignmentWithoutStopDate(self, sequence):
    reference = sequence["reference"]
    person = self.portal.acl_users.getUser(reference).getUserValue()
    assignment_list = person.objectValues(portal_type="Assignment")
    self.assertEqual(len(assignment_list), 1)
    assignment = assignment_list[0]
    self.assertEqual(assignment.getStartDate(), None)
    self.assertEqual(assignment.getStopDate(), None)

  def stepCheckAssignmentWithStopDate(self, sequence):
    reference = sequence["reference"]
    person = self.portal.acl_users.getUser(reference).getUserValue()
    assignment_list = person.objectValues(portal_type="Assignment")
    self.assertEqual(len(assignment_list), 1)
    assignment = assignment_list[0]
    self.assertNotEqual(assignment.getStartDate(), None)
    self.assertTrue(assignment.getStartDate() < DateTime())
    assignment_duration = sequence['assignment_duration']
    self.assertTrue(assignment.getStopDate() < DateTime()+assignment_duration)
    self.assertTrue(assignment.getStopDate() > DateTime()+assignment_duration-1)

  def getUserFolder(self):
    """Returns the acl_users. """
    return self.getPortal().acl_users

  def _assertUserExists(self, login, password):
    """Checks that a user with login and password exists and can log in to the
    system.
    """
    from Products.PluggableAuthService.interfaces.plugins import\
                                                      IAuthenticationPlugin
    uf = self.getUserFolder()
    for _, plugin in uf._getOb('plugins').listPlugins(IAuthenticationPlugin):
      if plugin.authenticateCredentials(
                  {'login': login, 'password': password}) is not None:
        break
    else:
      self.fail("No plugin could authenticate '%s' with password '%s'" %
              (login, password))

  def _assertUserDoesNotExists(self, login, password):
    """Checks that a user with login and password does not exists and cannot
    log in to the system.
    """
    from Products.PluggableAuthService.interfaces.plugins import\
                                                        IAuthenticationPlugin
    uf = self.getUserFolder()
    for plugin_name, plugin in uf._getOb('plugins').listPlugins(
                              IAuthenticationPlugin):
      if plugin.authenticateCredentials(
                {'login': login, 'password': password}) is not None:
        self.fail(
           "Plugin %s should not have authenticated '%s' with password '%s'" %
           (plugin_name, login, password))

  def stepCreateSimpleSubscriptionRequest(self, sequence=None, sequence_list=None,
      **kw):
    '''
    Create a simple subscription request
    '''
    request = self.portal.REQUEST
    request['PARENTS'] = [self.app]
    form_url = self.portal.absolute_url_path() + '/ERP5Site_viewNewCredentialRequestDialog'

    # logout to be annonymous
    self.logout()
    # check annonymous can access subscription form
    self.assertIn("Desired Login Name", request.traverse(form_url)())
    # fill in and submit the subscription form
    credential_reference = 'homie'
    result = self.portal.ERP5Site_newCredentialRequest(\
        first_name='Homer',
        last_name='Simpson',
        reference=credential_reference,
        password='secret',
        date_of_birth=DateTime('1970/01/01'),
        default_email_text='homer.simpson@fox.com',
        role_list=['internal'],
        )
    portal_status_message = sequence.get("portal_status_message",
        "Thanks%20for%20your%20registration.%20You%20will%20be%20receive%20an%20email%20to%20activate%20your%20account.")
    self.assertTrue('portal_status_message=%s' % portal_status_message in result, result)

    credential_request_module = self.portal.getDefaultModule('Credential Request')
    result = credential_request_module.contentValues(\
        portal_type='Credential Request', first_name='Homer',
        last_name='Simpson', reference='homie')
    self.assertEqual(len(result), 1)
    sequence.edit(subscription_request=result[0],
        login_reference=credential_reference)

  def stepAcceptSubscriptionRequest(self, sequence=None, sequence_list=None,
      **kw):
    self.login()
    subscription_request = sequence.get('subscription_request')
    subscription_request.accept()
    self.logout()

  def stepSubmitSubscriptionRequest(self, sequence=None, sequence_list=None,
      **kw):
    self.login()
    subscription_request = sequence.get('subscription_request')
    subscription_request.submit()
    self.logout()

  def stepCheckAccountIsCreated(self, sequence=None, sequence_list=None, **kw):
    # check a person have been created
    person_module = self.portal.getDefaultModule('Person')
    person_result = person_module.contentValues(reference='homie')
    self.assertEqual(len(person_result), 1)
    person = person_result[0].getObject()
    self.assertEqual(person.getTitle(), 'Homer Simpson')
    self.assertEqual(person.getDefaultEmailText(), 'homer.simpson@fox.com')

    # check homie can log in the system
    self._assertUserExists('homie', 'secret')
    self.loginByUserName('homie')
    from AccessControl import getSecurityManager
    self.assertEqual(getSecurityManager().getUser().getUserName(), 'homie')

  def stepCreateCredentialUpdate(self, sequence=None, sequence_list=None, **kw):
    '''
    Create a credential update object an fill it with some modified
    information
    '''
    self.login()
    # get the 'homie' person object
    result = self.portal.portal_catalog(portal_type='ERP5 Login', reference='homie')
    self.assertEqual(len(result), 1)
    homie = result[0].getParentValue()

    # create a credential update
    credential_update_module = self.portal.getDefaultModule(\
        'Credential Update')
    credential_update = credential_update_module.newContent(\
        first_name='Homie',
        last_name='Simpsons', # add a 's' to the end of the last_name
        reference='homie',
        password='new_password',
        default_email_text='homie.simpsons@fox.com',
        destination_decision=homie.getRelativeUrl())

    credential_update.submit()
    self.assertEqual(credential_update.getValidationState(), 'submitted')
    sequence.edit(credential_update=credential_update)

  def stepAcceptCredentialUpdate(self, sequence=None, sequence_list=None,
      **kw):
    credential_update = sequence.get('credential_update')
    credential_update.accept()

  def stepCheckCredentialUpdate(self, sequence=None, sequence_list=None,
      **kw):
    self.login()
    # check the user with the updated password exists
    self._assertUserExists('homie', 'new_password')
    # check the user with the old password don't exists anymore
    self._assertUserDoesNotExists('homie', 'secret')

    # check that informations on the person object have been updated
    related_login_result = self.portal.portal_catalog(portal_type='ERP5 Login', reference='homie')
    self.assertEqual(len(related_login_result), 1)
    related_person = related_login_result[0].getParentValue()
    self.assertEqual(related_person.getLastName(), 'Simpsons')
    self.assertEqual(related_person.getDefaultEmailText(),
    'homie.simpsons@fox.com')

  def stepCreateSubscriptionRequestWithSecurityQuestionCategory(self, sequence=None,
      sequence_list=None, **kw):
    request = self.portal.REQUEST
    request['PARENTS'] = [self.app]

    # fill in and submit the subscription form
    result = self._createCredentialRequest(\
        first_name='Homer',
        last_name='Simpson',
        reference='homie',
        password='secret',
        default_email_text='homer.simpson@fox.com',
        default_credential_question_question='credential/library_card_number',
        default_credential_question_answer='923R4293'
        )
    self.assertIn('portal_status_message=Thanks%20for%20your%20registration.%20You%20will%20be%20receive%20an%20email%20to%20activate%20your%20account.', result)

    self.tic()
    credential_request_module = self.portal.getDefaultModule('Credential Request')
    result = credential_request_module.contentValues(\
        portal_type='Credential Request', first_name='Homer',
        last_name='Simpson', reference='homie')
    self.assertEqual(len(result), 1)
    sequence.edit(subscription_request=result[0])

  def stepCheckSecurityQuestionCategoryAsBeenCopiedOnPersonObject(self, sequence=None,
      sequence_list=None, **kw):
    person_module = self.portal.getDefaultModule('Person')
    related_person_result = person_module.contentValues(reference='homie')
    self.assertEqual(len(related_person_result), 1)
    related_person = related_person_result[0]
    self.assertEqual(related_person.getDefaultCredentialQuestionQuestion(),
        'credential/library_card_number')
    self.assertEqual(related_person.getDefaultCredentialQuestionAnswer(),
        '923R4293')

  def stepCreateSubscriptionRequestWithSecurityQuestionFreeText(self, sequence=None,
      sequence_list=None, **kw):
    request = self.portal.REQUEST
    request['PARENTS'] = [self.app]

    # logout to be annonymous
    self.logout()
    # fill in and submit the subscription form
    result = self.portal.ERP5Site_newCredentialRequest(\
        first_name='Homer',
        last_name='Simpson',
        reference='homie',
        password='secret',
        default_email_text='homer.simpson@fox.com',
        default_credential_question_question_free_text='Which '\
            'car model do you have ?',
        default_credential_question_answer='Renault 4L'
        )
    self.assertIn('portal_status_message=Thanks%20for%20your%20registration.%20You%20will%20be%20receive%20an%20email%20to%20activate%20your%20account.', result)

    self.tic()
    credential_request_module = self.portal.getDefaultModule('Credential Request')
    result = credential_request_module.contentValues(\
        portal_type='Credential Request', first_name='Homer',
        last_name='Simpson', reference='homie')
    self.assertEqual(len(result), 1)
    sequence.edit(subscription_request=result[0])

  def stepCheckSecurityQuestionFreeTextAsBeenCopiedOnPersonObject(self, sequence=None,
      sequence_list=None, **kw):
    person_module = self.portal.getDefaultModule('Person')
    related_person_result = person_module.contentValues(reference='homie')
    self.assertEqual(len(related_person_result), 1)
    related_person = related_person_result[0]
    self.assertEqual(related_person.getDefaultCredentialQuestionQuestionFreeText(),
        'Which car model do you have ?')
    self.assertEqual(related_person.getDefaultCredentialQuestionAnswer(),
        'Renault 4L')

  def stepCreatePerson(self, sequence=None, sequence_list=None,
      **kw):
    """
      Create a simple person
    """
    portal = self.getPortalObject()
    # create a person with 'secret' as password
    self.login()
    person_module = portal.getDefaultModule('Person')
    person = person_module.newContent(title='Barney',
                             reference='barney',
                             start_date=DateTime('1970/01/01'),
                             default_email_text='barney@duff.com')
    # create an assignment
    assignment = person.newContent(portal_type='Assignment',
                      function='member')
    assignment.open()
    # create a login
    login = person.newContent(
      portal_type='ERP5 Login',
      reference=person.getReference() + '-login',
      password='secret',
    )
    login.validate()
    sequence.edit(person_reference=person.getReference(),
                  login_reference=login.getReference(),
                  default_email_text=person.getDefaultEmailText())

  def stepCreateSameEmailPersonList(self, sequence=None, sequence_list=None,
      **kw):
    """
      Create a list of person with same email
    """
    default_email_text = "bart@duff.com"
    person_list = []
    username_list = []
    for reference in ['userX', 'bart', 'homer']:
      portal = self.getPortalObject()
      # create a person with 'secret' as password
      self.login()
      person_module = portal.getDefaultModule('Person')
      person = person_module.newContent(title=reference,
                               reference=reference,
                               default_email_text=default_email_text)
      # create an assignment
      assignment = person.newContent(portal_type='Assignment',
                        function='member')
      assignment.open()
      username = person.getReference() + '-login'
      # create a login
      login = person.newContent(
        portal_type='ERP5 Login',
        reference=username,
        password='secret',
      )
      login.validate()
      person_list.append(person)
      username_list.append(username)

    sequence.edit(person_list=person_list,
                  username_list=username_list,
                  default_email_text=default_email_text)

  def stepCreateCredentialRecovery(self, sequence=None, sequence_list=None,
      **kw):
    '''
    Create a simple subscription request
    '''
    portal = self.getPortalObject()
    person_reference = sequence["person_reference"]
    login_reference = sequence["login_reference"]
    person = portal.portal_catalog.getResultValue(portal_type="Person",
        reference=person_reference)
    sequence.edit(barney=person)
    # check barney can log in the system
    self._assertUserExists('barney-login', 'secret')
    self.loginByUserName('barney-login')
    from AccessControl import getSecurityManager
    self.assertEqual(getSecurityManager().getUser().getIdOrUserName(), person.Person_getUserId())

    self.login()
    # create a credential recovery
    credential_recovery_module = portal.getDefaultModule('Credential Recovery')
    credential_recovery = credential_recovery_module.newContent(portal_type=\
        'Credential Recovery')

    # associate it with barney
    credential_recovery.setDestinationDecisionValue(person)
    credential_recovery.setReference(login_reference)
    sequence.edit(credential_recovery=credential_recovery)

  def stepCreateCredentialRecoveryForUsername(self, sequence=None, sequence_list=None,
      **kw):
    '''
    Create a credential recovery for username case
    '''
    portal = self.getPortalObject()
    default_email_text = sequence.get("default_email_text")
    query_kw = {"email.url_string" : default_email_text}
    result = portal.portal_catalog(portal_type="Email", parent_portal_type="Person", **query_kw)

    person_list = [x.getObject().getParentValue() for x in result]
    self.assertEqual(len(person_list), 3)
    sequence.edit(person_list=person_list)
    # create a credential recovery
    credential_recovery_module = portal.getDefaultModule('Credential Recovery')
    credential_recovery = credential_recovery_module.newContent(portal_type=\
        'Credential Recovery')

    # associate it with barney
    credential_recovery.setDestinationDecisionValueList(person_list)
    credential_recovery.setDefaultEmailText(default_email_text)
    sequence.edit(credential_recovery=credential_recovery)

  def stepRequestCredentialRecoveryWithERP5Site_newCredentialRecovery(self,
      sequence=None, sequence_list=None, **kw):
    login_reference = sequence["login_reference"]
    self.portal.ERP5Site_newCredentialRecovery(reference=login_reference)

  def stepRequestCredentialRecoveryWithERP5Site_newCredentialRecoveryByEmail(
     self, sequence=None, sequence_list=None, **kw):
    default_email_text = sequence["default_email_text"]
    self.portal.ERP5Site_newCredentialRecovery(
                    default_email_text=default_email_text)

  def stepLoginAsCurrentLoginReference(self, sequence=None,
      sequence_list=None, **kw):
    login_reference = sequence["login_reference"]
    self.loginByUserName(login_reference)

  def stepCreateCredentialUpdateWithERP5Site_newCredentialUpdate(self,
      sequence=None, sequence_list=None, **kw):
    self.portal.ERP5Site_newPersonCredentialUpdate(first_name="tom",
        default_email_text="tom@host.com")

  def stepCreateCredentialRecoveryWithSensitiveAnswer(self, sequence=None,
      sequence_list=None, **kw):
    login_reference = sequence["login_reference"]
    result = self.portal.ERP5Site_newCredentialRecovery(
        reference=login_reference,
        default_credential_question_question='credential/library_card_number',
        default_credential_question_answer='ABCDeF',
        )
    message_str = "You%20didn%27t%20enter%20the%20correct%20answer."
    self.assertNotIn(message_str, result)
    self.tic()
    self.login()
    result_list = self.portal.portal_catalog(
        portal_type='Credential Recovery', reference=login_reference)
    self.assertEqual(1, len(result_list))
    credential_recovery = result_list[0]
    sequence.edit(credential_recovery=credential_recovery)

  def stepSelectCredentialUpdate(self, sequence=None, sequence_list=None,
      **kw):
    self.login()
    credential_update = self.portal.portal_catalog.getResultValue(
        portal_type="Credential Update")
    sequence["credential_update"] = credential_update

  def stepCheckCredentialRecoveryCreation(self, sequence=None,
      sequence_list=None, **kw):
    login_reference = sequence["login_reference"]
    result_list = self.portal.portal_catalog(
        portal_type='Credential Recovery', reference=login_reference)
    self.assertEqual(1, len(result_list))
    credential_recovery = result_list[0]
    person = credential_recovery.getDestinationDecisionValue()
    self.assertEqual("Barney", person.getTitle())
    self.assertEqual("barney@duff.com", person.getEmailText())
    sequence["credential_recovery"] = credential_recovery

  def stepSubmitCredentialRecovery(self, sequence=None, sequence_list=None,
      **kw):
    credential_recovery = sequence.get('credential_recovery')
    credential_recovery.submit()

  def stepAcceptCredentialRecovery(self, sequence=None, sequence_list=None,
      **kw):
    credential_recovery = sequence.get('credential_recovery')
    credential_recovery.accept()

  def stepCheckEmailIsSent(self, sequence=None, sequence_list=None, **kw):
    '''
      Check an email containing the password reset link as been sent
    '''
    barney = sequence.get('barney')
    if not barney:
      reference = sequence.get('person_reference')
      barney = self.portal.portal_catalog.getResultValue(portal_type="Person",
          reference=reference)

    # after accept, an email is send containing the reset link
    last_message = self.portal.MailHost._last_message
    rawstr = r"""PasswordTool_viewResetPassword"""
    decoded_message = self.decode_email(last_message[2])
    body_message = decoded_message['body']
    match_obj = re.search(rawstr, body_message)

    # check the reset password link is in the mail
    self.assertNotEqual(match_obj, None)

    # check the mail is sent to the requester :
    send_to = decoded_message['headers']['to']
    self.assertEqual(barney.getDefaultEmailText(), send_to)

  def stepCheckEmailIsSentForUsername(self, sequence=None, sequence_list=None, **kw):
    '''
      Check an email containing the usernames as been sent
    '''
    # after accept, only one email is send containing the user names
    previous_message = self.portal.MailHost._previous_message
    last_message = self.portal.MailHost._last_message
    if len(previous_message):
      self.assertNotEqual(previous_message[2], last_message[2])
    decoded_message = self.decode_email(last_message[2])
    body_message = decoded_message['body']
    for username in sequence['username_list']:
      self.assertIn(username, body_message)

    # check the mail is sent to the requester :
    send_to = decoded_message['headers']['to']
    self.assertEqual(send_to, sequence['default_email_text'])

  def stepCheckPasswordChange(self, sequence=None, sequence_list=None, **kw):
    """
      check it's possible to change the user password using the link in the
      email
    """
    # get the url
    last_message = self.portal.MailHost._last_message
    rawstr = r"""PasswordTool_viewResetPassword"""
    decoded_message = self.decode_email(last_message[2])
    body_message = decoded_message['body']
    match_obj = re.search(rawstr, body_message)
    # check the reset password link is in the mail
    self.assertNotEqual(match_obj, None)
    url = None
    for line in body_message.splitlines():
      match_obj = re.search(rawstr, line)
      if match_obj is not None:
        url = line[line.find('http'):]
    url = url.strip()
    self.assertNotEqual(url, None)
    self.publish(url)
    parameters = cgi.parse_qs(six.moves.urllib.parse.urlparse(url)[4])
    self.assertTrue(
      'reset_key' in parameters,
      'reset_key not found in mail message : %s' % body_message
    )
    key = parameters['reset_key'][0]
    # before changing, check that the user exists with 'secret' password
    self._assertUserExists('barney-login', 'secret')
    self.portal.portal_password.changeUserPassword(user_login="barney-login",
                                                   password="new_password",
                                                   password_confirm="new_password",
                                                   password_key=key)
    self.tic()
    # reset the cache
    self.portal.portal_caches.clearAllCache()
    # check we cannot login anymore with the previous password 'secret'
    self._assertUserDoesNotExists('barney-login', 'secret')

    # check we can now login with the new password 'new_password'
    self._assertUserExists('barney-login', 'new_password')

  def _createCredentialRequest(self, first_name="Barney",
                               last_name="Simpson",
                               reference="barney",
                               password="secret",
                               default_email_text="barney@duff.com",
                               **kw):
    self.logout()
    result = self.portal.ERP5Site_newCredentialRequest(first_name=first_name,
        last_name=last_name,
        reference=reference,
        password=password,
        career_subordination_title="",
        default_email_text=default_email_text,
        default_telephone_text="223344",
        default_address_street_address="Test Street",
        default_address_city="Campos",
        default_address_zip_code="28024030",
        **kw)
    self.login()
    self.tic()
    return result

  def stepCreateCredentialRequestSample(self, sequence=None,
      sequence_list=None, **kw):
    credential_reference = "credential_reference"
    self._createCredentialRequest(reference=credential_reference)
    sequence.edit(credential_reference=credential_reference)

  def stepCheckIfMailMessageWasPosted(self, sequence=None,
      sequence_list=None, **kw):
    credential_reference_str = sequence["credential_reference"]
    portal_catalog = self.portal.portal_catalog
    credential_reference = portal_catalog.getResultValue(
        portal_type="Credential Request", reference=credential_reference_str)
    mail_message = portal_catalog.getResultValue(portal_type="Mail Message",
                        default_follow_up_uid=credential_reference.getUid())
    self.assertEqual(mail_message.getSimulationState(), "started")
    self.assertIn("key=%s" % mail_message.getReference(), mail_message.getTextContent())

  def stepSetPreferredCredentialAlarmAutomaticCallAsFalse(self, sequence):
    sequence.edit(automatic_call=False)

  def stepSetAssigneeRoleToCurrentPersonInCredentialUpdateModule(self,
      sequence=None, sequence_list=None, **kw):
    user, = self.portal.acl_users.searchUsers(login=sequence['login_reference'], exact_match=True)
    self.portal.credential_update_module.manage_setLocalRoles(user['id'],
        ['Assignor',])

  def stepSetAssigneeRoleToCurrentPersonInCredentialRecoveryModule(self,
      sequence=None, sequence_list=None, **kw):
    user, = self.portal.acl_users.searchUsers(login=sequence['login_reference'], exact_match=True)
    self.portal.credential_recovery_module.manage_setLocalRoles(user['id'],
        ['Assignor',])

  def stepLogin(self, sequence):
    self.login()

  def stepCheckPersonAfterSubscriptionRequest(self, sequence=None,
      sequence_list=None, **kw):
    self.login()
    person = self.portal.acl_users.getUser(sequence['login_reference']).getUserValue()
    self.assertEqual("Homer", person.getFirstName())
    self.assertEqual("Simpson", person.getLastName())
    self.assertEqual("homer.simpson@fox.com", person.getDefaultEmailText())
    self.assertEqual(DateTime('1970/01/01'), person.getStartDate())
    self.logout()

  def stepSetAuditorRoleToCurrentPerson(self, sequence=None,
      sequence_list=None, **kw):
    self.login()
    person = self.portal.acl_users.getUser(sequence['login_reference']).getUserValue()
    person.manage_setLocalRoles(person.Person_getUserId(), ["Auditor"])
    self.logout()

  def stepCheckPersonAfterUpdatePerson(self, sequence=None,
      sequence_list=None, **kw):
    person = self.portal.acl_users.getUser(sequence['login_reference']).getUserValue()
    self.assertEqual("tom", person.getFirstName())
    self.assertEqual("Simpson", person.getLastName())
    self.assertEqual("tom@host.com", person.getDefaultEmailText())
    self.assertEqual(DateTime('1970/01/01'), person.getStartDate())

  def stepCheckPersonWhenCredentialUpdateFail(self, sequence=None,
      sequence_list=None, **kw):
    person = self.portal.portal_catalog.getResultValue(
      reference=sequence["person_reference"], portal_type="Person")
    self.assertEqual("Barney", person.getFirstName())

  def stepCheckCredentialRecoveryNotEmptyDestinationDecision(self, sequence):
    credential_recovery = self.portal.portal_catalog.getResultValue(
       portal_type="Credential Recovery", sort_on=(("creation_date", "DESC"),),
       validation_state="submitted")
    self.assertNotEqual(None, credential_recovery.getDestinationDecisionValue())

  def test_01_simpleSubscriptionRequest(self):
    '''
    Check that is possible to subscribe to erp5
    '''
    sequence_list = SequenceList()
    sequence_string = 'CreateSimpleSubscriptionRequest Tic '\

    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_02_acceptSubscriptionRequest(self):
    '''
    Check that after approval, the account is created and the user is able to
    log in the system.
    '''
    sequence_list = SequenceList()
    sequence_string = 'SetCredentialAssignmentPropertyList '\
                      'CreateSimpleSubscriptionRequest Tic '\
                      'SubmitSubscriptionRequest Tic '\
                      'AcceptSubscriptionRequest Tic '\
                      'CheckAccountIsCreated Tic '\

    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_03_simpleCredentialUpdate(self):
    """
    Check it's possible to update credential informations using credential
    update
    """
    sequence_list = SequenceList()
    sequence_string = 'SetCredentialAssignmentPropertyList ' \
                      'CreateSimpleSubscriptionRequest '\
                      'SubmitSubscriptionRequest Tic '\
                      'AcceptSubscriptionRequest Tic '\
                      'CreateCredentialUpdate '\
                      'AcceptCredentialUpdate Tic '\
                      'CheckCredentialUpdate '\

    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def stepSetCredentialRequestCreatedMessage(self, sequence=None, **kw):
    sequence['portal_status_message'] = 'Credential%20Request%20Created'

  def test_04_automaticCredentialRequestApproval(self):
    '''
    if the property preferred_credential_request_automatic_approval is True on
    System Preference object. it means that the Credential Request object
    should be accepted automatically and account created without any human
    intervention.
    Check that the user is create without human intervention
    '''
    sequence_list = SequenceList()
    sequence_string = 'SetCredentialRequestAutomaticApprovalPreferences '\
                      'SetCredentialAssignmentPropertyList '\
                      'SetCredentialRequestCreatedMessage '\
                      'CreateSimpleSubscriptionRequest Tic '\
                      'CheckAccountIsCreated '\

    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_05_automaticCredentialUpdateApproval(self):
    '''
    if the property preferred_credential_update_automatic_approval is True on
    System Preference object. it means that the Credential Update object
    should be accepted automatically and account created without any human
    intervention.
    Check that the user is create without human intervention
    '''
    sequence_list = SequenceList()
    sequence_string = 'SetPersonCredentialUpdateAutomaticApprovalPreferences '\
                      'SetCredentialAssignmentPropertyList '\
                      'CreateSimpleSubscriptionRequest '\
                      'SubmitSubscriptionRequest Tic '\
                      'AcceptSubscriptionRequest Tic '\
                      'CheckAccountIsCreated '\
                      'CreateCredentialUpdate Tic '\
                      'CheckCredentialUpdate '\

    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_06_checkSecurityQuestionCategoryDefinition(self):
    '''
    Check that its possible to define a security question selecting a category
    or by entering free text.
    '''
    sequence_list = SequenceList()
    sequence_string = 'CreateSubscriptionRequestWithSecurityQuestionCategory '\
                      'SubmitSubscriptionRequest Tic '\
                      'AcceptSubscriptionRequest Tic '\
                      'CheckSecurityQuestionCategoryAsBeenCopiedOnPersonObject '\

    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_07_checkSecurityQuestionFreeTextDefinition(self):
    '''
    Check that its possible to define a security question selecting a category
    or by entering free text.
    '''
    sequence_list = SequenceList()
    sequence_string = 'CreateSubscriptionRequestWithSecurityQuestionFreeText '\
                      'SubmitSubscriptionRequest Tic '\
                      'AcceptSubscriptionRequest Tic '\
                      'CheckSecurityQuestionFreeTextAsBeenCopiedOnPersonObject '\

    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_08_passwordRecovery(self):
    '''
    check that a user that forget his password is able to set a new one and
    log in the system with this new password
    '''
    sequence_list = SequenceList()
    sequence_string = 'CreatePerson Tic '\
                      'CreateCredentialRecovery Tic '\
                      'SubmitCredentialRecovery Tic '\
                      'AcceptCredentialRecovery Tic '\
                      'CheckEmailIsSent Tic '\
                      'CheckPasswordChange Tic '\

    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_09_usernameRecovery(self):
    '''
    check that a user that forget his username(s) is able to
    get an email containing them
    '''
    sequence_list = SequenceList()
    sequence_string = 'CreateSameEmailPersonList Tic '\
                      'CreateCredentialRecoveryForUsername Tic '\
                      'SubmitCredentialRecovery Tic '\
                      'AcceptCredentialRecovery Tic '\
                      'CheckEmailIsSentForUsername'

    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def testMailMessagePosted(self):
    """ Test if the Mail Message was posted correctly """
    sequence_list = SequenceList()
    sequence_string = 'SetPreferredCredentialAlarmAutomaticCallAsFalse '\
                      'SetCredentialRequestAutomaticApprovalPreferences '\
                      'CreateCredentialRequestSample '\
                      'CheckIfMailMessageWasPosted '\

    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def testMailFromMailMessageEvent(self):
    """
      Check that the email is created correctly after create on Credentail
      Request with user's information
    """
    sequence = dict(automatic_call=False)
    self.stepSetCredentialRequestAutomaticApprovalPreferences(sequence)
    self._createCredentialRequest(first_name="Vifib",
                                 last_name="Test",
                                 reference="vifibtest")
    portal_catalog = self.portal.portal_catalog
    credential_request, = portal_catalog(
        portal_type="Credential Request", reference="vifibtest")
    mail_message = portal_catalog.getResultValue(
        portal_type="Mail Message",
        default_follow_up_uid=credential_request.getUid())
    last_message = self.portal.MailHost._last_message
    self.assertNotEqual((), last_message)
    mfrom, mto, message_text = last_message
    self.assertEqual(mfrom, 'Portal Administrator <postmaster@localhost>')
    self.assertEqual(['Vifib Test <barney@duff.com>'], mto)
    self.assertNotEqual(re.search(r"Subject\:.*Welcome", message_text), None)
    self.assertNotEqual(re.search(r"Hello\ Vifib\ Test\,", message_text), None)
    decoded_message = self.decode_email(last_message[2])
    body_message = decoded_message['body']
    self.assertNotEqual(re.search("key=%s" % mail_message.getReference(),
                                   body_message), None)

  def testAssignmentCreationUsingSystemPreferenceProperty(self):
    """
      Check that the category list are used correctly to create a new
      assignment
    """
    sequence = dict(automatic_call=False)
    self.stepSetCredentialRequestAutomaticApprovalPreferences(sequence)
    self.stepSetCredentialAssignmentPropertyList()
    self._createCredentialRequest()
    sequence = dict(reference="barney",
                   assignment_function="member",
                   assignment_role="internal")
    self.stepCheckAssignmentAfterActiveLogin(sequence)
    category_list = ["role/client", "function/agent"]
    self.stepSetCredentialAssignmentPropertyList(
        dict(category_list=category_list))
    self._createCredentialRequest(reference="credential_user")
    sequence = dict(reference="credential_user",
                   assignment_function="agent",
                   assignment_role="client")
    self.stepCheckAssignmentAfterActiveLogin(sequence)

  def testAssignmentCreationUsingSystemPreferenceDurationProperty(self):
    """
      Check that the category list are used correctly to create a new
      assignment
    """
    sequence = dict(automatic_call=False)
    self.stepSetCredentialRequestAutomaticApprovalPreferences(sequence)
    self.stepSetCredentialAssignmentPropertyList()
    self.stepSetCredentialAssignmentDurationProperty(
      dict(assignment_duration=0))
    self._createCredentialRequest()
    sequence = dict(reference="barney",
                   assignment_function="member",
                   assignment_role="internal")
    self.stepCheckAssignmentAfterActiveLogin(sequence)
    self.stepCheckAssignmentWithoutStopDate(sequence)
    category_list = ["role/client", "function/agent"]
    self.stepSetCredentialAssignmentPropertyList(
        dict(category_list=category_list))
    assignment_duration = 20
    self.stepSetCredentialAssignmentDurationProperty(
      dict(assignment_duration=assignment_duration))
    self._createCredentialRequest(reference="credential_user")
    sequence = dict(reference="credential_user",
                   assignment_function="agent",
                   assignment_role="client",
                   assignment_duration=assignment_duration)
    self.stepCheckAssignmentAfterActiveLogin(sequence)
    self.stepCheckAssignmentWithStopDate(sequence)

  def testERP5Site_activeLogin(self):
    """
      Test if the script WebSection_activeLogin will create one user
    correctly
    """
    sequence = dict(automatic_call=False)
    self.stepSetCredentialRequestAutomaticApprovalPreferences(sequence)
    self.stepSetCredentialAssignmentPropertyList()
    self.tic()
    self._createCredentialRequest()
    portal_catalog = self.portal.portal_catalog
    credential_request = portal_catalog.getResultValue(
        portal_type="Credential Request", reference="barney")
    mail_message = portal_catalog.getResultValue(portal_type="Mail Message",
        default_follow_up_uid=credential_request.getUid())
    self.logout()
    self.portal.ERP5Site_activeLogin(mail_message.getReference())
    self.login()
    self.tic()
    person = self.portal.acl_users.getUser('barney').getUserValue()
    assignment_list = person.objectValues(portal_type="Assignment")
    self.assertNotEqual(assignment_list, [])
    self.assertEqual(len(assignment_list), 1)
    assignment = assignment_list[0]
    self.assertEqual(assignment.getValidationState(), "open")
    self.assertEqual(person.getValidationState(), "validated")

  def testERP5Site_newCredentialRequest(self):
    """
      Check that the script ERP5Site_newCredentialRequest will create one
      Credential Request correctly
    """
    sequence = dict(automatic_call=False)
    self.stepSetCredentialRequestAutomaticApprovalPreferences(sequence)
    self.stepSetCredentialAssignmentPropertyList()
    self._createCredentialRequest()
    portal_catalog = self.portal.portal_catalog
    credential_request = portal_catalog.getResultValue(
        portal_type="Credential Request", reference="barney")
    self.assertEqual(credential_request.getFirstName(), "Barney")
    self.assertEqual(credential_request.getDefaultEmailText(),
        "barney@duff.com")
    self.assertEqual(credential_request.getRole(), "internal")
    self.assertEqual(credential_request.getFunction(), "member")

  def test_double_ERP5Site_newCredentialRequest(self):
    """Check that ERP5Site_newCredentialRequest will not create conflicting
       credentials."""
    sequence = dict(automatic_call=True)
    self.stepSetCredentialRequestAutomaticApprovalPreferences(sequence)
    self.stepSetCredentialAssignmentPropertyList()
    response = self._createCredentialRequest()
    self.assertIn('Credential%20Request%20Created.', response)
    portal_catalog = self.portal.portal_catalog
    credential_request = portal_catalog.getResultValue(
        portal_type="Credential Request", reference="barney")
    self.assertEqual(credential_request.getFirstName(), "Barney")
    self.assertEqual(credential_request.getDefaultEmailText(),
        "barney@duff.com")
    self.assertEqual(credential_request.getRole(), "internal")
    self.assertEqual(credential_request.getFunction(), "member")

    self.portal.portal_alarms.accept_submitted_credentials.activeSense()
    self.tic()
    self.assertEqual('accepted', credential_request.getValidationState())

    response = self._createCredentialRequest()
    self.assertIn('Selected%20login%20is%20already%20in%20use%2C%20pl'
      'ease%20choose%20different%20one',  response)

    self.portal.portal_alarms.accept_submitted_credentials.activeSense()
    self.tic()

  def test_double_ERP5Site_newCredentialRequest_indexation(self):
    """Check that ERP5Site_newCredentialRequest will react correctly in case
       if indexation is still ongoing."""
    sequence = dict(automatic_call=True)
    self.stepSetCredentialRequestAutomaticApprovalPreferences(sequence)
    self.stepSetCredentialAssignmentPropertyList()
    reference = self._testMethodName
    self.logout()
    response = self.portal.ERP5Site_newCredentialRequest(reference=reference,
        default_email_text='some@one.com',
        password="secret")
    self.login()
    self.assertIn('Credential%20Request%20Created.', response)
    self.commit()
    self.logout()
    response = self.portal.ERP5Site_newCredentialRequest(reference=reference,
        default_email_text='some@one.com',
        password="secret")
    self.login()
    # Now is time to assert that even if no reindexation was done yet, another
    # request will already refuse to create new credential request.
    self.assertIn('Selected%20login%20is%20already%20in%20use%2C%20pl'
      'ease%20choose%20different%20one', response)
    self.tic()
    # just to be sure that last response not resulted with creation of object
    self.assertEqual(1, self.portal.portal_catalog.countResults(
      portal_type='Credential Request', reference=reference)[0][0])

  def testERP5Site_newCredentialRecoveryWithNoSecurityQuestion(self):
    """
      Check that password recovery works when security question and answer are
      None
    """
    sequence_list = SequenceList()
    sequence_string = "CreatePerson Tic " \
           "RequestCredentialRecoveryWithERP5Site_newCredentialRecovery Tic " \
           "CheckCredentialRecoveryCreation " \
           "AcceptCredentialRecovery Tic "\
           "CheckEmailIsSent Tic "\
           "CheckPasswordChange "\

    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def testERP5Site_newCredentialUpdateWithNoSecurityQuestion(self):
    """
      Check that the script ERP5Site_newCredentialUpdate creates correctly one
      Credential Update object is create correctly and the user is updated with
      new properties
    """
    sequence_list = SequenceList()
    sequence_string = "CreateSimpleSubscriptionRequest Tic " \
           "SubmitSubscriptionRequest Tic " \
           "AcceptSubscriptionRequest Tic " \
           "stepCheckPersonAfterSubscriptionRequest " \
           "SetAuditorRoleToCurrentPerson " \
           "SetAssigneeRoleToCurrentPersonInCredentialUpdateModule Tic " \
           "LoginAsCurrentLoginReference " \
           "CreateCredentialUpdateWithERP5Site_newCredentialUpdate Tic " \
           "SelectCredentialUpdate " \
           "AcceptCredentialUpdate Tic "\
           "CheckPersonAfterUpdatePerson "\

    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_ERP5Site_newCredentialUpdate_change_password(self):
    reference = self._testMethodName
    person = self.portal.person_module.newContent(
        portal_type='Person',
        reference=reference,
        role='internal',
    )
    assignment = person.newContent(portal_type='Assignment', function='manager')
    assignment.open()
    # create a login
    username = person.getReference() + '-login'
    login = person.newContent(
        portal_type='ERP5 Login',
        reference=username,
        password='secret',
    )
    login.validate()
    old_password = login.getPassword()
    self.tic()

    self.login(person.getUserId())
    self.portal.ERP5Site_viewNewPersonCredentialUpdateDialog()
    ret = self.portal.ERP5Site_newPersonCredentialUpdate(password='new_password')
    self.assertEqual(
      six.moves.urllib.parse.parse_qs(six.moves.urllib.parse.urlparse(ret).query)['portal_status_message'],
      ['Password changed.'],
    )
    self.tic()
    self.assertNotEqual(login.getPassword(), old_password)
    self._assertUserExists(username, 'new_password')

  def test_no_reset_assignment_ERP5Site_newCredentialUpdate(self):
    """Checks that assignments are left intact after credential update"""
    reference = self._testMethodName
    person = self.portal.person_module.newContent(portal_type='Person',
      reference=reference,
      role='internal')
    assignment = person.newContent(portal_type='Assignment', function='manager')
    assignment.open()
    # create a login
    login = person.newContent(
      portal_type='ERP5 Login',
      reference=person.getReference() + '-login',
      password='secret',
    )
    login.validate()
    self.commit()
    credential_update = self.portal.credential_update_module.newContent(
        portal_type='Credential Update',
        first_name='Some Name',
        destination_decision_value=person
      )
    credential_update.submit()
    credential_update.accept()
    self.tic()

    self.assertEqual('Some Name', person.getFirstName())
    self.assertEqual('manager', assignment.getFunction())

  def stepCreatePersonWithQuestionUsingCamelCase(self, sequence):
    person_module = self.portal.getDefaultModule('Person')
    person = person_module.newContent(title='Barney',
                             reference='barney',
                             default_email_text='barney@duff.com')
    # create an assignment
    assignment = person.newContent(portal_type='Assignment',
                      function='member')
    assignment.open()
    # create a login
    login = person.newContent(
      portal_type='ERP5 Login',
      reference=person.getReference() + '-login',
      password='secret',
    )
    login.validate()
    sequence.edit(person_reference=person.getReference(),
                  login_reference=login.getReference())

  def test_checkCredentialQuestionIsNotCaseSensitive(self):
    '''
      Check that if the user enter an answer with a different case, this will still
    enought to reset his passord
    '''
    sequence_list = SequenceList()
    sequence_string = "CreatePersonWithQuestionUsingCamelCase Tic " \
        "LoginAsCurrentLoginReference " \
        "CreateCredentialRecoveryWithSensitiveAnswer Tic " \
        "AcceptCredentialRecovery Tic " \
        "CheckEmailIsSent Tic "\
        "CheckPasswordChange Tic "\

    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def _prepareContractAndPreference(self):
    self.contract_reference = self._testMethodName
    self.contract_content = 'My contract %s.' % self.contract_reference
    preference = self._getPreference()
    preference.edit(
      preferred_credential_contract_document_reference=self.contract_reference)
    self._enablePreference()
    # reset the cache in order to have this preference working
    self.portal.portal_caches.clearAllCache()

    self.contract = self.portal.web_page_module.newContent(
      portal_type='Web Page',
      reference=self.contract_reference,
      language='en',
      version='1',
      text_content=self.contract_content
    )
    self.contract.publish()
    self.tic()

  def test_ERP5Site_viewCredentialRequestForm_contract(self):
    """Check that if contract document is configured and it is published it
       is shown while using join form"""
    self._prepareContractAndPreference()
    # render the form anonymous...
    self.logout()
    result = self.portal.ERP5Site_viewCredentialRequestForm()
    # but check as superuser
    self.login()
    self.assertIn('%s/asStrippedHTML' % self.contract.getRelativeUrl(), result)

    # check if really contract has been correctly rendered
    self.logout()
    rendered = self.contract.asStrippedHTML()
    self.assertIn(self.contract_content, rendered)

  def test_ERP5Site_viewCredentialRequestForm_contract_web(self):
    """Check that if contract document is configured and it is published it
       is shown while using join form in Web site"""
    self._prepareContractAndPreference()

    # create cool web site
    web_site = self.portal.web_site_module.newContent(portal_type='Web Site')
    web_site.publish()
    self.tic()

    # render the form anonymous...
    self.logout()
    result = web_site.ERP5Site_viewCredentialRequestForm()
    # but check as superuser
    self.login()
    self.assertIn(self.contract_reference, result)

    # check if really contract has been correctly rendered
    self.logout()
    rendered = self.portal.unrestrictedTraverse('%s/%s' % (
        web_site.getRelativeUrl(), self.contract_reference)).getTextContent()
    self.assertIn(self.contract_content, rendered)

  def test_ERP5Site_viewCredentialRequestForm_no_contract(self):
    """Check that if no contract is configured none is shown nor it is not
       required to accept it"""
    self.logout()
    result = self.portal.ERP5Site_viewCredentialRequestForm()
    self.assertNotIn('Contract', result)
    self.assertNotIn('your_term_confirmation', result)

  def test_ERP5Site_newCredentialRecovery_using_default_email_text(self):
    """
      Check that using the script ERP5Site_newCredentialRecovery and passing
      the default_email_text, the login is recover correctly
    """
    sequence_list = SequenceList()
    sequence_string = "CreatePerson Tic " \
      "RequestCredentialRecoveryWithERP5Site_newCredentialRecoveryByEmail Tic " \
      "CheckCredentialRecoveryNotEmptyDestinationDecision"
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_ERP5Site_newCredentialRecovery_activity_fail_once(self):
    self.stepSetCredentialRecoveryAutomaticApprovalPreferences()
    self.login()
    person = self.portal.person_module.newContent(
        portal_type='Person',
        default_email_coordinate_text='nobody@example.com',
    )
    assignment = person.newContent(portal_type='Assignment', function='manager')
    assignment.open()
    login = person.newContent(
        portal_type='ERP5 Login',
        reference=self._testMethodName,
        password='secret',
    )
    login.validate()
    self.tic()

    ret = self.portal.ERP5Site_newCredentialRecovery(reference=self._testMethodName)
    self.assertEqual(
      six.moves.urllib.parse.parse_qs(six.moves.urllib.parse.urlparse(ret).query)['portal_status_message'],
      ['We have sent you an email to enable you to reset your password. Please check your inbox and your junk/spam mail for this email and follow the link to reset your password.'],
    )
    person.setDefaultEmailCoordinateText(None)
    # Execute alarm, it will fail because this person has no email
    with self.assertRaisesRegex(
        RuntimeError,
        "An email has been sent to you"):
      self.tic()

    # run alarm again, this does not cause another activity failure.
    self.portal.portal_alarms.accept_submitted_credentials.activeSense()
    with self.assertRaises(RuntimeError):
      self.tic()
    self.assertEqual(len(self.portal.portal_activities.getMessageList()), 1)
    self.portal.portal_activities.manageClearActivities()
    self.commit()

  def test_credential_request_properties(self):
    # test to prevent regression with a bug in property sheet definition
    cr = self.portal.credential_request_module.newContent(
      portal_type='Credential Request')
    self.assertEqual(cr.getDefaultAddressCity(), None)
    self.assertEqual(cr.getDefaultAddressRegion(), None)
    self.assertEqual(cr.getOrganisationDefaultAddressCity(), None)
    self.assertEqual(cr.getOrganisationDefaultAddressRegion(), None)

    cr.setDefaultAddressRegion('europe/fr')

    self.assertEqual(cr.getDefaultAddressCity(), None)
    self.assertEqual(cr.getDefaultAddressRegion(), 'europe/fr')
    self.assertEqual(cr.getOrganisationDefaultAddressCity(), None)
    self.assertEqual(cr.getOrganisationDefaultTelephoneText(), None)
    self.assertEqual(cr.getOrganisationDefaultAddressRegion(), None)

    cr.deleteContent('default_address')

    cr.setOrganisationDefaultAddressCity('Lille')
    cr.setOrganisationDefaultAddressRegion('europe/fr')

    self.assertEqual(cr.getOrganisationDefaultAddressCity(), 'Lille')
    self.assertEqual(cr.getOrganisationDefaultAddressRegion(), 'europe/fr')
    self.assertEqual(cr.getDefaultAddressCity(), None)
    self.assertEqual(cr.getDefaultAddressRegion(), None)

  def test_Ticket_getWorkflowStateTranslatedTitle(self):
    self.assertEqual(
      self.portal.credential_recovery_module.newContent(
        portal_type='Credential Recovery').Ticket_getWorkflowStateTranslatedTitle(),
     'Draft')
    self.assertEqual(
      self.portal.credential_request_module.newContent(
        portal_type='Credential Request').Ticket_getWorkflowStateTranslatedTitle(),
     'Draft')
    self.assertEqual(
      self.portal.credential_update_module.newContent(
        portal_type='Credential Update').Ticket_getWorkflowStateTranslatedTitle(),
     'Draft')


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5Credential))
  return suite
