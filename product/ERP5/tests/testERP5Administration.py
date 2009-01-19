##############################################################################
#
# Copyright (c) 2004, 2005, 2006 Nexedi SARL and Contributors. 
# All Rights Reserved.
#          Sebastien Robin <seb@nexedi.com>
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

from Products.ERP5.tests.testInventoryAPI import InventoryAPITestCase

class TestERP5Administration(InventoryAPITestCase):
  """Test for erp5_administration business template.
  """
  def getTitle(self):
    return "ERP5Administration"

  def getBusinessTemplateList(self):
    """ 
        Same list as for Inventory API and add erp5_administration
    """
    return InventoryAPITestCase.getBusinessTemplateList(self) + ('erp5_administration',)

  def test_01_RunCheckStockTableAlarm(self):
    """
    Create a new alarm and check that it is able to detect any divergence
    between the predicate table and zodb objects
    """
    portal = self.getPortal()
    mvt = self._makeMovement(quantity=100)
    get_transaction().commit()
    self.tic()
    alarm = portal.portal_alarms.check_stock
    alarm.activeSense()
    get_transaction().commit()
    self.tic()
    last_active_process = alarm.getLastActiveProcess()
    self.assertFalse(last_active_process.ActiveProcess_sense())
    portal.erp5_sql_connection.manage_test("update stock set quantity=5")
    alarm.activeSense()
    get_transaction().commit()
    self.tic()
    last_active_process = alarm.getLastActiveProcess()
    self.assertTrue(last_active_process.ActiveProcess_sense())

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5Administration))
  return suite

