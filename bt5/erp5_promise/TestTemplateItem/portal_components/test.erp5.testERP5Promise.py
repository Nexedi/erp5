##############################################################################
#
# Copyright (c) 2012 Nexedi SA and Contributors. All Rights Reserved.
#                    Rafael Monnerat <rafael@nexedi.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import unittest
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

class TestERP5Promise(ERP5TypeTestCase):
  def _updateConversionServerConfiguration(self):
    pass

  def getBusinessTemplateList(self):
    """
        Return the list of business templates.
    """
    return ("erp5_base", "erp5_promise")

  def _test_promise_alarm(self, alarm_id):
    alarm = self.portal.portal_alarms[alarm_id]
    alarm.activeSense()
    self.tic()
    self.assertTrue(alarm.sense())
    alarm.solve()
    self.tic()
    alarm.activeSense()
    self.tic()
    self.assertFalse(alarm.sense())

  def test_promise_conversion_server(self):
    self.portal.portal_preferences.default_system_preference.setPreferredDocumentConversionServerUrlList([])
    self._test_promise_alarm("promise_conversion_server")

  def test_promise_kumofs_server(self):
    self.portal.portal_memcached.persistent_memcached_plugin.setUrlString(None)
    self._test_promise_alarm("promise_kumofs_server")

  def test_promise_memcached_server(self):
    self.portal.portal_memcached.default_memcached_plugin.setUrlString(None)
    self._test_promise_alarm("promise_memcached_server")

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5Promise))
  return suite
