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

import unittest
import os

from zope.interface.verify import verifyObject 
from DateTime import DateTime

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase


class ShortMessageTestCase(ERP5TypeTestCase):
  pass

class TestShortMessageGateway(ShortMessageTestCase):

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


class TestShortMessageSending(ShortMessageTestCase):
  def beforeTearDown(self):
    self.abort()
    self.tic()
    for module in (
            self.portal.portal_sms,
            self.portal.person_module,
            self.portal.event_module ):
        module.manage_delObjects(list(module.objectIds()))
    self.tic()

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


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestShortMessageGateway))
  suite.addTest(unittest.makeSuite(TestShortMessageSending))
  return suite
