##############################################################################
#
# Copyright (c) 2002-2017 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################
import email
import mock
import time
import six
# pylint:disable=no-name-in-module
if six.PY3:
  from email import message_from_bytes
else:
  from email import message_from_string as message_from_bytes
# pylint:enable=no-name-in-module
from email.generator import Generator

from Products.ERP5Type.tests.ERP5TypeLiveTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.Sequence import SequenceList
from Products.ERP5Type.Utils import bytes2str, str2bytes
from Products.ZSQLCatalog.SQLCatalog import SimpleQuery
from DateTime import DateTime

from six import StringIO
import re

def normalize_email_bytes(email_bytes):
  # type: (bytes) -> str
  """
  Normalizes the representation of email text, so that it can be compared.

  The fields of the message are written in a predefined order, with
  the `unixfrom` field removed and no line wrapping.

  The code is intended to be compatible with both Python 2 and Python 3.

  Args:
    email_bytes: Content of the email, including headers.

  Returns:
    Normalized string representation of the e-mail contents.
  """
  # Unfolding removes newlines followed by whitespace, as per RFC5322.
  # This SHOULD be done by Python itself, but seemingly no-one cared
  # enough.
  email_bytes_unfolded = re.sub(
    br"\r?\n(?P<space>\s)",
    br"\g<space>",
    email_bytes,
  )
  msg = message_from_bytes(email_bytes_unfolded)

  fp = StringIO()
  g = Generator(fp, mangle_from_=False, maxheaderlen=0)
  g.flatten(msg)

  return fp.getvalue()


class TestInterfacePost(ERP5TypeTestCase):
  """
  Tests the creation of "Post" documents when their related event type
  is sent.
  """

  default_mail_text_content = \
    'Hello dear customer,\nConnect to your space online to get free money'

  def getTitle(self):
    return "Interface Post Test"

  def afterSetUp(self):
    self.portal.MailHost.reset()

    user_list = self.portal.portal_catalog(portal_type='Person', reference='user')
    if user_list:
      self.user = user_list[0]
    else:
      self.user = self.createSimpleUser('user', 'user', 'admin')
      self.user.edit(
        default_email_coordinate_text='user@example.com'
      )
      self.user.validate()

    # Make sure to have a difference of at least 1 second between test_launch_date
    # and creation_date of new documents, otherwise they won't be found by catalog
    # during the fatest test sequences
    self.test_launch_date = DateTime()
    time.sleep(1)

    self.sender = self.portal.person_module.newContent(
      portal_type='Person',
      title='sender',
      default_email_coordinate_text='sender@example.com',
    )
    self.recipient = self.portal.person_module.newContent(
      portal_type='Person',
      title='recipient',
      default_email_coordinate_text='recipient@example.com',
    )
    self.recipient_list = [self.recipient,]

  def beforeTearDown(self):
    for module_id in ('event_module', 'internet_message_post_module', 'letter_post_module'):
      module = getattr(self.portal, module_id)
      module.manage_delObjects(list(module.objectIds()))

  def _portal_catalog(self, **kw):
    result_list = self.portal.portal_catalog(**kw)
    uid_list = [x.uid for x in result_list]
    if len(uid_list):
      return self.portal.portal_catalog(
        uid=uid_list,
        query=SimpleQuery(
          creation_date=self.test_launch_date,
          comparison_operator='>'
        ),
      )
    else:
      return result_list

  def _stepCreateEvent(self, portal_type, sequence=None, sequence_list=None):
    event = self.portal.event_module.newContent(
      portal_type=portal_type,
      source_value=self.sender,
      destination_value_list=self.recipient_list,
      title='Promotional campaign',
      text_content=self.default_mail_text_content,
    )
    sequence['mail_message'] = event
    sequence.setdefault('mail_message_list', []).append(event)
    return event

  def stepCreateMailMessage(self, sequence=None, sequence_list=None):
    self._stepCreateEvent(portal_type='Mail Message',
                          sequence=sequence,
                          sequence_list=sequence_list)

  def stepCreateLetter(self, sequence=None, sequence_list=None):
    letter = self._stepCreateEvent(portal_type='Letter',
                                   sequence=sequence,
                                   sequence_list=sequence_list)
    sequence.setdefault('letter_list', []).append(letter)

  def stepSendAllLetter(self, sequence=None, sequence_list=None):
    for letter in sequence['letter_list']:
      letter.send()

  def stepCreateInternetMessagePost(self, sequence=None, sequence_list=None):
    internet_message_post = self.portal.internet_message_post_module.newContent(
      portal_type='Internet Message Post',
      reference='ref1',
    )
    sequence['internet_message_post'] = internet_message_post
    sequence.setdefault('internet_message_post_list', []).append(internet_message_post)

  def stepCreateLetterPost(self, sequence=None, sequence_list=None):
    letter_post = self.portal.letter_post_module.newContent(
      portal_type='Letter Post',
      reference='ref1',
    )
    sequence['letter_post'] = letter_post
    sequence.setdefault('letter_post_list', []).append(letter_post)

  def stepStartMailMessage(self, sequence=None, sequence_list=None):
    self.portal.portal_workflow.doActionFor(
      sequence['mail_message'],
      'start_action'
    )

  def _prepareExportOfAllPostByPortalType(self, portal_type):
    result_list = self._portal_catalog(portal_type=portal_type)
    for result in result_list:
      result.prepareExport()

  def stepPrepareExportOfAllInternetMessagePost(self, sequence=None, sequence_list=None):
    self._prepareExportOfAllPostByPortalType('Internet Message Post')

  def stepPrepareExportOfAllLetterPost(self, sequence=None, sequence_list=None):
    self._prepareExportOfAllPostByPortalType('Letter Post')

  def stepChangeMailMessageTextContent(self, sequence=None, sequence_list=None):
    mail_message = sequence['mail_message']
    mail_message.setTextContent("Hello customer,\nsome agent is trying to hack the system")

  def stepCheckMailMessage(self, sequence=None, sequence_list=None):
    mail_message = sequence['mail_message']
    self.assertEqual(mail_message.getSimulationState(), 'started')
    self.assertIn(mail_message.getTextContent(), self.default_mail_text_content)

  def _checkOnlyOnePostIsExportedByPortalType(self, portal_type):
    result_list = self._portal_catalog(
      portal_type=portal_type,
      simulation_state='exported',
    )
    self.assertEqual(
      len(result_list),
      1,
      "More than 1 exportable Internet Message Post has been exported."
    )

    result_list = self._portal_catalog(
      portal_type=portal_type,
      simulation_state='unexportable',
    )
    self.assertGreaterEqual(
      len(result_list),
      1,
      "No Internet Message Post's export has been cancelled after exporting one of them."
    )

  def stepCheckOnlyOneInternetMessagePostIsExported(self, sequence=None, sequence_list=None):
    self._checkOnlyOnePostIsExportedByPortalType('Internet Message Post')

  def stepCheckOnlyOneLetterPostIsExported(self, sequence=None, sequence_list=None):
    self._checkOnlyOnePostIsExportedByPortalType('Letter Post')

  def stepCheckAllLetterPostIsExportPrepared(self, sequence=None, sequence_list=None):
    letter_post_list = self._portal_catalog(
      portal_type='Letter Post',
      simulation_state='export_prepared',
    )
    self.assertEqual(len(letter_post_list), len(sequence['letter_list']))
    for letter_post in letter_post_list:
      self.assertTrue(letter_post.hasData())
      self.assertEqual(letter_post.getContentType(), 'application/pdf')
      self.assertIn(
        letter_post.getAggregateRelatedValue(),
        sequence['letter_list']
      )

  def stepCheckAllLetterPostAreExported(self, sequence=None, sequence_list=None):
    letter_post_list = self._portal_catalog(
      portal_type='Letter Post',
      simulation_state='exported',
    )
    self.assertEqual(len(letter_post_list), len(sequence['letter_list']))
    for letter_post in letter_post_list:
      self.assertEqual(letter_post.getSimulationState(), 'exported')

  def stepCheckInternetMessagePostCreated(self, sequence=None, sequence_list=None):
    mail_message = sequence['mail_message']
    internet_message_post_list = mail_message.getAggregateValueList(
      portal_type='Internet Message Post')

    self.assertEqual(len(internet_message_post_list), len(self.recipient_list))

    sequence['internet_message_post'] = internet_message_post_list[0]
    sequence['internet_message_post_list'] = internet_message_post_list

    self.assertEqual(0, len(mail_message.getAggregateDocumentTitleList([])),
      "Internet Message Post shouldn't be an attachment"
    )

    for internet_message_post in internet_message_post_list:
      self.assertEqual(internet_message_post.getSimulationState(), 'exported')
      mail_object = email.message_from_string(bytes2str(internet_message_post.getData()))
      self.assertEqual(
        internet_message_post.getReference(), mail_object['message-id'].strip('<>')
      )
      self.assertEqual(
        mail_message.getTextContent(),
        internet_message_post.InternetMessagePost_getFirstPartFromMultipartMessage()
      )

  def stepCheckOnlyOneMessageHasBeenSentFromMailHost(self, sequence=None, sequence_list=None):
    self.assertEqual(1, len(self.portal.MailHost.getMessageList()))

  def stepCheckLatestMessageFromMailHost(self, sequence=None, sequence_list=None):
    last_message, = self.portal.MailHost._message_list
    self.assertNotEqual((), last_message)
    _, _, message_text = last_message
    self.assertEqual(
      normalize_email_bytes(message_text),
      normalize_email_bytes(sequence['internet_message_post'].getData()),
    )

  def _getMailHostMessageForRecipient(self, recipient_email_address):
    message_list = self.portal.MailHost._message_list
    result_list = []
    for message in message_list:
      _, to_list, _ = message
      for recipient in to_list:
        if recipient_email_address in recipient:
          result_list.append(message)
    return result_list

  def stepCheckLatestMessageListFromMailHost(self, sequence=None, sequence_list=None):
    message_list = self.portal.MailHost._message_list
    self.assertEqual(len(message_list), len(self.recipient_list))
    for post in sequence['internet_message_post_list']:
      post_recipient = email.message_from_string(bytes2str(post.getData()))['to']
      message_list = self._getMailHostMessageForRecipient(post_recipient)
      self.assertEqual(len(message_list), 1)
      message = message_list[0]
      _, _, message_text = message
      self.assertEqual(
        normalize_email_bytes(message_text),
        normalize_email_bytes(post.getData()),
      )

  def stepCheckMailMessagePreviewDisplaysLatestInternetMessagePostData(self, sequence=None, sequence_list=None):
    mail_message = sequence['mail_message']
    self.assertNotEqual(mail_message.getTextContent(), self.default_mail_text_content)
    self.assertIn(
      self.default_mail_text_content,
      mail_message.MailMessage_viewPreview.my_text_content.render(),
    )

  def stepCheckCreateAndIngestInternetMessagePostResponse(self, sequence=None, sequence_list=None):
    post = sequence['internet_message_post']

    # Create a response mail object
    mail_object = email.message_from_string(bytes2str(post.getData()))

    sender = mail_object['from']
    recipient = mail_object['to']

    mail_object.replace_header('from', recipient)
    mail_object.replace_header('to', sender)
    mail_object.add_header('In-Reply-To', mail_object['message-id'])
    mail_object.add_header('References', mail_object['in-reply-to'])
    mail_object.replace_header('message-id', email.utils.make_msgid())
    mail_object.replace_header('subject', 'Re: {}'.format(mail_object['subject']))

    # Ingest it
    response_post = self.portal.internet_message_post_module.newContent(
      portal_type='Internet Message Post',
      data=str2bytes(mail_object.as_string()),
    )
    response_post.prepareImport()
    sequence['internet_message_post_response'] = response_post

  def stepCheckMailMessageResponseCreated(self, sequence=None, sequence_list=None):
    response_list = self._portal_catalog(
      portal_type='Mail Message',
      title='Re: Promotional campaign',
    )
    self.assertEqual(len(response_list), 1)
    response, = response_list
    self.assertEqual(
      response.getCausalityValue(),
      sequence['mail_message'],
    )
    self.assertEqual(
      response.getAggregateValue(portal_type='Internet Message Post'),
      sequence['internet_message_post_response']
    )
    self.assertEqual(response.getSourceTitle(), 'recipient')
    self.assertEqual(response.getDestinationTitle(), 'sender')
    self.assertEqual(response.getSimulationState(), 'delivered')

  def stepLaunchExportOnLetterPostModule(self, sequence=None, sequence_list=None):
    self.portal.letter_post_module.LetterPostModule_exportExportableLetterPostActivity(
      user_name=self.user.getUserId(),
      comment='To print',
      localizer_language='fr',
    )

  def stepCheckAggregatingPDFDocument(self, sequence=None, sequence_list=None):
    pdf_document_list = self._portal_catalog(portal_type='PDF')
    self.assertEqual(len(pdf_document_list), 1)
    pdf_document, = pdf_document_list
    self.assertEqual(2, int(pdf_document.getContentInformation()['Pages']))

  def stepMakeEntitySendEmailFailOnce(self, sequence=None):
    def Entity_sendEmail(*args, **kw):
      self.Entity_sendEmail_patcher.stop()
      raise ValueError("Fail on first execution")
    self.Entity_sendEmail_patcher = mock.patch(
        'erp5.portal_type.Person.Entity_sendEmail',
        create=True,
        side_effect=Entity_sendEmail)
    self.Entity_sendEmail_mock = self.Entity_sendEmail_patcher.start()
    self.addCleanup(self.Entity_sendEmail_patcher.stop)

  def stepCheckEntitySendEmailCalled(self, sequence=None):
    self.Entity_sendEmail_mock.assert_called()

  def test_emailSendingIsPilotedByInternetMessagePost(self):
    """
    """
    sequence_list = SequenceList()
    sequence_string = """
      stepCreateMailMessage
      stepStartMailMessage
      stepTic
      stepCheckMailMessage
      stepCheckInternetMessagePostCreated
      stepCheckOnlyOneMessageHasBeenSentFromMailHost
      stepCheckLatestMessageFromMailHost
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_deliveredMailMessagePreviewDisplaysLatestInternetMessagePostData(self):
    """
    """
    sequence_list = SequenceList()
    sequence_string = """
      stepCreateMailMessage
      stepStartMailMessage
      stepCheckMailMessage
      stepTic
      stepCheckInternetMessagePostCreated
      stepCheckLatestMessageFromMailHost
      stepChangeMailMessageTextContent
      stepCheckMailMessagePreviewDisplaysLatestInternetMessagePostData
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_sentMailMessageCreateOneInternetMessagePostForEachRecipient(self):
    """
    In case of multi recipients for emails, one mail message content is generated
    and sent through the MailHost. As the purpose of Internet Message Post is to
    track what goes out of ERP5, one Internet Message Post must be created for each
    of these mail message contents.
    """
    recipient_2 = self.portal.person_module.newContent(
      portal_type='Person',
      title='recipient_2',
      default_email_coordinate_text='recipient_2@example.com',
    )
    self.recipient_list.append(recipient_2)

    sequence_list = SequenceList()
    sequence_string = """
      stepCreateMailMessage
      stepStartMailMessage
      stepCheckMailMessage
      stepTic
      stepCheckInternetMessagePostCreated
      stepCheckLatestMessageListFromMailHost
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_Entity_sendEmailCanRaiseOnceWithoutSpammingRecipient(self):
    """
    Entity_sendEmail used to be launched in an activity with retry_max=0 and
    retry_conflict=False. But now that it creates Internet Message Posts, it
    should be able to retry on ConflictError. We should also make sure that
    in this case the mail isn't sent (as MailHost isn't transactional)
    """
    sequence_list = SequenceList()
    sequence_string = """
      stepMakeEntitySendEmailFailOnce
      stepCreateMailMessage
      stepStartMailMessage
      stepCheckMailMessage
      stepTic
      stepCheckInternetMessagePostCreated
      stepCheckOnlyOneMessageHasBeenSentFromMailHost
      stepCheckLatestMessageListFromMailHost
      stepCheckEntitySendEmailCalled
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_ingestedInternetMessagePostCreateMailMessageWithCausality(self):
    sequence_list = SequenceList()
    sequence_string = """
      stepCreateMailMessage
      stepStartMailMessage
      stepCheckMailMessage
      stepTic
      stepCheckInternetMessagePostCreated
      stepCheckLatestMessageListFromMailHost
      stepCheckCreateAndIngestInternetMessagePostResponse
      stepTic
      stepCheckMailMessageResponseCreated
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_exportAllExportableLetterPostInAPDFDocument(self):
    """
    Test the action on Letter Post Module to export all exportable Letter Posts
    and aggregate their content in a unique PDF document (easy to print)
    """
    sequence_list = SequenceList()
    sequence_string = """
      stepCreateLetter
      stepCreateLetter
      stepSendAllLetter
      stepTic
      stepCheckAllLetterPostIsExportPrepared
      stepLaunchExportOnLetterPostModule
      stepTic
      stepCheckAllLetterPostAreExported
      stepTic
      stepCheckOnlyOneMessageHasBeenSentFromMailHost
      stepCheckAggregatingPDFDocument
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)
