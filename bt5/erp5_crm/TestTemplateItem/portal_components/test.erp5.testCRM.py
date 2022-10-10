# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2007 Nexedi SA and Contributors. All Rights Reserved.
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
import six.moves.urllib.parse
import os
import textwrap
from unittest import expectedFailure

from Products.CMFCore.WorkflowCore import WorkflowException
from Products.ERP5Type.tests.utils import FileUpload
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5OOo.tests.testIngestion import FILENAME_REGULAR_EXPRESSION
from Products.ERP5OOo.tests.testIngestion import REFERENCE_REGULAR_EXPRESSION
from email.header import decode_header
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders, message_from_string
from DateTime import DateTime

import Products.ERP5.tests

def makeFilePath(name):
  return os.path.join(os.path.dirname(Products.ERP5.tests.__file__),
                      'test_data', 'crm_emails', name)

def makeFileUpload(name):
  path = makeFilePath(name)
  return FileUpload(path, name)

clear_module_name_list = """
campaign_module
event_module
meeting_module
organisation_module
person_module
sale_opportunity_module
portal_categories/resource
portal_categories/function
""".strip().splitlines()

class BaseTestCRM(ERP5TypeTestCase):

  def afterSetUp(self):
    super(BaseTestCRM, self).afterSetUp()
    self.portal.MailHost.reset()

  def beforeTearDown(self):
    self.abort()
    # clear modules if necessary
    for module_name in clear_module_name_list:
      module = self.portal.unrestrictedTraverse(module_name)
      module.manage_delObjects(list(module.objectIds()))
    self.tic()
    super(BaseTestCRM, self).beforeTearDown()

class TestCRM(BaseTestCRM):
  def getTitle(self):
    return "CRM"

  def getBusinessTemplateList(self):
    return ('erp5_full_text_mroonga_catalog',
            'erp5_core_proxy_field_legacy',
            'erp5_base',
            'erp5_ingestion',
            'erp5_pdm',
            'erp5_crm',)

  def test_Event_getQuantity(self):
    event_module = self.portal.event_module
    for portal_type in self.portal.getPortalEventTypeList():
      event = event_module.newContent(portal_type=portal_type)
      # quantity on events is 1 by default
      self.assertEqual(1, event.getQuantity())
      # but it can be overriden
      event.setQuantity(321)
      self.assertEqual(321, event.getQuantity())

  def test_Event_isMovement(self):
    event_module = self.portal.event_module
    for portal_type in self.portal.getPortalEventTypeList():
      event = event_module.newContent(portal_type=portal_type)
      self.assertTrue(event.isMovement(),
        "%s is not a movement" % portal_type)

  def test_Event_stop_date_field_enabled(self):
    """
      Checks if Event_view display stop_date to Phone calls and visits
    """
    phone_call = self.portal.event_module.newContent(
      portal_type="Phone Call", temp_object=True)
    self.assertTrue(phone_call.Event_view.my_stop_date.get_value("enabled"))
    visit = self.portal.event_module.newContent(
      portal_type="Visit", temp_object=True)
    self.assertTrue(visit.Event_view.my_stop_date.get_value("enabled"))
    mail_message = self.portal.event_module.newContent(
      portal_type="Mail Message", temp_object=True)
    self.assertFalse(mail_message.Event_view.my_stop_date.get_value("enabled"))

  def test_Event_CreateRelatedEvent(self):
    # test workflow to create a related event from responded event
    event_module = self.portal.event_module
    ticket = self.portal.campaign_module.newContent(portal_type='Campaign',)
    for ptype in [x for x in self.portal.getPortalEventTypeList() if x !=
        'Acknowledgement']:
      event = event_module.newContent(portal_type=ptype,
                                      follow_up_value=ticket)

      event.stop()

      self.assertEqual(len(event.getCausalityRelatedValueList()), 0)

      self.tic()

      event.Event_createResponse(response_event_portal_type=ptype,
                                 response_event_title='New Title',
                                 response_event_text_content='New Desc',
                                 response_workflow_action='plan',
                                 )

      self.tic()

      self.assertEqual(len(event.getCausalityRelatedValueList()), 1)

      related_event = event.getCausalityRelatedValue()

      self.assertEqual(related_event.getPortalType(), ptype)
      self.assertEqual(related_event.getTitle(), 'New Title')
      self.assertEqual(related_event.getTextContent(), 'New Desc')
      self.assertEqual(related_event.getFollowUpValue(), ticket)

  def test_Event_CreateRelatedEventUnauthorized(self):
    # test that we don't get Unauthorized error when invoking the "Create
    # Related Event" without add permission on the module,
    # but will get WorkflowException error.
    event = self.portal.event_module.newContent(portal_type='Letter')
    self.portal.event_module.manage_permission('Add portal content', [], 0)
    self.assertRaises(WorkflowException,
                      event.Event_createRelatedEvent,
                      portal_type='Letter',
                      title='New Title',
                      description='New Desc')

  def test_Ticket_CreateRelatedEvent(self):
    # test action to create a related event from a ticket
    ticket = self.portal.meeting_module.newContent(portal_type='Meeting')
    for ptype in [x for x in self.portal.getPortalEventTypeList() if x !=
        'Acknowledgement']:
      # incoming
      ticket.Ticket_newEvent(portal_type=ptype,
                             title='Incoming Title',
                             event_workflow_action='deliver')
      self.tic()
      new_event, = ticket.getFollowUpRelatedValueList(portal_type=ptype)
      self.assertEqual('delivered', new_event.getSimulationState())

      # outgoing
      ticket.Ticket_newEvent(portal_type=ptype,
                             title='Outgoing Title',
                             event_workflow_action='plan')
      self.tic()
      new_event, = [event for event in ticket.getFollowUpRelatedValueList(portal_type=ptype) if\
                   event.getTitle() == 'Outgoing Title']
      self.assertEqual('planned', new_event.getSimulationState())

  def test_Ticket_CreateRelatedEventUnauthorized(self):
    # test that we don't get Unauthorized error when invoking the "Create
    # New Event" without add permission on the module
    ticket = self.portal.meeting_module.newContent(portal_type='Meeting')
    self.portal.event_module.manage_permission('Add portal content', [], 0)
    ticket.Ticket_newEvent(portal_type='Letter',
                           title='New Title',
                           event_workflow_action='plan')

  def test_Ticket_getArrowItemList(self):
    # test Ticket_getArrowItemList script
    pers1 = self.portal.person_module.newContent(
      portal_type='Person', title='Person 1')
    pers2 = self.portal.person_module.newContent(
      portal_type='Person', title='Person 2')
    ticket = self.portal.meeting_module.newContent(portal_type='Meeting')
    ticket.setDestinationDecisionValue(pers1)
    ticket.setSourceValue(pers1)

    self.assertEqual(
      [('', ''), ('Person 1', pers1.getRelativeUrl())],
      ticket.Ticket_getArrowItemList())

    # logged in user is also returned
    user = self.createUser(
      self.id(), person_kw={"first_name": "John", "last_name": "Doe"})
    self.tic()
    self.portal.acl_users.zodb_roles.assignRoleToPrincipal('Assignee', user.getUserId())
    self.login(user.getUserId())
    self.assertEqual(
      [('', ''),
       ('John Doe', user.getRelativeUrl()),
       ('Person 1', pers1.getRelativeUrl())],
      ticket.Ticket_getArrowItemList())

    # multiple category value are supported
    ticket.setSourceSectionValueList([user, pers2])
    self.assertEqual(
      [('', ''),
       ('John Doe', user.getRelativeUrl()),
       ('Person 1', pers1.getRelativeUrl()),
       ('Person 2', pers2.getRelativeUrl())],
      ticket.Ticket_getArrowItemList())

  def checkCreateRelatedEventSelectionParamsOnPersonModule(self, direction):
    # create related event from selected persons.
    person_module = self.portal.person_module
    pers1 = person_module.newContent(portal_type='Person', title='Pers1')
    pers2 = person_module.newContent(portal_type='Person', title='Pers2')
    pers3 = person_module.newContent(portal_type='Person', title='Pers3')
    self.portal.person_module.view()
    self.portal.portal_selections.setSelectionCheckedUidsFor(
                          'person_module_selection', [])
    self.portal.portal_selections.setSelectionParamsFor(
                          'person_module_selection', dict(title='Pers1'))
    self.tic()
    person_module.PersonModule_newEvent(portal_type='Mail Message',
                                        title='The Event Title',
                                        description='The Event Descr.',
                                        direction=direction,
                                        selection_name='person_module_selection',
                                        follow_up='',
                                        text_content='Event Content',
                                        form_id='PersonModule_viewPersonList')

    self.tic()

    if direction == "outgoing":
      getter_id = "getDestinationRelatedValue"
    elif direction == "incoming":
      getter_id = "getSourceRelatedValue"
    related_event = getattr(pers1, getter_id)(portal_type='Mail Message')
    self.assertNotEqual(None, related_event)
    self.assertEqual('The Event Title', related_event.getTitle())
    self.assertEqual('The Event Descr.', related_event.getDescription())
    self.assertEqual('Event Content', related_event.getTextContent())

    for person in (pers2, pers3):
      self.assertEqual(None, getattr(person, getter_id)(
                                       portal_type='Mail Message'))

  def test_PersonModule_CreateOutgoingRelatedEventSelectionParams(self):
    self.checkCreateRelatedEventSelectionParamsOnPersonModule('outgoing')

  def test_PersonModule_CreateIncomingRelatedEventSelectionParams(self):
    self.checkCreateRelatedEventSelectionParamsOnPersonModule('incoming')

  def test_PersonModule_CreateRelatedEventCheckedUid(self):
    # create related event from selected persons.
    person_module = self.portal.person_module
    pers1 = person_module.newContent(portal_type='Person', title='Pers1')
    pers2 = person_module.newContent(portal_type='Person', title='Pers2')
    pers3 = person_module.newContent(portal_type='Person', title='Pers3')
    self.portal.person_module.view()
    self.portal.portal_selections.setSelectionCheckedUidsFor(
          'person_module_selection',
          [pers1.getUid(), pers2.getUid()])
    self.tic()
    person_module.PersonModule_newEvent(portal_type='Mail Message',
                                        title='The Event Title',
                                        description='The Event Descr.',
                                        direction='outgoing',
                                        selection_name='person_module_selection',
                                        follow_up='',
                                        text_content='Event Content',
                                        form_id='PersonModule_viewPersonList')

    self.tic()

    for person in (pers1, pers2):
      related_event = person.getDestinationRelatedValue(
                            portal_type='Mail Message')
      self.assertNotEqual(None, related_event)
      self.assertEqual('The Event Title', related_event.getTitle())
      self.assertEqual('The Event Descr.', related_event.getDescription())
      self.assertEqual('Event Content', related_event.getTextContent())

    self.assertEqual(None, pers3.getDestinationRelatedValue(
                                portal_type='Mail Message'))

  def test_SaleOpportunityClosed(self):
    # test the workflow of sale opportunities, when the sale opportunity is
    # finaly closed
    so = self.portal.sale_opportunity_module.newContent(
                              portal_type='Sale Opportunity')
    self.assertEqual('draft', so.getSimulationState())
    self.portal.portal_workflow.doActionFor(so, 'open_action')
    self.assertEqual('open', so.getSimulationState())
    self.portal.portal_workflow.doActionFor(so, 'suspend_action')
    self.assertEqual('suspended', so.getSimulationState())
    self.portal.portal_workflow.doActionFor(so, 'open_action')
    self.assertEqual('open', so.getSimulationState())
    self.portal.portal_workflow.doActionFor(so, 'close_action')
    self.assertEqual('closed', so.getSimulationState())


  def test_SaleOpportunityDeleted(self):
    # test the workflow of sale opportunities, cancel it
    so = self.portal.sale_opportunity_module.newContent(
                              portal_type='Sale Opportunity')
    self.assertEqual('draft', so.getSimulationState())
    self.portal.portal_workflow.doActionFor(so, 'delete_action')
    self.assertEqual('deleted', so.getSimulationState())

  def test_SaleOpportunityExpired(self):
    # test the workflow of sale opportunities, when the sale opportunity
    # expires
    so = self.portal.sale_opportunity_module.newContent(
                              portal_type='Sale Opportunity')
    self.assertEqual('draft', so.getSimulationState())
    self.portal.portal_workflow.doActionFor(so, 'open_action')
    self.assertEqual('open', so.getSimulationState())
    self.portal.portal_workflow.doActionFor(so, 'expire_action')
    self.assertEqual('expired', so.getSimulationState())

  def test_Ticket_getWorkflowStateTranslatedTitle(self):
    self.assertEqual(
      self.portal.campaign_module.newContent(
        portal_type='Campaign').Ticket_getWorkflowStateTranslatedTitle(),
     'Draft')
    self.assertEqual(
      self.portal.meeting_module.newContent(
        portal_type='Meeting').Ticket_getWorkflowStateTranslatedTitle(),
     'Draft')
    self.assertEqual(
      self.portal.support_request_module.newContent(
        portal_type='Support Request').Ticket_getWorkflowStateTranslatedTitle(),
     'Draft')
    self.assertEqual(
      self.portal.sale_opportunity_module.newContent(
        portal_type='Sale Opportunity').Ticket_getWorkflowStateTranslatedTitle(),
     'Draft')

  @expectedFailure
  def test_Event_AcknowledgeAndCreateEvent(self):
    """
    Make sure that when acknowledge event, we can create a new event.

    XXX This is probably meaningless in near future. event_workflow
    will be reviewed in order to have steps closer to usual packing
    list workflow. For now we have a conflict name between the
    acknowledge method of event_workflow and Acknowledgement features
    that comes with AcknowledgementTool. So for now disable site
    message in this test.
    """
    portal_workflow = self.portal.portal_workflow

    event_type_list = [x for x in self.portal.getPortalEventTypeList() \
                       if x not in  ['Site Message', 'Acknowledgement']]

    # if create_event option is false, it does not create a new event.
    for portal_type in event_type_list:
      ticket = self.portal.meeting_module.newContent(portal_type='Meeting',
                                                     title='Meeting1')
      ticket_url = ticket.getRelativeUrl()
      event = self.portal.event_module.newContent(portal_type=portal_type,
                                                  follow_up=ticket_url)
      self.tic()
      self.assertEqual(len(event.getCausalityRelatedValueList()), 0)
      event.receive()
      portal_workflow.doActionFor(event, 'acknowledge_action', create_event=0)
      self.tic()
      self.assertEqual(len(event.getCausalityRelatedValueList()), 0)

    # if create_event option is true, it create a new event.
    for portal_type in event_type_list:
      ticket = self.portal.meeting_module.newContent(portal_type='Meeting',
                                                     title='Meeting1')
      ticket_url = ticket.getRelativeUrl()
      event = self.portal.event_module.newContent(portal_type=portal_type,
                                                  follow_up=ticket_url)
      self.tic()
      self.assertEqual(len(event.getCausalityRelatedValueList()), 0)
      event.receive()
      portal_workflow.doActionFor(event, 'acknowledge_action', create_event=1)
      self.tic()
      self.assertEqual(len(event.getCausalityRelatedValueList()), 1)
      new_event = event.getCausalityRelatedValue()
      self.assertEqual(new_event.getFollowUp(), ticket_url)

    # if quote_original_message option is true, the new event content will be
    # the current event message quoted.
    for portal_type in event_type_list:
      ticket = self.portal.meeting_module.newContent(portal_type='Meeting',
                                                     title='Meeting1')
      ticket_url = ticket.getRelativeUrl()
      event = self.portal.event_module.newContent(portal_type=portal_type,
                                                  follow_up=ticket_url,
                                                  title='Event Title',
                                                  text_content='Event Content',
                                                  content_type='text/plain')
      self.tic()
      self.assertEqual(len(event.getCausalityRelatedValueList()), 0)
      event.receive()
      portal_workflow.doActionFor(event, 'acknowledge_action',
                                  create_event=1,
                                  quote_original_message=1)
      self.tic()
      self.assertEqual(len(event.getCausalityRelatedValueList()), 1)
      new_event = event.getCausalityRelatedValue()
      self.assertEqual(new_event.getFollowUp(), ticket_url)
      self.assertEqual(new_event.getContentType(), 'text/plain')
      self.assertEqual(new_event.getTextContent(), '> Event Content')
      self.assertEqual(new_event.getTitle(), 'Re: Event Title')

  def test_SupportRequest_referenceAutomaticallyGenerated(self):
    """
      When you create or clone a Support Request document, it must
      have the reference generated automatically.
    """
    portal_type = "Support Request"
    title = "Title of the Support Request"
    module = self.portal.support_request_module
    support_request = module.newContent(portal_type=portal_type,
                                        title=title,)
    self.tic()

    self.assertNotEqual(None, support_request.getReference())

    new_support_request = support_request.Base_createCloneDocument(
                                                                 batch_mode=1)
    self.assertEqual(new_support_request.getTitle(), title)
    self.assertNotEqual(None, support_request.getReference())
    self.assertNotEqual(support_request.getReference(),
                                        new_support_request.getReference())

  def test_posting_event_updates_support_request_modification_date(self):
    """Posting an event following up a support request updates the support request date.
    """
    sr = self.portal.support_request_module.newContent(portal_type='Support Request')
    sr_modification_date = sr.getModificationDate()
    event = self.portal.event_module.newContent(
        portal_type='Web Message',
        follow_up_value=sr
    )
    self.assertEqual(sr.getModificationDate(), sr_modification_date)
    event.start()
    self.commit()
    self.assertGreater(sr.getModificationDate(), sr_modification_date)


  def test_Event_getResourceItemList(self):
    """Event_getResourceItemList returns
    category item list with base category in path, just
    like resource.getCategoryChildItemList(base=True) does.
    This is not the expected behaviour because it
    duplicates the base_category in categories_list:
      - resource/resource/my_category_id
    This test checks that relative_url return
    by Event_getResourceItemList are consistent.
    Check also the support of backward compatibility to not break UI
    if resource is already defined with base_category
    in its relative_url value.
    """
    # create resource categories.
    resource = self.portal.portal_categories.resource
    for i in range(3):
      resource.newContent(portal_type='Category',
                          title='Title%s' % i,
                          id=i)
    # create a person like a resource to declare it as a resource
    person = self.portal.person_module.newContent(portal_type='Person')
    resource_list = [category.getRelativeUrl() \
                                      for category in resource.contentValues()]
    resource_list.append(person.getRelativeUrl())
    # XXX this preference is obsolete, this is now based on use category
    system_preference = self.getDefaultSystemPreference()
    system_preference.setPreferredEventResourceList(resource_list)
    self.tic()
    # Then create One event and play with it
    portal_type = 'Visit'
    module = self.portal.getDefaultModule(portal_type)
    event = module.newContent(portal_type=portal_type)
    # Check that existing valid resource relations which should not be normaly
    # found by Event_getResourceItemList are present.
    self.assertNotIn(event.getResource(),\
                       [item[1] for item in event.Event_getResourceItemList()])
    event.setResource('0')
    self.assertTrue(event.getResourceValue() is not None)
    self.assertIn(event.getResource(),\
                       [item[1] for item in event.Event_getResourceItemList()])
    # Check Backward compatibility support
    # When base_category value is stored in categories_list
    # resource/resource/my_category_id instead of resource/my_category_id
    event.setResource('resource/0')
    self.assertTrue(event.getResourceValue() is not None)
    self.assertIn(event.getResource(),\
                       [item[1] for item in event.Event_getResourceItemList()])

    # Check that relation with an object which
    # is not a Category works.
    event.setResourceValue(person)
    self.assertIn(event.getResource(),\
                       [item[1] for item in event.Event_getResourceItemList()])

  def test_EventPath(self):
    """
      Check that configuring the Event Path on Campaign, all events are
      created according to the domain selected
    """
    mapping_method_id = "NotificationMessage_getSubstitutionMappingDictFromEvent"
    portal = self.portal
    notification_message_reference = 'campaign-Event.Path'
    service = portal.service_module.newContent(portal_type='Service')
    notification_message = portal.notification_message_module.newContent(
        content_type="text/html",
        portal_type="Notification Message",
        specialise_value=service,
        text_content_substitution_mapping_method_id=mapping_method_id,
        text_content="Hello ${destination_title}")
    sender = portal.person_module.newContent(portal_type="Person",
        reference='sender', first_name='Sender')
    first_user = portal.person_module.newContent(portal_type="Person",
        reference='validated_user', first_name="First User")
    first_user.validate()
    organisation = portal.organisation_module.newContent(portal_type="Organisation",
        title="Dummy SA")
    organisation.validate()
    base_domain = portal.portal_domains.newContent(portal_type="Base Domain",
      id='event_path_domain')
    person_domain = base_domain.newContent(portal_type="Domain",
      title="All Customers")
    person_domain.setCriterionPropertyList(['portal_type', 'validation_state'])
    person_domain.setCriterion('portal_type', identity=['Person'])
    person_domain.setCriterion('validation_state', identity=['validated'])
    organisation_domain = base_domain.newContent(portal_type="Domain",
      title="All Organisations")
    organisation_domain.setCriterionPropertyList(['portal_type'])
    organisation_domain.setCriterion('portal_type', identity=['Organisation'])

    campaign = self.portal.campaign_module.newContent(
        portal_type="Campaign",
        default_event_path_event_portal_type="Mail Message",)

    # This action checks everything is properly defined
    ret = campaign.Ticket_createEventFromDefaultEventPath()
    self.assertEqual(
        six.moves.urllib.parse.parse_qs(six.moves.urllib.parse.urlparse(ret).query)['portal_status_message'],
        ["Recipients must be defined"])
    campaign.setDefaultEventPathDestination(
        "portal_domains/%s" % person_domain.getRelativeUrl())

    campaign.setDefaultEventPathEventPortalType(None)
    ret = campaign.Ticket_createEventFromDefaultEventPath()
    self.assertEqual(
        six.moves.urllib.parse.parse_qs(six.moves.urllib.parse.urlparse(ret).query)['portal_status_message'],
        ["Event Type must be defined"])
    campaign.setDefaultEventPathEventPortalType('Mail Message')

    ret = campaign.Ticket_createEventFromDefaultEventPath()
    self.assertEqual(
        six.moves.urllib.parse.parse_qs(six.moves.urllib.parse.urlparse(ret).query)['portal_status_message'],
        ["Sender must be defined"])
    campaign.setDefaultEventPathSource(sender.getRelativeUrl())

    ret = campaign.Ticket_createEventFromDefaultEventPath()
    self.assertEqual(
        six.moves.urllib.parse.parse_qs(six.moves.urllib.parse.urlparse(ret).query)['portal_status_message'],
        ["Notification Message must be defined"])
    campaign.setDefaultEventPathResource(notification_message.getRelativeUrl())

    ret = campaign.Ticket_createEventFromDefaultEventPath()
    self.assertEqual(
        six.moves.urllib.parse.parse_qs(six.moves.urllib.parse.urlparse(ret).query)['portal_status_message'],
        ["Notification Message must be validated"])
    notification_message.setReference(notification_message_reference)

    ret = campaign.Ticket_createEventFromDefaultEventPath()
    self.assertEqual(
        six.moves.urllib.parse.parse_qs(six.moves.urllib.parse.urlparse(ret).query)['portal_status_message'],
        ["Notification Message must be validated"])
    notification_message.validate()
    self.tic()

    ret = campaign.Ticket_createEventFromDefaultEventPath()
    self.assertEqual(
        six.moves.urllib.parse.parse_qs(six.moves.urllib.parse.urlparse(ret).query)['portal_status_message'],
        ["Events are being created in background"])
    self.tic()
    event_list = [event for event in campaign.getFollowUpRelatedValueList()
      if event.getPortalType() != 'Mail Message']
    self.assertEqual(event_list, [])
    event_list = campaign.getFollowUpRelatedValueList(portal_type='Mail Message')
    self.assertNotEqual(event_list, [])
    destination_list = [x.getDestinationValue() for x in event_list]
    self.assertEqual(destination_list, [first_user])
    mail_message = event_list[0]
    self.assertEqual(sender.getRelativeUrl(), mail_message.getSource())
    self.assertEqual(mail_message.getContentType(), "text/html")
    self.assertEqual(mail_message.getTextContent(), "Hello %s" % first_user.getTitle())
    self.assertEqual(mail_message.getResourceValue(), service)

    campaign = portal.campaign_module.newContent(portal_type="Campaign",
        default_event_path_event_portal_type="Visit",
        default_event_path_destination='portal_domains/%s' % organisation_domain.getRelativeUrl(),
        default_event_path_source=sender.getRelativeUrl(),
        default_event_path_resource=notification_message.getRelativeUrl())
    self.tic()
    campaign.Ticket_createEventFromDefaultEventPath()
    self.tic()
    event_list = [event for event in campaign.getFollowUpRelatedValueList()
      if event.getPortalType() != 'Visit']
    self.assertEqual([], event_list)
    event_list = campaign.getFollowUpRelatedValueList(portal_type='Visit')
    self.assertNotEqual([], event_list)
    destination_uid_list = [x.getDestinationUid() for x in event_list]
    self.assertEqual([organisation.getUid()], destination_uid_list)

    resource_value_list = [x.getResourceValue() for x in event_list]
    self.assertEqual([service], resource_value_list)

  def test_OutcomePath(self):
    service = self.portal.service_module.newContent(portal_type='Service')
    currency = self.portal.currency_module.newContent(portal_type='Currency')

    campaign = self.portal.campaign_module.newContent(portal_type="Campaign")
    campaign.setDefaultOutcomePathQuantity(3)
    campaign.setDefaultOutcomePathQuantityUnit('unit/piece')
    campaign.setDefaultOutcomePathResourceValue(service)
    campaign.setDefaultOutcomePathPrice(4)
    campaign.setDefaultOutcomePathPriceCurrency(currency.getRelativeUrl())

    self.assertEqual(3*4, campaign.getDefaultOutcomePathTotalPrice())

    self.assertEqual(3, campaign.getDefaultOutcomePathQuantity())
    self.assertEqual('unit/piece', campaign.getDefaultOutcomePathQuantityUnit())
    self.assertEqual(service.getRelativeUrl(),
      campaign.getDefaultOutcomePathResource())
    self.assertEqual(4, campaign.getDefaultOutcomePathPrice())
    self.assertEqual(currency.getRelativeUrl(),
      campaign.getDefaultOutcomePathPriceCurrency())

    outcome_path = campaign._getOb('default_outcome_path')
    self.assertEqual('Outcome Path', outcome_path.getPortalType())

class TestCRMMailIngestion(BaseTestCRM):
  """Test Mail Ingestion for standalone CRM.
  """
  def getTitle(self):
    return "CRM Mail Ingestion"

  def getBusinessTemplateList(self):
    # Mail Ingestion must work with CRM alone.
    return ('erp5_core_proxy_field_legacy',
            'erp5_full_text_mroonga_catalog',
            'erp5_base',
            'erp5_ingestion',
            'erp5_ingestion_mysql_innodb_catalog',
            'erp5_pdm',
            'erp5_crm',
            )

  def afterSetUp(self):
    super(TestCRMMailIngestion, self).afterSetUp()
    portal = self.portal

    # create customer organisation and person
    portal.organisation_module.newContent(
            id='customer',
            portal_type='Organisation',
            title='Customer')
    customer_organisation = portal.organisation_module.customer
    portal.person_module.newContent(
            id='sender',
            title='Sender',
            subordination_value=customer_organisation,
            default_email_text='sender@customer.com')
    # also create the recipients
    portal.person_module.newContent(
            id='me',
            title='Me',
            default_email_text='me@erp5.org')
    portal.person_module.newContent(
            id='he',
            title='He',
            default_email_text='he@erp5.org')

    # make sure customers are available to catalog
    self.tic()

  def _readTestData(self, filename):
    """read test data from data directory."""
    return open(makeFilePath(filename)).read()

  def _ingestMail(self, filename=None, data=None):
    """ingest an email from the mail in data dir named `filename`"""
    if data is None:
      data=self._readTestData(filename)
    return self.portal.portal_contributions.newContent(
                    container_path='event_module',
                    filename='postfix_mail.eml',
                    data=data)

  def test_findTypeByName_MailMessage(self):
    # without this, ingestion will not work
    self.assertEqual(
      'Mail Message',
      self.portal.portal_contribution_registry.findPortalTypeName(
      filename='postfix_mail.eml', content_type='message/rfc822', data=b'Test'
      ))

  def test_Base_getEntityListFromFromHeader(self):
    expected_values = (
      ('me@erp5.org', ['person_module/me']),
      ('me@erp5.org, he@erp5.org', ['person_module/me', 'person_module/he']),
      ('Sender <sender@customer.com>', ['person_module/sender']),
      # tricks to confuse the e-mail parser:
      # a comma in the name
      ('"Sender," <sender@customer.com>, he@erp5.org', ['person_module/sender',
                                                        'person_module/he']),
      # multiple e-mails in the "Name" part that shouldn't be parsed
      ('"me@erp5.org,sender@customer.com," <he@erp5.org>', ['person_module/he']),
      # capitalised version
      ('"me@erp5.org,sEnder@CUSTOMER.cOm," <he@ERP5.OrG>', ['person_module/he']),
      # a < sign
      ('"He<" <he@erp5.org>', ['person_module/he']),
    )
    portal = self.portal
    for header, expected_paths in expected_values:
      paths = [entity.getRelativeUrl()
               for entity in portal.Base_getEntityListFromFromHeader(header)]
      self.assertEqual(paths, expected_paths,
                        '%r should return %r, but returned %r' %
                        (header, expected_paths, paths))

  def test_document_creation(self):
    # CRM email ingestion creates a Mail Message in event_module
    event = self._ingestMail('simple')
    self.assertEqual(len(self.portal.event_module), 1)
    self.assertEqual(event, self.portal.event_module.contentValues()[0])
    self.assertEqual('Mail Message', event.getPortalType())
    self.assertEqual('text/plain', event.getContentType())
    self.assertEqual('message/rfc822', event._baseGetContentType())
    # check if parsing of metadata from content is working
    content_dict = {'source_list': ['person_module/sender'],
                    'destination_list': ['person_module/me',
                                         'person_module/he']}
    self.assertEqual(event.getPropertyDictFromContent(), content_dict)

  def test_title(self):
    # title is found automatically, based on the Subject: header in the mail
    event = self._ingestMail('simple')
    self.assertEqual('Simple Mail Test', event.getTitle())
    self.assertEqual('Simple Mail Test', event.getTitleOrId())

  def test_asText(self):
    # asText requires portal_transforms
    event = self._ingestMail('simple')
    self.assertEqual('Hello,\nContent of the mail.\n', str(event.asText()))

  def test_sender(self):
    # source is found automatically, based on the From: header in the mail
    event = self._ingestMail('simple')
    # metadata discovery is done in an activity
    self.tic()
    self.assertEqual('person_module/sender', event.getSource())

  def test_recipient(self):
    # destination is found automatically, based on the To: header in the mail
    event = self._ingestMail('simple')
    self.tic()
    destination_list = event.getDestinationList()
    destination_list.sort()
    self.assertEqual(['person_module/he', 'person_module/me'],
                      destination_list)

  def test_clone(self):
    # cloning an event must keep title and text-content
    event = self._ingestMail('simple')
    self.tic()
    self.assertEqual('Simple Mail Test', event.getTitle())
    self.assertEqual('Simple Mail Test', event.getTitleOrId())
    self.assertEqual('Hello,\nContent of the mail.\n', str(event.asText()))
    self.assertEqual('Hello,\nContent of the mail.\n', str(event.getTextContent()))
    self.assertEqual('Mail Message', event.getPortalType())
    self.assertEqual('text/plain', event.getContentType())
    self.assertEqual('message/rfc822', event._baseGetContentType())
    # check if parsing of metadata from content is working
    content_dict = {'source_list': ['person_module/sender'],
                    'destination_list': ['person_module/me',
                                         'person_module/he']}
    self.assertEqual(event.getPropertyDictFromContent(), content_dict)
    new_event = event.Base_createCloneDocument(batch_mode=1)
    self.tic()
    self.assertEqual('Simple Mail Test', new_event.getTitle())
    self.assertEqual('Simple Mail Test', new_event.getTitleOrId())
    self.assertEqual('Hello,\nContent of the mail.\n', str(new_event.asText()))
    self.assertEqual('Hello,\nContent of the mail.\n', str(new_event.getTextContent()))
    self.assertEqual('Mail Message', new_event.getPortalType())
    self.assertEqual('text/plain', new_event.getContentType())

    # check that metadatas read from data are copied on cloned event
    self.assertEqual(new_event.getSourceList(), ['person_module/sender'])
    self.assertEqual(new_event.getDestinationList(), ['person_module/me',
                                                       'person_module/he'])

    # cloned event got a new reference
    self.assertNotEqual(new_event.getReference(), event.getReference())

  def test_getPropertyDictFromContent_and_defined_arrow(self):
    # If source/destination are set on event, then getPropertyDictFromContent
    # should not lookup one based on email address.
    self.portal.person_module.newContent(
        portal_type='Person',
        default_email_coordinate_text='destination@example.com',)
    organisation = self.portal.organisation_module.newContent(
        portal_type='Organisation',
        default_email_coordinate_text='destination@example.com',)
    source_person = self.portal.person_module.newContent(
        portal_type='Person',
        default_email_coordinate_text='source@example.com',)
    self.tic()
    event = self.portal.event_module.newContent(
        portal_type='Mail Message',
        destination_value=organisation,
        data=('\r\n'.join(textwrap.dedent('''
        From: Source <source@example.com>
        To: destination <destination@example.com>
        Subject: mail subject

        content
        ''').splitlines()[1:])).encode())

    property_dict = event.getPropertyDictFromContent()
    # destination is set on the event. In this case it is kept as is.
    self.assertEqual([organisation.getRelativeUrl()],
        property_dict['destination_list'])
    # source is not set. In this case it is searched in catalog based on email
    # address
    self.assertEqual([source_person.getRelativeUrl()],
        property_dict['source_list'])


  def test_follow_up(self):
    # follow up is found automatically, based on the content of the mail, and
    # what you defined in preference regexpr.
    # But, we don't want it to associate with the first campaign simply
    # because we searched against nothing
    self.portal.campaign_module.newContent(portal_type='Campaign')
    self.tic()
    event = self._ingestMail('simple')
    self.tic()
    self.assertEqual(None, event.getFollowUp())

  def test_portal_type_determination(self):
    """
    Make sure that ingested email will be correctly converted to
    appropriate portal type by email metadata.
    """
    def getLastCreatedEvent(module):
      object_list = module.contentValues()
      object_list.sort(key=lambda e:e.getCreationDate())
      return object_list[-1]

    portal = self.portal
    message = message_from_string(self._readTestData('simple'))
    message.replace_header('subject', 'Visit:Company A')
    data = message.as_string()
    self._ingestMail(data=data)
    self.tic()
    document = getLastCreatedEvent(portal.event_module)
    self.assertEqual(document.getPortalType(), 'Visit')

    message = message_from_string(self._readTestData('simple'))
    message.replace_header('subject', 'Fax:Company B')
    data = message.as_string()
    self._ingestMail(data=data)
    self.tic()
    document = getLastCreatedEvent(portal.event_module)
    self.assertEqual(document.getPortalType(), 'Fax Message')

    message = message_from_string(self._readTestData('simple'))
    message.replace_header('subject', 'TEST:Company B')
    data = message.as_string()
    self._ingestMail(data=data)
    self.tic()
    document = getLastCreatedEvent(portal.event_module)
    self.assertEqual(document.getPortalType(), 'Mail Message')

    message = message_from_string(self._readTestData('simple'))
    message.replace_header('subject', 'visit:Company A')
    data = message.as_string()
    self._ingestMail(data=data)
    self.tic()
    document = getLastCreatedEvent(portal.event_module)
    self.assertEqual(document.getPortalType(), 'Visit')

    message = message_from_string(self._readTestData('simple'))
    message.replace_header('subject', 'phone:Company B')
    data = message.as_string()
    self._ingestMail(data=data)
    self.tic()
    document = portal.event_module[portal.event_module.objectIds()[-1]]
    self.assertEqual(document.getPortalType(), 'Phone Call')

    message = message_from_string(self._readTestData('simple'))
    message.replace_header('subject', 'LETTER:Company C')
    data = message.as_string()
    self._ingestMail(data=data)
    self.tic()
    document = getLastCreatedEvent(portal.event_module)
    self.assertEqual(document.getPortalType(), 'Letter')

    message = message_from_string(self._readTestData('simple'))
    body = message.get_payload()
    message.set_payload('Visit:%s' % body)
    data = message.as_string()
    self._ingestMail(data=data)
    self.tic()
    document = getLastCreatedEvent(portal.event_module)
    self.assertEqual(document.getPortalType(), 'Visit')

    message = message_from_string(self._readTestData('simple'))
    body = message.get_payload()
    message.set_payload('PHONE CALL:%s' % body)
    data = message.as_string()
    self._ingestMail(data=data)
    self.tic()
    document = getLastCreatedEvent(portal.event_module)
    self.assertEqual(document.getPortalType(), 'Phone Call')

  def test_forwarder_mail(self):
    """
    Make sure that if ingested email is forwarded one, the sender of
    original mail should be the sender of event and the sender of
    forwarded mail should be the recipient of event.
    """
    document = self._ingestMail(filename='forwarded')

    self.tic()

    self.assertEqual(document.getContentInformation().get('From'), 'Me <me@erp5.org>')
    self.assertEqual(document.getContentInformation().get('To'), 'crm@erp5.org')
    self.assertEqual(document.getSourceValue().getTitle(), 'Sender')
    self.assertEqual(document.getDestinationValue().getTitle(), 'Me')

  def test_forwarder_mail_with_attachment(self):
    """
    Make sure that if ingested email is forwarded one, the sender of
    original mail should be the sender of event and the sender of
    forwarded mail should be the recipient of event.
    """
    document = self._ingestMail(filename='forwarded_attached')

    self.tic()

    self.assertEqual(document.getContentInformation().get('From'), 'Me <me@erp5.org>')
    self.assertEqual(document.getContentInformation().get('To'), 'crm@erp5.org')
    self.assertEqual(document.getSourceValue().getTitle(), 'Sender')
    self.assertEqual(document.getDestinationValue().getTitle(), 'Me')

  def test_encoding(self):
    document = self._ingestMail(filename='encoded')

    self.tic()

    self.assertEqual(document.getContentInformation().get('To'),
                     'Me <me@erp5.org>')
    self.assertEqual(document.getSourceValue().getTitle(), 'Sender')
    self.assertEqual(document.getDestinationValue().getTitle(), 'Me')
    self.assertEqual(document.getContentInformation().get('Subject'),
                     'Test éncödèd email')
    self.assertEqual(document.getTitle(), 'Test éncödèd email')
    self.assertEqual(document.getTextContent(), 'cöntént\n')


  def test_HTML_multipart_attachments(self):
    """Test that html attachments are cleaned up.
    and check the behaviour of getTextContent
    if multipart/alternative return html
    if multipart/mixed return text
    """
    document = self._ingestMail(filename='sample_multipart_mixed_and_alternative')
    self.tic()
    stripped_html = document.asStrippedHTML()
    self.assertNotIn('<form', stripped_html)
    self.assertNotIn('<form', document.getAttachmentData(4))
    self.assertEqual('This is my content.\n*ERP5* is a Free _Software_\n',
                      document.getAttachmentData(2))
    self.assertEqual('text/html', document.getContentType())
    self.assertEqual('\n<html>\n<head>\n\n<meta http-equiv="content-type"'\
                      ' content="text/html; charset=utf-8" />\n'\
                      '</head>\n<body text="#000000"'\
                      ' bgcolor="#ffffff">\nThis is my content.<br />\n'\
                      '<b>ERP5</b> is a Free <u>Software</u><br />'\
                      '\n\n</body>\n</html>\n', document.getAttachmentData(3))
    self.assertEqual(document.getAttachmentData(3), document.getTextContent())

    # now check a message with multipart/mixed
    mixed_document = self._ingestMail(filename='sample_html_attachment')
    self.tic()
    self.assertEqual(mixed_document.getAttachmentData(1),
                      mixed_document.getTextContent())
    self.assertEqual('Hi, this is the Message.\nERP5 is a free software.\n\n',
                      mixed_document.getTextContent())
    self.assertEqual('text/plain', mixed_document.getContentType())

  def test_flawed_html_attachment(self):
    portal_type = 'Mail Message'
    event = self.portal.getDefaultModule(portal_type).newContent(portal_type=portal_type)
    # build message content with flwd attachment
    html_filename = 'broken_html.html'
    file_path = '%s/test_data/%s' % (
      os.path.dirname(Products.ERP5.tests.__file__),
      html_filename)
    html_message = open(file_path, 'r').read()
    message = MIMEMultipart('alternative')
    message.attach(MIMEText('text plain content', _charset='utf-8'))
    part = MIMEBase('text', 'html')
    part.set_payload(html_message)
    encoders.encode_base64(part)

    part.add_header('Content-Disposition', 'attachment')
    part.add_header('Content-ID', '<%s>' % \
                    ''.join(['%s' % ord(i) for i in html_filename]))
    message.attach(part)
    event.setData(message.as_string())
    self.tic()
    self.assertIn('html', event.getTextContent())
    self.assertEqual(len(event.getAttachmentInformationList()), 2)
    self.assertTrue(bool(event.getAttachmentData(1)))
    self.assertTrue(bool(event.getAttachmentData(2)))

  def test_getMessageTextPart(self):
    portal_type = 'Mail Message'
    event = self.portal.getDefaultModule(portal_type).newContent(portal_type=portal_type)
    for filename in ('gmail.eml', 'outlook.eml', 'roundcube.eml'):
      file_path = '%s/test_data/%s' % (
        os.path.dirname(Products.ERP5.tests.__file__),
        filename)
      with open(file_path, 'rb') as f:
        event.setData(f.read())
      self.assertTrue(event.getTextContent().startswith('<'))





## TODO:
##
##  def test_attachements(self):
##    event = self._ingestMail('with_attachements')
##

class TestCRMMailSend(BaseTestCRM):
  """Test Mail Sending for CRM
  """
  def getTitle(self):
    return "CRM Mail Sending"

  def getBusinessTemplateList(self):
    # In this test, We will attach some document portal types in event.
    # So we add DMS and Web.
    return ('erp5_base',
            'erp5_ingestion',
            'erp5_ingestion_mysql_innodb_catalog',
            'erp5_crm',
            'erp5_web',
            'erp5_dms',
            )

  def afterSetUp(self):
    super(TestCRMMailSend, self).afterSetUp()
    portal = self.portal
    # create customer organisation and person
    portal.organisation_module.newContent(
            id='customer',
            portal_type='Organisation',
            title='Customer')
    customer_organisation = portal.organisation_module.customer
    portal.person_module.newContent(
            id='recipient',
            # The ',' below is to force quoting of the name in e-mail
            # addresses on Zope 2.12
            title='Recipient,',
            subordination_value=customer_organisation,
            default_email_text='recipient@example.com')
    portal.person_module.newContent(
            id='non_ascii_recipient',
            # The ',' below is to force quoting of the name in e-mail
            # addresses on Zope 2.12
            title='Recipient, 🐈 fan',
            subordination_value=customer_organisation,
            default_email_text='recipient@example.com')
    # also create the sender
    portal.person_module.newContent(
            id='me',
            # The ',' below is to force quoting of the name in e-mail
            # addresses on Zope 2.12
            title='Me,',
            default_email_text='me@erp5.org')
    portal.person_module.newContent(
            id='non_ascii_me',
            # The ',' below is to force quoting of the name in e-mail
            # addresses on Zope 2.12
            title='Me, 🐈 fan',
            default_email_text='me@erp5.org')

    # set preference
    pref = self.getDefaultSystemPreference()
    pref.setPreferredDocumentFilenameRegularExpression(FILENAME_REGULAR_EXPRESSION)
    pref.setPreferredDocumentReferenceRegularExpression(REFERENCE_REGULAR_EXPRESSION)

    # make sure customers are available to catalog
    self.tic()

  def test_MailFromMailMessageEvent(self):
    # passing start_action transition on event workflow will send an email to the
    # person as destination
    text_content = 'Mail Content'
    event = self.portal.event_module.newContent(portal_type='Mail Message')
    event.setSource('person_module/me')
    event.setDestination('person_module/recipient')
    event.setTitle('A Mail')
    event.setTextContent(text_content)
    self.portal.portal_workflow.doActionFor(event, 'start_action')
    self.tic()
    last_message, = self.portal.MailHost._message_list
    self.assertNotEqual((), last_message)
    mfrom, mto, messageText = last_message
    self.assertEqual('"Me," <me@erp5.org>', mfrom)
    self.assertEqual(['"Recipient," <recipient@example.com>'], mto)
    self.assertEqual(event.getTextContent(), text_content)
    message = message_from_string(messageText)

    self.assertEqual('A Mail', decode_header(message['Subject'])[0][0])
    part = None
    for i in message.get_payload():
      if i.get_content_type()=='text/plain':
        part = i
    self.assertEqual(text_content, part.get_payload(decode=True))

    #
    # Test multiple recipients.
    #
    event = self.portal.event_module.newContent(portal_type='Mail Message')
    event.setSource('person_module/me')
    # multiple recipients.
    event.setDestinationList(['person_module/recipient', 'person_module/me'])
    event.setTitle('A Mail')
    event.setTextContent(text_content)
    self.portal.portal_workflow.doActionFor(event, 'start_action')
    self.tic()
    last_message_1, last_message_2 = self.portal.MailHost._message_list[-2:]
    self.assertNotEqual((), last_message_1)
    self.assertNotEqual((), last_message_2)
    # check last message 1 and last message 2 (the order is random)
    # both should have 'From: Me'
    self.assertEqual(['"Me," <me@erp5.org>', '"Me," <me@erp5.org>'],
                      [x[0] for x in (last_message_1, last_message_2)])
    # one should have 'To: Me' and the other should have 'To: Recipient'
    self.assertEqual([['"Me," <me@erp5.org>'], ['"Recipient," <recipient@example.com>']],
                      sorted([x[1] for x in (last_message_1, last_message_2)]))

  def test_MailFromMailMessageEventNoSendMail(self):
    # for Mail Message, passing start_action transition on event workflow will send an email to the
    # person as destination. To prevent this, one can use initial_stop_action to mark
    # the event receieved.
    event = self.portal.event_module.newContent(portal_type='Mail Message')
    event.setSource('person_module/me')
    event.setDestination('person_module/recipient')
    event.setTitle('A Mail')
    event.setTextContent('Mail Content')
    self.portal.portal_workflow.doActionFor(event, 'initial_stop_action')
    self.assertEqual('stopped', event.getSimulationState())
    self.tic()
    # no mail sent
    last_message = self.portal.MailHost._last_message
    self.assertEqual((), last_message)

  def test_MailFromOtherEvents(self):
    # passing start_action transition on event workflow will not send an email
    # when the portal type is not Mail Message
    for ptype in [t for t in self.portal.getPortalEventTypeList()
        if t not in ('Mail Message', 'Document Ingestion Message',
          'Acknowledgement')]:
      event = self.portal.event_module.newContent(portal_type=ptype)
      event.setSource('person_module/me')
      event.setDestination('person_module/recipient')
      event.setTextContent('Hello !')
      self.portal.portal_workflow.doActionFor(event, 'start_action')

      self.tic()
      # this means no message have been set
      self.assertEqual([], self.portal.MailHost._message_list)
      self.assertEqual((), self.portal.MailHost._last_message)

  def test_MailMessageHTML(self):
    # test sending a mail message edited as HTML (the default with FCKEditor),
    # then the mail should have HTML.
    text_content = 'Hello<br />World'
    event = self.portal.event_module.newContent(portal_type='Mail Message')
    event.setSource('person_module/me')
    event.setDestination('person_module/recipient')
    event.setContentType('text/html')
    event.setTextContent(text_content)
    self.portal.portal_workflow.doActionFor(event, 'start_action')
    self.tic()
    # content type is kept
    self.assertEqual(event.getContentType(), 'text/html')

    last_message = self.portal.MailHost._last_message
    self.assertNotEqual((), last_message)
    mfrom, mto, messageText = last_message
    self.assertEqual('"Me," <me@erp5.org>', mfrom)
    self.assertEqual(['"Recipient," <recipient@example.com>'], mto)

    message = message_from_string(messageText)
    part = None
    for i in message.get_payload():
      if i.get_content_type()=='text/html':
        part = i
    self.assertNotEqual(part, None)
    self.assertEqual('<html><body>%s</body></html>' % text_content, part.get_payload(decode=True))

  def test_MailMessageEncoding(self):
    # test sending a mail message with non ascii characters
    event = self.portal.event_module.newContent(portal_type='Mail Message')
    event.setSource('person_module/non_ascii_me')
    event.setDestinationList(['person_module/non_ascii_recipient'])
    event.setTitle('Héhé')
    event.setTextContent('Hàhà')
    self.portal.portal_workflow.doActionFor(event, 'start_action')
    self.tic()
    last_message = self.portal.MailHost._last_message
    self.assertNotEqual((), last_message)
    mfrom, mto, messageText = last_message
    self.assertEqual('=?utf-8?q?Me=2C_=F0=9F=90=88_fan?= <me@erp5.org>', mfrom)
    self.assertEqual(['=?utf-8?q?Recipient=2C_=F0=9F=90=88_fan?= <recipient@example.com>'], mto)

    message = message_from_string(messageText)

    self.assertEqual('Héhé', decode_header(message['Subject'])[0][0])
    self.assertEqual('Me, 🐈 fan', decode_header(message['From'])[0][0])
    self.assertEqual('Recipient, 🐈 fan', decode_header(message['To'])[0][0])
    part = None
    for i in message.get_payload():
      if i.get_content_type()=='text/plain':
        part = i
    self.assertEqual('Hàhà', part.get_payload(decode=True))

  def test_MailAttachmentPdf(self):
    """
    Make sure that pdf document is correctly attached in email
    """
    # Add a document which will be attached.
    # pdf
    filename = 'sample_attachment.pdf'
    file_object = makeFileUpload(filename)
    document = self.portal.portal_contributions.newContent(file=file_object)

    self.tic()

    # Add a ticket
    ticket = self.portal.campaign_module.newContent(portal_type='Campaign',
                                                    title='Advertisement')
    # Create a event
    ticket.Ticket_newEvent(portal_type='Mail Message',
                           title='Our new product',
                           text_content='Buy this now!',
                           event_workflow_action='plan')

    # Set sender and attach a document to the event.
    event, = self.portal.event_module.objectValues()
    event.edit(source='person_module/me',
               destination='person_module/recipient',
               aggregate=document.getRelativeUrl(),
               text_content='This is an advertisement mail.')

    mail_text = event.send(download=True)

    # Check mail text.
    message = message_from_string(mail_text)
    part = None
    for i in message.get_payload():
      if i.get_content_type()=='text/plain':
        part = i
    self.assertEqual(part.get_payload(decode=True), event.getTextContent())

    # Check attachment
    # pdf
    self.assertIn(filename,
                 [i.get_filename() for i in message.get_payload()])
    part = None
    for i in message.get_payload():
      if i.get_filename()==filename:
        part = i
    self.assertEqual(part.get_payload(decode=True), str(document.getData()))

  def test_MailAttachmentText(self):
    """
    Make sure that text document is correctly attached in email
    """
    # Add a document which will be attached.
    filename = 'sample_attachment.odt'
    file_object = makeFileUpload(filename)
    document = self.portal.portal_contributions.newContent(file=file_object)

    self.tic()

    # Add a ticket
    ticket = self.portal.campaign_module.newContent(portal_type='Campaign',
                                                    title='Advertisement')
    # Create a event
    ticket.Ticket_newEvent(portal_type='Mail Message',
                           title='Our new product',
                           text_content='Buy this now!',
                           event_workflow_action='plan')

    # Set sender and attach a document to the event.
    event, = self.portal.event_module.objectValues()
    event.edit(source='person_module/me',
               destination='person_module/recipient',
               aggregate=document.getRelativeUrl(),
               text_content='This is an advertisement mail.')

    mail_text = event.send(download=True)

    # Check mail text.
    message = message_from_string(mail_text)
    part = None
    for i in message.get_payload():
      if i.get_content_type()=='text/plain':
        part = i
    self.assertEqual(part.get_payload(decode=True), event.getTextContent())

    # Check attachment
    # odt
    self.assertIn(filename,
                 [i.get_filename() for i in message.get_payload()])
    part = None
    for i in message.get_payload():
      if i.get_filename() == filename:
        part = i
    self.assertTrue(len(part.get_payload(decode=True))>0)

  def test_MailAttachmentFile(self):
    """
    Make sure that file document is correctly attached in email
    """
    # Add a document which will be attached.
    filename = 'sample_attachment.zip'
    file_object = makeFileUpload(filename)
    document = self.portal.portal_contributions.newContent(file=file_object)
    self.tic()

    # Add a ticket
    ticket = self.portal.campaign_module.newContent(portal_type='Campaign',
                                                    title='Advertisement')
    # Create a event
    ticket.Ticket_newEvent(portal_type='Mail Message',
                           title='Our new product',
                           text_content='Buy this now!',
                           event_workflow_action='plan')

    # Set sender and attach a document to the event.
    event, = self.portal.event_module.objectValues()
    event.edit(source='person_module/me',
               destination='person_module/recipient',
               aggregate=document.getRelativeUrl(),
               text_content='This is an advertisement mail.')

    mail_text = event.send(download=True)
    # Check mail text.
    message = message_from_string(mail_text)
    part = None
    for i in message.get_payload():
      if i.get_content_type()=='text/plain':
        part = i
    self.assertEqual(part.get_payload(decode=True), event.getTextContent())

    # Check attachment
    # zip
    self.assertIn(filename,
                 [i.get_filename() for i in message.get_payload()])
    part = None
    for i in message.get_payload():
      if i.get_filename() == filename:
        part = i
    self.assertTrue(len(part.get_payload(decode=True))>0)

  def test_MailAttachmentImage(self):
    """
    Make sure that image document is correctly attached in email
    """
    # Add a document which will be attached.
    filename = 'sample_attachment.gif'
    file_object = makeFileUpload(filename)
    document = self.portal.portal_contributions.newContent(file=file_object)

    self.tic()

    # Add a ticket
    ticket = self.portal.campaign_module.newContent(portal_type='Campaign',
                                                    title='Advertisement')
    # Create a event
    ticket.Ticket_newEvent(portal_type='Mail Message',
                           title='Our new product',
                           text_content='Buy this now!',
                           event_workflow_action='plan')

    # Set sender and attach a document to the event.
    event, = self.portal.event_module.objectValues()
    event.edit(source='person_module/me',
               destination='person_module/recipient',
               aggregate=document.getRelativeUrl(),
               text_content='This is an advertisement mail.')

    mail_text = event.send(download=True)

    # Check mail text.
    message = message_from_string(mail_text)
    part = None
    for i in message.get_payload():
      if i.get_content_type()=='text/plain':
        part = i
    self.assertEqual(part.get_payload(decode=True), event.getTextContent())

    # Check attachment
    # gif
    self.assertIn(filename,
                 [i.get_filename() for i in message.get_payload()])
    part = None
    for i in message.get_payload():
      if i.get_filename() == filename:
        part = i
    self.assertEqual(part.get_payload(decode=True), str(document.getData()))

  def test_MailAttachmentWebPage(self):
    """
    Make sure that webpage document is correctly attached in email
    """
    # Add a document which will be attached.
    filename = 'sample_attachment.html'
    document = self.portal.portal_contributions.newContent(
                          data='<html><body>Hello world!</body></html>',
                          filename=filename)
    self.tic()

    # Add a ticket
    ticket = self.portal.campaign_module.newContent(portal_type='Campaign',
                                                    title='Advertisement')
    # Create a event
    ticket.Ticket_newEvent(portal_type='Mail Message',
                           title='Our new product',
                           text_content='Buy this now!',
                           event_workflow_action='plan')

    # Set sender and attach a document to the event.
    event, = self.portal.event_module.objectValues()
    event.edit(source='person_module/me',
               destination='person_module/recipient',
               aggregate=document.getRelativeUrl(),
               text_content='This is an advertisement mail.')

    mail_text = event.send(download=True)

    # Check mail text.
    message = message_from_string(mail_text)
    part = None
    for i in message.get_payload():
      if i.get_content_type()=='text/plain':
        part = i
    self.assertEqual(part.get_payload(decode=True), event.getTextContent())

    # Check attachment
    # html
    self.assertIn(filename,
                 [i.get_filename() for i in message.get_payload()])
    part = None
    for i in message.get_payload():
      if i.get_filename() == filename:
        part = i
    self.assertEqual(part.get_payload(decode=True),
                     str(document.getTextContent()))
    self.assertEqual(part.get_content_type(), 'text/html')

  def test_AttachPdfToMailUsingNewEventDialog(self):
    """
    Make sure that pdf document is correctly attached in email
    """
    # Add a document which will be attached.
    # pdf
    filename = 'sample_attachment.pdf'
    file_object = makeFileUpload(filename)

    # Add a ticket
    ticket = self.portal.campaign_module.newContent(portal_type='Campaign',
                                                    title='Advertisement')
    # Create a event
    ticket.Ticket_newEvent(portal_type='Mail Message',
                           title='Our new product',
                           text_content='Buy this now!',
                           event_workflow_action='plan',
                           attachment_file=file_object)

    # Check that attachment is embedded in Mail Message
    event, = self.portal.event_module.objectValues()
    document, = event.objectValues(portal_type='Embedded File')
    self.assertEqual(document.getFilename(), filename)

    # Set sender to the event.
    event.edit(source='person_module/me',
               destination='person_module/recipient',
               text_content='This is an advertisement mail.')

    mail_text = event.send(download=True)

    # Check mail text.
    message = message_from_string(mail_text)
    part = None
    for i in message.get_payload():
      if i.get_content_type()=='text/plain':
        part = i
    self.assertEqual(part.get_payload(decode=True), event.getTextContent())

    # Check attachment
    # pdf
    self.assertIn(filename,
                 [i.get_filename() for i in message.get_payload()])
    part = None
    for i in message.get_payload():
      if i.get_filename()==filename:
        part = i
    self.assertEqual(part.get_payload(decode=True), str(document.getData()))

  def test_AttachFileToMailUsingNewEventDialog(self):
    """
    Make sure that file document is correctly attached in email
    """
    # Add a document which will be attached.
    filename = 'sample_attachment.zip'
    file_object = makeFileUpload(filename)

    # Add a ticket
    ticket = self.portal.campaign_module.newContent(portal_type='Campaign',
                                                    title='Advertisement')
    # Create a event
    ticket.Ticket_newEvent(portal_type='Mail Message',
                           title='Our new product',
                           text_content='Buy this now!',
                           event_workflow_action='plan',
                           attachment_file=file_object)

    # Check that attachment is embedded in Mail Message
    event, = self.portal.event_module.objectValues()
    document, = event.objectValues(portal_type='Embedded File')
    self.assertEqual(document.getFilename(), filename)

    # Set sender to the event.
    event, = self.portal.event_module.objectValues()
    event.edit(source='person_module/me',
               destination='person_module/recipient',
               text_content='This is an advertisement mail.')

    mail_text = event.send(download=True)
    # Check mail text.
    message = message_from_string(mail_text)
    part = None
    for i in message.get_payload():
      if i.get_content_type()=='text/plain':
        part = i
    self.assertEqual(part.get_payload(decode=True), event.getTextContent())

    # Check attachment
    # zip
    self.assertIn(filename,
                 [i.get_filename() for i in message.get_payload()])
    part = None
    for i in message.get_payload():
      if i.get_filename() == filename:
        part = i
    self.assertTrue(len(part.get_payload(decode=True))>0)

  def test_testValidatorForAttachmentField(self):
    """
    If an Event Type doesn't allow Emebedded Files in its sub portal types,
    then the dialog should tell the user that attachment can't be uploaded
    """
    # Add a document which will be attached.
    filename = 'sample_attachment.zip'
    file_object = makeFileUpload(filename)

    # Add a ticket
    ticket = self.portal.campaign_module.newContent(portal_type='Campaign',
                                                    title='Advertisement')

    # Check that hypothesis is True
    self.assertNotIn(
      'Embedded File',
      self.portal.portal_types['Phone Call'].getTypeAllowedContentTypeList()
    )

    request_form = self.portal.REQUEST.form
    request_form['field_your_portal_type'] = 'Phone Call'

    self.assertFalse(
      ticket.Ticket_validateAttachmentFileField(file_object, self.portal.REQUEST))

    # Check that hypothesis is True
    self.assertIn(
      'Embedded File',
      self.portal.portal_types['Mail Message'].getTypeAllowedContentTypeList()
    )
    request_form['field_your_portal_type'] = 'Mail Message'

    self.assertTrue(
      ticket.Ticket_validateAttachmentFileField(file_object, self.portal.REQUEST))

  def test_MailRespond(self):
    """
    Test we can answer an incoming event and quote it
    """
    # Add a ticket
    ticket = self.portal.campaign_module.newContent(portal_type='Campaign',
                                                    title='Advertisement')
    # Create a event
    ticket.Ticket_newEvent(portal_type='Mail Message',
                           title='Our new product',
                           text_content='Buy this now!',
                           event_workflow_action='deliver')

    # Set sender and attach a document to the event.
    event, = self.portal.event_module.objectValues()
    event.edit(source='person_module/me',
               destination='person_module/recipient',
               text_content='This is an advertisement mail.')
    first_event_id = event.getId()
    event.Event_createResponse(response_event_portal_type='Mail Message',
                               response_event_title='Answer',
                               response_event_text_content='> This is an advertisement mail.',
                               response_workflow_action='send',
                               )

    self.assertEqual(event.getSimulationState(), "delivered")

    # answer event must have been created
    self.assertEqual(len(self.portal.event_module), 2)
    for ev in self.portal.event_module.objectValues():
      if ev.getId() != first_event_id:
        answer_event = ev

    # check properties of answer event
    self.assertEqual(answer_event.getSimulationState(), "started")
    self.assertEqual(answer_event.getCausality(), event.getRelativeUrl())
    self.assertEqual(answer_event.getDestination(), 'person_module/me')
    self.assertEqual(answer_event.getSource(), 'person_module/recipient')
    self.assertEqual(answer_event.getTextContent(), '> This is an advertisement mail.')
    self.assertEqual(answer_event.getFollowUpValue(), ticket)
    self.assertTrue(answer_event.getData() is not None)

  def test_MailAttachmentFileWithoutDMS(self):
    """
    Make sure that file document is correctly attached in email
    """
    # Add a document on a person which will be attached.

    def add_document(filename, container, portal_type):
      f = makeFileUpload(filename)
      document = container.newContent(portal_type=portal_type)
      document.edit(file=f, reference=filename)
      return document
    filename = 'sample_attachment.txt'
    # txt
    document_txt = add_document(filename,
                                self.portal.person_module['me'], 'Embedded File')

    self.tic()

    # Add a ticket
    ticket = self.portal.campaign_module.newContent(portal_type='Campaign',
                                                    title='Advertisement')
    # Create a event
    ticket.Ticket_newEvent(portal_type='Mail Message',
                           title='Our new product',
                           text_content='Buy this now!',
                           event_workflow_action='plan')

    # Set sender and attach a document to the event.
    event, = self.portal.event_module.objectValues()
    event.edit(source='person_module/me',
               destination='person_module/recipient',
               aggregate=document_txt.getRelativeUrl(),
               text_content='This is an advertisement mail.')

    mail_text = event.send(download=True)

    # Check mail text.
    message = message_from_string(mail_text)
    part = None
    for i in message.get_payload():
      if i.get_content_type()=='text/plain':
        part = i
        break
    self.assertEqual(part.get_payload(decode=True), event.getTextContent())

    # Check attachment
    # txt
    self.assertIn(filename,
                 [i.get_filename() for i in message.get_payload()])
    part = None
    for i in message.get_payload():
      if i.get_filename() == filename:
        part = i
    self.assertTrue(len(part.get_payload(decode=True))>0)



  def test_MailAttachmentImageWithoutDMS(self):
    """
    Make sure that image document is correctly attached in email without dms
    """
    # Add a document on a person which will be attached.

    def add_document(filename, container, portal_type):
      f = makeFileUpload(filename)
      document = container.newContent(portal_type=portal_type)
      document.edit(file=f, reference=filename)
      return document

    # gif
    filename = 'sample_attachment.gif'
    document_gif = add_document(filename,
                                self.portal.person_module['me'], 'Embedded File')

    self.tic()

    # Add a ticket
    ticket = self.portal.campaign_module.newContent(portal_type='Campaign',
                                                    title='Advertisement')
    # Create a event
    ticket.Ticket_newEvent(portal_type='Mail Message',
                           title='Our new product',
                           text_content='Buy this now!',
                           event_workflow_action='plan')

    # Set sender and attach a document to the event.
    event, = self.portal.event_module.objectValues()
    event.edit(source='person_module/me',
               destination='person_module/recipient',
               aggregate=document_gif.getRelativeUrl(),
               text_content='This is an advertisement mail.')

    mail_text = event.send(download=True)

    # Check mail text.
    message = message_from_string(mail_text)
    part = None
    for i in message.get_payload():
      if i.get_content_type()=='text/plain':
        part = i
    self.assertEqual(part.get_payload(decode=True), event.getTextContent())

    # Check attachment
    # gif
    self.assertIn(filename,
                 [i.get_filename() for i in message.get_payload()])
    part = None
    for i in message.get_payload():
      if i.get_filename() == filename:
        part = i
    self.assertEqual(part.get_payload(decode=True), str(document_gif.getData()))

  def test_cloneEvent(self):
    """
      All events uses after script and interaciton
      workflow add a test for clone
    """
    # XXX in the case of title, getTitle ignores the title attribute,
    # if any data is stored. In the case of text_content, getTextContent
    # respects the behaviour is the same as Title.
    portal_type = 'Mail Message'
    dummy_title = 'Dummy title'
    real_title = 'Real Title'
    dummy_content = 'Dummy content'
    real_content = 'Real content'
    event = self.portal.event_module.newContent(portal_type=portal_type,
                                                title=dummy_title,
                                                text_content=dummy_content,)
    self.assertFalse(event.hasFile(), '%r has a file' % (event,))
    self.assertEqual(event.getTitle(), dummy_title)
    self.assertEqual(event.getTextContent(), dummy_content)

    event.setData(('Subject: %s\r\n\r\n%s' % (real_title, real_content)).encode())
    self.assertTrue(event.hasFile(), '%r has no file' % (event,))
    self.assertEqual(event.getTitle(), real_title)
    self.assertEqual(event.getTextContent(), real_content)

    self.tic()
    new_event = event.Base_createCloneDocument(batch_mode=1)
    self.assertFalse(new_event.hasFile(), '%r has a file' % (new_event,))
    self.assertEqual(new_event.getData(), '')
    self.assertEqual(new_event.getTitle(), real_title)
    self.assertEqual(new_event.getTextContent(), real_content)
    self.assertNotEqual(new_event.getReference(), event.getReference())

  def test_cloneTicketAndEventList(self):
    """
      All events uses after script and interaciton
      workflow add a test for clone
    """
    portal = self.portal
    event_list = []
    destination_list = []
    for i in range (0,100):
      person = portal.person_module.newContent(
                 portal_type='Person',
                 title = 'Person %s' %i)
      destination_list.append(person)
    campaing = portal.campaign_module.newContent(
                 portal_type='Campaign',
                 reference = 'Test')
    for i in range(0,3):
      event = portal.event_module.newContent(
                portal_type='Mail Message',
                title = 'Mail %s' %i,
                follow_up = campaing.getRelativeUrl())
      event.setDestinationList([x.getRelativeUrl() for x in destination_list])
      event_list.append(event)
    self.tic()

    # use Ticket_cloneTicketAndEventList
    campaing.Ticket_cloneTicketAndEventList()
    self.tic()
    cloned_campaign = [x for x in portal.campaign_module.objectValues() if x!=campaing][0]
    cloned_event_list = [x for x in portal.event_module.objectValues() if x.getFollowUpValue()==cloned_campaign]
    self.assertEqual(campaing.getTitle(), cloned_campaign.getTitle())
    self.assertEqual(campaing.getReference(), cloned_campaign.getReference())

    for i in range(0,3):
      self.assertSameSet(event_list[i].getDestinationValueList(), cloned_event_list[i].getDestinationValueList())


  def test_Base_addEvent(self):
    """Check Base_addEvent script with a logged in user.
    """
    # create categories.
    resource = self.portal.portal_categories.resource
    for i in range(3):
      resource.newContent(portal_type='Category',
                          title='Title%s' % i,
                          id=i)
    self.portal.portal_categories.function.newContent(portal_type='Category',
                                                      id='crm_agent')
    # create user and configure security settings
    portal_type_list = self.portal.getPortalEventTypeList()\
                       + self.portal.getPortalEntityTypeList()\
                       + ('Event Module',)
    for portal_type in portal_type_list:
      portal_type_object = getattr(self.portal.portal_types, portal_type)
      portal_type_object.newContent(id='manager_role',
                                    portal_type='Role Information',
                                    role_name_list=('Manager',),
                                    role_category_list=('function/crm_agent', ))
      portal_type_object.updateRoleMapping()
    user = self.createSimpleUser('Agent', 'crm_agent', 'crm_agent')
    self.tic()
    try:
      # create entites
      organisation_portal_type = 'Organisation'
      person_portal_type = 'Person'
      my_company = self.portal.getDefaultModule(organisation_portal_type)\
                              .newContent(portal_type=organisation_portal_type,
                                          title='Software provider')
      organisation = self.portal.getDefaultModule(organisation_portal_type)\
                              .newContent(portal_type=organisation_portal_type,
                                          title='Soap Service Express')
      person = self.portal.getDefaultModule(person_portal_type).newContent(
                              portal_type=person_portal_type,
                              first_name='John',
                              last_name='Doe',
                              default_email_text='john.doe@example.com',
                              default_career_subordination_value=organisation)
      another_person = self.portal.getDefaultModule(person_portal_type)\
                  .newContent(portal_type=person_portal_type,
                              first_name='Jane',
                              last_name='Doe',
                              default_email_text='jane.doe@example.com',
                              default_career_subordination_value=organisation)
      user.setDefaultCareerSubordinationValue(my_company)
      # log in user
      self.loginByUserName('crm_agent')

      ### Incoming on Person ###
      # Submit the dialog on person
      title = 'Incoming email'
      direction = 'incoming'
      portal_type = 'Note'
      resource = resource['1'].getCategoryRelativeUrl()
      person.Base_addEvent(title, direction, portal_type, resource)

      # Index Event
      self.tic()

      # check created Event
      event = person.getSourceRelatedValue()
      self.assertEqual(event.getTitle(), title)
      self.assertEqual(event.getResource(), resource)
      self.assertTrue(event.hasStartDate())
      self.assertEqual(event.getSource(), person.getRelativeUrl())
      self.assertEqual(event.getSourceSection(),
                        organisation.getRelativeUrl())
      self.assertEqual(event.getDestination(), user.getRelativeUrl())
      self.assertEqual(event.getDestinationSection(), user.getSubordination())

      ### Outgoing on Person ###
      # Check another direction
      title = 'Outgoing email'
      direction = 'outgoing'
      another_person.Base_addEvent(title, direction, portal_type, resource)

      # Index Event
      self.tic()

      # check created Event
      event = another_person.getDestinationRelatedValue()
      self.assertEqual(event.getTitle(), title)
      self.assertEqual(event.getResource(), resource)
      self.assertTrue(event.hasStartDate())
      self.assertEqual(event.getDestination(),
                        another_person.getRelativeUrl())
      self.assertEqual(event.getDestinationSection(),
                        organisation.getRelativeUrl())
      self.assertEqual(event.getSource(), user.getRelativeUrl())
      self.assertEqual(event.getSourceSection(), user.getSubordination())

      ### Outgoing on Organisation ###
      # check on Organisation
      event = organisation.Base_addEvent(title, direction,
                                         portal_type, resource)

      # Index Event
      self.tic()

      # check created Event
      _, event = sorted(organisation.getDestinationSectionRelatedValueList(),
          key=lambda x: x.getCreationDate())
      self.assertEqual(event.getTitle(), title)
      self.assertEqual(event.getResource(), resource)
      self.assertTrue(event.hasStartDate())
      self.assertEqual(event.getDestination(),
                        organisation.getRelativeUrl())
      self.assertEqual(event.getDestinationSection(),
                        organisation.getRelativeUrl())
      self.assertEqual(event.getSource(), user.getRelativeUrl())
      self.assertEqual(event.getSourceSection(), user.getSubordination())

      ### Outgoing on Career ###
      # Now check Base_addEvent on any document (follow_up)
      career = person.default_career
      career.Base_addEvent(title, direction, portal_type, resource)

      # Index Event
      self.tic()

      # check created Event
      event = career.getFollowUpRelatedValue()
      self.assertEqual(event.getTitle(), title)
      self.assertEqual(event.getResource(), resource)
      self.assertTrue(event.hasStartDate())
      self.assertEqual(event.getSource(), user.getRelativeUrl())
      self.assertEqual(event.getSourceSection(), user.getSubordination())
    finally:
      # clean up created roles on portal_types
      self.login() # admin
      for portal_type in portal_type_list:
        portal_type_object = getattr(self.portal.portal_types, portal_type)
        portal_type_object._delObject('manager_role')
        portal_type_object.updateRoleMapping()
      self.tic()

  def test_MailMessage_Event_send_generate_activity_list(self):
    """
      Check that after post a Mail Message, the activities are generated
      correctly
    """
    person = self.portal.person_module.newContent(portal_type="Person")
    person.edit(default_email_text="test@test.com", title="test%s" % person.getId())
    self.tic()
    mail_message = self.portal.event_module.newContent(portal_type="Mail Message")
    relative_url_list = [z.getRelativeUrl() for z in self.portal.person_module.searchFolder()]
    self.assertEqual(5, len(relative_url_list))
    mail_message.setDestinationList(relative_url_list)
    mail_message.setSource(relative_url_list[0])
    mail_text_content = "Body Text Content"
    mail_message.setTextContent(mail_text_content)
    # directly call MailMessage_send to pass a packet size of 1, so that we
    # have one activity per recipient
    mail_message.MailMessage_send(packet_size=1)
    self.commit()
    portal_activities = self.portal.portal_activities
    portal_activities.manageInvoke(object_path=mail_message.getPath(),
      method_id='immediateReindexObject')
    portal_activities.manageInvoke(object_path=mail_message.getPath(),
      method_id='MailMessage_sendByActivity')
    self.commit()
    message_list = [i for i in portal_activities.getMessageList() \
                    if "event_relative_url" in i.kw]
    try:
      # 5 recipients -> 5 activities
      self.assertEqual(5, len(message_list))
    finally:
      self.tic()

    self.assertEqual(5, len(self.portal.MailHost._message_list))
    for message_info in self.portal.MailHost._message_list:
      self.assertIn(mail_text_content, message_info[-1])
      message = message_from_string(message_info[-1])
      self.assertTrue(DateTime(message.get("Date")).isCurrentDay())

  def test_MailMessage_send_simple_case(self):
    """
      Check that the method send send one email passing all parameters directly
      from_url, to_url, reply_url, subject, body, attachment_format, attachment_list
    """
    mail_message = self.portal.event_module.newContent(portal_type="Mail Message")
    self.tic()
    mail_message.send(from_url='FG ER <eee@eee.com>',
                      to_url='Expert User <expert@in24.test>',
                      subject="Simple Case",
                      body="Body Simple Case",
                      attachment_list=[])
    self.tic()
    (from_url, to_url, last_message,), = self.portal.MailHost._message_list
    self.assertIn("Body Simple Case", last_message)
    self.assertEqual('FG ER <eee@eee.com>', from_url)
    self.assertEqual(['Expert User <expert@in24.test>'], to_url)

  def test_MailMessage_send_extra_headers(self):
    """Test sending message with extra headers
    """
    mail_message = self.portal.event_module.newContent(
        portal_type="Mail Message",
        source='person_module/me',
        destination='person_module/recipient')

    mail_message.send(extra_header_dict={"X-test-header": "test"})
    self.tic()
    (_, _, last_message,), = self.portal.MailHost._message_list
    message = message_from_string(last_message)
    self.assertEqual("test", message.get("X-test-header"))


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestCRM))
  suite.addTest(unittest.makeSuite(TestCRMMailIngestion))
  suite.addTest(unittest.makeSuite(TestCRMMailSend))
  return suite
