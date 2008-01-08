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
import os
import email

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5OOo.tests.testIngestion import conversion_server_host
from Products.ERP5OOo.tests.testIngestion import FILE_NAME_REGULAR_EXPRESSION
from Products.ERP5OOo.tests.testIngestion import REFERENCE_REGULAR_EXPRESSION


class TestCRMMailIngestion(ERP5TypeTestCase):
  """Test Mail Ingestion for CRM.
  """

  def getBusinessTemplateList(self):
    return ('erp5_base', 'erp5_web', 'erp5_dms',
            'erp5_dms_mysql_innodb_catalog', 'erp5_crm')

  def afterSetUp(self):
    portal = self.portal
    if 'portal_transforms' not in portal.objectIds():
      # XXX this should be done in bt5 (or ERP5Site, as install order is
      # important)
      # install needed tools
      dispatcher = portal.manage_addProduct 
      dispatcher['MimetypesRegistry'].manage_addTool('MimeTypes Registry')
      dispatcher['PortalTransforms'].manage_addTool('Portal Transforms')
      
      # XXX this should not be necessary either 
      # set prefered file name regular expression
      pref = portal.portal_preferences.default_site_preference
      pref.setPreferredDocumentFileNameRegularExpression('.*')
      pref.setPreferredDocumentReferenceRegularExpression('.*')
      pref.enable()

      # XXX do this in ERP5Site.py ?
      # sets up content type registry
      ctr = self.portal.content_type_registry
      ctr.addPredicate('mail_message', 'extension')
      ctr.getPredicate('mail_message').edit(extensions='eml')
      ctr.assignTypeName('mail_message', 'Mail Message')
      ctr.reorderPredicate('mail_message', 0)

    # create customer organisation and person
    if 'customer' not in portal.organisation_module.objectIds():
      customer_organisation = portal.organisation_module.newContent(
              id='customer',
              portal_type='Organisation',
              title='Customer')
      portal.person_module.newContent(
              id='sender',
              title='Sender',
              subordination_value=customer_organisation,
              default_email_text='sender@customer.com')
      # also create the recipient
      portal.person_module.newContent(
              id='me',
              title='Me',
              default_email_text='me@erp5.org')

      # make sure customers are available to catalog
      get_transaction().commit()
      self.tic()

  def beforeTearDown(self):
    get_transaction().abort()
    # clear modules if necessary
    for module in (self.portal.event_module,):
      module.manage_delObjects(list(module.objectIds()))
    get_transaction().commit()
    self.tic()

  def _ingestMail(self, filename):
    """ingest an email from the mail in data dir named `filename`"""
    data = file(os.path.join(os.path.dirname(__file__),
                  'test_data', 'crm_emails', filename)).read()
    return self.portal.portal_contributions.newContent(
                    portal_type='Mail Message',
                    container_path='event_module',
                    file_name='postfix_mail.eml',
                    data=data)

  def test_findTypeByName_MailMessage(self):
    # without this, ingestion will not work
    registry = self.portal.content_type_registry
    self.assertEquals('Mail Message',
        registry.findTypeName('postfix_mail.eml', 'message/rfc822', ''))

  def test_document_creation(self):
    # CRM email ingestion creates a Mail Message in event_module
    event = self._ingestMail('simple')
    self.assertEquals(len(self.portal.event_module), 1)
    self.assertEquals(event, self.portal.event_module.contentValues()[0])
    self.assertEquals('Mail Message', event.getPortalType())
    self.assertEquals('message/rfc822', event.getContentType())
  
  def test_title(self):
    # tite is found automatically, based on the Subject: header in the mail
    event = self._ingestMail('simple')
    self.assertEquals('Simple Mail Test', event.getTitle())

  def test_asText(self):
    # asText requires portal_transforms
    event = self._ingestMail('simple')
    self.assertEquals('Hello,\nContent of the mail.\n', str(event.asText()))
 
  def test_sender(self):
    # source is found automatically, based on the From: header in the mail
    event = self._ingestMail('simple')
    # metadata discovery is done in an activity
    get_transaction().commit()
    self.tic()
    self.assertEquals('person_module/sender', event.getSource())

  def test_recipient(self):
    # destination is found automatically, based on the To: header in the mail
    event = self._ingestMail('simple')
    get_transaction().commit()
    self.tic()
    self.assertEquals('person_module/me', event.getDestination())

  def test_follow_up(self):
    # follow up is found automatically, based on the content of the mail, and
    # what you defined in preference regexpr.
    # But, we don't want it to associate with the first campaign simply
    # because we searched against nothing
    self.portal.campaign_module.newContent(portal_type='Campaign')
    get_transaction().commit()
    self.tic()
    event = self._ingestMail('simple')
    get_transaction().commit()
    self.tic()
    self.assertEquals(None, event.getFollowUp())
 
 
## TODO:
##  def test_forwarder_mail(self):
##    # if there is a forwarded email, import the forwarded email
##    event = self._ingestMail('forwarded')
##
##  def test_attachements(self):
##    event = self._ingestMail('with_attachements')
##
##  def test_encoding(self):
##    event = self._ingestMail('utf8')
##

TEST_HOME = os.path.dirname(__file__)

def openTestFile(filename):
  return file(os.path.join(TEST_HOME, 'test_data', 'crm_emails', filename))

class TestCRMMailSend(ERP5TypeTestCase):
  """Test Mail Sending for CRM
  """

  def getBusinessTemplateList(self):
    return ('erp5_base', 'erp5_web', 'erp5_dms',
            'erp5_dms_mysql_innodb_catalog', 'erp5_crm')

  def afterSetUp(self):
    portal = self.portal
    if 'portal_transforms' not in portal.objectIds():
      # XXX this should be done in bt5 (or ERP5Site, as install order is
      # important)
      # install needed tools
      dispatcher = portal.manage_addProduct 
      dispatcher['MimetypesRegistry'].manage_addTool('MimeTypes Registry')
      dispatcher['PortalTransforms'].manage_addTool('Portal Transforms')

    # create customer organisation and person
    if 'customer' not in portal.organisation_module.objectIds():
      customer_organisation = portal.organisation_module.newContent(
              id='customer',
              portal_type='Organisation',
              title='Customer')
      portal.person_module.newContent(
              id='sender',
              title='Sender',
              subordination_value=customer_organisation,
              default_email_text='sender@customer.com')
      # also create the recipient
      portal.person_module.newContent(
              id='me',
              title='Me',
              default_email_text='me@erp5.org')

    # set preference
    default_pref = self.portal.portal_preferences.default_site_preference
    default_pref.setPreferredOoodocServerAddress(conversion_server_host[0])
    default_pref.setPreferredOoodocServerPortNumber(conversion_server_host[1])
    default_pref.setPreferredDocumentFileNameRegularExpression(FILE_NAME_REGULAR_EXPRESSION)
    default_pref.setPreferredDocumentReferenceRegularExpression(REFERENCE_REGULAR_EXPRESSION)
    default_pref.enable()

    # make sure customers are available to catalog
    get_transaction().commit()
    self.tic()

  def beforeTearDown(self):
    get_transaction().abort()
    # clear modules if necessary
    for module in (self.portal.event_module,):
      module.manage_delObjects(list(module.objectIds()))
    get_transaction().commit()
    self.tic()

  def test_MailAttachmentPdf(self):
    """
    Make sure that pdf document is correctly attached in email
    """
    # Add a document which will be attached.

    def add_document(filename, id, container, portal_type):
      f = openTestFile(filename)
      document = container.newContent(id=id, portal_type=portal_type)
      document.edit(file=f, reference=filename)
      return document

    # pdf
    document_pdf = add_document('sample_attachment.pdf', '1',
                                self.portal.document_module, 'PDF')

    get_transaction().commit()
    self.tic()
    get_transaction().commit()

    # Add a ticket
    ticket = self.portal.campaign_module.newContent(id='1',
                                                    portal_type='Campaign',
                                                    title='Advertisement')
    # Create a event
    ticket.Ticket_newEvent(portal_type='Mail Message',
                           title='Our new product',
                           description='Buy this now!',
                           direction='outgoing')

    # Set sender and attach a document to the event.
    event = self.portal.event_module.objectValues()[0]
    event.edit(source='person_module/me',
               destination='person_module/sender',
               aggregate=document_pdf.getRelativeUrl(),
               text_content='This is an advertisement mail.')

    mail_text = event.send(download=True)

    # Check mail text.
    message = email.message_from_string(mail_text)
    part = None
    for i in message.get_payload():
      if i.get_content_type()=='text/plain':
        part = i
    self.assertEqual(part.get_payload(decode=True), event.getTextContent())

    # Check attachment
    # pdf
    self.assert_('sample_attachment.pdf' in 
                 [i.get_filename() for i in message.get_payload()])
    part = None
    for i in message.get_payload():
      if i.get_filename()=='sample_attachment.pdf':
        part = i
    self.assertEqual(part.get_payload(decode=True), str(document_pdf.getData()))

  def test_MailAttachmentText(self):
    """
    Make sure that text document is correctly attached in email
    """
    # Add a document which will be attached.

    def add_document(filename, id, container, portal_type):
      f = openTestFile(filename)
      document = container.newContent(id=id, portal_type=portal_type)
      document.edit(file=f, reference=filename)
      return document

    # odt
    document_odt = add_document('sample_attachment.odt', '2',
                                self.portal.document_module, 'Text')
    
    get_transaction().commit()
    self.tic()
    get_transaction().commit()

    # Add a ticket
    ticket = self.portal.campaign_module.newContent(id='1',
                                                    portal_type='Campaign',
                                                    title='Advertisement')
    # Create a event
    ticket.Ticket_newEvent(portal_type='Mail Message',
                           title='Our new product',
                           description='Buy this now!',
                           direction='outgoing')

    # Set sender and attach a document to the event.
    event = self.portal.event_module.objectValues()[0]
    event.edit(source='person_module/me',
               destination='person_module/sender',
               aggregate=document_odt.getRelativeUrl(),
               text_content='This is an advertisement mail.')

    mail_text = event.send(download=True)

    # Check mail text.
    message = email.message_from_string(mail_text)
    part = None
    for i in message.get_payload():
      if i.get_content_type()=='text/plain':
        part = i
    self.assertEqual(part.get_payload(decode=True), event.getTextContent())

    # Check attachment
    # odt
    self.assert_('sample_attachment.odt' in 
                 [i.get_filename() for i in message.get_payload()])
    part = None
    for i in message.get_payload():
      if i.get_filename()=='sample_attachment.odt':
        part = i
    self.assert_(len(part.get_payload(decode=True))>0)

  def test_MailAttachmentFile(self):
    """
    Make sure that file document is correctly attached in email
    """
    # Add a document which will be attached.

    def add_document(filename, id, container, portal_type):
      f = openTestFile(filename)
      document = container.newContent(id=id, portal_type=portal_type)
      document.edit(file=f, reference=filename)
      return document

    # zip
    document_zip = add_document('sample_attachment.zip', '3',
                                self.portal.document_module, 'File')

    get_transaction().commit()
    self.tic()
    get_transaction().commit()

    # Add a ticket
    ticket = self.portal.campaign_module.newContent(id='1',
                                                    portal_type='Campaign',
                                                    title='Advertisement')
    # Create a event
    ticket.Ticket_newEvent(portal_type='Mail Message',
                           title='Our new product',
                           description='Buy this now!',
                           direction='outgoing')

    # Set sender and attach a document to the event.
    event = self.portal.event_module.objectValues()[0]
    event.edit(source='person_module/me',
               destination='person_module/sender',
               aggregate=document_zip.getRelativeUrl(),
               text_content='This is an advertisement mail.')

    mail_text = event.send(download=True)

    # Check mail text.
    message = email.message_from_string(mail_text)
    part = None
    for i in message.get_payload():
      if i.get_content_type()=='text/plain':
        part = i
    self.assertEqual(part.get_payload(decode=True), event.getTextContent())

    # Check attachment
    # zip
    self.assert_('sample_attachment.zip' in 
                 [i.get_filename() for i in message.get_payload()])
    part = None
    for i in message.get_payload():
      if i.get_filename()=='sample_attachment.zip':
        part = i
    self.assert_(len(part.get_payload(decode=True))>0)

  def test_MailAttachmentImage(self):
    """
    Make sure that image document is correctly attached in email
    """
    # Add a document which will be attached.

    def add_document(filename, id, container, portal_type):
      f = openTestFile(filename)
      document = container.newContent(id=id, portal_type=portal_type)
      document.edit(file=f, reference=filename)
      return document

    # gif
    document_gif = add_document('sample_attachment.gif', '4',
                                self.portal.image_module, 'Image')

    get_transaction().commit()
    self.tic()
    get_transaction().commit()

    # Add a ticket
    ticket = self.portal.campaign_module.newContent(id='1',
                                                    portal_type='Campaign',
                                                    title='Advertisement')
    # Create a event
    ticket.Ticket_newEvent(portal_type='Mail Message',
                           title='Our new product',
                           description='Buy this now!',
                           direction='outgoing')

    # Set sender and attach a document to the event.
    event = self.portal.event_module.objectValues()[0]
    event.edit(source='person_module/me',
               destination='person_module/sender',
               aggregate=document_gif.getRelativeUrl(),
               text_content='This is an advertisement mail.')

    mail_text = event.send(download=True)

    # Check mail text.
    message = email.message_from_string(mail_text)
    part = None
    for i in message.get_payload():
      if i.get_content_type()=='text/plain':
        part = i
    self.assertEqual(part.get_payload(decode=True), event.getTextContent())

    # Check attachment
    # gif
    self.assert_('sample_attachment.gif' in 
                 [i.get_filename() for i in message.get_payload()])
    part = None
    for i in message.get_payload():
      if i.get_filename()=='sample_attachment.gif':
        part = i
    self.assertEqual(part.get_payload(decode=True), str(document_gif.getData()))

  def test_MailAttachmentWebPage(self):
    """
    Make sure that webpage document is correctly attached in email
    """
    # Add a document which will be attached.

    document_html = self.portal.web_page_module.newContent(id='5',
                                                           portal_type='Web Page')
    document_html.edit(text_content='<html><body>Hello world!</body></html>',
                       reference='sample_attachment.html')

    get_transaction().commit()
    self.tic()
    get_transaction().commit()

    # Add a ticket
    ticket = self.portal.campaign_module.newContent(id='1',
                                                    portal_type='Campaign',
                                                    title='Advertisement')
    # Create a event
    ticket.Ticket_newEvent(portal_type='Mail Message',
                           title='Our new product',
                           description='Buy this now!',
                           direction='outgoing')

    # Set sender and attach a document to the event.
    event = self.portal.event_module.objectValues()[0]
    event.edit(source='person_module/me',
               destination='person_module/sender',
               aggregate=document_html.getRelativeUrl(),
               text_content='This is an advertisement mail.')

    mail_text = event.send(download=True)

    # Check mail text.
    message = email.message_from_string(mail_text)
    part = None
    for i in message.get_payload():
      if i.get_content_type()=='text/plain':
        part = i
    self.assertEqual(part.get_payload(decode=True), event.getTextContent())

    # Check attachment
    # html
    self.assert_('sample_attachment.html' in 
                 [i.get_filename() for i in message.get_payload()])
    part = None
    for i in message.get_payload():
      if i.get_filename()=='sample_attachment.html':
        part = i
    self.assertEqual(part.get_payload(decode=True), str(document_html.getTextContent))

  def test_MailRespond(self):
    """
    Test we can answer an incoming event and quote it
    """
    # Add a ticket
    ticket = self.portal.campaign_module.newContent(id='1',
                                                    portal_type='Campaign',
                                                    title='Advertisement')
    # Create a event
    ticket.Ticket_newEvent(portal_type='Mail Message',
                           title='Our new product',
                           description='Buy this now!',
                           direction='incoming')

    # Set sender and attach a document to the event.
    event = self.portal.event_module.objectValues()[0]
    event.edit(source='person_module/me',
               destination='person_module/sender',
               text_content='This is an advertisement mail.')
    first_event_id = event.getId()
    self.getWorkflowTool().doActionFor(event, 'respond_action', 
                                       wf_id='event_workflow',
                                       respond_event_quotation = 1,
                                       respond_event_portal_type = "Mail Message",
                                       respond_event_title = "Answer",
                                       respond_event_description = "Answer Advertissement Mail",
                                       )

    self.assertEqual(event.getSimulationState(), "responded")
    # answer event must have been created
    self.assertEqual(len(self.portal.event_module), 2)
    for ev in self.portal.event_module.objectValues():
      if ev.getId() != first_event_id:
        answer_event = ev

    # check properties of answer event
    self.assertEqual(answer_event.getSimulationState(), "planned")
    self.assertEqual(answer_event.getCausality(), event.getRelativeUrl())
    self.assertEqual(answer_event.getDestination(), 'person_module/me')
    self.assertEqual(answer_event.getSource(), 'person_module/sender')
    self.assertEqual(answer_event.getTextContent(), '> This is an advertisement mail.')


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestCRMMailIngestion))
  suite.addTest(unittest.makeSuite(TestCRMMailSend))
  return suite
