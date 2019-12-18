##############################################################################
#
# Copyright (c) 2002-2016 Nexedi SA and Contributors. All Rights Reserved.
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

from test import pystone
from time import time
pystone.clock = time
from Products.ERP5Type.tests.testPerformance import TestPerformanceMixin
from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Testing import ZopeTestCase

class TestWorkflowPerformance(TestPerformanceMixin):

  maxDiff = None

  def getTitle(self):
    return "Workflow Performance"

  def afterSetUp(self):
    super(TestWorkflowPerformance, self).afterSetUp()
    self.foo_module.manage_delObjects(list(self.foo_module.objectIds()))

  def testWorkflowActionAndGetState(self):

    foo_list = []
    foo_list_append = foo_list.append
    range_10 = range(10)
    portal_workflow = self.portal.portal_workflow
    foo_count = 100

    for x in xrange(foo_count):
      foo = self.foo_module.newContent()
      foo_list_append(foo)

    self.assertEqual('draft', foo_list[0].getSimulationState())

    start = time()
    for foo in foo_list:
      foo.getSimulationState()
      action_list = portal_workflow.listActions(object=foo)
      for x in range_10:
        try:
          portal_workflow.doActionFor(foo, 'dummy_failing_action')
        except ValidationFailed:
          pass
        portal_workflow.doActionFor(foo, 'dummy_action')
      portal_workflow.doActionFor(foo, 'validate_action')
      foo.getSimulationState()

    end = time()

    print "\n%s pystones/second" % pystone.pystones()[1]
    message = "\n%s took %.4gs (%s foo(s))" % (self._testMethodName,
                                             end - start, foo_count)
    print message
    ZopeTestCase._print(message)

    # some checking to make sure we tested something relevant
    self.assertEqual('validated', foo.getSimulationState())
    expected_action_id_list = ['custom_action_no_dialog', 'custom_dialog_action',
                               'custom_dialog_required_action',
                               'display_status_action', 'dummy_action',
                               'dummy_crashing_action',
                               'dummy_failing_action', 'validate_action']
    expected_action_id_list.sort()
    found_action_id_list = [x['id'] for x in action_list if x['category'] == 'workflow']
    found_action_id_list.sort()
    self.assertEqual(expected_action_id_list, found_action_id_list)
    self.assertEqual(23, len(foo.Base_getWorkflowHistoryItemList('foo_workflow', display=0)))
