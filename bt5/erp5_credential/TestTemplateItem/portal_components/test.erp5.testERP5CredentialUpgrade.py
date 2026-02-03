##############################################################################
#
# Copyright (c) 2026 Nexedi SA and Contributors. All Rights Reserved.
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
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
from erp5.component.test.testERP5CredentialAlarm import TestERP5CredentialAlarmMixin

class TestCredentialAssignmentRequestMigration(TestERP5CredentialAlarmMixin):

  def test_migration_constraint(self):
    function_category = self.getCustomerFunctionCategoryValue()
    manager_category = self.getManagerFunctionCategoryValue()
    person = self.portal.person_module.newContent(
      portal_type='Person'
    )

    self.tic()
    good_assignment_request = self.portal.assignment_request_module.newContent(
      portal_type='Assignment Request',
      destination_decision_value=person,
      destination_project_value=self.createNewProject(),
      function_value=function_category
    )

    bad_assignment_request = self.portal.assignment_request_module.newContent(
      portal_type='Assignment Request',
      destination_value=person,
      destination_project_value=self.createNewProject(),
      function_value=manager_category
    )
    self.tic()

    self.assertEqual(good_assignment_request.checkConsistency(), [])
    self.assertNotEqual(bad_assignment_request.checkConsistency(), [])
    self.assertEqual(len(bad_assignment_request.checkConsistency()), 1)

    bad_assignment_request.fixConsistency()
    self.assertEqual(bad_assignment_request.checkConsistency(), [])

  def test_alarm_constraint(self):
    function_category = self.getCustomerFunctionCategoryValue()
    manager_category = self.getManagerFunctionCategoryValue()
    person = self.portal.person_module.newContent(
      portal_type='Person'
    )

    self.tic()
    good_assignment_request = self.portal.assignment_request_module.newContent(
      portal_type='Assignment Request',
      destination_decision_value=person,
      destination_project_value=self.createNewProject(),
      function_value=function_category
    )

    bad_assignment_request = self.portal.assignment_request_module.newContent(
      portal_type='Assignment Request',
      destination_value=person,
      destination_project_value=self.createNewProject(),
      function_value=manager_category
    )
    self.tic()

    self.assertEqual(good_assignment_request.checkConsistency(), [])
    self.assertNotEqual(bad_assignment_request.checkConsistency(), [])
    self.assertEqual(len(bad_assignment_request.checkConsistency()), 1)

    self.portal.portal_alarms.AlarmTool_checkAssignmentRequestDestinationDecisionMigrationConsistency(fixit=1)
    self.commit()
    self.assertEqual(1, len([m for m in self.portal.portal_activities.getMessageList()]))
    self.tic()
    self.assertEqual(bad_assignment_request.checkConsistency(), [])

    self.portal.portal_alarms.AlarmTool_checkAssignmentRequestDestinationDecisionMigrationConsistency(fixit=1)
    self.commit()
    self.assertEqual(0, len([m for m in self.portal.portal_activities.getMessageList()]))
    self.tic()
