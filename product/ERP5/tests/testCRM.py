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

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

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

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestCRMMailIngestion))
  return suite
