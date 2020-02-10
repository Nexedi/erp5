##############################################################################
#
# Copyright (c) 2019 Nexedi SA and Contributors. All Rights Reserved.
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
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.Timeout import TimeoutReachedError, Deadline
import time

class TestTimeout(ERP5TypeTestCase):
  """
    Test MariaDB / ZODB Deadline
  """
  def getBusinessTemplateList(self):
    return ()

  def getTitle(self):
    return "Query Deadline"

  def afterSetUp(self):
    self.login()

  def test_query_deadline(self):
    # We create a Z SQL Method that takes too long
    method_id = 'Base_zSlowQuery'
    self.portal.portal_skins.custom.manage_addProduct['ZSQLMethods'].manage_addZSQLMethod(
      id=method_id,
      title='',
      connection_id='erp5_sql_connection',
      arguments='t',
      template="SELECT uid, path FROM catalog WHERE SLEEP(<dtml-var t>) = 0 AND path='%s'" % self.portal.portal_templates.getPath(),
    )
    self.portal.changeSkin(None)
    # finish within deadline
    with Deadline(3.0):
      getattr(self.portal, method_id)(t=2)
    # query timeout by deadline
    with Deadline(1.0):
      with self.assertRaises(TimeoutReachedError):
        getattr(self.portal, method_id)(t=2)
    # can be nested, but cannot extend the deadline
    with Deadline(1.0):
      with Deadline(3.0):
        with self.assertRaises(TimeoutReachedError):
          getattr(self.portal, method_id)(t=2)
    with Deadline(5.0):
      with Deadline(1.0):
        with self.assertRaises(TimeoutReachedError):
          getattr(self.portal, method_id)(t=2)
      # not yet reached for outer deadline
      getattr(self.portal, method_id)(t=1)

  def test_zodb_deadline(self):
    with Deadline(1.0):
      time.sleep(2)
      with self.assertRaises(TimeoutReachedError):
        [x.getObject() for x in self.portal.portal_templates.searchFolder()]
