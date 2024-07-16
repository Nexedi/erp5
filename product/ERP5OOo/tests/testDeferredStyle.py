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

import textwrap
import unittest
import textwrap
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import createZODBPythonScript
from Testing import ZopeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from Acquisition import aq_base
from Products.ERP5OOo.tests.utils import Validator
from lxml import html
import email, six.moves.urllib.parse, six.moves.http_client
from Products.Formulator.MethodField import Method


class DeferredStyleTestCase(ERP5TypeTestCase, ZopeTestCase.Functional):
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
    self.portal.MailHost.reset()
    person_module = self.portal.person_module
    if person_module._getOb('pers', None) is None:
      person = person_module.newContent(id='pers', portal_type='Person',
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
    document_id_list = list(self.portal.document_module.objectIds())
    if document_id_list:
      self.portal.document_module.manage_delObjects(ids=document_id_list)
    test_skin_id_list = [
        x for x in self.portal.portal_skins.custom.objectIds()
        if 'TestDeferredStyle' in x]
    if test_skin_id_list:
      self.portal.portal_skins.custom.manage_delObjects(ids=test_skin_id_list)
    self.tic()

  def loginAsUser(self, username):
    """Login as a user and assign Manager role to this user.
    """
    uf = self.portal.acl_users
    user = uf.getUser(username).__of__(uf)
    uf.zodb_roles.assignRoleToPrincipal('Manager', user.getId())
    newSecurityManager(None, user)


class TestDeferredStyleBase(DeferredStyleTestCase):
  """Tests deferred styles for ERP5."""

  def test_skin_selection(self):
    self.assertIn('Deferred', self.portal.portal_skins.getSkinSelections())

  def test_report_view(self):
    self.loginAsUser(self.username)
    self.portal.changeSkin('Deferred')
    response = self.publish(
        '/%s/person_module/pers/Base_viewHistory?deferred_portal_skin=%s'
        % (self.portal.getId(), self.skin), '%s:%s' % (self.username, self.password))
    self.tic()
    last_message = self.portal.MailHost._last_message
    self.assertNotEqual(last_message, ())
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
    relative_url =six.moves.urllib.parse.urlparse(link)
    report = self.publish(relative_url.path+"?"+relative_url.query, '%s:%s' % (self.username, self.password))
    self.assertEqual(six.moves.http_client.OK, report.getStatus())
    self.assertEqual(report.getHeader('content-type'), content_type or self.content_type)

  def _checkDocument(self):
    document_list = self.portal.document_module.objectValues()
    self.assertEqual(len(document_list), 1)
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
    self.loginAsUser(self.username)
    self.portal.changeSkin('Deferred')
    response = self.publish(
        '/%s/person_module/pers/Base_viewHistory?deferred_portal_skin=%s'
        % (self.portal.getId(), self.skin), '%s:%s' % (self.username, self.password))
    self.tic()
    self._checkDocument()

    last_message = self.portal.MailHost._last_message
    self.assertNotEqual(last_message, ())
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
    self.loginAsUser(self.username)
    self.portal.changeSkin('Deferred')
    response = self.publish(
        '/%s/person_module/pers/Base_viewHistory?deferred_portal_skin=%s'
        % (self.portal.getId(), self.skin), '%s:%s' % (self.username, self.password))
    self.tic()
    self._checkDocument()

    last_message = self.portal.MailHost._last_message
    self.assertNotEqual(last_message, ())
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
    self.loginAsUser(self.username)
    self.portal.changeSkin('Deferred')
    response = self.publish(
        '/%s/person_module/pers/Base_viewHistory?deferred_portal_skin=%s&format=pdf'
        % (self.portal.getId(), self.skin), '%s:%s' % (self.username, self.password))
    self.tic()
    # A document has been created
    self._checkDocument()

    last_message = self.portal.MailHost._last_message
    self.assertNotEqual(last_message, ())
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
    self.loginAsUser(self.username)
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
    self.assertNotEqual(last_message, ())
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
    self.loginAsUser(self.username)
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
    self.loginAsUser(self.username)
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

  def test_report_method_access_request(self):
    """Parameters propagated through the report dialog request form should
    be available in selection parameters.
    """
    report_form_name = 'ERP5Site_viewTestDeferredStyleRequestIndependenceReport'
    get_report_section_script_name = 'ERP5Site_getTestDeferredStyleRequestIndependenceReportSectionList'
    report_section_form_name = 'ERP5Site_viewTestDeferredStyleRequestIndependenceReportSection'
    get_line_list_script_name = 'ERP5Site_getTestDeferredStyleRequestIndependenceReportLineList'
    skin_folder = self.portal.portal_skins.custom

    # ERP5 Report
    skin_folder.manage_addProduct['ERP5Form'].addERP5Report(report_form_name, report_form_name)
    report = getattr(skin_folder, report_form_name)
    report.report_method = get_report_section_script_name
    report.title = self.id()
    report.manage_addField(
        id='your_field_from_request',
        fieldname='StringField',
        title='')
    report.your_field_from_request.manage_tales_xmlrpc(
        {'default': 'python: "in_report_field: set_in_dialog_request == %s" % context.REQUEST.get("set_in_dialog_request")'})

    # XXX we need this because ERP5 Report are not usable, but only
    # after they are saved to DB and automatically migrated. The getProperty
    # above, which is also what ods_style does, only work after the report
    # state is updated.
    report.__setstate__(aq_base(getattr(skin_folder, report_form_name)).__getstate__())
    self.assertEqual(report.getProperty('title'), self.id())

    # Report section method
    createZODBPythonScript(
        skin_folder,
        get_report_section_script_name,
        '',
        textwrap.dedent(
            """\
            from Products.ERP5Form.Report import ReportSection
            container.REQUEST.set('set_in_report_method', 'set_in_report_method')
            return [ReportSection(form_id='%s',
                                  path=context.getPhysicalPath())]
            """ % (report_section_form_name)))

    # ERP5 Form for report section, with a listbox using the list method
    skin_folder.manage_addProduct['ERP5Form'].addERP5Form(
                        report_section_form_name, report_section_form_name)
    report_section_form = getattr(skin_folder, report_section_form_name)
    report_section_form.title = self.id()
    report_section_form.manage_addField(
        id='listbox',
        fieldname='ProxyField',
        title='')
    report_section_form.listbox.manage_edit_xmlrpc(
        dict(form_id='Base_viewFieldLibrary',
            field_id='my_view_mode_listbox'))
    report_section_form.move_field_group(('listbox',), 'left', 'bottom')
    report_section_form.listbox.manage_edit_surcharged_xmlrpc(
      {
        'selection_name': 'test_%s_selection' % self.id(),
        'title': self.id(),
        'list_method': Method(get_line_list_script_name),
      }
    )

    # List method script
    createZODBPythonScript(
        skin_folder,
        get_line_list_script_name,
        'set_in_dialog_request=None, **kw',
        textwrap.dedent(
            """\
            from Products.PythonScripts.standard import Object
            portal = context.getPortalObject()
            return [Object(
                uid='new_',
                title='in_list_method: set_in_dialog_request == %s, set_in_report_method == %s' % (
                    set_in_dialog_request,
                    container.REQUEST.get('set_in_report_method'),
                ))]
            """))

    self.loginAsUser('bob')
    self.portal.changeSkin('Deferred')
    response = self.publish(
        '/%s/person_module/%s?deferred_portal_skin=%s&set_in_dialog_request=set_in_dialog_request'
        % (self.portal.getId(), report_form_name, self.skin),
        '%s:%s' % (self.username, self.password),)
    self.tic()

    # inspect the report as text and check the selection was initialized from
    # request parameter.
    mail_message = email.message_from_string(self.portal.MailHost._last_message[2])
    part, = [x for x in mail_message.walk() if x.get_content_type() == self.content_type]

    doc = self.portal.document_module.newContent(
      portal_type=self.portal_type,
      content_type=self.content_type,
      data=part.get_payload(decode=True),
      temp_object=True,
    )
    doc.convertToBaseFormat()
    report_as_txt = doc.asText()

    self.assertIn(
        'in_list_method: set_in_dialog_request == set_in_dialog_request, set_in_report_method == set_in_report_method',
        report_as_txt)
    self.assertIn('in_report_field: set_in_dialog_request == set_in_dialog_request', report_as_txt)


class TestODSDeferredStyle(TestDeferredStyleBase):
  skin = 'ODS'
  content_type = 'application/vnd.oasis.opendocument.spreadsheet'
  attachment_file_extension = '.ods'
  portal_type="Spreadsheet"

  def test_report_view_sheet_per_report_section(self):
    """Test the sheet_per_report_section feature of erp5_ods_style.
    """
    self.loginAsUser(self.username)
    self.portal.changeSkin('Deferred')
    response = self.publish(
        '/%s/person_module/pers/Base_viewHistory?deferred_portal_skin=%s&sheet_per_report_section:int=1'
        % (self.portal.getId(), self.skin), '%s:%s' % (self.username, self.password))
    self.tic()
    last_message = self.portal.MailHost._last_message
    self.assertNotEqual(last_message, ())
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


class TestODTDeferredStyle(TestDeferredStyleBase):
  skin = 'ODT'
  content_type = 'application/vnd.oasis.opendocument.text'
  attachment_file_extension = '.odt'
  portal_type = "Text"


class TestDeferredReportAlarm(DeferredStyleTestCase):
  def getBusinessTemplateList(self):
    return super(TestDeferredReportAlarm, self).getBusinessTemplateList() + (
        'erp5_pdm',
        'erp5_simulation',
        'erp5_trade',
        'erp5_accounting',
        'erp5_knowledge_pad',
        'erp5_web',
        'erp5_ingestion',
        'erp5_ingestion_mysql_innodb_catalog',
        'erp5_dms',
    )

  def test_alarm(self):
    # create some data for reports
    self.portal.person_module.newContent(portal_type='Person', first_name="not_included")
    self.portal.person_module.newContent(portal_type='Person', first_name="yes_included").validate()

    # make a script to configure the reports
    report_configuration_script_id = 'Alarm_getTestReportList{}'.format(self.id())
    report_after_generation_script_id = 'Alarm_afterReportGenerated{}'.format(self.id())
    createZODBPythonScript(
        self.portal.portal_skins.custom,
        report_configuration_script_id,
        '',
        textwrap.dedent(
        '''\
        # coding: utf-8
        portal = context.getPortalObject()

        report_data_list = [
          # For the first two reports, we us included script:
          #  Alarm_contributeAndShareReportDocument
          # which creates a document in document module.

          # First with person module view
          {
            'form_id': 'PersonModule_viewPersonList',
            'context': portal.person_module,
            'parameters': {
                'validation_state': 'validated',
            },
            'skin_name': 'ODS',
            'language': 'fr',
            'format': 'txt',
            'callback_script_id': 'Alarm_contributeAndShareReportDocument',
            'callback_script_kwargs': {
                'title': 'Persons {}'.format(DateTime()),
                'reference': 'TEST-Persons.Report',
                'language': 'fr',
            },
          },
          # Then with an accounting report (which uses report_view and a different
          # approach to generate report).
          {
            'form_id': 'AccountModule_viewTrialBalanceReport',
            'context': portal.accounting_module,
            'parameters': {
                'from_date': DateTime(2021, 1, 1),
                'at_date': DateTime(2021, 12, 31),
                'section_category': 'group',
                'section_category_strict': False,
                'simulation_state': ['delivered'],
                'show_empty_accounts': True,
                'expand_accounts': False,
                'per_account_class_summary': False,
                'show_detailed_balance_columns': False,
            },
            'skin_name': 'ODS',
            'language': 'fr',
            'callback_script_id': 'Alarm_contributeAndShareReportDocument',
            'callback_script_kwargs': {
                'title': 'Trial Balance {}'.format(DateTime()),
                'reference': 'TEST-Trial.Balance.Report',
                'language': 'fr',
            },
          },

          # then another report to verify the callback script protocol.
          {
            'form_id': 'Person_view',
            'context': portal.person_module.contentValues()[0],
            'skin_name': 'ODS',
            'language': portal.Localizer.get_default_language(),
            'parameters': {},
            'callback_script_id': '%s',
            'callback_script_kwargs': {
                'foo': 'bar'
            },
          },
        ]

        return report_data_list
        ''' % report_after_generation_script_id))

    createZODBPythonScript(
        self.portal.portal_skins.custom,
        report_after_generation_script_id,
        'subject, attachment_list, foo',
        textwrap.dedent(
        '''\
        context.setTitle('after script called with foo=' + foo)
        '''
    ))

    alarm = self.portal.portal_alarms.template_report_alarm.Base_createCloneDocument(
        batch_mode=True)
    alarm.edit(
        report_configuration_script_id=report_configuration_script_id
    )
    alarm.activeSense()
    self.tic()

    # the first two reports are created
    person_report, = self.portal.portal_catalog.getDocumentValueList(
        reference='TEST-Persons.Report',
        language='fr',
    )
    self.assertIn('yes_included', person_report.getTextContent())
    self.assertNotIn('not_included', person_report.getTextContent())

    trial_balance_report, = self.portal.portal_catalog.getDocumentValueList(
        reference='TEST-Trial.Balance.Report',
        language='fr',
    )
    self.assertEqual(trial_balance_report.getPortalType(), 'Spreadsheet')

    # the third report, used to check the callback script protocol, modified the alarm title
    self.assertEqual(alarm.getTitle(), 'after script called with foo=bar')


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestODSDeferredStyle))
  suite.addTest(unittest.makeSuite(TestODTDeferredStyle))
  suite.addTest(unittest.makeSuite(TestDeferredReportAlarm))
  return suite
