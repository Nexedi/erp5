##############################################################################
#
# Copyright (c) 2026 Nexedi SA and Contributors. All Rights Reserved.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
##############################################################################

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
import json
import mock


class TestMailMessageFindAndSetFollowUpPurchasePackingList(ERP5TypeTestCase):
  """Tests for MailMessage_findAndSetFollowUpPurchasePackingList skin script."""

  def afterSetUp(self):
    self.portal = self.getPortal()
    self._setupOpenaiConnector()
    self._cleanup_list = []

  def beforeTearDown(self):
    for obj_path in self._cleanup_list:
      try:
        parent_path, obj_id = obj_path.rsplit('/', 1)
        parent = self.portal.restrictedTraverse(parent_path)
        parent.manage_delObjects([obj_id])
      except Exception:
        pass
    self.tic()

  def _setupOpenaiConnector(self):
    results = self.portal.portal_web_services.searchFolder(reference='openai')
    if results:
      self._connector = results[0].getObject()
    else:
      self._connector = self.portal.portal_web_services.newContent(
        portal_type='Openai Connector',
        title='openai',
        reference='openai',
        url_string='https://api.openai.com/v1',
      )
      self.tic()

  def _makeOrganisation(self, title):
    org = self.portal.organisation_module.newContent(
      portal_type='Organisation',
      title=title,
    )
    self._cleanup_list.append(org.getRelativeUrl())
    return org

  def _makeMailMessageWithPDF(self, filename='invoice.pdf',
                               body=None):
    if body is None:
      body = b'%PDF-1.4 test'
    from email.mime.multipart import MIMEMultipart
    from email.mime.base import MIMEBase
    from email.mime.text import MIMEText
    from email import encoders

    msg = MIMEMultipart()
    msg['Subject'] = 'Test Delivery Note'
    msg['From'] = 'supplier@example.com'
    msg['To'] = 'warehouse@example.com'
    msg.attach(MIMEText('Please find attached delivery note.'))

    part = MIMEBase('application', 'pdf')
    part.set_payload(body)
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment', filename=filename)
    msg.attach(part)

    mail_message = self.portal.event_module.newContent(
      portal_type='Mail Message',
      title='Test Mail with PDF',
    )
    mail_message.setData(msg.as_string())
    self._cleanup_list.append(mail_message.getRelativeUrl())
    self.tic()
    return mail_message

  def _makeMailMessageWithoutPDF(self):
    from email.mime.text import MIMEText

    msg = MIMEText('Plain text email, no attachment.')
    msg['Subject'] = 'No attachment'
    msg['From'] = 'someone@example.com'
    msg['To'] = 'warehouse@example.com'

    mail_message = self.portal.event_module.newContent(
      portal_type='Mail Message',
      title='Test Mail without PDF',
    )
    mail_message.setData(msg.as_string())
    self._cleanup_list.append(mail_message.getRelativeUrl())
    self.tic()
    return mail_message

  def _makePurchasePackingList(self, title='Test PPL',
                                source_section_title=None,
                                source_title=None, reference='',
                                comment='', start_date=None):
    ppl = self.portal.purchase_packing_list_module.newContent(
      portal_type='Purchase Packing List',
      title=title,
      reference=reference,
      comment=comment,
    )
    if source_section_title:
      org = self._makeOrganisation(source_section_title)
      ppl.setSourceSectionValue(org)
    if source_title:
      org = self._makeOrganisation(source_title)
      ppl.setSourceValue(org)
    if start_date:
      ppl.setStartDate(start_date)
    self._cleanup_list.append(ppl.getRelativeUrl())
    self.tic()
    return ppl

  def _mockConnectorResponse(self, extracted_dict):
    response_json = json.dumps(extracted_dict)
    return mock.patch.object(
      self._connector.__class__, 'getResponse',
      return_value=response_json,
    )

  def test_no_pdf_attachment(self):
    """Script returns error when mail has no PDF attachment."""
    mail_message = self._makeMailMessageWithoutPDF()
    result = mail_message.MailMessage_findAndSetFollowUpPurchasePackingList()
    self.assertEqual(result, 'No PDF attachment found')

  def test_json_parse_failure(self):
    """Script returns error when OpenAI returns invalid JSON."""
    mail_message = self._makeMailMessageWithPDF()
    with mock.patch.object(
      self._connector.__class__, 'getResponse',
      return_value='This is not valid JSON',
    ):
      result = mail_message.MailMessage_findAndSetFollowUpPurchasePackingList()
    self.assertIn('JSON parse failed', result)

  def test_supplier_name_match(self):
    """Script links to PPL when supplier name matches."""
    ppl = self._makePurchasePackingList(
      title='PPL from Teiling',
      source_section_title='Teiling GmbH + Co KG',
      reference='INV-001',
    )
    mail_message = self._makeMailMessageWithPDF()
    extracted = {
      'supplier_name': 'Teiling GmbH + Co KG',
      'shipper_name': None,
      'shipping_date': None,
      'total_price': None,
      'order_reference': None,
    }
    with self._mockConnectorResponse(extracted):
      result = mail_message.MailMessage_findAndSetFollowUpPurchasePackingList()
    self.assertIn('Linked', result)
    self.assertEqual(
      mail_message.getFollowUpValue().getRelativeUrl(),
      ppl.getRelativeUrl(),
    )

  def test_order_reference_match_in_comment(self):
    """Script links to PPL when order reference matches comment."""
    ppl = self._makePurchasePackingList(
      title='PPL with comment ref',
      comment='Belegnummer 20260112121314926',
    )
    mail_message = self._makeMailMessageWithPDF()
    extracted = {
      'supplier_name': 'Zyxwvut Nonexistent Corp',
      'shipper_name': None,
      'shipping_date': None,
      'total_price': None,
      'order_reference': '20260112121314926',
    }
    with self._mockConnectorResponse(extracted):
      result = mail_message.MailMessage_findAndSetFollowUpPurchasePackingList()
    self.assertIn('Linked', result)
    self.assertEqual(
      mail_message.getFollowUpValue().getRelativeUrl(),
      ppl.getRelativeUrl(),
    )

  def test_no_confident_match(self):
    """Script returns no-match when no PPL scores above 0."""
    self._makePurchasePackingList(
      title='Unrelated PPL',
      source_section_title='Completely Different Company XYZ123',
    )
    mail_message = self._makeMailMessageWithPDF()
    extracted = {
      'supplier_name': 'Zyxwvut Qrplmn Nonexistent Corp',
      'shipper_name': None,
      'shipping_date': None,
      'total_price': None,
      'order_reference': None,
    }
    with self._mockConnectorResponse(extracted):
      result = mail_message.MailMessage_findAndSetFollowUpPurchasePackingList()
    self.assertIn('No confident match', result)

  def test_combined_scoring(self):
    """Multiple matching factors increase the score."""
    ppl = self._makePurchasePackingList(
      title='Full match PPL',
      source_section_title='Acme Supplies GmbH',
      comment='Order ref ABC123',
      reference='ABC123',
    )
    mail_message = self._makeMailMessageWithPDF()
    extracted = {
      'supplier_name': 'Acme Supplies GmbH',
      'shipper_name': None,
      'shipping_date': None,
      'total_price': None,
      'order_reference': 'abc123',
    }
    with self._mockConnectorResponse(extracted):
      result = mail_message.MailMessage_findAndSetFollowUpPurchasePackingList()
    self.assertIn('Linked', result)
    # supplier(4) + ref in comment(6) + ref in reference(6) = 16
    self.assertIn('score=16', result)
    self.assertEqual(
      mail_message.getFollowUpValue().getRelativeUrl(),
      ppl.getRelativeUrl(),
    )

  def test_markdown_json_stripping(self):
    """Script strips markdown code fences from OpenAI response."""
    self._makePurchasePackingList(
      title='PPL for markdown test',
      source_section_title='Markdown Test Corp',
    )
    mail_message = self._makeMailMessageWithPDF()
    json_body = json.dumps({
      'supplier_name': 'Markdown Test Corp',
      'shipper_name': None,
      'shipping_date': None,
      'total_price': None,
      'order_reference': None,
    })
    wrapped = '```json\n' + json_body + '\n```'
    with mock.patch.object(
      self._connector.__class__, 'getResponse',
      return_value=wrapped,
    ):
      result = mail_message.MailMessage_findAndSetFollowUpPurchasePackingList()
    self.assertIn('Linked', result)
