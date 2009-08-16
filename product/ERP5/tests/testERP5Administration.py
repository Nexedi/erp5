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
import transaction
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
    sql_test = portal.erp5_sql_connection.manage_test
    alarm = portal.portal_alarms.check_stock

    def checkActiveProcess(failed):
      transaction.commit()
      self.tic()
      self.assertEqual(alarm.getLastActiveProcess().ActiveProcess_sense(),
                       failed)
    def checkStock(row_count):
      alarm.activeSense()
      checkActiveProcess(1)
      alarm.solve()
      checkActiveProcess(1)
      alarm.activeSense()
      checkActiveProcess(0)
      self.assertEqual(row_count, sql_test("select count(*) from stock")[0][0])

    alarm.setAlarmNotificationMode('never')
    mvt = self._makeMovement(quantity=1.23)
    transaction.commit()
    self.tic()
    alarm.activeSense()
    checkActiveProcess(0)

    row_count = sql_test("select count(*) from stock")[0][0]
    sql_test("update stock set quantity=5")
    checkStock(row_count)   # alarm.solve will reindex 'mvt'
    mvt.getParentValue()._delOb(mvt.getId())
    checkStock(row_count-2) # alarm.solve will unindex 'mvt'

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5Administration))
  return suite

