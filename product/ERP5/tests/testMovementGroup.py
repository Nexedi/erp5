# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008 Nexedi SA and Contributors. All Rights Reserved.
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################

import os
import unittest
from DateTime import DateTime
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

class MovementGroupTestCase(ERP5TypeTestCase):

  def getPortalName(self):
    """ID of the portal. """
    return os.environ.get('erp5_tests_portal_id') or 'movement_group_test'

  def getBusinessTemplateList(self):
    return ('erp5_base', 'erp5_pdm', 'erp5_simulation', 'erp5_trade')

  def afterSetUp(self):
    self.builder = self.portal.portal_deliveries.newContent(
          portal_type='Delivery Builder',
          delivery_module = 'internal_packing_list_module',
          delivery_portal_type = 'Internal Packing List',
          delivery_line_portal_type = 'Internal Packing List Line',
          delivery_cell_portal_type = 'Internal Packing List Cell',
      )
    self.folder = self.portal.portal_simulation.newContent(
                              portal_type='Applied Rule')

class TestPropertyMovementGroup(MovementGroupTestCase):
  def test_property_movement_group_grouping(self):
    movement_list = ( self.folder.newContent(
                        temp_object=1,
                        portal_type='Simulation Movement',
                        start_date=DateTime(2001, 1, 1)),
                      self.folder.newContent(
                        temp_object=1,
                        portal_type='Simulation Movement',
                        start_date=DateTime(2001, 1, 1)))
    self.builder.newContent(
                  portal_type='Property Movement Group',
                  collect_order_group='delivery',
                  tested_property_list=('start_date',))
    movement_group_node = self.builder.collectMovement(movement_list)
    group_list = movement_group_node.getGroupList()
    self.assertEqual(1, len(group_list))
    self.assertEqual(dict(start_date=DateTime(2001, 1, 1)),
                      group_list[0].getGroupEditDict())

  def test_property_movement_group_separating(self):
    movement_list = ( self.folder.newContent(
                        temp_object=1,
                        portal_type='Simulation Movement',
                        start_date=DateTime(2001, 1, 1)),
                      self.folder.newContent(
                        temp_object=1,
                        portal_type='Simulation Movement',
                        start_date=DateTime(2001, 1, 2)))
    self.builder.newContent(
                  portal_type='Property Movement Group',
                  collect_order_group='delivery',
                  tested_property_list=('start_date',))
    movement_group_node = self.builder.collectMovement(movement_list)
    group_list = movement_group_node.getGroupList()
    self.assertEqual(2, len(group_list))
    self.assertEqual(1, len([group for group in group_list if
      group.getGroupEditDict() == dict(start_date=DateTime(2001, 1, 1))]))
    self.assertEqual(1, len([group for group in group_list if
      group.getGroupEditDict() == dict(start_date=DateTime(2001, 1, 2))]))

  def test_property_movement_group_and_separating(self):
    movement_list = ( self.folder.newContent(
                        temp_object=1,
                        portal_type='Simulation Movement',
                        title='A',
                        start_date=DateTime(2001, 1, 1)),
                      self.folder.newContent(
                        temp_object=1,
                        title='A',
                        portal_type='Simulation Movement',
                        start_date=DateTime(2001, 1, 2)))
    self.builder.newContent(
                  portal_type='Property Movement Group',
                  collect_order_group='delivery',
                  tested_property_list=('start_date', 'title'))
    movement_group_node = self.builder.collectMovement(movement_list)
    group_list = movement_group_node.getGroupList()
    self.assertEqual(2, len(group_list))
    self.assertEqual(1, len([group for group in group_list if
      group.getGroupEditDict() == dict(title='A',
                                       start_date=DateTime(2001, 1, 1))]))
    self.assertEqual(1, len([group for group in group_list if
      group.getGroupEditDict() == dict(title='A',
                                       start_date=DateTime(2001, 1, 2))]))


class TestPropertyAssignmentMovementGroup(MovementGroupTestCase):
  def test_property_assignment_movement_group_max(self):
    movement_list = ( self.folder.newContent(
                        temp_object=1,
                        portal_type='Simulation Movement',
                        start_date=DateTime(2001, 1, 1)),
                      self.folder.newContent(
                        temp_object=1,
                        portal_type='Simulation Movement',
                        start_date=DateTime(2001, 1, 2)))
    self.builder.newContent(
                  portal_type='Property Assignment Movement Group',
                  collect_order_group='delivery',
                  tested_property_list=('start_date',),
                  grouping_method='max',)
    movement_group_node = self.builder.collectMovement(movement_list)
    group_list = movement_group_node.getGroupList()
    self.assertEqual(1, len(group_list))
    self.assertEqual(dict(start_date=DateTime(2001, 1, 2)),
                      group_list[0].getGroupEditDict())

  def test_property_assignment_movement_group_min(self):
    movement_list = ( self.folder.newContent(
                        temp_object=1,
                        portal_type='Simulation Movement',
                        start_date=DateTime(2001, 1, 1)),
                      self.folder.newContent(
                        temp_object=1,
                        portal_type='Simulation Movement',
                        start_date=DateTime(2001, 1, 2)))
    self.builder.newContent(
                  portal_type='Property Assignment Movement Group',
                  collect_order_group='delivery',
                  tested_property_list=('start_date',),
                  grouping_method='min',)
    movement_group_node = self.builder.collectMovement(movement_list)
    group_list = movement_group_node.getGroupList()
    self.assertEqual(1, len(group_list))
    self.assertEqual(dict(start_date=DateTime(2001, 1, 1)),
                      group_list[0].getGroupEditDict())

  def test_property_assignment_movement_group_avg(self):
    movement_list = ( self.folder.newContent(
                        temp_object=1,
                        portal_type='Simulation Movement',
                        int_index=1,),
                      self.folder.newContent(
                        temp_object=1,
                        portal_type='Simulation Movement',
                        int_index=3,),)
    self.builder.newContent(
                  portal_type='Property Assignment Movement Group',
                  collect_order_group='delivery',
                  tested_property_list=('int_index',),
                  grouping_method='avg',)
    movement_group_node = self.builder.collectMovement(movement_list)
    group_list = movement_group_node.getGroupList()
    self.assertEqual(1, len(group_list))
    self.assertEqual(dict(int_index=2),
                      group_list[0].getGroupEditDict())

  def test_property_assignment_movement_group_common_match(self):
    movement_list = ( self.folder.newContent(
                        temp_object=1,
                        portal_type='Simulation Movement',
                        start_date=DateTime(2001, 1, 1)),
                      self.folder.newContent(
                        temp_object=1,
                        portal_type='Simulation Movement',
                        start_date=DateTime(2001, 1, 1)))
    self.builder.newContent(
                  portal_type='Property Assignment Movement Group',
                  collect_order_group='delivery',
                  tested_property_list=('start_date',),
                  grouping_method='common',)
    movement_group_node = self.builder.collectMovement(movement_list)
    group_list = movement_group_node.getGroupList()
    self.assertEqual(1, len(group_list))
    self.assertEqual(dict(start_date=DateTime(2001, 1, 1)),
                      group_list[0].getGroupEditDict())

  def test_property_assignment_movement_group_common_doesnot_match(self):
    movement_list = ( self.folder.newContent(
                        temp_object=1,
                        portal_type='Simulation Movement',
                        start_date=DateTime(2001, 1, 1)),
                      self.folder.newContent(
                        temp_object=1,
                        portal_type='Simulation Movement',
                        start_date=DateTime(2001, 1, 2)))
    self.builder.newContent(
                  portal_type='Property Assignment Movement Group',
                  collect_order_group='delivery',
                  tested_property_list=('start_date',),
                  grouping_method='common',)
    movement_group_node = self.builder.collectMovement(movement_list)
    group_list = movement_group_node.getGroupList()
    self.assertEqual(1, len(group_list))
    self.assertEqual({}, group_list[0].getGroupEditDict())

class TestOrderMovementGroup(MovementGroupTestCase):
  """Tests Order Movement Group - grouping and separating by
  root Applied Rule Causality, in case if that causality is Order"""
  document_portal_type = 'Sale Order'
  def test_order_movement_group_grouping(self):
    order = self.portal.getDefaultModule(self.document_portal_type) \
      .newContent(portal_type=self.document_portal_type)
    applied_rule = self.portal.portal_simulation.newContent(
      portal_type='Applied Rule',
      causality_value = order
    )

    movement_list = (
      applied_rule.newContent(portal_type='Simulation Movement'),
      applied_rule.newContent(portal_type='Simulation Movement')
    )

    self.builder.newContent(
                  portal_type='Order Movement Group',
                  collect_order_group='delivery')

    movement_group_node = self.builder.collectMovement(movement_list)
    group_list = movement_group_node.getGroupList()
    self.assertEqual(1, len(group_list))
    self.assertEqual(dict(causality_list=[order.getRelativeUrl()]),
                      group_list[0].getGroupEditDict())

  def test_order_movement_group_separating(self):
    order_1 = self.portal.getDefaultModule(self.document_portal_type) \
      .newContent(portal_type=self.document_portal_type)
    applied_rule_1 = self.portal.portal_simulation.newContent(
      portal_type='Applied Rule',
      causality_value = order_1
    )

    order_2 = self.portal.getDefaultModule(self.document_portal_type) \
      .newContent(portal_type=self.document_portal_type)
    applied_rule_2 = self.portal.portal_simulation.newContent(
      portal_type='Applied Rule',
      causality_value = order_2
    )

    movement_list = (
      applied_rule_1.newContent(portal_type='Simulation Movement'),
      applied_rule_2.newContent(portal_type='Simulation Movement')
    )

    self.builder.newContent(
                  portal_type='Order Movement Group',
                  collect_order_group='delivery')

    movement_group_node = self.builder.collectMovement(movement_list)
    group_list = movement_group_node.getGroupList()
    self.assertEqual(2, len(group_list))
    self.assertEqual(1, len([group for group in group_list if
      group.getGroupEditDict() == dict(causality_list=[order_1.getRelativeUrl()])]))
    self.assertEqual(1, len([group for group in group_list if
      group.getGroupEditDict() == dict(causality_list=[order_2.getRelativeUrl()])]))

class TestOrderMovementGroupDelivery(TestOrderMovementGroup):
  """Tests Order Movement Group - grouping and separating by
  root Applied Rule Causality, in case if that causality is Delivery"""
  document_portal_type = 'Sale Packing List'

class TestDeliveryCausalityAssignmentMovementGroup(MovementGroupTestCase):
  """Tests Delivery Causality Assignment Movement Group
  This Movement Group never separates"""
  order_portal_type = 'Sale Order'
  order_line_portal_type = 'Sale Order Line'
  delivery_portal_type = 'Sale Packing List'
  delivery_line_portal_type = 'Sale Packing List Line'

  def test_delivery_causality_assignment_movement_group(self):
    order = self.portal.getDefaultModule(self.order_portal_type) \
      .newContent(portal_type=self.order_portal_type)
    order_line_1 = order.newContent(portal_type=self.order_line_portal_type)
    order_line_2 = order.newContent(portal_type=self.order_line_portal_type)

    delivery_1 = self.portal.getDefaultModule(self.delivery_portal_type) \
      .newContent(portal_type=self.delivery_portal_type)
    delivery_1_line = delivery_1.newContent(portal_type=self.delivery_line_portal_type)

    delivery_2 = self.portal.getDefaultModule(self.delivery_portal_type) \
      .newContent(portal_type=self.delivery_portal_type)
    delivery_2_line = delivery_2.newContent(portal_type=self.delivery_line_portal_type)

    applied_rule = self.portal.portal_simulation.newContent(
      portal_type='Applied Rule',
      causality_value = order
    )
    order_movement_list = (
      applied_rule.newContent(
        portal_type='Simulation Movement',
        order_value = order_line_1,
        delivery_value = delivery_1_line),
      applied_rule.newContent(
        portal_type='Simulation Movement',
        order_value = order_line_2,
        delivery_value = delivery_2_line),
    )

    movement_list = [
        q.newContent(portal_type='Applied Rule') \
        .newContent(portal_type='Simulation Movement') \
        for q in order_movement_list
    ]

    self.builder.newContent(
                  portal_type='Delivery Causality Assignment Movement Group',
                  collect_order_group='delivery')

    movement_group_node = self.builder.collectMovement(movement_list)
    group_list = movement_group_node.getGroupList()

    self.assertEqual(1, len(group_list))
    self.assertEqual(dict(causality_list=[delivery_1.getRelativeUrl(),
      delivery_2.getRelativeUrl()]),
                      group_list[0].getGroupEditDict())

class TestDuplicatedKeyRaiseException(MovementGroupTestCase):
  """Test, that it is not allowed to have more than one movement group to update
  same key during building process"""
  document_portal_type = 'Sale Order'
  def test(self):
    order = self.portal.getDefaultModule(self.document_portal_type) \
      .newContent(portal_type=self.document_portal_type)
    applied_rule = self.portal.portal_simulation.newContent(
      portal_type='Applied Rule',
      causality_value = order
    )

    movement_list = (
      applied_rule.newContent(portal_type='Simulation Movement'),
      applied_rule.newContent(portal_type='Simulation Movement')
    )

    self.builder.newContent(
                  portal_type='Order Movement Group',
                  collect_order_group='delivery')

    self.builder.newContent(
                  portal_type='Order Movement Group',
                  collect_order_group='delivery')

    movement_relative_url_list = [q.getRelativeUrl() for q in movement_list]
    from erp5.component.mixin.BuilderMixin import DuplicatedPropertyDictKeysError
    self.assertRaises(
      DuplicatedPropertyDictKeysError,
      self.builder.build,
      movement_relative_url_list = movement_relative_url_list
    )

class TestCategoryMovementGroup(MovementGroupTestCase):
  def test_category_movement_group_grouping(self):
    movement_list = ( self.folder.newContent(
                        temp_object=1,
                        portal_type='Simulation Movement',
                        source='1'),
                      self.folder.newContent(
                        temp_object=1,
                        portal_type='Simulation Movement',
                        source='1'))
    self.builder.newContent(
                  portal_type='Category Movement Group',
                  collect_order_group='delivery',
                  tested_property_list=('source',))
    movement_group_node = self.builder.collectMovement(movement_list)
    group_list = movement_group_node.getGroupList()
    self.assertEqual(1, len(group_list))
    self.assertEqual(dict(source_list=['1']),
                      group_list[0].getGroupEditDict())

  def test_category_movement_group_separating(self):
    movement_list = ( self.folder.newContent(
                        temp_object=1,
                        portal_type='Simulation Movement',
                        source='1'),
                      self.folder.newContent(
                        temp_object=1,
                        portal_type='Simulation Movement',
                        source='2'))
    self.builder.newContent(
                  portal_type='Category Movement Group',
                  collect_order_group='delivery',
                  tested_property_list=('source',))
    movement_group_node = self.builder.collectMovement(movement_list)
    group_list = movement_group_node.getGroupList()
    self.assertEqual(2, len(group_list))
    self.assertEqual(1, len([group for group in group_list if
      group.getGroupEditDict() == dict(source_list=['1'])]))
    self.assertEqual(1, len([group for group in group_list if
      group.getGroupEditDict() == dict(source_list=['2'])]))

  def test_category_movement_group_and_separating(self):
    movement_list = ( self.folder.newContent(
                        temp_object=1,
                        portal_type='Simulation Movement',
                        destination='A',
                        source='1'),
                      self.folder.newContent(
                        temp_object=1,
                        destination='A',
                        portal_type='Simulation Movement',
                        source='2'))
    self.builder.newContent(
                  portal_type='Category Movement Group',
                  collect_order_group='delivery',
                  tested_property_list=('destination', 'source'))
    movement_group_node = self.builder.collectMovement(movement_list)
    group_list = movement_group_node.getGroupList()
    self.assertEqual(2, len(group_list))
    self.assertEqual(1, len([group for group in group_list if
      group.getGroupEditDict() == dict(destination_list=['A'],
                                       source_list=['1'])]))
    self.assertEqual(1, len([group for group in group_list if
      group.getGroupEditDict() == dict(destination_list=['A'],
                                       source_list=['2'])]))


class TestMovementGroupCommonAPI(MovementGroupTestCase):

  def test_separateMethod(self):
    """Make sure that _separate method works if argument is an empty list."""
    import Products.ERP5Type.Document
    for portal_type in self.portal.portal_types.objectValues():
      portal_type_id = portal_type.getId()
      if portal_type_id.endswith("Movement Group"):
        movement_group = self.builder.newContent(portal_type=portal_type_id)
        self.assertEqual(movement_group._separate([]), [])

class TestPropertyGroupingMovementGroup(MovementGroupTestCase):

  def test_property_movement_group_grouping(self):
    movement_list = ( self.folder.newContent(
                        temp_object=1,
                        portal_type='Simulation Movement',
                        start_date=DateTime(2001, 1, 1)),
                      self.folder.newContent(
                        temp_object=1,
                        portal_type='Simulation Movement',
                        start_date=DateTime(2001, 1, 1)))
    self.builder.newContent(
                  portal_type='Property Grouping Movement Group',
                  collect_order_group='delivery',
                  tested_property_list=('start_date',))
    movement_group_node = self.builder.collectMovement(movement_list)
    group_list = movement_group_node.getGroupList()
    self.assertEqual(1, len(group_list))
     # This movent group must not assign the properties
    self.assertEqual({}, group_list[0].getGroupEditDict())

  def test_property_movement_group_separating(self):
    movement_list = ( self.folder.newContent(
                        temp_object=1,
                        portal_type='Simulation Movement',
                        start_date=DateTime(2001, 1, 1)),
                      self.folder.newContent(
                        temp_object=1,
                        portal_type='Simulation Movement',
                        start_date=DateTime(2001, 1, 2)))
    self.builder.newContent(
                  portal_type='Property Grouping Movement Group',
                  collect_order_group='delivery',
                  tested_property_list=('start_date',))
    movement_group_node = self.builder.collectMovement(movement_list)
    group_list = movement_group_node.getGroupList()
    self.assertEqual(2, len(group_list))
    for group in group_list:
      # This movent group must not assign the properties
      self.assertEqual({}, group.getGroupEditDict())

  def test_property_movement_group_and_separating(self):
    movement_list = ( self.folder.newContent(
                        temp_object=1,
                        portal_type='Simulation Movement',
                        title='B',
                        start_date=DateTime(2001, 1, 1)),
                      self.folder.newContent(
                        temp_object=1,
                        portal_type='Simulation Movement',
                        title='B',
                        start_date=DateTime(2001, 1, 1)),
                      self.folder.newContent(
                        temp_object=1,
                        title='A',
                        portal_type='Simulation Movement',
                        start_date=DateTime(2001, 1, 2)),
                      self.folder.newContent(
                        temp_object=1,
                        title='A',
                        portal_type='Simulation Movement',
                        start_date=DateTime(2001, 1, 3)))
    self.builder.newContent(
                  portal_type='Property Grouping Movement Group',
                  collect_order_group='delivery',
                  tested_property_list=('start_date', 'title'))
    movement_group_node = self.builder.collectMovement(movement_list)
    group_list = movement_group_node.getGroupList()

    # must not be 4
    self.assertEqual(3, len(group_list))

    for group in group_list:
      # This movent group must not assign the properties
      self.assertEqual({}, group.getGroupEditDict())

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestPropertyMovementGroup))
  suite.addTest(unittest.makeSuite(TestPropertyAssignmentMovementGroup))
  suite.addTest(unittest.makeSuite(TestOrderMovementGroup))
  suite.addTest(unittest.makeSuite(TestOrderMovementGroupDelivery))
  suite.addTest(unittest.makeSuite(TestDeliveryCausalityAssignmentMovementGroup))
  suite.addTest(unittest.makeSuite(TestDuplicatedKeyRaiseException))
  suite.addTest(unittest.makeSuite(TestCategoryMovementGroup))
  suite.addTest(unittest.makeSuite(TestMovementGroupCommonAPI))
  suite.addTest(unittest.makeSuite(TestPropertyGroupingMovementGroup))
  return suite

