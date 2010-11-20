# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#          Julien Muchembled <jm@nexedi.com>
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

import unittest
import urllib
import transaction
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

class TestConflictResolution(ERP5TypeTestCase):

  def getTitle(self):
    return "Conflict Resolution"

  def getBusinessTemplateList(self):
    return ('erp5_base',)

  def afterSetUp(self):
    other_node = self.getOtherZEOClientNode()
    self.other_node = self.portal.portal_web_services.connect(
      "http://%s%s" % (other_node, self.portal.getPath()),
      'ERP5TypeTestCase', '', 'xml-rpc')
    self.login()

  def getOtherZEOClientNode(self):
    from ZEO.ClientStorage import ClientStorage
    storage = self.portal._p_jar._storage
    activity_tool = self.portal.portal_activities
    node_list = list(activity_tool.getProcessingNodeList())
    node_list.remove(activity_tool.getCurrentNode())
    assert node_list and isinstance(storage, ClientStorage), \
      "this unit test must be run with at least 2 ZEO clients"
    return node_list[0]

  def testZODBCookie(self):
    cookie_name = self._testMethodName
    portal = self.portal
    self.assertEqual(0, portal.getCacheCookie(cookie_name))
    transaction.commit()
    portal.newCacheCookie(cookie_name) # 1
    self.other_node.newCacheCookie(cookie_name) # 1
    self.other_node.newCacheCookie(cookie_name) # 2
    transaction.commit() # max(1, 2) + 1
    self.assertEqual(3, portal.getCacheCookie(cookie_name))

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestConflictResolution))
  return suite
