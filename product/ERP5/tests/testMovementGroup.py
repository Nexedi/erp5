##############################################################################
# -*- coding: utf8 -*-
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

import unittest

from DateTime import DateTime

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

class MovementGroupTestCase(ERP5TypeTestCase):
  def getBusinessTemplateList(self):
    return ('erp5_base', )

  def afterSetUp(self):
    self.builder = self.portal.portal_deliveries.newContent(
                              portal_type='Delivery Builder',
                              id='test_builder')
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
    self.assertEquals(1, len(group_list))
    self.assertEquals(dict(start_date=DateTime(2001, 1, 1)),
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
    self.assertEquals(2, len(group_list))
    self.assertEquals(1, len([group for group in group_list if
      group.getGroupEditDict() == dict(start_date=DateTime(2001, 1, 1))]))
    self.assertEquals(1, len([group for group in group_list if
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
    self.assertEquals(2, len(group_list))
    self.assertEquals(1, len([group for group in group_list if
      group.getGroupEditDict() == dict(title='A',
                                       start_date=DateTime(2001, 1, 1))]))
    self.assertEquals(1, len([group for group in group_list if
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
    self.assertEquals(1, len(group_list))
    self.assertEquals(dict(start_date=DateTime(2001, 1, 2)),
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
    self.assertEquals(1, len(group_list))
    self.assertEquals(dict(start_date=DateTime(2001, 1, 1)),
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
    self.assertEquals(1, len(group_list))
    self.assertEquals(dict(int_index=2),
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
    self.assertEquals(1, len(group_list))
    self.assertEquals(dict(start_date=DateTime(2001, 1, 1)),
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
    self.assertEquals(1, len(group_list))
    self.assertEquals(dict(), group_list[0].getGroupEditDict())


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestPropertyMovementGroup))
  suite.addTest(unittest.makeSuite(TestPropertyAssignmentMovementGroup))
  return suite
