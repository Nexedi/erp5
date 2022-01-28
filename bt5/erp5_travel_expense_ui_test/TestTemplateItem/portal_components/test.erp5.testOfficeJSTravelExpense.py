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
from DateTime import DateTime

class TestOfficeJSTravelExpense(ERP5TypeTestCase):
  def afterSetUp(self):
    for rule in self.getPortalObject().portal_rules.contentValues():
      if rule.getValidationState() == 'draft':
        rule.validate()
    self.tic()

  def test_create_expense_request_from_record(self):
    """
    """
    now = DateTime()
    date = "%s" % now.Date().replace('/','-')
    quantity = 3.14
    resource = "currency_module/CNY"
    resource_title = "Money"
    comment="New Work is Comming %s" % now
    latitude = 121012012
    longitude = 121012012.30
    record = self.portal.expense_record_module.newContent(
      date=date,
      quantity=quantity,
      resource=resource,
      resource_title=resource_title,
      comment=comment,
      source_reference = '%s' % now,
      source='person_module/hr_user',
      latitude=latitude,
      longitude=longitude,
      )
    record.setTitle("Test Expense Record %s" % now)
    self.tic()
    self.portal.portal_alarms.alarm_process_draft_record_list.activeSense()
    self.tic()
    self.assertTrue(record.getSimulationState(), "delivered")
    ticket = record.getFollowUpValue()
    new_record = self.portal.portal_catalog.getResultValue(
      portal_type="Expense Record",
      strict_follow_up_uid=record.getFollowUpUid(),
      simulation_state="stopped"
      )
    self.assertIsNotNone(new_record)
    self.assertEqual(
      record.getDestinationReference(),
      ticket.getReference()
    )
    self.assertEqual(quantity,ticket.getPrice())
    self.assertEqual(DateTime(date),ticket.getStartDate())
    self.assertEqual(resource,ticket.getPriceCurrency())
    self.assertEqual(comment,ticket.getDescription())
    self.assertEqual(longitude,ticket.getLongitude())
    self.assertEqual(latitude,ticket.getLatitude())

    self.assertEqual(
      record.getDestinationReference(),
      new_record.getDestinationReference()
    )

  def test_accept_expense_record_create_purchase_invoice_transaction(self):
    """
    """
    now = DateTime()
    date = "%s" % now.Date().replace('/','-')
    quantity = 3.14
    resource = "currency_module/CNY"
    resource_title = "Money"
    comment="New Work is Comming %s" % now
    latitude = 121012012
    longitude = 121012012.30
    record = self.portal.expense_record_module.newContent(
      date=date,
      quantity=quantity,
      resource=resource,
      resource_title=resource_title,
      source_reference = '%s' % now,
      source='person_module/hr_user',
      comment=comment,
      latitude=latitude,
      longitude=longitude,
      )

    record.setTitle("Test Expense Record %s" % now)
    self.tic()
    self.portal.portal_alarms.alarm_process_draft_record_list.activeSense()
    self.tic()
    ticket = record.getFollowUpValue()
    ticket.accept()
    self.tic()
    purchase_invoice_transaction = self.portal.portal_catalog.getResultValue(
      portal_type="Purchase Invoice Transaction",
      strict_causality_uid=ticket.getUid(),
      )
    self.assertIsNotNone(purchase_invoice_transaction)
    self.assertEqual(ticket.getDestinationDecision(), purchase_invoice_transaction.getSourceSection())
    self.assertEqual(ticket.getSourceProject(),purchase_invoice_transaction.getSourceProject())
    self.assertEqual(ticket.getSourceSection(),purchase_invoice_transaction.getDestinationSection(),)
    self.assertEqual(ticket.getPriceCurrency(),purchase_invoice_transaction.getResource())
    self.assertEqual(ticket.getStartDate(),purchase_invoice_transaction.getStartDate())
    self.assertEqual("confirmed",purchase_invoice_transaction.getSimulationState())
    line_list = purchase_invoice_transaction.objectValues(portal_type="Purchase Invoice Transaction Line")
    self.assertEqual(2, len(line_list))

  def test_change_expense_record_create_new_record(self):
    """
    """
    now = DateTime()
    date = "%s" % now.Date().replace('/','-')
    quantity = 3.14
    resource = "currency_module/CNY"
    resource_title = "Money"
    comment="New Work is Comming %s" % now
    latitude = 121012012
    longitude = 121012012.30
    record = self.portal.expense_record_module.newContent(
      date=date,
      quantity=quantity,
      resource=resource,
      resource_title=resource_title,
      comment=comment,
      source_reference = '%s' % now,
      source='person_module/hr_user',
      latitude=latitude,
      longitude=longitude,
      )

    record.setTitle("Test Expense Record %s" % now)
    self.tic()
    self.portal.portal_alarms.alarm_process_draft_record_list.activeSense()
    self.tic()
    ticket = record.getFollowUpValue()
    ticket.accept()
    self.portal.portal_alarms.create_representative_record_for_expense_validation_request()
    self.tic()
    expense_record_list = ticket.getFollowUpRelatedValueList(portal_type='Expense Record')
    self.assertEqual(len(expense_record_list), 3)
    self.assertEqual(1, len(self.portal.portal_catalog(
      portal_type="Expense Record",
      strict_follow_up_uid=ticket.getUid(),
      simulation_state="stopped"
    )))
    self.assertEqual(2, len(self.portal.portal_catalog(
      portal_type="Expense Record",
      strict_follow_up_uid=ticket.getUid(),
      simulation_state="delivered"
    )))

  def test_create_leave_request_from_record(self):
    """
    """
    now = DateTime()
    record = self.portal.record_module.newContent(
      portal_type = "Leave Request Record",
      resource = 'service_module/hr_test_need_to_sync',
      start_date =  now.Date(),
      stop_date = now.Date(),
      source_reference = "%s" % now,
      source='person_module/hr_user',
      title = "Test Leave Record %s" % now
    )
    self.tic()
    self.portal.portal_alarms.alarm_process_draft_record_list.activeSense()
    self.tic()
    self.assertTrue(record.getSimulationState(), "delivered")
    ticket = record.getFollowUpValue()
    new_record = self.portal.portal_catalog.getResultValue(
      portal_type="Leave Request Record",
      strict_follow_up_uid=record.getFollowUpUid(),
      simulation_state="stopped"
    )
    self.assertIsNotNone(new_record)
    self.assertEqual(record.getSource(), ticket.getDestination())
    self.assertEqual(record.getResource(), ticket.getResource())
    self.assertEqual(record.getStartDate(), ticket.getStartDate())
    self.assertEqual(record.getStopDate().latestTime(), ticket.getStopDate())

  def test_change_leave_request_create_record(self):
    """
    """
    now = DateTime()
    record = self.portal.record_module.newContent(
      portal_type = "Leave Request Record",
      resource = 'service_module/hr_test_need_to_sync',
      start_date =  now.Date(),
      stop_date = now.Date(),
      source_reference = "%s" % now,
      source='person_module/hr_user',
      title = "Test Leave Record %s" % now
    )
    self.tic()
    self.portal.portal_alarms.alarm_process_draft_record_list.activeSense()
    self.tic()
    self.assertTrue(record.getSimulationState(), "delivered")
    ticket = record.getFollowUpValue()
    ticket.confirm()
    self.tic()
    self.portal.portal_alarms.create_representative_record_for_leave_request()
    self.tic()
    record_list = ticket.getFollowUpRelatedValueList(portal_type='Leave Request Record')
    self.assertEqual(len(record_list), 3)
    self.assertEqual(1, len(self.portal.portal_catalog(
      portal_type="Leave Request Record",
      strict_follow_up_uid=ticket.getUid(),
      simulation_state="stopped"
    )))
    self.assertEqual(2, len(self.portal.portal_catalog(
      portal_type="Leave Request Record",
      strict_follow_up_uid=ticket.getUid(),
      simulation_state="delivered"
    )))

  def test_create_travel_request_from_record(self):
    """
    """
    now = DateTime()
    record = self.portal.record_module.newContent(
      portal_type = "Travel Request Record",
      start_date =  now.Date(),
      stop_date = now.Date(),
      source_reference = "%s" % now,
      source='person_module/hr_user',
      title = "Test Leave Record %s" % now
    )
    self.tic()
    self.portal.portal_alarms.alarm_process_draft_record_list.activeSense()
    self.tic()
    self.assertTrue(record.getSimulationState(), "delivered")
    ticket = record.getFollowUpValue()
    new_record = self.portal.portal_catalog.getResultValue(
      portal_type="Travel Request Record",
      strict_follow_up_uid=record.getFollowUpUid(),
      simulation_state="stopped"
    )
    self.assertIsNotNone(new_record)
    self.assertEqual(record.getSource(), ticket.getDestinationDecision())
    self.assertEqual(record.getStartDate(), ticket.getStartDate())
    self.assertEqual(record.getStopDate(), ticket.getStopDate())

  def test_change_travel_request_create_record(self):
    """
    """
    now = DateTime()
    record = self.portal.record_module.newContent(
      portal_type = "Travel Request Record",
      start_date =  now.Date(),
      stop_date = now.Date(),
      source_reference = "%s" % now,
      source='person_module/hr_user',
      title = "Test Travel Request Record %s" % now
    )
    self.tic()
    self.portal.portal_alarms.alarm_process_draft_record_list.activeSense()
    self.tic()
    ticket = record.getFollowUpValue()
    ticket.accept()
    self.tic()
    self.portal.portal_alarms.create_representative_record_for_travel_request.activeSense()
    self.tic()
    record_list = ticket.getFollowUpRelatedValueList(portal_type='Travel Request Record')
    self.assertEqual(len(record_list), 3)
    self.assertEqual(1, len(self.portal.portal_catalog(
      portal_type="Travel Request Record",
      strict_follow_up_uid=ticket.getUid(),
      simulation_state="stopped"
    )))
    self.assertEqual(2, len(self.portal.portal_catalog(
      portal_type="Travel Request Record",
      strict_follow_up_uid=ticket.getUid(),
      simulation_state="delivered"
    )))

