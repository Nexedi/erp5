##############################################################################
#
# Copyright (c) 2002-2021 Nexedi SA and Contributors. All Rights Reserved.
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

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
import mock
from DateTime import DateTime

def submitRequest(recipient, sender, document):
  return 'request', 'response'

class testMailevaSOAPConnector(ERP5TypeTestCase):

  def afterSetUp(self):
    maileva_connector = self.portal.portal_catalog.getResultValue(
      portal_type='Maileva SOAP Connector',
      reference='test_maileva_soap_connector',
      validation_state='validated')

    if not maileva_connector:
      maileva_connector = self.portal.portal_web_services.newContent(
        portal_type='Maileva SOAP Connector',
        user_id='test',
        password='test',
        url_string='mytest',
        reference='test_maileva_soap_connector')
      maileva_connector.validate()
    if not getattr(self.portal.portal_categories.region, 'france', None):
      self.portal.portal_categories.region.newContent(
        portal_type='Category',
        id='france',
        codification='FR')
    if not getattr(self.portal.portal_categories.social_title, 'testmr', None):
      self.portal.portal_categories.social_title.newContent(
        portal_type='Category',
        id='testmr',
        title='MR')

    sender = self.portal.portal_catalog.getResultValue(
      portal_type='Organisation',
      reference='test_maileva_connector_sender',
    )
    if not sender:
      sender = self.portal.organisation_module.newContent(
        portal_type='Organisation',
        reference='test_maileva_connector_sender',
        corporate_name='test_maileva_connector_sender',
        default_address_region='france',
        default_address_street_address="122\nRue 11",
        default_address_zip_code="59000",
        default_address_city="LILLE"
      )
    recipient = self.portal.portal_catalog.getResultValue(
      portal_type='Person',
      reference='test_maileva_connector_recipient',
    )
    if not recipient:
      recipient = self.portal.person_module.newContent(
        portal_type='Person',
        social_title="testmr",
        reference='test_maileva_connector_recipient',
        default_address_region='france',
        default_address_street_address="123\nRue 12",
        career_subordination_value=sender,
        default_address_zip_code="59000",
        default_address_city="LILLE"
      )
      career = recipient.getDefaultCareerValue()
      career.edit(
        start_date = DateTime("2021/12/01"),
        title='default_career',
        reference='00000001'
      )
      career.start()

    document = self.portal.portal_catalog.getResultValue(
      portal_type='PDF',
      reference='test_maileva_connector_document',
    )
    if not document:
      document = self.portal.document_module.newContent(
        portal_type='PDF',
        reference='test_maileva_connector_document'
      )

    self.maileva_connector = maileva_connector
    self.sender = sender
    self.recipient = recipient
    self.document = document
    self.tic()

  def getTitle(self):
    return "Test Maileva SOAP Connector"

  def test_send_pdf_to_maileva(self):
    self.portal.system_event_module.manage_delObjects([x.getId() for x in self.document.getFollowUpRelatedValueList(portal_type='Maileva Exchange')])
    self.tic()
    with mock.patch(
        'erp5.component.document.MailevaSOAPConnector.MailevaSOAPConnector.submitRequest',
        side_effect=submitRequest,
    ):
      self.document.activate().PDF_sendToMailevaByActivity(
      recipient =  self.recipient.getRelativeUrl(),
      sender = self.sender.getRelativeUrl(),
      connector = self.maileva_connector.getRelativeUrl())
      self.tic()
      event = self.maileva_connector.getResourceRelatedValue(portal_type='Maileva Exchange')
      self.assertEqual(event.getValidationState(), 'confirmed')
      self.assertEqual(event.getSourceValue(), self.sender)
      self.assertEqual(event.getDestinationValue(), self.recipient)
      self.assertEqual(event.getFollowUpValue(), self.document)
      self.assertEqual(event.getProperty('request', ''), 'request')
      self.assertEqual(event.getProperty('response', ''), 'response')
      self.tic()

  def test_maileva_xml(self):
    xml = self.maileva_connector.generateRequestXML(self.recipient, self.sender, self.document)
    self.assertEqual(xml, '''<?xml version="1.0" encoding="UTF-8"?>

  <pjs:Campaign xmlns:com="http://www.maileva.fr/CommonSchema" xmlns:pjs="http://www.maileva.fr/MailevaPJSSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:mlv="http://www.maileva.fr/MailevaSpecificSchema" xmlns:spec="http://www.maileva.fr/MailevaSpecificSchema" Version="5.0" Application="connecteur_Maileva">
    <pjs:User AuthType="PLAINTEXT">
      <pjs:Login>test</pjs:Login>
      <pjs:Password>test</pjs:Password>
    </pjs:User>
    <pjs:Requests>
      <pjs:Request MediaType="DIGITAL" TrackId="Bulletindesalaires">
        <pjs:Recipients>
          <pjs:Internal>
            <pjs:Recipient Id="1">
              <com:PaperAddress>
                <com:AddressLines>
                  <com:AddressLine1>MR test_maileva_connector_recipient</com:AddressLine1>
                  <com:AddressLine2>123</com:AddressLine2>
                  <com:AddressLine3>Rue 12</com:AddressLine3>
                  
                  
                  <com:AddressLine6>59000 LILLE</com:AddressLine6>
                </com:AddressLines>
                <com:Country>france</com:Country>
                <com:CountryCode>FR</com:CountryCode>
              </com:PaperAddress>
              <com:DigitalAddress>
                <com:FirstName></com:FirstName>
                <com:LastName></com:LastName>
                <com:Identifier>00000001</com:Identifier>
                <com:JobPosition>default_career</com:JobPosition>
                <com:JobStartDate>2021-12-01</com:JobStartDate>
              </com:DigitalAddress>
            </pjs:Recipient>
          </pjs:Internal>
        </pjs:Recipients>
        <pjs:Senders>
          <pjs:Sender Id="001">
            <com:PaperAddress>
              <com:AddressLines>
                <com:AddressLine1>test_maileva_connector_sender</com:AddressLine1>
                <com:AddressLine2>122</com:AddressLine2>
                <com:AddressLine3>Rue 11</com:AddressLine3>
                
                
                <com:AddressLine6>59000 LILLE CEDEX</com:AddressLine6>
              </com:AddressLines>
              <com:Country>france</com:Country>
              <com:CountryCode>FR</com:CountryCode>
            </com:PaperAddress>
          </pjs:Sender>
        </pjs:Senders>
        <pjs:DocumentData>
          <pjs:Documents>
            <pjs:Document Id="001">
              <com:Content>
                <com:Value></com:Value>
              </com:Content>
            </pjs:Document>
          </pjs:Documents>
        </pjs:DocumentData>
        <pjs:Options>
          <pjs:RequestOption>
            <spec:DigitalOption>
              <spec:FoldOption>
                <spec:DepositTitle>test_maileva_connector_document</spec:DepositTitle>
              </spec:FoldOption>
              <spec:DepositType>PAYSLIP</spec:DepositType>
              <spec:DigitalArchiving>600</spec:DigitalArchiving>
            </spec:DigitalOption>
          </pjs:RequestOption>
        </pjs:Options>
      </pjs:Request>
    </pjs:Requests>
  </pjs:Campaign>
'''
)

  def test_send_state_workflow(self):
    pdf = self.portal.document_module.newContent(portal_type='PDF')
    self.tic()
    self.assertEqual(pdf.getSendState(),'draft')
    self.assertTrue(self.portal.portal_workflow.isTransitionPossible(pdf, 'send'))
    self.assertTrue(self.portal.portal_workflow.isTransitionPossible(pdf, 'fail'))
    self.assertTrue(self.portal.portal_workflow.isTransitionPossible(pdf, 'succeed'))
    pdf.send()
    self.assertEqual(pdf.getSendState(),'sending')
    self.tic()
    self.assertTrue(self.portal.portal_workflow.isTransitionPossible(pdf, 'fail'))
    self.assertTrue(self.portal.portal_workflow.isTransitionPossible(pdf, 'succeed'))
    pdf.fail()
    self.assertEqual(pdf.getSendState(), 'failed')
    self.tic()
    self.assertTrue(self.portal.portal_workflow.isTransitionPossible(pdf, 'succeed'))
    self.assertTrue(self.portal.portal_workflow.isTransitionPossible(pdf, 'send'))
    pdf.succeed()
    self.tic()
    self.assertEqual(pdf.getSendState(), 'success')
