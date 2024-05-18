##############################################################################
#
# Copyright (c) 2008 Nexedi SA and Contributors. All Rights Reserved.
#          Romain Courteaud <romain@nexedi.com>
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
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import getSecurityManager
from Products.ERP5Type.tests.Sequence import SequenceList
from Products.ERP5Type.tests.utils import DummyMailHost
import email
import six
from email.header import decode_header, make_header
from email.utils import parseaddr

# Copied from bt5/erp5_egov/TestTemplateItem/testEGovMixin.py
def decode_email(file_):
  # Prepare result
  theMail = {
    'attachment_list': [],
    'body': '',
    # Place all the email header in the headers dictionary in theMail
    'headers': {}
  }
  # Get Message
  msg = email.message_from_string(file_.decode())
  # Back up original file
  theMail['__original__'] = file_
  for key, value in msg.items():
    decoded_value_list = decode_header(value)
    new_value = make_header(decoded_value_list)
    if six.PY2:
      # Recode headers to UTF-8 if needed
      new_value = new_value.__unicode__().encode('utf-8')
    theMail['headers'][key.lower()] = new_value
  # Filter mail addresses
  for header in ('resent-to', 'resent-from', 'resent-cc', 'resent-sender',
                  'to', 'from', 'cc', 'sender', 'reply-to'):
    header_field = theMail['headers'].get(header)
    if header_field:
      theMail['headers'][header] = parseaddr(header_field.encode())[1]
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
      charset = part.get_content_charset() or 'utf-8'
      payload = part.get_payload(decode=True)
      #LOG('CMFMailIn -> ',0,'charset: %s, payload: %s' % (charset,payload))
      if charset:
        payload = payload.decode(charset)
      if six.PY2:
        payload = payload.encode('utf-8')
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

class TestNotificationTool(ERP5TypeTestCase):
  """
  Test notification tool
  """

  def getBusinessTemplateList(self):
    return ('erp5_base',)

  def getTitle(self):
    return "Notification Tool"

  def createUser(self, name, role_list): # pylint:disable=arguments-differ
    user_folder = self.getPortal().acl_users
    user_folder._doAddUser(name, 'password', role_list, [])

  def changeUser(self, name):
    self.old_user = getSecurityManager().getUser()
    self.loginByUserName(name)

  def changeToPreviousUser(self):
    newSecurityManager(None, self.old_user)

  def afterSetUp(self):
    self.createUser('erp5user', ['Associate', 'Auditor', 'Author'])
    self.createUser('manager', ['Manager'])
    portal = self.getPortal()
    if 'MailHost' in portal.objectIds():
      portal.manage_delObjects(['MailHost'])
    portal._setObject('MailHost', DummyMailHost('MailHost'))
    self.portal.MailHost.reset()
    portal.email_from_address = 'site@example.invalid'
    self.portal.portal_caches.clearAllCache()
    self.tic()
    self.loginByUserName('erp5user')

  def beforeTearDown(self):
    self.abort()
    # clear modules if necessary
    self.loginByUserName('manager')
    self.portal.person_module.manage_delObjects(
            list(self.portal.person_module.objectIds()))
    self.tic()

  def stepAddUserA(self, sequence=None, sequence_list=None, **kw):
    """
    Create a user
    """
    person = self.portal.person_module.newContent(portal_type="Person",
                                                  default_email_text="userA@example.invalid")
    self.changeUser('manager')
    person.edit(reference="userA", password="passwordA")
    assignment = person.newContent(portal_type='Assignment')
    assignment.open()
    self.changeToPreviousUser()
    sequence['user_a_id'] = person.Person_getUserId()

  def stepAddUserB(self, sequence=None, sequence_list=None, **kw):
    """
    Create a user
    """
    person = self.portal.person_module.newContent(portal_type="Person",
                                                  default_email_text="userB@example.invalid")
    self.changeUser('manager')
    person.edit(reference="userB", password="passwordA")
    assignment = person.newContent(portal_type='Assignment')
    assignment.open()
    self.changeToPreviousUser()
    sequence['user_b_id'] = person.Person_getUserId()

  def stepAddUserWithoutEmail(self, sequence=None, sequence_list=None, **kw):
    """
    Create a user
    """
    person = self.portal.person_module.newContent(portal_type="Person")

    self.changeUser('manager')
    person.edit(reference="userWithoutEmail", password="passwordA")
    assignment = person.newContent(portal_type='Assignment')
    assignment.open()
    self.changeToPreviousUser()
    sequence['user_without_email_id'] = person.Person_getUserId()

  def test_01_defaultBehaviour(self):
    self.assertRaises(
      TypeError,
      self.portal.portal_notifications.sendMessage,
    )
    self.assertRaises(
      TypeError,
      self.portal.portal_notifications,
    )

  def stepCheckNotificationWithoutSender(self, sequence=None,
                                         sequence_list=None, **kw):
    """
    Check that notification works without sender
    """
    self.portal.portal_notifications.sendMessage(
        recipient=sequence['user_a_id'], subject='Subject', message='Message')
    last_message = self.portal.MailHost._last_message
    self.assertNotEqual(last_message, ())
    mfrom, mto, _ = last_message
    self.assertEqual('Portal Administrator <site@example.invalid>', mfrom)
    self.assertEqual(['userA@example.invalid'], mto)

  def test_02_noSender(self):
    sequence_list = SequenceList()
    sequence_string = '\
        AddUserA \
        Tic \
        CheckNotificationWithoutSender \
        '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def stepCheckNotificationFailsWithoutSubject(self, sequence=None,
                                               sequence_list=None, **kw):
    """
    Check that notification fails when no subject is given
    """
    self.assertRaises(
      TypeError,
      self.portal.portal_notifications.sendMessage,
        recipient=sequence['user_a_id'], message='Message'
    )

  def test_03_noSubject(self):
    sequence_list = SequenceList()
    sequence_string = '\
        AddUserA \
        Tic \
        CheckNotificationFailsWithoutSubject \
        '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_04_noRecipient(self):
    self.portal.portal_notifications.sendMessage(
        subject='Subject', message='Message')
    last_message = self.portal.MailHost._last_message
    self.assertNotEqual(last_message, ())
    mfrom, mto, _ = last_message
    self.assertEqual('Portal Administrator <site@example.invalid>', mfrom)
    self.assertEqual(['site@example.invalid'], mto)

  def stepCheckNotificationWithoutMessage(self, sequence=None,
                                          sequence_list=None, **kw):
    """
    Check that notification is send when no message is passed
    """
    self.portal.portal_notifications.sendMessage(
        recipient=sequence['user_a_id'], subject='Subject', )
    last_message = self.portal.MailHost._last_message
    self.assertNotEqual(last_message, ())
    mfrom, mto, _ = last_message
    self.assertEqual('Portal Administrator <site@example.invalid>', mfrom)
    self.assertEqual(['userA@example.invalid'], mto)

  def test_05_noMessage(self):
    sequence_list = SequenceList()
    sequence_string = '\
        AddUserA \
        Tic \
        CheckNotificationWithoutMessage \
        '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def stepCheckSimpleNotification(self, sequence=None,
                                  sequence_list=None, **kw):
    """
    Check that notification is send in standard use case
    """
    self.portal.portal_notifications.sendMessage(
        recipient=sequence['user_a_id'], subject='Subject', message='Message')
    last_message = self.portal.MailHost._last_message
    self.assertNotEqual(last_message, ())
    mfrom, mto, messageText = last_message
    self.assertEqual('Portal Administrator <site@example.invalid>', mfrom)
    self.assertEqual(['userA@example.invalid'], mto)
    # Check Message
    mail_dict = decode_email(messageText)
    self.assertEqual(mail_dict['headers']['subject'], 'Subject')
    self.assertEqual(mail_dict['body'], 'Message')
    self.assertSameSet([], mail_dict['attachment_list'])

  def test_06_simpleMessage(self):
    sequence_list = SequenceList()
    sequence_string = '\
        AddUserA \
        Tic \
        CheckSimpleNotification \
        '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def stepCheckNotificationWithAttachment(self, sequence=None,
                                          sequence_list=None, **kw):
    """
    Check attachment
    """
    self.portal.portal_notifications.sendMessage(
        recipient=sequence['user_a_id'], subject='Subject', message='Message',
        attachment_list=[
          {
            'name': 'Attachment 1',
            'content': b'Text 1',
            'mime_type': 'text/plain',
          },
          {
            'name': 'Attachment 2',
            'content': b'Text 2',
            'mime_type': 'application/octet-stream',
          },
        ])
    last_message = self.portal.MailHost._last_message

    self.assertNotEqual(last_message, ())
    mfrom, mto, messageText = last_message
    self.assertEqual('Portal Administrator <site@example.invalid>', mfrom)
    self.assertEqual(['userA@example.invalid'], mto)

    # Check Message
    mail_dict = decode_email(messageText)
    self.assertEqual(mail_dict['headers']['subject'], 'Subject')
    self.assertEqual(mail_dict['body'], 'Message')
    # "Attachment 1" is decoded as str because there was a charset in the
    # message, this is how this `decode_email` utility function from this
    # test works.
    self.assertSameSet([('Attachment 1', 'text/plain', 'Text 1'),
                        ('Attachment 2', 'application/octet-stream', b'Text 2')],
                       mail_dict['attachment_list'])

  def test_07_AttachmentMessage(self):
    sequence_list = SequenceList()
    sequence_string = '\
        AddUserA \
        Tic \
        CheckNotificationWithAttachment \
        '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def stepCheckMultiRecipientNotification(self, sequence=None,
                                          sequence_list=None, **kw):
    """
    Check that notification can be send to multiple recipient
    """
    self.portal.portal_notifications.sendMessage(
        recipient=[sequence['user_a_id'], sequence['user_b_id']], subject='Subject', message='Message')
    last_message = self.portal.MailHost._last_message

    self.assertNotEqual(last_message, ())
    mfrom, mto, _ = last_message
    self.assertEqual('Portal Administrator <site@example.invalid>', mfrom)
    self.assertEqual(['userB@example.invalid'], mto)

    previous_message = self.portal.MailHost._previous_message
    self.assertNotEqual(last_message, ())
    mfrom, mto, _ = previous_message
    self.assertEqual('Portal Administrator <site@example.invalid>', mfrom)
    self.assertEqual(['userA@example.invalid'], mto)

  def test_08_MultiRecipient(self):
    sequence_list = SequenceList()
    sequence_string = '\
        AddUserA \
        AddUserB \
        Tic \
        CheckMultiRecipientNotification \
        '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def stepCheckPersonWithoutEmail(self, sequence=None,
                                  sequence_list=None, **kw):
    """
    Check that notification fails when the destination hasn't a email adress
    """
    with self.assertRaisesRegex(ValueError, "email must be set"):
      self.portal.portal_notifications.sendMessage(
          recipient=sequence['user_without_email_id'], subject='Subject', message='Message')

  def test_08_PersonWithoutEmail(self):
    sequence_list = SequenceList()
    sequence_string = '\
        AddUserWithoutEmail \
        Tic \
        CheckPersonWithoutEmail \
        '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_09_InvalideRecipient(self):
    with self.assertRaises(ValueError):
      self.portal.portal_notifications.sendMessage(
          recipient='UnknowUser', subject='Subject', message='Message')

  def stepCheckPersonNotification(self, sequence=None,
                                  sequence_list=None, **kw):
    """
    Check that notification is send when recipient is a Person
    """
    person = self.portal.Base_getUserValueByUserId(sequence['user_a_id'])
    self.portal.portal_notifications.sendMessage(
        recipient=person.getObject(), subject='Subject', message='Message')
    last_message = self.portal.MailHost._last_message
    self.assertNotEqual(last_message, ())
    mfrom, mto, messageText = last_message
    self.assertEqual('Portal Administrator <site@example.invalid>', mfrom)
    self.assertEqual(['userA@example.invalid'], mto)
    # Check Message
    mail_dict = decode_email(messageText)
    self.assertEqual(mail_dict['headers']['subject'], 'Subject')
    self.assertEqual(mail_dict['body'], 'Message')
    self.assertSameSet([], mail_dict['attachment_list'])

  def test_10_PersonNotification(self):
    sequence_list = SequenceList()
    sequence_string = '\
        AddUserA \
        Tic \
        CheckPersonNotification\
        '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def stepCheckNotificationPlainTextFormat(self, sequence=None,
                                  sequence_list=None, **kw):
    """
    Check that if notification format is plain text.
    """

    message = """\
> Hello, will you go to the park on sunday?
Yes, I will go."""

    self.portal.portal_notifications.sendMessage(
        recipient=sequence['user_a_id'], subject='Subject',
        message_text_format='text/plain', message=message)
    last_message = self.portal.MailHost._last_message
    self.assertNotEqual(last_message, ())
    mfrom, mto, messageText = last_message
    self.assertEqual('Portal Administrator <site@example.invalid>', mfrom)
    self.assertEqual(['userA@example.invalid'], mto)
    # Check Message
    mail_dict = decode_email(messageText)
    self.assertEqual(mail_dict['headers']['subject'], 'Subject')
    self.assertEqual(mail_dict['body'], message)
    self.assertSameSet([], mail_dict['attachment_list'])

  def test_11_TextMessage(self):
    sequence_list = SequenceList()
    sequence_string = '\
        AddUserA \
        Tic \
        CheckNotificationPlainTextFormat \
        '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def stepCheckNotificationHtmlFormat(self, sequence=None,
                                  sequence_list=None, **kw):
    """
    Check that if notification format is html.
    """

    message = """<a href="http://www.erp5.com/">Click Here!!</a>"""

    self.portal.portal_notifications.sendMessage(
        recipient=sequence['user_a_id'], subject='Subject',
        message_text_format='text/html', message=message)
    last_message, = self.portal.MailHost._message_list
    mfrom, mto, messageText = last_message
    self.assertEqual('Portal Administrator <site@example.invalid>', mfrom)
    self.assertEqual(['userA@example.invalid'], mto)
    # Check Message
    mail_dict = decode_email(messageText)
    self.assertEqual(mail_dict['headers']['subject'], 'Subject')
    self.assertEqual(mail_dict['body'], '<html><body>%s</body></html>' % message)
    self.assertSameSet([], mail_dict['attachment_list'])

  def test_12_HtmlMessage(self):
    sequence_list = SequenceList()
    sequence_string = '\
        AddUserA \
        Tic \
        CheckNotificationHtmlFormat \
        '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def stepCheckNotificationWithoutPermissionOnRecipient(self, sequence=None):
    """
    Check that notification is send by user who cannot see recipient
    """
    self.logout()
    self.portal.portal_notifications.sendMessage(
        recipient=sequence['user_a_id'], subject='Subject', message='Message')
    last_message = self.portal.MailHost._last_message
    self.assertNotEqual(last_message, ())

  def test_permission_on_recipient_not_needed(self):
    """Notification Tool can be used to send Messages even when user does not
    have permission on sender or recipent documents.
    """
    sequence_list = SequenceList()
    sequence_string = '\
        AddUserA \
        Tic \
        CheckNotificationWithoutPermissionOnRecipient \
        '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestNotificationTool))
  return suite
