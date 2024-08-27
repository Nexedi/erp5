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
from lxml import etree
import os.path
import Products.ERP5.tests



# For mock
class dotdict(dict):
  """dot.notation access to dictionary attributes"""
  __getattr__ = dict.get
  __setattr__ = dict.__setitem__
  __delattr__ = dict.__delitem__

class ServiceWithSuccess:
  get_notification_detail = False
  def submit(self, **kw):
    return 'success'
  def checkPendingNotifications(self, notification_type):
    # if already get, no longer available in list
    if ServiceWithSuccess.get_notification_detail:
      return []
    return [dotdict({
      'id': 192625,
      'reqId': 579400,
      'reqTrackId': 'test_tracking_id',
      'depositId': '2520180000X',
      'depositTrackId': '070ca402c5aa45e1bc06a513451ad76b'
    })]
  def getPendingNotificationDetails(self, track_id):
    # first time is always PENDING
    if ServiceWithSuccess.get_notification_detail:
      status = 'SENT'
    else:
      ServiceWithSuccess.get_notification_detail = True
      status = 'PENDING'

    return dotdict({
      'id': 192625,
      'status': status,
      'notificationStatus': 'ACCEPT',
      'notificationType': 'GENERAL'
    })

class ClientWithSuccess:
  def __init__(self):
    self.service = ServiceWithSuccess()

def submitRequestWithSuccess(**kw):
  return ClientWithSuccess()




class ServiceWithFailure:
  get_notification_detail = False
  def submit(self, **kw):
    return 'success'
  def checkPendingNotifications(self, notification_type):
    if ServiceWithFailure.get_notification_detail:
      return []
    return [dotdict({
      'id': 192625,
      'reqId': 579400,
      'reqTrackId': 'test_tracking_id',
      'depositId': '2520180000X',
      'depositTrackId': '070ca402c5aa45e1bc06a513451ad76b'
    })]
  def getPendingNotificationDetails(self, track_id):
    if ServiceWithFailure.get_notification_detail:
      status = 'SENT'
    else:
      ServiceWithFailure.get_notification_detail = True
      status = 'PENDING'
    return dotdict({
      'id': 192625,
      'status': status,
      'notificationStatus': 'NACCEPT',
      'notificationType': 'GENERAL'
    })

class ClientWithFailure:
  def __init__(self):
    self.service = ServiceWithFailure()

def submitRequestWithFailure(**kw):
  return ClientWithFailure()





class ServiceWithException:
  def submit(self, **kw):
    raise RuntimeError('exception')

class ClientWithException:
  def __init__(self):
    self.service = ServiceWithException()

def submitRequestWithException(**kw):
  return ClientWithException()


class testMailevaSOAPConnector(ERP5TypeTestCase):

  def afterSetUp(self):
    maileva_connector = self.portal.portal_catalog.getResultValue(
      portal_type='Maileva SOAP Connector',
      reference='maileva_soap_connector',
      validation_state='validated')

    if not maileva_connector:
      maileva_connector = self.portal.portal_web_services.newContent(
        portal_type='Maileva SOAP Connector',
        user_id='test',
        password='test',
        submit_url_string='mysubmit',
        tracking_url_string='mytracking',
        reference='maileva_soap_connector')
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
        first_name='first',
        last_name='last',
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


    document = self.portal.document_module.newContent(portal_type='PDF')

    self.maileva_connector = maileva_connector
    self.sender = sender
    self.recipient = recipient
    self.document = document
    # Reset class varaible to simulate properly web service behavior
    ServiceWithSuccess.get_notification_detail = False
    ServiceWithFailure.get_notification_detail = False
    self.tic()

  def getTitle(self):
    return "Test Maileva SOAP Connector"

  def test_send_pdf_to_maileva_with_success(self):
    self.portal.system_event_module.manage_delObjects([x.getId() for x in self.portal.system_event_module.objectValues(portal_type='Maileva Exchange')])
    self.tic()
    with mock.patch(
      'suds.client.Client',
      side_effect=submitRequestWithSuccess,
    ):
      self.document.PDF_sendToMaileva(
      recipient =  self.recipient,
      sender = self.sender)
      self.tic()
      event = self.maileva_connector.getResourceRelatedValue(portal_type='Maileva Exchange')
      self.assertEqual(event.getValidationState(), 'confirmed')
      self.assertEqual(event.getSourceValue(), self.sender)
      self.assertEqual(event.getDestinationValue(), self.recipient)
      self.assertEqual(event.getFollowUpValue(), self.document)
      self.assertEqual(self.document.getSendState(), 'sending')
      self.assertNotEqual(event.getRequest(), None)
      self.assertEqual(event.getResponse(), 'success')
      self.tic()
      # check response
      event.setReference('test_tracking_id')
      self.portal.portal_alarms.check_maileva_document_status.activeSense()
      self.tic()
      self.assertEqual(getattr(event, 'track_id', ""), 192625)
      self.assertEqual(event.getValidationState(), 'confirmed')
      self.assertEqual(self.document.getSendState(), 'sending')
      self.assertIn('PENDING', event.getProperty('response_detail', ''))

      self.portal.portal_alarms.check_maileva_document_status.activeSense()
      self.tic()
      self.assertEqual(getattr(event, 'track_id', ""), 192625)
      self.assertEqual(event.getValidationState(), 'acknowledged')
      self.assertEqual(self.document.getSendState(), 'success')
      self.assertIn('SENT', event.getProperty('response_detail', ''))

  def test_send_pdf_to_maileva_with_failure(self):
    self.portal.system_event_module.manage_delObjects([x.getId() for x in self.portal.system_event_module.objectValues(portal_type='Maileva Exchange')])
    self.tic()
    with mock.patch(
      'suds.client.Client',
      side_effect=submitRequestWithFailure,
    ):
      self.document.PDF_sendToMaileva(
      recipient =  self.recipient,
      sender = self.sender)
      self.tic()
      event = self.maileva_connector.getResourceRelatedValue(portal_type='Maileva Exchange')
      self.assertEqual(event.getValidationState(), 'confirmed')
      self.assertEqual(event.getSourceValue(), self.sender)
      self.assertEqual(event.getDestinationValue(), self.recipient)
      self.assertEqual(event.getFollowUpValue(), self.document)
      self.assertEqual(self.document.getSendState(), 'sending')
      self.assertNotEqual(event.getRequest(), None)
      self.assertEqual(event.getResponse(), 'success')
      self.tic()
      # check response
      event.setReference('test_tracking_id')
      self.portal.portal_alarms.check_maileva_document_status.activeSense()
      self.tic()
      self.assertEqual(getattr(event, 'track_id', ""), 192625)
      self.assertEqual(event.getValidationState(), 'confirmed')
      self.assertEqual(self.document.getSendState(), 'sending')
      self.assertIn('PENDING', event.getProperty('response_detail', ''))

      self.portal.portal_alarms.check_maileva_document_status.activeSense()
      self.tic()
      self.assertEqual(getattr(event, 'track_id', ""), 192625)
      self.assertEqual(event.getValidationState(), 'acknowledged')
      self.assertEqual(self.document.getSendState(), 'failed')
      self.assertIn('SENT', event.getProperty('response_detail', ''))
      self.assertIn('NACCEPT', event.getProperty('response_detail', ''))


  def test_failed_to_submit_to_maileva(self):
    self.portal.system_event_module.manage_delObjects([x.getId() for x in self.portal.system_event_module.objectValues(portal_type='Maileva Exchange')])
    self.tic()
    with mock.patch(
      'suds.client.Client',
      side_effect=submitRequestWithException,
    ):
      self.document.PDF_sendToMaileva(
      recipient =  self.recipient,
      sender = self.sender)
      self.tic()
      event = self.maileva_connector.getResourceRelatedValue(portal_type='Maileva Exchange')
      self.assertEqual(event.getValidationState(), 'acknowledged')
      self.assertEqual(event.getSourceValue(), self.sender)
      self.assertEqual(event.getDestinationValue(), self.recipient)
      self.assertEqual(event.getFollowUpValue(), self.document)
      self.assertEqual(self.document.getSendState(), 'failed')
      self.assertNotEqual(event.getRequest(), None)
      self.assertIn('exception', event.getResponse())
      self.tic()

  def test_maileva_xml(self):
    xml = self.maileva_connector.generateRequestXML(self.recipient, self.sender, self.document, 'test_track_id')
    self.assertEqual(etree.tostring(etree.fromstring(xml)), etree.tostring(etree.fromstring('''  <SOAP-ENV:Envelope xmlns:ns0="http://connector.services.siclv2.maileva.fr/" xmlns:ns1="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:com="http://www.maileva.fr/CommonSchema" xmlns:pjs="http://www.maileva.fr/MailevaPJSSchema" xmlns:spec="http://www.maileva.fr/MailevaSpecificSchema">
  <SOAP-ENV:Header/>
   <SOAP-ENV:Body>
      <ns0:submit>
        <campaign Version="5.0" Application="connecteur_Maileva">
          <pjs:Requests>
            <pjs:Request MediaType="DIGITAL" TrackId="test_track_id">
              <pjs:Recipients>
                <pjs:Internal>
                  <pjs:Recipient Id="1">
                    <com:PaperAddress>
                      <com:AddressLines>
                        <com:AddressLine1>MR first last</com:AddressLine1>
                        <com:AddressLine2>123</com:AddressLine2>
                        <com:AddressLine3>Rue 12</com:AddressLine3>
                        <com:AddressLine6>59000 LILLE</com:AddressLine6>
                      </com:AddressLines>
                      <com:Country>france</com:Country>
                      <com:CountryCode>FR</com:CountryCode>
                    </com:PaperAddress>
                    <com:DigitalAddress>
                      <com:FirstName>first</com:FirstName>
                      <com:LastName>last</com:LastName>
                      <com:Identifier>00000001</com:Identifier>
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
                    <com:MergeFields>
                      <com:MergeField>
                        <com:PageNumber>1</com:PageNumber>
                        <com:FontName>Arial</com:FontName>
                        <com:FontSize>12</com:FontSize>
                        <com:FontColor>#000000</com:FontColor>
                        <com:FontBold>false</com:FontBold>
                        <com:FontItalic>false</com:FontItalic>
                        <com:FontUnderline>false</com:FontUnderline>
                        <com:PosUnit>CM</com:PosUnit>
                        <com:PosX>12.0</com:PosX>
                        <com:PosY>7.0</com:PosY>
                        <com:Content>
                          <com:Automatic>DIGITAL_SECURITY_CODE</com:Automatic>
                        </com:Content>
                        <com:Orientation>0</com:Orientation>
                        <com:Halign>CENTER</com:Halign>
                      </com:MergeField>
                    </com:MergeFields>
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
                      <spec:PostageClass>ECOPLI_GRAND_COMPTE</spec:PostageClass>
                      <spec:DepositTitle>%s</spec:DepositTitle>
                      <spec:DepositDescription>%s</spec:DepositDescription>
                      <spec:UseFlyLeaf>true</spec:UseFlyLeaf>
                    </spec:FoldOption>
                    <spec:DepositType>PAYSLIP</spec:DepositType>
                    <spec:DigitalArchiving>600</spec:DigitalArchiving>
                  </spec:DigitalOption>
                </pjs:RequestOption>
              </pjs:Options>
              <pjs:Notifications>
                <pjs:Notification Type="GENERAL">
                 <spec:Format>XML</spec:Format>
                  <spec:Protocols>
                    <spec:Protocol>
                      <spec:Ws/>
                    </spec:Protocol>
                  </spec:Protocols>
                </pjs:Notification>
              </pjs:Notifications>
            </pjs:Request>
          </pjs:Requests>
        </campaign>
     </ns0:submit>
    </SOAP-ENV:Body>
  </SOAP-ENV:Envelope>
''' %  (self.document.getTitle(),  self.document.getTitle())))
)

  def test_maileva_request_validation(self):
    xml = self.maileva_connector.generateRequestXML(self.recipient, self.sender, self.document, 'test_track_id', 'maileva_connection_for_test')
    # lxml doesn't support https in schemaLocation, download locally
    with open(os.path.join(os.path.dirname(Products.ERP5.tests.__file__), 'test_data', "MailevaPJSSchema.xsd")) as f:
      xsd = etree.parse(f)
    schema_validator = etree.XMLSchema(xsd)
    schema_validator.assertValid(etree.fromstring(xml))

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
