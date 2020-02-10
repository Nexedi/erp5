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

from erp5.component.test.testNotificationTool import TestNotificationTool

class TestCRMNotificationTool(TestNotificationTool):
  """Make sure that notification tool works with crm"""

  def getTitle(self):
    return "Notification Tool With CRM"

  def beforeTearDown(self):
    TestNotificationTool.beforeTearDown(self)
    self.portal.event_module.manage_delObjects(
            list(self.portal.event_module.objectIds()))
    self.tic()

  def test_store_as_event(self):
    # passing store_as_event=True to NotificationTool.sendMessage will store
    # the message in an event
    person = self.portal.person_module.newContent(
        portal_type="Person",
        default_email_text="userA@example.invalid")
    self.tic()
    self.portal.portal_notifications.sendMessage(
                                  store_as_event=True,
                                  recipient=person,
                                  subject='Subject',
                                  message='Message')
    self.tic()
    last_message, = self.portal.MailHost._message_list
    mfrom, mto, messageText = last_message
    self.assertEqual('Portal Administrator <site@example.invalid>', mfrom)
    self.assertEqual(['userA@example.invalid'], mto)

    # check that an event has been created
    event_list = self.portal.event_module.contentValues()
    self.assertEqual(1, len(event_list))

    event = event_list[0]
    self.assertEqual('Mail Message', event.getPortalTypeName())
    self.assertEqual('Subject', event.getTitle())
    self.assertEqual('Message', event.getTextContent())
    self.assertNotEquals(None, event.getStartDate())
    self.assertEqual(person, event.getDestinationValue())
    self.assertEqual('started', event.getSimulationState())

  def test_check_consistency(self):
    # This test only applies when erp5_crm is installed and we have
    # a constraint on mail message
    person_without_email = self.portal.person_module.newContent(
      portal_type="Person",)
    self.tic()
    with self.assertRaises(ValueError) as exception_context:
      self.portal.portal_notifications.sendMessage(
        check_consistency=True,
        recipient=person_without_email,
        subject='Subject',
        message='Message')
    consistency_message_list, = exception_context.exception.args
    consistency_message, = consistency_message_list
    from Products.ERP5Type.ConsistencyMessage import ConsistencyMessage
    self.assertIsInstance(consistency_message, ConsistencyMessage)
    self.assertEqual(
      'Recipients email must be defined',
      str(consistency_message.getTranslatedMessage()))

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestCRMNotificationTool))
  return suite
