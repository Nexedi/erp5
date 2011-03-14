# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

from Products.ERP5Legacy.tests import Legacy_getBusinessTemplateList

test_suite_list = []
from Products.ERP5.tests.testTask import *
test_suite_list.append(test_suite)
from Products.ERP5.tests.testTaskReporting import *
test_suite_list.append(test_suite)
from Products.ERP5.tests.testTaskReportDivergence import *
test_suite_list.append(test_suite)
# testProject breaks testTaskReporting so we run it after
from Products.ERP5.tests.testProject import *
test_suite_list.append(test_suite)

# WARNING: TestProject is tested with rules using 'order' category
TestProject.rule_id_list = 'default_order_rule', 'default_delivery_rule'
TestProject.business_process = None
Legacy_getBusinessTemplateList(TestProject)

TestTaskMixin.business_process = None
Legacy_getBusinessTemplateList(TestTaskMixin)

TestTaskReporting.createBusinessProcess = lambda self: None
Legacy_getBusinessTemplateList(TestTaskReporting)

def stepAcceptDateDecision(self, sequence=None, **kw):
  task_report = sequence.get('task_report')
  # XXX This is not really cool, when we will have nice api, it is required
  # to use it
  self.getPortal().portal_deliveries\
      .task_report_builder.solveDeliveryGroupDivergence(
      task_report.getRelativeUrl(),
      property_dict={'start_date':[self.datetime + 15]})

TestTaskReportDivergenceMixin.stepAcceptDateDecision = stepAcceptDateDecision


def test_suite():
  suite = test_suite_list[0]()
  for test_suite in test_suite_list[1:]:
    suite.addTests(test_suite())
  return suite
