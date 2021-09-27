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
    sender = self.portal.portal_catalog.getResultValue(
      portal_type='Organisation',
      reference='test_maileva_connector_sender',
    )
    if not sender:
      sender = self.portal.organisation_module.newContent(
        portal_type='Organisation',
        reference='test_maileva_connector_sender',
        default_address_region='europe/west/france',
        default_address_street_address="122\nRue 11"
      )
    recipient = self.portal.portal_catalog.getResultValue(
      portal_type='Person',
      reference='test_maileva_connector_recipient',
    )
    if not recipient:
      recipient = self.portal.person_module.newContent(
        portal_type='Person',
        reference='test_maileva_connector_recipient',
        default_address_region='europe/west/france',
        default_address_street_address="123\nRue 12"
      )
      recipient.newContent(
        portal_type='Career',
        subordination_value = sender
      ).start()

    document = self.portal.portal_catalog.getResultValue(
      portal_type='PDF',
      reference='test_maileva_connector_document',
    )
    if not document:
      sender = self.portal.document_module.newContent(
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
    self.assertEqual(xml, '\n<?xml version="1.0" encoding="UTF-8"?>\n  <pjs:campaign xmlns:com="http://www.maileva.fr/CommonSchema" xmlns:pjs="http://www.maileva.fr/MailevaPJSSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:mlv="http://www.maileva.fr/MailevaSpecificSchema" xmlns:spec="http://www.maileva.fr/MailevaSpecificSchema">\n    Version="5.0" Application="connecteur_Maileva">\n    <pjs:user authtype="PLAINTEXT">\n      <pjs:login>test</pjs:login>\n      <pjs:password>test</pjs:password>\n    </pjs:user>\n    <pjs:requests>\n      <pjs:request mediatype="DIGITAL" trackid="Bulletindesalaires">\n        <pjs:senders>\n          <pjs:sender id="001">\n            <com:paperaddress>\n              <com:addresslines>\n                <com:addressline1>None</com:addressline1>\n                <com:addressline2>122</com:addressline2>\n                <com:addressline3>Rue 11</com:addressline3>\n                \n                \n                \n              </com:addresslines>\n              <com:country>France</com:country>\n              <com:countrycode>FR</com:countrycode>\n            </com:paperaddress>\n          </pjs:sender>\n        </pjs:senders>\n        <pjs:recipients>\n          <pjs:internal>\n            <pjs:recipient id="1">\n              <com:paperaddress>\n                <com:addresslines>\n                  <com:addressline1>None test_maileva_connector_recipient</com:addressline1>\n                  <com:addressline2>123</com:addressline2>\n                  <com:addressline3>Rue 12</com:addressline3>\n                  \n                  \n                  \n                </com:addresslines>\n                <com:country>France</com:country>\n                <com:countrycode>FR</com:countrycode>\n              </com:paperaddress>\n              <com:digitaladdress>\n                <com:firstname></com:firstname>\n                <com:lastname></com:lastname>\n                <com:identifier></com:identifier>\n                <com:jobposition>default_career</com:jobposition>\n                <com:jobstartdate></com:jobstartdate>\n              </com:digitaladdress>\n            </pjs:recipient>\n          </pjs:internal>\n        </pjs:recipients>\n        <pjs:documentdata>\n          <pjs:documents>\n            <pjs:document id="001">\n              <com:content>\n                <com:value></com:value>\n              </com:content>\n            </pjs:document>\n          </pjs:documents>\n        </pjs:documentdata>\n        <pjs:options>\n          <pjs:requestoption>\n            <mlv:digitaloption>\n              <mlv:foldoption>\n                <mlv:deposittitle>test_maileva_connector_document</mlv:deposittitle>\n              </mlv:foldoption>\n              <mlv:deposittype>PAYSLIP</mlv:deposittype>\n              <mlv:digitalarchiving>600</mlv:digitalarchiving>\n            </mlv:digitaloption>\n          </pjs:requestoption>\n        </pjs:options>\n      </pjs:request>\n    </pjs:requests>\n</pjs:campaign>\n')

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
