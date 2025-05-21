# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2018 Nexedi SA and Contributors. All Rights Reserved.
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

import responses

from zope.interface.verify import verifyObject

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase


class TestShortMessageGatewayInterface(ERP5TypeTestCase):

  def _verifyGatewayPortalType(self, portal_type):
    gateway = self.portal.portal_sms.newContent(portal_type=portal_type)
    from erp5.component.interface.ISmsSendingGateway import ISmsSendingGateway
    verifyObject(ISmsSendingGateway, gateway)
    from erp5.component.interface.ISmsReceivingGateway import ISmsReceivingGateway
    verifyObject(ISmsReceivingGateway, gateway)


  def test_EssendexGateway(self):
    self._verifyGatewayPortalType('Essendex Gateway')

  def test_MobytGateway(self):
    self._verifyGatewayPortalType('Mobyt Gateway')

  def test_DummyGateway(self):
    self._verifyGatewayPortalType('Dummy Gateway')


class ShortMessageTestCase(ERP5TypeTestCase):
  def beforeTearDown(self):
    self.abort()
    self.tic()
    for module in (
            self.portal.portal_sms,
            self.portal.person_module,
            self.portal.event_module ):
      module.manage_delObjects(list(module.objectIds()))
    self.tic()


class TestDummyGatewayShortMessageSending(ShortMessageTestCase):
  def test_ShortMessage_start(self):
    gateway = self.portal.portal_sms.newContent(
      reference='default',
      portal_type='Mobyt Gateway',
    )
    self.tic()
    sender = self.portal.person_module.newContent(
        portal_type='Person',
        default_mobile_telephone_telephone_number='1234')
    recipient = self.portal.person_module.newContent(
        portal_type='Person',
        default_mobile_telephone_telephone_number='5678')
    short_message = self.portal.event_module.newContent(
        portal_type="Short Message",
        source_value=sender,
        destination_value=recipient,
        text_content='Hello')
    short_message.start()

    with responses.RequestsMock() as rsps:
      rsps.add(
        responses.POST,
        "https://multilevel.mobyt.fr/sms/send.php",
        content_type="text/plain;charset=utf-8",
        body="OK 1AC2415293544A8EB11EE028EDA52CB3",
      )
      self.tic()

    self.assertEqual(short_message.getDestinationReference(), '1AC2415293544A8EB11EE028EDA52CB3')
    self.assertEqual(gateway, short_message.getGatewayValue())

    with responses.RequestsMock() as rsps:
      rsps.add(
        responses.POST,
        "https://multilevel.mobyt.fr/sms/send.php",
        content_type="text/plain;charset=utf-8",
        body="KO  impossible créer un queue du message",
      )
      with self.assertRaisesRegexp(Exception, "^impossible créer un queue du message$"):
        self.portal.portal_sms.send(
          text='error',
          sender=sender.getRelativeUrl(),
          recipient=recipient.getRelativeUrl(),
          document_relative_url=short_message.getRelativeUrl()
        )

    with responses.RequestsMock() as rsps:
      rsps.add(
        responses.POST,
        "https://multilevel.mobyt.fr/sms/batch-status.php",
        content_type="text/plain;charset=utf-8",
        body=(
          "id,timestamp,dest,status,status_text,request_id\n"
          "3c815709-06bd-4bf4-b4ac-09c0ca73d410,2025-05-20 03:28:36,+817041064410,200,Delivered,1AC2415293544A8EB11EE028EDA52CB3"
        ),
      )
      status = gateway.getMessageStatus('1AC2415293544A8EB11EE028EDA52CB3')
    self.assertEqual(status, 'delivered')


class TestMobytShortMessageSending(ShortMessageTestCase):
  def test_ShortMessage_start(self):
    gateway = self.portal.portal_sms.newContent(
      reference='default',
      portal_type='Dummy Gateway')
    self.tic()
    sender = self.portal.person_module.newContent(
        portal_type='Person',
        default_mobile_telephone_telephone_number='1234')
    recipient = self.portal.person_module.newContent(
        portal_type='Person',
        default_mobile_telephone_telephone_number='5678')
    short_message = self.portal.event_module.newContent(
        portal_type="Short Message",
        source_value=sender,
        destination_value=recipient,
        text_content='Hello')
    short_message.start()
    self.tic()

    # sending message should have updated the document with message id and gateway
    self.assertTrue(short_message.getDestinationReference())
    self.assertEqual(gateway, short_message.getGatewayValue())
