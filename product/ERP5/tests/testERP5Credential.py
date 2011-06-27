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
import email, re
from email.Header import decode_header, make_header
from email.Utils import parseaddr
from zLOG import LOG
import transaction
import cgi
from urlparse import urlparse

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
      'erp5_full_text_myisam_catalog',
      'erp5_base',
      'erp5_jquery',
      'erp5_ingestion_mysql_innodb_catalog',
      'erp5_ingestion',
      'erp5_web',
      'erp5_crm',
      'erp5_credential')

  def afterSetUp(self):
    """Prepare the test."""
    self.createCategories()
    self.enableAlarm()
    self.validateNotificationMessages()
    # add a dummy mailhost not to send real messages
    if 'MailHost' in self.portal.objectIds():
      self.portal.manage_delObjects(['MailHost'])
    self.portal._setObject('MailHost', DummyMailHost('MailHost'))

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
    for cat_string in self.getNeededCategoryList() :
      base_cat = cat_string.split("/")[0]
      # if base_cat not exist, create it
      if getattr(self.getPortal().portal_categories, base_cat, None) == None:
        self.getPortal().portal_categories.newContent(\
                                          portal_type='Base Category',
                                          id=base_cat)
      base_cat_value = self.getPortal().portal_categories[base_cat]
      for cat in cat_string.split("/")[1:] :
        if not cat in base_cat_value.objectIds() :
          base_cat_value = base_cat_value.newContent(
                    portal_type='Category',
                    id=cat,
                    title=cat.replace('_', ' ').title(),)
        else:
          base_cat_value = base_cat_value[cat]
    # check categories have been created
    for cat_string in self.getNeededCategoryList() :
      self.assertNotEquals(None,
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
           )

  def beforeTearDown(self):
    self.login()
    transaction.abort()
    # clear modules if necessary
    module_list = (self.portal.getDefaultModule('Credential Request'),
        self.portal.getDefaultModule('Credential Update'),
        self.portal.getDefaultModule('Credential Recovery'),
        self.portal.getDefaultModule('Person'))
    for module in module_list:
      module.manage_delObjects(list(module.objectIds()))
    self.stepUnSetCredentialAutomaticApprovalPreferences()
    transaction.commit()
    self.tic()
    self.logout()

  # Copied from bt5/erp5_egov/TestTemplateItem/testEGovMixin.py
  def decode_email(self, file):
    # Prepare result
    theMail = {
      'attachment_list': [],
      'body': '',
      # Place all the email header in the headers dictionary in theMail
      'headers': {}
    }
    # Get Message
    msg = email.message_from_string(file)
    # Back up original file
    theMail['__original__'] = file
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
    if preference.getPreferenceState() in ('enable', 'global'):
      preference.disable()

  def stepUnSetCredentialAutomaticApprovalPreferences(self, sequence=None,
      sequence_list=None, **kw):
    self.login()
    preference = self._getPreference()
    preference.edit(preferred_credential_request_automatic_approval=False,
                    preferred_credential_recovery_automatic_approval=False,
                    preferred_organisation_credential_update_automatic_approval=False,
                    preferred_person_credential_update_automatic_approval=False,
                    preferred_credential_alarm_automatic_call=True)

    self._enablePreference()
    transaction.commit()
    self.tic()
    self.logout()

  def stepSetCredentialRequestAutomaticApprovalPreferences(self, sequence=None):
    self.login()
    preference = self._getPreference()
    automatic_call = sequence.get("automatic_call", True)
    preference.edit(preferred_credential_request_automatic_approval=True,
                    preferred_credential_alarm_automatic_call=automatic_call)
    self._enablePreference()
    self.stepTic()
    self.logout()

  def stepSetCredentialAssignmentPropertyList(self, sequence={}):
    category_list = sequence.get("category_list",
        ["role/internal", "function/member"])
    self.login()
    preference = self._getPreference()
    preference.edit(preferred_subscription_assignment_category_list=category_list)
    self._enablePreference()
    self.stepTic()
    self.logout()

  def stepSetOrganisationCredentialUpdateAutomaticApprovalPreferences(self, sequence=None,
      sequence_list=None, **kw):
    self.login()
    preference = self._getPreference()
    preference.edit(preferred_organisation_credential_update_automatic_approval=True)
    self._enablePreference()
    transaction.commit()
    self.tic()
    self.logout()

  def stepSetCredentialRecoveryAutomaticApprovalPreferences(self, sequence=None,
      sequence_list=None, **kw):
    self.login()
    preference = self._getPreference()
    preference.edit(preferred_credential_recovery_automatic_approval=True)
    self._enablePreference()
    transaction.commit()
    self.tic()
    self.logout()

  def stepSetPersonCredentialUpdateAutomaticApprovalPreferences(self, sequence=None,
      sequence_list=None, **kw):
    self.login()
    preference = self._getPreference()
    preference.edit(preferred_person_credential_update_automatic_approval=True)
    self._enablePreference()
    transaction.commit()
    self.tic()
    self.logout()

  def stepCheckAssignmentAfterActiveLogin(self, sequence):
    portal_catalog = self.portal.portal_catalog
    reference = sequence["reference"]
    assignment_function = sequence["assignment_function"]
    assignment_role = sequence["assignment_role"]
    credential_request = portal_catalog.getResultValue(portal_type="Credential Request",
                                                       reference=reference)
    mail_message = portal_catalog.getResultValue(portal_type="Mail Message",
                                                 follow_up=credential_request)
    self.stepTic()
    self.logout()
    self.portal.ERP5Site_activeLogin(mail_message.getReference())
    self.login("ERP5TypeTestCase")
    self.stepTic()
    person = portal_catalog.getResultValue(reference=reference,
                                           portal_type="Person")
    assignment_list = person.objectValues(portal_type="Assignment")
    self.assertEquals(len(assignment_list), 1)
    assignment = assignment_list[0]
    self.assertEquals(assignment.getFunction(), assignment_function)
    self.assertEquals(assignment.getRole(), assignment_role)

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
    self.assertNotEquals(uf.getUserById(login, None), None)
    for plugin_name, plugin in uf._getOb('plugins').listPlugins(
                                IAuthenticationPlugin ):
      if plugin.authenticateCredentials(
                  {'login':login, 'password':password}) is not None:
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
                              IAuthenticationPlugin ):
      if plugin.authenticateCredentials(
                {'login':login, 'password':password}) is not None:
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
    self.assertTrue("Desired Login Name" in request.traverse(form_url)())
    # fill in and submit the subscription form

    result = self.portal.ERP5Site_newCredentialRequest(\
        first_name='Homer',
        last_name='Simpson',
        reference='homie',
        password='secret',
        default_email_text='homer.simpson@fox.com',
        role_list=['internal'],
        )
    self.assertTrue('portal_status_message=Credential%20Request%20Created.'\
        in result)

    credential_request_module = self.portal.getDefaultModule('Credential Request')
    result = credential_request_module.contentValues(\
        portal_type='Credential Request', first_name='Homer',
        last_name='Simpson', reference='homie')
    self.assertEquals(len(result), 1)
    sequence.edit(subscription_request=result[0])

  def stepAcceptSubscriptionRequest(self, sequence=None, sequence_list=None,
      **kw):
    self.login()
    subscription_request = sequence.get('subscription_request')
    subscription_request.accept()
    self.logout()

  def stepCheckAccountIsCreated(self, sequence=None, sequence_list=None, **kw):
    # check a person have been created
    person_module = self.portal.getDefaultModule('Person')
    person_result = person_module.contentValues(reference='homie')
    self.assertEquals(len(person_result), 1)
    person = person_result[0].getObject()
    self.assertEquals(person.getTitle(), 'Homer Simpson')
    self.assertEquals(person.getDefaultEmailText(), 'homer.simpson@fox.com')

    # check homie can log in the system
    self._assertUserExists('homie', 'secret')
    self.login('homie')
    from AccessControl import getSecurityManager
    self.assertEquals(str(getSecurityManager().getUser()), 'homie')

  def stepCreateCredentialUpdate(self, sequence=None, sequence_list=None, **kw):
    '''
    Create a credential update object an fill it with some modified
    informations
    '''
    self.login()
    # get the 'homie' person object
    person_module = self.portal.getDefaultModule('Person')
    result = person_module.searchFolder(reference='homie')
    self.assertEquals(len(result), 1)
    homie = result[0]

    # create a credential update
    credential_update_module = self.portal.getDefaultModule(\
        'Credential Update')
    credential_update = credential_update_module.newContent(\
        first_name='Homie',
        last_name='Simpsons', # add a 's' to the end of the last_name
        password='new_password',
        default_email_text='homie.simpsons@fox.com',
        destination_decision=homie.getRelativeUrl())

    credential_update.submit()
    self.assertEquals(credential_update.getValidationState(), 'submitted')
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
    person_module = self.portal.getDefaultModule('Person')
    related_person_result = person_module.searchFolder(reference='homie')
    self.assertEquals(len(related_person_result), 1)
    related_person = related_person_result[0]
    self.assertEquals(related_person.getLastName(), 'Simpsons')
    self.assertEquals(related_person.getDefaultEmailText(),
    'homie.simpsons@fox.com')

  def stepCreateSubscriptionRequestWithSecurityQuestionCategory(self, sequence=None,
      sequence_list=None, **kw):
    request = self.portal.REQUEST
    request['PARENTS'] = [self.app]
    form_url = self.portal.absolute_url_path() + '/ERP5Site_viewNewCredentialRequestDialog'

    # logout to be annonymous
    self.logout()
    # fill in and submit the subscription form
    result = self.portal.ERP5Site_newCredentialRequest(\
        first_name='Homer',
        last_name='Simpson',
        reference='homie',
        password='secret',
        default_email_text='homer.simpson@fox.com',
        default_credential_question_question='credential/library_card_number',
        default_credential_question_answer='923R4293'
        )
    self.assertTrue('portal_status_message=Credential%20Request%20Created.'\
        in result)

    transaction.commit()
    self.tic()
    credential_request_module = self.portal.getDefaultModule('Credential Request')
    result = credential_request_module.contentValues(\
        portal_type='Credential Request', first_name='Homer',
        last_name='Simpson', reference='homie')
    self.assertEquals(len(result), 1)
    sequence.edit(subscription_request=result[0])

  def stepCheckSecurityQuestionCategoryAsBeenCopiedOnPersonObject(self, sequence=None,
      sequence_list=None, **kw):
    person_module = self.portal.getDefaultModule('Person')
    related_person_result = person_module.contentValues(reference='homie')
    self.assertEquals(len(related_person_result), 1)
    related_person = related_person_result[0]
    self.assertEquals(related_person.getDefaultCredentialQuestionQuestion(),
        'credential/library_card_number')
    self.assertEquals(related_person.getDefaultCredentialQuestionAnswer(),
        '923R4293')

  def stepCreateSubscriptionRequestWithSecurityQuestionFreeText(self, sequence=None,
      sequence_list=None, **kw):
    request = self.portal.REQUEST
    request['PARENTS'] = [self.app]
    form_url = self.portal.absolute_url_path() + '/ERP5Site_viewNewCredentialRequestDialog'

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
    self.assertTrue('portal_status_message=Credential%20Request%20Created.'\
        in result)

    transaction.commit()
    self.tic()
    credential_request_module = self.portal.getDefaultModule('Credential Request')
    result = credential_request_module.contentValues(\
        portal_type='Credential Request', first_name='Homer',
        last_name='Simpson', reference='homie')
    self.assertEquals(len(result), 1)
    sequence.edit(subscription_request=result[0])

  def stepCheckSecurityQuestionFreeTextAsBeenCopiedOnPersonObject(self, sequence=None,
      sequence_list=None, **kw):
    person_module = self.portal.getDefaultModule('Person')
    related_person_result = person_module.contentValues(reference='homie')
    self.assertEquals(len(related_person_result), 1)
    related_person = related_person_result[0]
    self.assertEquals(related_person.getDefaultCredentialQuestionQuestionFreeText(),
        'Which car model do you have ?')
    self.assertEquals(related_person.getDefaultCredentialQuestionAnswer(),
        'Renault 4L')

  def stepCreateCredentialRecovery(self, sequence=None, sequence_list=None,
      **kw):
    '''
    Create a simple subscription request
    '''
    portal = self.getPortalObject()
    # create a person with 'secret' as password
    self.login()
    person_module = portal.getDefaultModule('Person')
    barney = person_module.newContent(title='Barney',
                             reference='barney',
                             password='secret',
                             default_email_text='barney@duff.com')
    # create an assignment
    assignment = barney.newContent(portal_type='Assignment',
                      function='member')
    assignment.open()
    transaction.commit()
    self.tic()
    sequence.edit(barney=barney)
    # check barney can log in the system
    self._assertUserExists('barney', 'secret')
    self.login('barney')
    from AccessControl import getSecurityManager
    self.assertEquals(str(getSecurityManager().getUser()), 'barney')

    self.login()
    # create a credential recovery
    credential_recovery_module = portal.getDefaultModule('Credential Recovery')
    credential_recovery = credential_recovery_module.newContent(portal_type=\
        'Credential Recovery')

    # associate it with barney
    credential_recovery.setDestinationDecisionValue(barney)
    sequence.edit(credential_recovery=credential_recovery)

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

    # after accept, an email is send containing the reset link
    last_message = self.portal.MailHost._last_message
    rawstr = r"""PasswordTool_viewResetPassword"""
    decoded_message = self.decode_email(last_message[2])
    body_message = decoded_message['body']
    match_obj = re.search(rawstr, body_message)

    # check the reset password link is in the mail
    self.assertNotEquals(match_obj, None)

    # check the mail is sent to the requester :
    send_to = decoded_message['headers']['to']
    self.assertEqual(barney.getDefaultEmailText(), send_to)

  def stepCheckPasswordChange(self, sequence=None, sequence_list=None, **kw):
    '''
      check it's possible to change the user password using the link in the
      email
    '''
    # get the url
    last_message = self.portal.MailHost._last_message
    rawstr = r"""PasswordTool_viewResetPassword"""
    decoded_message = self.decode_email(last_message[2])
    body_message = decoded_message['body']
    match_obj = re.search(rawstr, body_message)
    # check the reset password link is in the mail
    self.assertNotEquals(match_obj, None)
    url = None
    for line in body_message.splitlines():
      match_obj = re.search(rawstr, line)
      if match_obj is not None:
        url = line[line.find('http:'):]
    url = url.strip()
    self.assertNotEquals(url, None)
    response = self.publish(url)
    parameters = cgi.parse_qs(urlparse(url)[4])
    self.assertTrue('reset_key' in parameters)
    key = parameters['reset_key'][0]
    self.logout()
    # before changing, check that the user exists with 'secret' password
    self._assertUserExists('barney', 'secret')
    self.portal.portal_password.changeUserPassword(user_login="barney",
                                                   password="new_password",
                                                   password_confirmation="new_password",
                                                   password_key=key)
    transaction.commit()
    self.tic()
    # reset the cache
    self.portal.portal_caches.clearAllCache()
    # check we cannot login anymore with the previous password 'secret'
    self._assertUserDoesNotExists('barney', 'secret')

    # check we can now login with the new password 'new_password'
    self._assertUserExists('barney', 'new_password')

  def test_01_simpleSubsciptionRequest(self):
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
    sequence_string = 'CreateSimpleSubscriptionRequest Tic '\
                      'AcceptSubscriptionRequest Tic '\
                      'CheckAccountIsCreated Tic '\

    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_03_simpleCredentialUpdate(self):
    '''
    check it's possible to update credential informations using credential
    update
    '''
    sequence_list = SequenceList()
    sequence_string = 'CreateSimpleSubscriptionRequest '\
                      'AcceptSubscriptionRequest Tic '\
                      'CreateCredentialUpdate '\
                      'AcceptCredentialUpdate Tic '\
                      'CheckCredentialUpdate '\

    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_04_automaticCredentialRequestApproval(self):
    '''
    if the workflow credential_automatic_accept_interraction_workflow
    is defined on Credential Request portal_type, the Credential Request object
    should be accepted automatically and account created without any human
    intervention
    '''
    sequence_list = SequenceList()
    sequence_string = 'SetCredentialRequestAutomaticApprovalPreferences '\
                      'CreateSimpleSubscriptionRequest Tic '\
                      'CheckAccountIsCreated '\

    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_05_automaticCredentialUpdateApproval(self):
    '''
    if the workflow credential_automatic_accept_interraction_workflow
    is defined on Credential Update portal_type, the Credential Update object
    should be accepted automatically and object modified without any human
    intervention
    '''
    sequence_list = SequenceList()
    sequence_string = 'SetPersonCredentialUpdateAutomaticApprovalPreferences '\
                      'CreateSimpleSubscriptionRequest '\
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
    sequence_string = 'CreateCredentialRecovery Tic '\
                      'SubmitCredentialRecovery Tic '\
                      'AcceptCredentialRecovery Tic '\
                      'CheckEmailIsSent Tic '\
                      'CheckPasswordChange Tic '\

    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def _createCredentialRequest(self, first_name="Gabriel",
                               last_name="Monnerat",
                               reference="gabriel",
                               password="123",
                               default_email_text="gabriel@test.com"):
    self.logout()
    self.portal.ERP5Site_newCredentialRequest(first_name=first_name,
        last_name=last_name,
        reference=reference,
        password=password,
        career_subordination_title="",
        default_email_text=default_email_text,
        default_telephone_text="223344",
        default_address_street_address="Test Street",
        default_address_city="Campos",
        default_address_zip_code="28024030")
    self.login("ERP5TypeTestCase")
    self.stepTic()

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
                                                 follow_up=credential_reference)
    self.assertEquals(mail_message.getSimulationState(), "started")
    self.assertTrue( "key=%s" % mail_message.getReference() in mail_message.getTextContent())

  def stepSetPreferredCredentialAlarmAutomaticCallAsFalse(self, sequence):
    sequence.edit(automatic_call=False)

  def testMailMessagePosted(self):
    """ Test if the Mail Message was posted correctly """
    sequence_list = SequenceList()
    sequence_string = 'SetPreferredCredentialAlarmAutomaticCallAsFalse '\
                      'SetCredentialRequestAutomaticApprovalPreferences '\
                      'CreateCredentialRequestSample '\
                      'CheckIfMailMessageWasPosted '\
                      'stepUnSetCredentialAutomaticApprovalPreferences'\

    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def testMailFromMailMessageEvent(self):
    """ """
    sequence = dict(automatic_call=False)
    self.stepSetCredentialRequestAutomaticApprovalPreferences(sequence)
    self._createCredentialRequest(first_name="Vifib", 
                                 last_name="Test",
                                 reference="vifibtest")
    portal_catalog = self.portal.portal_catalog
    credential_request = portal_catalog.getResultValue(
        portal_type="Credential Request", reference="vifibtest", 
        first_name="Vifib", last_name="Test")
    mail_message = portal_catalog.getResultValue(
        portal_type="Mail Message", follow_up=credential_request)
    last_message = self.portal.MailHost._last_message
    self.assertNotEquals((), last_message)
    mfrom, mto, message_text = last_message
    self.assertEquals(mfrom, 'Portal Administrator <postmaster@localhost>')
    self.assertEquals(['Vifib Test <gabriel@test.com>'], mto)
    self.assertNotEquals(re.search("Subject\:.*Welcome", message_text), None)
    self.assertNotEquals(re.search("Hello\ Vifib\ Test\,", message_text), None)
    self.assertNotEquals(re.search("key\=..%s" % mail_message.getReference(),
      message_text), None)
    self.stepUnSetCredentialAutomaticApprovalPreferences()

  def testERP5Site_activeLogin(self):
    """ Test if the script WebSection_activeLogin will create one user
    correctly """
    sequence = dict(automatic_call=False)
    self.stepSetCredentialRequestAutomaticApprovalPreferences(sequence)
    self._createCredentialRequest()
    portal_catalog = self.portal.portal_catalog
    credential_request = portal_catalog.getResultValue(
        portal_type="Credential Request", reference="gabriel")
    mail_message = portal_catalog.getResultValue(portal_type="Mail Message",
                                                 follow_up=credential_request)
    self.logout()
    self.portal.ERP5Site_activeLogin(mail_message.getReference())
    self.login("ERP5TypeTestCase")
    self.stepTic()
    person = portal_catalog.getResultValue(reference="gabriel",
        portal_type="Person")
    assignment_list = person.objectValues(portal_type="Assignment")
    self.assertNotEquals(assignment_list, [])
    self.assertEquals(len(assignment_list), 1)
    assignment = assignment_list[0]
    self.assertEquals(assignment.getValidationState(), "open")
    self.assertEquals(person.getValidationState(), "validated")
    self.stepUnSetCredentialAutomaticApprovalPreferences()

  def testERP5Site_newCredentialRequest(self):
    """ Test if the script ERP5Site_newCredentialRequest will create one
    Credential Request correctly """
    sequence = dict(automatic_call=False)
    self.stepSetCredentialRequestAutomaticApprovalPreferences(sequence)
    self._createCredentialRequest()
    portal_catalog = self.portal.portal_catalog
    credential_request = portal_catalog.getResultValue(
        portal_type="Credential Request", reference="gabriel")
    self.assertEquals(credential_request.getFirstName(), "Gabriel")
    self.assertEquals(credential_request.getDefaultEmailText(),
        "gabriel@test.com")
    self.stepUnSetCredentialAutomaticApprovalPreferences()

  def testBase_getDefaultAssignmentArgumentDict(self):
    sequence = dict(automatic_call=False)
    self.stepSetCredentialRequestAutomaticApprovalPreferences(sequence)
    self.stepSetCredentialAssignmentPropertyList()
    self._createCredentialRequest()
    sequence = dict(reference="gabriel",
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

  def test_xx_checkCredentialQuestionIsNotCaseSensitive(self):
    '''
    check that if the user enter an answer with a diffent case, this will still
    enought to reset his passord
    '''

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5Credential))
  return suite
