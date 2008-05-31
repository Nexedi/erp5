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

from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from zLOG import LOG
from Products.ERP5Type.tests.Sequence import SequenceList
from Products.ERP5Type.tests.utils import DummyMailHost
from DateTime import DateTime
import email
from email.Header import decode_header, make_header
from email.Utils import parseaddr

# Copied from ERP5Type/patches/CMFMailIn.py
def decode_email(file):
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
    elif content_type == "text/plain":
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

class TestNotificationTool(ERP5TypeTestCase):
  """
  Test notification tool
  """
  run_all_test = 1
  quiet = 1

  def getBusinessTemplateList(self):
    return ('erp5_base',)

  def getTitle(self):
    return "Notification Tool"

  def afterSetUp(self):
    portal = self.getPortal()
    if 'MailHost' in portal.objectIds():
      portal.manage_delObjects(['MailHost'])
    portal._setObject('MailHost', DummyMailHost('MailHost'))
    portal.email_from_address = 'site@example.invalid'
    self.portal.portal_caches.clearAllCache()
    get_transaction().commit()
    self.tic()

  def beforeTearDown(self):
    get_transaction().abort()
    # clear modules if necessary
    self.portal.person_module.manage_delObjects(
            list(self.portal.person_module.objectIds()))
    get_transaction().commit()
    self.tic()

  def stepTic(self,**kw):
    self.tic()

  def stepAddUserA(self, sequence=None, sequence_list=None, **kw):
    """
    Create a user
    """
    person = self.portal.person_module.newContent(portal_type="Person",
                                    reference="userA",
                                    password="passwordA",
                                    default_email_text="userA@example.invalid")
    assignment = person.newContent(portal_type='Assignment')
    assignment.open()

  def stepAddUserB(self, sequence=None, sequence_list=None, **kw):
    """
    Create a user
    """
    person = self.portal.person_module.newContent(portal_type="Person",
                                    reference="userB",
                                    password="passwordA",
                                    default_email_text="userB@example.invalid")
    assignment = person.newContent(portal_type='Assignment')
    assignment.open()

  def stepAddUserWithoutEmail(self, sequence=None, sequence_list=None, **kw):
    """
    Create a user
    """
    person = self.portal.person_module.newContent(portal_type="Person",
                                    reference="userWithoutEmail",
                                    password="passwordA")
    assignment = person.newContent(portal_type='Assignment')
    assignment.open()

  def test_01_defaultBehaviour(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test default behaviour of sendMessage'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)

    self.assertRaises(
      TypeError,
      self.portal.portal_notifications.sendMessage,
    )

  def stepCheckNotificationWithoutSender(self, sequence=None, 
                                         sequence_list=None, **kw):
    """
    Check that notification works without sender
    """
    self.portal.portal_notifications.sendMessage(
        recipient='userA', subject='Subject', message='Message')
    last_message = self.portal.MailHost._last_message
    self.assertNotEquals((), last_message)
    mfrom, mto, messageText = last_message
    self.assertEquals('site@example.invalid', mfrom)
    self.assertEquals(['userA@example.invalid'], mto)

  def test_02_noSender(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test no sender value'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)

    sequence_list = SequenceList()
    sequence_string = '\
        AddUserA \
        Tic \
        CheckNotificationWithoutSender \
        '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def stepCheckNotificationFailsWithoutSubject(self, sequence=None, 
                                               sequence_list=None, **kw):
    """
    Check that notification fails when no subject is given
    """
    self.assertRaises(
      TypeError,
      self.portal.portal_notifications.sendMessage,
        recipient='userA', message='Message'
    )

  def test_03_noSubject(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test no subject value'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)

    sequence_list = SequenceList()
    sequence_string = '\
        AddUserA \
        Tic \
        CheckNotificationFailsWithoutSubject \
        '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_04_noRecipient(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test no recipient value'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)

    self.portal.portal_notifications.sendMessage(
        subject='Subject', message='Message')
    last_message = self.portal.MailHost._last_message
    self.assertNotEquals((), last_message)
    mfrom, mto, messageText = last_message
    self.assertEquals('site@example.invalid', mfrom)
    self.assertEquals(['site@example.invalid'], mto)

  def stepCheckNotificationWithoutMessage(self, sequence=None, 
                                          sequence_list=None, **kw):
    """
    Check that notification is send when no message is passed
    """
    self.portal.portal_notifications.sendMessage(
        recipient='userA', subject='Subject', )
    last_message = self.portal.MailHost._last_message
    self.assertNotEquals((), last_message)
    mfrom, mto, messageText = last_message
    self.assertEquals('site@example.invalid', mfrom)
    self.assertEquals(['userA@example.invalid'], mto)

  def test_05_noMessage(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test no message value'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)

    sequence_list = SequenceList()
    sequence_string = '\
        AddUserA \
        Tic \
        CheckNotificationWithoutMessage \
        '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def stepCheckSimpleNotification(self, sequence=None, 
                                  sequence_list=None, **kw):
    """
    Check that notification is send in standard use case
    """
    self.portal.portal_notifications.sendMessage(
        recipient='userA', subject='Subject', message='Message')
    last_message = self.portal.MailHost._last_message
    self.assertNotEquals((), last_message)
    mfrom, mto, messageText = last_message
    self.assertEquals('site@example.invalid', mfrom)
    self.assertEquals(['userA@example.invalid'], mto)
    # Check Message
    mail_dict = decode_email(messageText)
    self.assertEquals(mail_dict['headers']['subject'], 'Subject')
    self.assertEquals(mail_dict['body'], 'Message')
    self.assertSameSet([], mail_dict['attachment_list'])

  def test_06_simpleMessage(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test simple message'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)

    sequence_list = SequenceList()
    sequence_string = '\
        AddUserA \
        Tic \
        CheckSimpleNotification \
        '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def stepCheckNotificationWithAttachment(self, sequence=None, 
                                          sequence_list=None, **kw):
    """
    Check attachment
    """
    self.portal.portal_notifications.sendMessage(
        recipient='userA', subject='Subject', message='Message',
        attachment_list=[
          {
            'name': 'Attachment 1',
            'content': 'Text 1',
            'mime_type': 'text/plain',
          },
          {
            'name': 'Attachment 2',
            'content': 'Text 2',
            'mime_type': 'application/octet-stream',
          },
        ])
    last_message = self.portal.MailHost._last_message

    self.assertNotEquals((), last_message)
    mfrom, mto, messageText = last_message
    self.assertEquals('site@example.invalid', mfrom)
    self.assertEquals(['userA@example.invalid'], mto)

    # Check Message
    mail_dict = decode_email(messageText)
    self.assertEquals(mail_dict['headers']['subject'], 'Subject')
    self.assertEquals(mail_dict['body'], 'Message')
    self.assertSameSet([('Attachment 1', 'text/plain', 'Text 1'),
                        ('Attachment 2', 'application/octet-stream', 'Text 2')], 
                       mail_dict['attachment_list'])

  def test_07_AttachmentMessage(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test attachments'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)

    sequence_list = SequenceList()
    sequence_string = '\
        AddUserA \
        Tic \
        CheckNotificationWithAttachment \
        '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def stepCheckMultiRecipientNotification(self, sequence=None, 
                                          sequence_list=None, **kw):
    """
    Check that notification can be send to multiple recipient
    """
    self.portal.portal_notifications.sendMessage(
        recipient=['userA', 'userB'], subject='Subject', message='Message')
    last_message = self.portal.MailHost._last_message

    self.assertNotEquals((), last_message)
    mfrom, mto, messageText = last_message
    self.assertEquals('site@example.invalid', mfrom)
    self.assertEquals(['userB@example.invalid'], mto)

    previous_message = self.portal.MailHost._previous_message
    self.assertNotEquals((), previous_message)
    mfrom, mto, messageText = previous_message
    self.assertEquals('site@example.invalid', mfrom)
    self.assertEquals(['userA@example.invalid'], mto)

  def test_08_MultiRecipient(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test multi recipient value'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)

    sequence_list = SequenceList()
    sequence_string = '\
        AddUserA \
        AddUserB \
        Tic \
        CheckMultiRecipientNotification \
        '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def stepCheckPersonWithoutEmail(self, sequence=None, 
                                  sequence_list=None, **kw):
    """
    Check that notification fails when the destination hasn't a email adress
    """
    self.assertRaises(
      AttributeError,
      self.portal.portal_notifications.sendMessage,
      recipient='userWithoutEmail', subject='Subject', message='Message'
    )

  def test_08_PersonWithoutEmail(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test no email value'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)

    sequence_list = SequenceList()
    sequence_string = '\
        AddUserWithoutEmail \
        Tic \
        CheckPersonWithoutEmail \
        '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_09_InvalideRecipient(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test invalide recipient'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    self.assertRaises(
      IndexError,
      self.portal.portal_notifications.sendMessage,
      recipient='UnknowUser', subject='Subject', message='Message'
    )

  def stepCheckPersonNotification(self, sequence=None, 
                                  sequence_list=None, **kw):
    """
    Check that notification is send when recipient is a Person
    """
    person = self.portal.portal_catalog(reference='userA', portal_type='Person')[0]
    self.portal.portal_notifications.sendMessage(
        recipient=person.getObject(), subject='Subject', message='Message')
    last_message = self.portal.MailHost._last_message
    self.assertNotEquals((), last_message)
    mfrom, mto, messageText = last_message
    self.assertEquals('site@example.invalid', mfrom)
    self.assertEquals(['userA@example.invalid'], mto)
    # Check Message
    mail_dict = decode_email(messageText)
    self.assertEquals(mail_dict['headers']['subject'], 'Subject')
    self.assertEquals(mail_dict['body'], 'Message')
    self.assertSameSet([], mail_dict['attachment_list'])

  def test_10_PersonNotification(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Person recipient'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)

    sequence_list = SequenceList()
    sequence_string = '\
        AddUserA \
        Tic \
        CheckPersonNotification\
        '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)


class TestNotificationToolWithCRM(TestNotificationTool):
  """Make sure that notification tool works with crm"""

  def getBusinessTemplateList(self):
    return ('erp5_base', 'erp5_crm')


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestNotificationTool))
  suite.addTest(unittest.makeSuite(TestNotificationToolWithCRM))
  return suite
