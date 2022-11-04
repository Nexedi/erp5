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

use_verbose_security = 0
if use_verbose_security:
  import AccessControl
  AccessControl.Implementation.setImplementation('python')
  AccessControl.ImplPython.setDefaultBehaviors(
              ownerous=True,
              authenticated=True,
              verbose=True)


class TestFreeSubscription(ERP5TypeTestCase):

  def getTitle(self):
    return "Free Subscription"

  def getBusinessTemplateList(self):
    return (
      'erp5_full_text_mroonga_catalog',
      'erp5_core_proxy_field_legacy',
      'erp5_base',
      'erp5_jquery',
      'erp5_ingestion_mysql_innodb_catalog',
      'erp5_ingestion',
      'erp5_web',
      'erp5_pdm',
      'erp5_crm',
      'erp5_dms',
      'erp5_free_subscription',
      'erp5_administration')

  def afterSetUp(self):
    """Prepare the test."""
    self.login()
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

  @reindex
  def enableAlarm(self):
    """activate the alarm"""
    portal = self.getPortalObject()
    alarm = portal.portal_alarms.accept_submitted_free_subscription_requests
    if not alarm.isEnabled():
      alarm.setEnabled(True)

  def validateNotificationMessages(self):
    '''validate all notification messages'''
    portal = self.getPortalObject()
    notification_message_module = portal.getDefaultModule('Notification Message')
    for notification_message in notification_message_module.contentValues():
      if notification_message.getValidationState() == 'draft':
        notification_message.validate()

  def beforeTearDown(self):
    self.abort()
    # clear modules if necessary
    module_list = (self.portal.getDefaultModule('Free Subscription Request'),
        self.portal.getDefaultModule('Free Subscription'),
        self.portal.getDefaultModule('Organisation'),
        self.portal.getDefaultModule('Service'),
        self.portal.getDefaultModule('Letter'),
        self.portal.getDefaultModule('Person'))
    for module in module_list:
      module.manage_delObjects(list(module.objectIds()))
    self.resetFreeSubscriptionSystemPreference()
    self.tic()

  def resetFreeSubscriptionSystemPreference(self):
    preference = self._getPreference()
    preference.edit(preferred_free_credential_request_automatic_approval=False,)
    self._enablePreference()

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

  def stepEnableFreeSubscriptionRequestAutomaticApprovalPreferences(self, sequence=None):
    preference = self._getPreference()
    preference.edit(preferred_free_subscription_request_automatic_approval=True,)
    self._enablePreference()

  def stepDisableFreeSubscriptionRequestAutomaticApprovalPreferences(self, sequence=None):
    preference = self._getPreference()
    preference.edit(preferred_free_subscription_request_automatic_approval=False,)
    self._enablePreference()

  def stepCreateSubscriptionFreeSubscriptionRequest(self, sequence=None, sequence_list=None):
    request = self.portal.free_subscription_request_module.newContent(
      source_value=sequence['sender'],
      destination_value=sequence['receiver'],
      resource_value=sequence['mailing'],
      free_subscription_request_type='subscription',
    )
    sequence.edit(free_subscription_request=request)

  def stepCreateUnsubscriptionFreeSubscriptionRequest(self, sequence=None, sequence_list=None):
    request = self.portal.free_subscription_request_module.newContent(
      source_value=sequence['sender'],
      destination_value=sequence['receiver'],
      resource_value=sequence['mailing'],
      causality_value=sequence['event'],
      follow_up_value=sequence['free_subscription'],
      free_subscription_request_type='unsubscription',
    )
    sequence.edit(free_subscription_request=request)

  def stepCheckFreeSubscriptionCreated(self, sequence=None, sequence_list=None):
    request = sequence['free_subscription_request']
    self.assertNotEquals(request.getFollowUp(), None)
    subscription = request.getFollowUpValue()
    self.assertEquals(subscription.getValidationState(), "validated")
    self.assertNotEquals(subscription.getReference(), None)

  def stepSubmitFreeSubscriptionRequest(self, sequence=None, sequence_list=None):
    request = sequence['free_subscription_request']
    request.submit()

  def stepCheckSubmittedFreeSubscriptionRequest(self, sequence=None, sequence_list=None):
    request = sequence['free_subscription_request']
    self.assertEquals(request.getValidationState(), 'submitted')
    self.assertNotEquals(request.getReference(), None)

  def stepAcceptFreeSubscriptionRequest(self, sequence=None, sequence_list=None):
    request = sequence['free_subscription_request']
    request.accept()

  def stepCheckAcceptedFreeSubscriptionRequest(self, sequence=None, sequence_list=None):
    request = sequence['free_subscription_request']
    self.assertEquals(request.getValidationState(), 'accepted')
    self.assertNotEquals(request.getReference(), None)

  def stepRejectFreeSubscriptionRequest(self, sequence=None, sequence_list=None):
    request = sequence['free_subscription_request']
    request.reject()

  def stepCheckRejectedFreeSubscriptionRequest(self, sequence=None, sequence_list=None):
    request = sequence['free_subscription_request']
    self.assertEquals(request.getValidationState(), 'accepted')

  def stepCheckFreeSubscriptionInvalidated(self, sequence=None, sequence_list=None):
    subscription = sequence['free_subscription']
    self.assertEquals(subscription.getValidationState(), "invalidated")

  def stepCreateReceiver(self, sequence=None, sequence_list=None,
      **kw):
    person = self.portal.person_module.newContent(title='Barney',
                             reference='barney',
                             password='secret',
                             start_date=DateTime('1970/01/01'),
                             default_email_text='barney@duff.com')
    person.validate()
    sequence.edit(receiver=person)

  def stepCreateSender(self, sequence=None, sequence_list=None,
      **kw):
    organisation = self.portal.organisation_module.newContent(title='CMR Company',
                             default_email_text='crm@duff.com')
    organisation.validate()
    sequence.edit(sender=organisation)

  def stepCreateMailingResource(self, sequence=None, sequence_list=None,
      **kw):
    service = self.portal.service_module.newContent(title='Mailling List #1',
                                                    reference="MAILNEWS")
    service.validate()
    sequence.edit(mailing=service)

  def stepCreateEvent(self, sequence=None, sequence_list=None,
      **kw):
    event = self.portal.event_module.newContent(
      portal_type="Letter",
      title='Lettre de mailling #1')
    event.send()
    sequence.edit(event=event)

  def stepCreateFreeSubscription(self, sequence=None, sequence_list=None,
      **kw):
    subscription = self.portal.free_subscription_module.newContent(
      title='Free Subscription for test',
      source_value=sequence['sender'],
      destination_value=sequence['receiver'],
      resource_value=sequence['mailing'],)
    subscription.validate()
    sequence.edit(free_subscription=subscription)

  def stepCreateNotificationMessage(self, sequence=None, sequence_list=None,
      **kw):
    message = self.portal.notification_message_module.newContent(
      title='Message de mailling #1',
      reference="newsl",
      content_type="text/html",
      language="en",
      text_content='<a href=%s/${unsubscribe_parameters}>Unsubscribe from mailling list</a><br>Bonjour' % \
        (self.portal.absolute_url(),),
      text_content_substitution_mapping_method_id='NotificationMessage_getSubstitutionMappingDictFromEvent',
      specialise_value=sequence['mailing'],
      )
    message.validate()
    sequence.edit(message=message)

  def stepCreateCommunicationPlan(self, sequence=None, sequence_list=None, **kw):
    domain = self.portal.portal_domains['communication_plan_domain'].newContent(
      title="People subscribed to newsletter",
      portal_type="Domain")
    domain.setCriterionPropertyList([
      'portal_type',
      'destination_free_subscription_resource_reference',
      'default_email_text'])
    domain.setCriterion('portal_type', identity=['Person'])
    domain.setCriterion('default_email_text', identity=['%@%'])
    domain.setCriterion('destination_free_subscription_resource_reference',
                        sequence['mailing'].getReference())

  def stepCreateCampaign(self, sequence=None, sequence_list=None,
      **kw):
    campaign = self.portal.campaign_module.newContent(
      title='Campaign de mailling #1',
      source_section_value=sequence['sender'],
      default_event_path_source_value=sequence['sender'],
      default_event_path_event_portal_type="Mail Message",
      default_event_path_resource_value=sequence['message'],
      default_event_path_destination_value=self.portal.portal_domains['communication_plan_domain']['1']
      )
    sequence.edit(campaign=campaign)

  def stepValidateCampaign(self, sequence=None, sequence_list=None,
      **kw):
    campaign = sequence['campaign']
    campaign.validate()
    self.tic()
    campaign.Ticket_createEventFromDefaultEventPath()

  def stepCheckEventCreated(self, sequence=None, sequence_list=None,
      **kw):
    event_list = self.portal.event_module.objectValues()
    self.assertEquals(len(event_list), 1)
    for event in event_list:
      self.assertEquals(event.getSimulationState(), "planned")
      self.assertEquals(event.getFollowUp(), sequence['campaign'].getRelativeUrl())
      self.assertEquals(event.getPortalType(), "Mail Message")
      self.assertEquals(event.getTextFormat(), "text/html")
      self.assertFalse("blank_image_url" in event.getTextContent())
      self.assertFalse("newsletter_url" in event.getTextContent())
      self.assertTrue("Bonjour" in event.getTextContent())
      content = event.getTextContent()
      unsubscription = content.split('<br />')[0]
      unsubscription_link = unsubscription.split('"')[1]
    sequence.edit(unsubscription_link=unsubscription_link,
                  event=event)

  def stepClickUnsubscriptionLinkInEvent(self, sequence=None, sequence_list=None,
      **kw):
    from urllib import urlopen
    link = sequence['unsubscription_link']
    self.logout()
    data = urlopen(link)
    self.assertFalse("Site Error" in data)
    self.assertFalse("You do not have enough permissions to access this page" in data.read())
    self.login()

  def stepCheckFreeSubscriptionRequestCreated(self, sequence=None, sequence_list=None,
      **kw):
    request_list = self.portal.free_subscription_request_module.objectValues()
    self.assertEquals(len(request_list), 1)
    request = request_list[0]
    self.assertEquals(request.getSourceValue(), sequence['sender'])
    self.assertEquals(request.getDestinationValue(), sequence['receiver'])
    self.assertEquals(request.getResourceValue(), sequence['mailing'])
    self.assertEquals(request.getCausalityValue(), sequence['event'])
    self.assertEquals(len(request.getFollowUpValueList()), 1)
    sequence.edit(
      free_subscription_request=request,
      free_subscription=request.getFollowUpValue())


  def test_01_NonAutomaticFreeSubscriptionRequestForSubscription(self):
    sequence_list = SequenceList()
    sequence_string = 'CreateReceiver CreateSender CreateMailingResource Tic '\
                      'DisableFreeSubscriptionRequestAutomaticApprovalPreferences Tic '\
                      'CreateSubscriptionFreeSubscriptionRequest Tic '\
                      'SubmitFreeSubscriptionRequest Tic '\
                      'CheckSubmittedFreeSubscriptionRequest '\
                      'AcceptFreeSubscriptionRequest Tic '\
                      'CheckAcceptedFreeSubscriptionRequest '\
                      'CheckFreeSubscriptionCreated'\

    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_02_AutomaticFreeSubscriptionRequestForSubscription(self):
    sequence_list = SequenceList()
    sequence_string = 'CreateReceiver CreateSender CreateMailingResource Tic '\
                      'EnableFreeSubscriptionRequestAutomaticApprovalPreferences Tic '\
                      'CreateSubscriptionFreeSubscriptionRequest Tic '\
                      'SubmitFreeSubscriptionRequest Tic '\
                      'CheckAcceptedFreeSubscriptionRequest '\
                      'CheckFreeSubscriptionCreated'\

    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_03_NonAutomaticFreeSubscriptionRequestForUnsubscription(self):
    sequence_list = SequenceList()
    sequence_string = 'CreateReceiver CreateSender CreateMailingResource '\
                      'CreateEvent CreateFreeSubscription Tic '\
                      'DisableFreeSubscriptionRequestAutomaticApprovalPreferences Tic '\
                      'CreateUnsubscriptionFreeSubscriptionRequest Tic '\
                      'SubmitFreeSubscriptionRequest Tic '\
                      'CheckSubmittedFreeSubscriptionRequest '\
                      'AcceptFreeSubscriptionRequest Tic '\
                      'CheckAcceptedFreeSubscriptionRequest '\
                      'CheckFreeSubscriptionInvalidated'\

    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_04_AutomaticFreeSubscriptionRequestForUnsubscription(self):
    sequence_list = SequenceList()
    sequence_string = 'CreateReceiver CreateSender CreateMailingResource '\
                      'CreateEvent CreateFreeSubscription Tic '\
                      'EnableFreeSubscriptionRequestAutomaticApprovalPreferences Tic '\
                      'CreateUnsubscriptionFreeSubscriptionRequest Tic '\
                      'SubmitFreeSubscriptionRequest Tic '\
                      'CheckAcceptedFreeSubscriptionRequest '\
                      'CheckFreeSubscriptionInvalidated'\

    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_05_UnsubscriptionFromURL(self):
    sequence_list = SequenceList()
    sequence_string = 'CreateReceiver CreateSender CreateMailingResource Tic '\
                      'CreateFreeSubscription Tic '\
                      'CreateNotificationMessage CreateCommunicationPlan CreateCampaign Tic ' \
                      'ValidateCampaign Tic CheckEventCreated ' \
                      'EnableFreeSubscriptionRequestAutomaticApprovalPreferences Tic '\
                      'ClickUnsubscriptionLinkInEvent Tic '\
                      'CheckFreeSubscriptionRequestCreated ' \
                      'CheckAcceptedFreeSubscriptionRequest '\
                      'CheckFreeSubscriptionInvalidated'\

    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)




def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestFreeSubscription))
  return suite
