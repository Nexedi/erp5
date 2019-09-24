# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#          Nicolas Delaby <nicolas@nexedi.com>
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
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import createZODBPythonScript
from Testing import ZopeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from Products.ERP5OOo.tests.utils import Validator
from lxml import html
import email, urlparse, httplib


class TestDeferredStyle(ERP5TypeTestCase, ZopeTestCase.Functional):
  """Tests deferred styles for ERP5."""
  skin = content_type = None
  recipient_email_address = 'invalid@example.com'
  attachment_file_extension = ''
  username = 'bob'
  password = 'bobpwd'
  # the weird '<' char is to force quoting of the first name on the e-mail
  # address. Zope 2.12 only surrounds names with quotes if they really need
  # quoting.
  first_name = 'Bob<Par'
  publication_section = "reporting"
  classification = "collaborative"

  def getTitle(self):
    return 'Test Deferred Style'

  def getBusinessTemplateList(self):
    return ('erp5_core_proxy_field_legacy',
            'erp5_base',
            'erp5_ods_style',
            'erp5_odt_style',
            'erp5_ingestion_mysql_innodb_catalog',
            'erp5_ingestion',
            'erp5_web',
            'erp5_dms',
            'erp5_deferred_style',
            'erp5_l10n_fr',)

  def afterSetUp(self):
    self.login()
    if not self.skin:
      raise NotImplementedError('Subclasses must define skin')

    self.portal.MailHost.reset()
    person_module = self.portal.person_module
    if person_module._getOb('pers', None) is None:
      person = person_module.newContent(id='pers', portal_type='Person',
                                        reference=self.username,
                                        first_name=self.first_name,
                                        default_email_text=self.recipient_email_address)
      assignment = person.newContent(portal_type='Assignment')
      assignment.open()
      login = person.newContent(
        portal_type='ERP5 Login',
        reference=self.username,
        password=self.password,
      )
      login.validate()
    system_preference = self.portal.portal_preferences._getOb('syspref', None)
    if system_preference is None:
      system_preference = self.portal.portal_preferences.newContent(
              id="syspref",
              portal_type="System Preference")
      system_preference.enable()
    # Fallback to former behaviour
    system_preference.edit(preferred_deferred_report_stored_as_document=False)
    # add categories
    if not getattr(self.portal.portal_categories.classification, 'collaborative', None):
      self.portal.portal_categories.classification.newContent(id="collaborative")
    if not getattr(self.portal.portal_categories.publication_section, 'reporting', None):
      self.portal.portal_categories.publication_section.newContent(id="reporting")
    self.tic()

  def beforeTearDown(self):
    document_ids = list(self.portal.document_module.objectIds())
    if len(document_ids):
      self.portal.document_module.manage_delObjects(ids=document_ids)
    self.tic()

  def loginAsUser(self, username):
    uf = self.portal.acl_users
    user = uf.getUser(username).__of__(uf)
    uf.zodb_roles.assignRoleToPrincipal('Manager', user.getId())
    newSecurityManager(None, user)

  def test_skin_selection(self):
    self.assertTrue('Deferred' in self.portal.portal_skins.getSkinSelections())

  def test_report_view(self):
    self.loginAsUser('bob')
    self.portal.changeSkin('Deferred')
    response = self.publish(
        '/%s/person_module/pers/Base_viewHistory?deferred_portal_skin=%s'
        % (self.portal.getId(), self.skin), '%s:%s' % (self.username, self.password))
    self.tic()
    last_message = self.portal.MailHost._last_message
    self.assertNotEquals((), last_message)
    mfrom, mto, message_text = last_message
    self.assertEqual('"%s" <%s>' % (self.first_name, self.recipient_email_address), mto[0])
    mail_message = email.message_from_string(message_text)
    for part in mail_message.walk():
      content_type = part.get_content_type()
      file_name = part.get_filename()
      if content_type == self.content_type:
        # "History" is the title of Base_viewHistory form
        file_name = part.get_filename()
        expected_file_name = 'History%s' % self.attachment_file_extension
        self.assertEqual(expected_file_name, file_name)
        self.assertEqual('attachment; filename="%s"' % expected_file_name,
                          part.get('Content-Disposition'))
        data = part.get_payload(decode=True)
        error_list = Validator().validate(data)
        if error_list:
          self.fail(''.join(error_list))
        break
    else:
      self.fail('Attachment not found in email\n%s' % message_text)


  def _checkEmailLink(self, part, extension=None, content_type=None):
    content = part.get_payload(decode=True)
    self.assertTrue("History%s" % extension or self.attachment_file_extension in content)
    tree = html.fromstring(content)
    link, = [href for href in tree.xpath('//a/@href') if href]
    relative_url =urlparse.urlparse(link)
    report = self.publish(relative_url.path+"?"+relative_url.query, '%s:%s' % (self.username, self.password))
    self.assertEqual(httplib.OK, report.getStatus())
    self.assertEqual(report.getHeader('content-type'), content_type or self.content_type)

  def _checkDocument(self):
    document_list = self.portal.document_module.objectValues()
    self.assertEquals(len(document_list), 1)
    document = document_list[0].getObject()
    expected_file_name = 'History%s' % self.attachment_file_extension
    self.assertEqual(expected_file_name, document.getFilename())
    self.assertEqual('History', document.getTitle())
    self.assertEqual(None, document.getReference())
    self.assertEqual("shared", document.getValidationState())
    self.assertEqual(self.publication_section, document.getPublicationSection())
    self.assertEqual(self.classification, document.getClassification())
    self.assertEqual(self.portal_type, document.getPortalType())

  def _defineSystemPreference(self, notification_message_reference=None):
    system_preference = self.portal.portal_preferences._getOb('syspref', None)
    system_preference.edit(
      preferred_deferred_report_stored_as_document=True,
      preferred_deferred_report_classification=self.classification,
      preferred_deferred_report_publication_section=self.publication_section,
      preferred_deferred_report_notification_message_reference=notification_message_reference)

  def test_report_stored_as_document(self):
    self._defineSystemPreference()
    self.loginAsUser('bob')
    self.portal.changeSkin('Deferred')
    response = self.publish(
        '/%s/person_module/pers/Base_viewHistory?deferred_portal_skin=%s'
        % (self.portal.getId(), self.skin), '%s:%s' % (self.username, self.password))
    self.tic()
    self._checkDocument()

    last_message = self.portal.MailHost._last_message
    self.assertNotEquals((), last_message)
    mfrom, mto, message_text = last_message
    self.assertEqual('"%s" <%s>' % (self.first_name, self.recipient_email_address), mto[0])
    mail_message = email.message_from_string(message_text)
    for part in mail_message.walk():
      content_type = part.get_content_type()
      if content_type == "text/html":
        self._checkEmailLink(part)
        break
    else:
      self.fail('Link not found in email\n%s' % message_text)

  def test_report_stored_as_document_with_notification_message(self):
    createZODBPythonScript(self.portal,
                           'NotificationMessage_getSubstitutionMappingDictFromArgument',
                           'mapping_dict',
                           '''return mapping_dict''')
    notification_message = self.portal.notification_message_module.newContent(
      reference="notification-deferred.report",
      content_type="text/html",
      text_content='Hi,\n\nHere is the link(s) to your report(s) : ${report_link_list}.\n\n',
      text_content_substitution_mapping_method_id='NotificationMessage_getSubstitutionMappingDictFromArgument',
    )
    notification_message.newContent(portal_type="Role Definition",
                                    role_name="Auditor",
                                    agent="person_module/pers")
    notification_message.validate()
    self.tic()
    self._defineSystemPreference("notification-deferred.report")
    self.loginAsUser('bob')
    self.portal.changeSkin('Deferred')
    response = self.publish(
        '/%s/person_module/pers/Base_viewHistory?deferred_portal_skin=%s'
        % (self.portal.getId(), self.skin), '%s:%s' % (self.username, self.password))
    self.tic()
    self._checkDocument()

    last_message = self.portal.MailHost._last_message
    self.assertNotEquals((), last_message)
    mfrom, mto, message_text = last_message
    self.assertEqual('"%s" <%s>' % (self.first_name, self.recipient_email_address), mto[0])
    mail_message = email.message_from_string(message_text)
    for part in mail_message.walk():
      content_type = part.get_content_type()
      if content_type == "text/html":
        self._checkEmailLink(part)
        break
    else:
      self.fail('Link not found in email\n%s' % message_text)

  def test_pdf_report_stored_as_document(self):
    self._defineSystemPreference()
    self.loginAsUser('bob')
    self.portal.changeSkin('Deferred')
    response = self.publish(
        '/%s/person_module/pers/Base_viewHistory?deferred_portal_skin=%s&format=pdf'
        % (self.portal.getId(), self.skin), '%s:%s' % (self.username, self.password))
    self.tic()
    # A document has been created
    self._checkDocument()

    last_message = self.portal.MailHost._last_message
    self.assertNotEquals((), last_message)
    mfrom, mto, message_text = last_message
    self.assertEqual('"%s" <%s>' % (self.first_name, self.recipient_email_address), mto[0])
    mail_message = email.message_from_string(message_text)
    for part in mail_message.walk():
      content_type = part.get_content_type()
      if content_type == "text/html":
        self._checkEmailLink(part, ".pdf", "application/pdf")
        break
    else:
      self.fail('Link not found in email\n%s' % message_text)

  def test_normal_form(self):
    self.loginAsUser('bob')
    # simulate a big request, for which Base_callDialogMethod will not issue a
    # redirect
    response = self.publish(
        '/%s/person_module/pers/Base_callDialogMethod?deferred_portal_skin=%s&'
        'dialog_method=Person_view&dialog_id=Person_view&'
        'deferred_style:int=1&junk=%s'  % (self.portal.getId(),
                                           self.skin,
                                           'X' * 2000),
        '%s:%s' % (self.username, self.password))
    self.tic()
    last_message = self.portal.MailHost._last_message
    self.assertNotEquals((), last_message)
    mfrom, mto, message_text = last_message
    self.assertEqual('"%s" <%s>' % (self.first_name, self.recipient_email_address), mto[0])
    mail_message = email.message_from_string(message_text)
    for part in mail_message.walk():
      content_type = part.get_content_type()
      if content_type == self.content_type:
        # "Person" is the title of Person_view form
        file_name = part.get_filename()
        expected_file_name = 'Person%s' % self.attachment_file_extension
        self.assertEqual(expected_file_name, file_name)
        self.assertEqual('attachment; filename="%s"' % expected_file_name,
                          part.get('Content-Disposition'))
        data = part.get_payload(decode=True)
        error_list = Validator().validate(data)
        if error_list:
          self.fail(''.join(error_list))
        break
    else:
      self.fail('Attachment not found in email\n%s' % message_text)

  def test_lang_negociation(self):
    # User's Accept-Language header is honored in reports.
    self.loginAsUser('bob')
    self.portal.changeSkin('Deferred')
    response = self.publish(
        '/%s/person_module/pers/Base_viewHistory?deferred_portal_skin=%s'
        % (self.portal.getId(), self.skin),
        '%s:%s' % (self.username, self.password),
        extra={
          'HTTP_ACCEPT_LANGUAGE': 'fr;q=0.9,en;q=0.8',
          })
    self.tic()
    mail_message = email.message_from_string(self.portal.MailHost._last_message[2])
    # mail subject is translated
    self.assertEqual('Historique', mail_message['subject'])
    # content is translated
    part, = [x for x in mail_message.walk() if x.get_content_type() == self.content_type]
    self.assertIn(
        'Historique',
        self.portal.portal_transforms.convertTo(
          'text/plain',
          part.get_payload(decode=True),
          context=self.portal,
          mimetype=self.content_type).getData())

  def test_lang_negociation_cookie(self):
    # User's LOCALIZER_LANGUAGE cookie is honored in reports and have priority over Accept-Language
    self.loginAsUser('bob')
    self.portal.changeSkin('Deferred')
    response = self.publish(
        '/%s/person_module/pers/Base_viewHistory?deferred_portal_skin=%s'
        % (self.portal.getId(), self.skin),
        '%s:%s' % (self.username, self.password),
        # user has configured preferred language to english
        extra={
          'HTTP_ACCEPT_LANGUAGE': 'en;q=0.9,fr;q=0.8',
          },
        # but has forced to french in a Localizer cookie
        env={
          'HTTP_COOKIE': 'LOCALIZER_LANGUAGE="fr"',
          })
    self.tic()
    mail_message = email.message_from_string(self.portal.MailHost._last_message[2])
    # mail subject is translated
    self.assertEqual('Historique', mail_message['subject'])
    # content is translated
    mail_message = email.message_from_string(self.portal.MailHost._last_message[2])
    part, = [x for x in mail_message.walk() if x.get_content_type() == self.content_type]
    self.assertIn(
        'Historique',
        self.portal.portal_transforms.convertTo(
          'text/plain',
          part.get_payload(decode=True),
          context=self.portal,
          mimetype=self.content_type).getData())
    self.tic()



class TestODSDeferredStyle(TestDeferredStyle):
  skin = 'ODS'
  content_type = 'application/vnd.oasis.opendocument.spreadsheet'
  attachment_file_extension = '.ods'
  portal_type="Spreadsheet"

  def test_report_view_sheet_per_report_section(self):
    """Test the sheet_per_report_section feature of erp5_ods_style.
    """
    self.loginAsUser('bob')
    self.portal.changeSkin('Deferred')
    response = self.publish(
        '/%s/person_module/pers/Base_viewHistory?deferred_portal_skin=%s&sheet_per_report_section:int=1'
        % (self.portal.getId(), self.skin), '%s:%s' % (self.username, self.password))
    self.tic()
    last_message = self.portal.MailHost._last_message
    self.assertNotEquals((), last_message)
    mfrom, mto, message_text = last_message
    self.assertEqual('"%s" <%s>' % (self.first_name, self.recipient_email_address), mto[0])
    mail_message = email.message_from_string(message_text)
    for part in mail_message.walk():
      content_type = part.get_content_type()
      file_name = part.get_filename()
      if content_type == self.content_type:
        # "History" is the title of Base_viewHistory form
        file_name = part.get_filename()
        expected_file_name = 'History%s' % self.attachment_file_extension
        self.assertEqual(expected_file_name, file_name)
        self.assertEqual('attachment; filename="%s"' % expected_file_name,
                          part.get('Content-Disposition'))
        data = part.get_payload(decode=True)
        error_list = Validator().validate(data)
        if error_list:
          self.fail(''.join(error_list))
        break
    else:
      self.fail('Attachment not found in email\n%s' % message_text)


class TestODTDeferredStyle(TestDeferredStyle):
  skin = 'ODT'
  content_type = 'application/vnd.oasis.opendocument.text'
  attachment_file_extension = '.odt'
  portal_type = "Text"

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestODSDeferredStyle))
  suite.addTest(unittest.makeSuite(TestODTDeferredStyle))
  return suite
