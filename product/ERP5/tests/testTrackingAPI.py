##############################################################################
#
# Copyright (c) 2004 Nexedi SARL and Contributors. All Rights Reserved.
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

"""Unit Tests for Tracking API.

"""

import os
import unittest

from DateTime import DateTime

from Products.ERP5.tests.testInventoryAPI import InventoryAPITestCase


class TestTrackingList(InventoryAPITestCase):
  """Tests Item Tracking
  """
  def testNodeUid(self):
    getTrackingList = self.getSimulationTool().getTrackingList
    start_date = DateTime()
    def makeMovement(aggregate=None):
      self._makeMovement(quantity=1, price=1,
                         aggregate_value=aggregate,
                         resource_value=self.resource,
                         start_date = start_date,
                         source_value=self.other_node,
                         destination_value=self.node)
    item_uid = self.item.getUid()
    other_item_uid = self.other_item.getUid()
    node_uid = self.node.getUid()
    self.assertEqual(len(getTrackingList(node_uid=node_uid,
                             at_date=start_date)),0)
    makeMovement(aggregate=self.item)
    result = getTrackingList(node_uid=node_uid,at_date=start_date)
    self.assertEqual(len(result),1)
    self.failIfDifferentSet([x.uid for x in result], [item_uid])
    makeMovement(aggregate=self.other_item)
    result = getTrackingList(node_uid=node_uid,at_date=start_date)
    self.assertEqual(len(result),2)
    self.failIfDifferentSet([x.uid for x in result], [item_uid, other_item_uid])

  def testSeveralAggregateOnMovement(self):
    getTrackingList = self.getSimulationTool().getTrackingList
    start_date = DateTime()
    def makeMovement(aggregate_list=None):
      self._makeMovement(quantity=1, price=1,
                         aggregate_list=aggregate_list,
                         resource_value=self.resource,
                         start_date = start_date,
                         source_value=self.other_node,
                         destination_value=self.node)
    item_uid = self.item.getUid()
    other_item_uid = self.other_item.getUid()
    node_uid = self.node.getUid()
    self.assertEqual(len(getTrackingList(node_uid=node_uid,
                             at_date=start_date)),0)
    makeMovement(aggregate_list=[self.item.getRelativeUrl(),
                                 self.other_item.getRelativeUrl()])
    result = getTrackingList(node_uid=node_uid,at_date=start_date)
    self.assertEqual(len(result),2)
    self.failIfDifferentSet([x.uid for x in result], [item_uid, other_item_uid])

  def testDates(self):
    """
      Test different dates parameters of getTrackingList.
    """
    getTrackingList = self.getSimulationTool().getTrackingList
    now = DateTime()
    node_1 = self._makeOrganisation(title='Node 1')
    node_2 = self._makeOrganisation(title='Node 2')
    date_0 = now - 4 # Before first movement
    date_1 = now - 3 # First movement
    date_2 = now - 2 # Between both movements
    date_3 = now - 1 # Second movement
    date_4 = now     # After last movement
    self._makeMovement(quantity=1, price=1,
                       aggregate_value=self.item,
                       resource_value=self.resource,
                       start_date=date_1,
                       source_value=None,
                       destination_value=node_1)
    self._makeMovement(quantity=1, price=1,
                       aggregate_value=self.item,
                       resource_value=self.resource,
                       start_date=date_3,
                       source_value=node_1,
                       destination_value=node_2)
    node_1_uid = node_1.getUid()
    node_2_uid = node_2.getUid()
    date_location_dict = {
      date_0: {'at_date': None,       'to_date': None},
      date_1: {'at_date': node_1_uid, 'to_date': None},
      date_2: {'at_date': node_1_uid, 'to_date': node_1_uid},
      date_3: {'at_date': node_2_uid, 'to_date': node_1_uid},
      date_4: {'at_date': node_2_uid, 'to_date': node_2_uid}
    }
    node_uid_to_node_number = {
      node_1_uid: 1,
      node_2_uid: 2
    }
    for date, location_dict in date_location_dict.iteritems():
      for param_id, location_uid in location_dict.iteritems():
        param_dict = {param_id: date}
        uid_list = [x.node_uid for x in getTrackingList(
                            aggregate_uid=self.item.getUid(), **param_dict)]
        if location_uid is None:
          self.assertEqual(len(uid_list), 0)
        else:
          self.assertEqual(len(uid_list), 1)
          self.assertEqual(uid_list[0], location_uid,
                           '%s=now - %i, aggregate should be at node %i but is at node %i' % \
                           (param_id, now - date, node_uid_to_node_number[location_uid], node_uid_to_node_number[uid_list[0]]))

  def testFutureTrackingList(self):
    movement = self._makeMovement(quantity=1, aggregate_value=self.item,)
    getFutureTrackingList = self.portal.portal_simulation.getFutureTrackingList
    node_uid = self.node.getUid()

    for state in ('planned', 'ordered', 'confirmed', 'ready', 'started',
                  'stopped', 'delivered'):
      movement.simulation_state = state
      movement.reindexObject()
      self.tic()
      tracking_node_uid_list = [brain.node_uid for brain in
        getFutureTrackingList(item=self.item.getRelativeUrl())]
      self.assertEqual([node_uid], tracking_node_uid_list,
        "%s != %s (state:%s)" % ([node_uid], tracking_node_uid_list, state))

    for state in ('draft', 'cancelled', 'deleted'):
      movement.simulation_state = state
      movement.reindexObject()
      self.tic()
      tracking_node_uid_list = [brain.node_uid for brain in
        getFutureTrackingList(item=self.item.getRelativeUrl())]
      self.assertEqual([], tracking_node_uid_list,
        "%s != %s (state:%s)" % ([], tracking_node_uid_list, state))

  def _createScenarioToTestTrackingListMethod(self,
    state_a="delivered", state_b="delivered", state_c="delivered"):
    """
      Scenario:
        Item 1 => A -> B -> C
        Item 2 => A -> B
    """
    now = DateTime()
    item_a = self.getItemModule().newContent(title="Item 1")
    item_b = self.getItemModule().newContent(title="Item 2")
    node_a = self._makeOrganisation(title='Node A')
    node_b = self._makeOrganisation(title='Node B')
    node_c = self._makeOrganisation(title='Node C')
    movement_a = self._makeMovement(source_value=node_a,
      destination_value=node_b, resource=self.resource,
      quantity=1, aggregate_value=item_a, start_date=now,
      simulation_state=state_a)
    movement_b = self._makeMovement(source_value=node_b,
      destination_value=node_c, resource=self.resource,
      quantity=1, aggregate_value=item_a, start_date=now+1,
      simulation_state=state_b)
    movement_c = self._makeMovement(source_value=node_a,
      destination_value=node_b, resource=self.resource,
      quantity=1, aggregate_value=item_b, start_date=now+1,
      simulation_state=state_c)
    self.tic()
    return {"item_a": item_a, "item_b": item_b,
      "node_a": node_a, "node_b": node_b,
      "movement_a": movement_a, "movement_b": movement_b,
      "movement_c": movement_c}

  def testTrackingListWithOutputParameter(self):
    """
      Add test to check if getTrackingList with output=1, returns only Item 2
      if you search for items in B
    """
    data_dict = self._createScenarioToTestTrackingListMethod()
    item_a = data_dict['item_a']
    item_b = data_dict['item_b']
    node_b = data_dict['node_b']

    getTrackingList = self.portal.portal_simulation.getTrackingList
    path_list = [i.path for i in getTrackingList(
      node_uid=node_b.getUid())]
    self.assertTrue(item_a.getPath() in path_list,
      "Is expected %s in B" % item_a.getPath())
    self.assertTrue(item_b.getPath() in path_list,
      "Is expected %s in B" % item_b.getPath())

    path_list = [i.path for i in getTrackingList(
      node_uid=node_b.getUid(), output=1)]
    self.assertTrue(item_a.getPath() not in path_list,
      "%s should not be in B" % item_a.getTitle())
    self.assertTrue(item_b.getPath() in path_list,
      "%s should be in B" % item_b.getTitle())

  def testCurrentTrackingListWithOutputParameter(self):
    """
      Add test to check if getCurrentTrackingList with B -> C started and not delivered,
      returns only Item 2 if you search for items in B
    """
    data_dict = self._createScenarioToTestTrackingListMethod(state_b="started")
    item_a = data_dict['item_a']
    item_b = data_dict['item_b']
    node_b = data_dict['node_b']

    getCurrentTrackingList = self.portal.portal_simulation.getCurrentTrackingList
    path_list = [i.path for i in getCurrentTrackingList(
      node_uid=node_b.getUid(), output=1)]
    self.assertTrue(item_a.getPath() not in path_list,
      "%s should not be in B" % item_a.getTitle())
    self.assertTrue(item_b.getPath() in path_list,
      "%s should be in B" % item_a.getTitle())

  # TODO: missing tests for input=1



def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestTrackingList))
  return suite
