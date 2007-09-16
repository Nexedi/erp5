##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                     Vincent Pelletier <vincent@nexedi.com>
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
from AccessControl.SecurityManagement import newSecurityManager
from Products.ERP5Type.tests.utils import installRealMemcachedTool

class TestMemcachedTool(ERP5TypeTestCase):
  """
    Test MemcachedTool.
    Note : When writing tests, keep in mind that the test must not give false
           positive or negative if the value already exists in an existing
           memcached server.
  """

  def getBusinessTemplateList(self):
    return tuple()

  def getTitle(self):
    return "MemcachedTool"

  def setUp(self):
    ERP5TypeTestCase.setUp(self)
    installRealMemcachedTool(self.getPortal())

  def afterSetUp(self):
    self.login()

  def login(self):
    uf = self.getPortal().acl_users
    uf._doAddUser('vincent', '', ['Manager'], [])
    user = uf.getUserById('vincent').__of__(uf)
    newSecurityManager(None, user)

  def getMemcachedDict(self):
    return self.getPortal().portal_memcached.getMemcachedDict(key_prefix='unit_test')

  def test_01_dictionnaryIsUsable(self):
    """
      Check that the received class has the minimum requirements which makes
      a dict usable from zope restricted environment.
    """
    tested_dict = self.getMemcachedDict()
    tested_attribute_id_list = ('__getitem__', '__setitem__', '__delitem__',
                                'get', 'set',
                                '__guarded_getitem__', '__guarded_setitem__',
                                '__guarded_delitem__')
    for attribut_id in tested_attribute_id_list:
      self.assertTrue(getattr(tested_dict, attribut_id, None) is not None)
    
  def test_02_insertValue(self):
    """
      Tests that inserting an item and reading it gets a consistent result.
    """
    tested_dict = self.getMemcachedDict()
    tested_key = 'test_key'
    tested_value = 'test_value'
    tested_other_value = 'test_other_value'

    tested_dict[tested_key] = tested_value
    self.assertTrue(tested_dict[tested_key] == tested_value)
    tested_dict[tested_key] = tested_other_value
    self.assertTrue(tested_dict[tested_key] == tested_other_value)

  def test_03_insertValueAndCommit(self):
    """
      Tests that values survives a commit (which causes the tool to flush its
      cache).
    """
    tested_dict = self.getMemcachedDict()
    tested_key = 'test_key'
    tested_value = 'test_value'
    # First, check that the local cache in memcachedTool works
    tested_dict[tested_key] = tested_value
    self.assertTrue(tested_dict[tested_key] is tested_value)
    get_transaction().commit()
    # After a commit, check that the value is commited and grabbed from memcached
    # again. Its value must not change, but the instance is not the same anymore.
    self.assertTrue(tested_dict[tested_key] is not tested_value)
    self.assertTrue(tested_dict[tested_key] == tested_value)

  def test_04_deleteValue(self):
    """
      Tests that deleting a value works.
      Note that deleting a value should raise a KeyError.
      But because of python-memcached limitations, all we get is a None value.
    """
    tested_dict = self.getMemcachedDict()
    tested_key = 'test_key'
    tested_value = 'test_value'
    tested_dict[tested_key] = tested_value
    self.assertTrue(tested_dict[tested_key] == tested_value)
    del tested_dict[tested_key]
    self.assertTrue(tested_dict[tested_key] is None)

  def test_05_deteteValueAndCommit(self):
    """
      Tests that deleted values are actually deleted in memcached.
    """
    tested_dict = self.getMemcachedDict()
    tested_key = 'test_key'
    tested_value = 'test_value'
    tested_dict[tested_key] = tested_value
    self.assertTrue(tested_dict[tested_key] == tested_value)
    del tested_dict[tested_key]
    get_transaction().commit()
    try:
      dummy = tested_dict[tested_key]
    except KeyError:
      pass
    except:
      self.fail('Wrong error type is raised when key is not found.')
    else:
      self.fail('No error is raised when key is not found.')

  def test_06_checkNonStringKeyFails(self):
    """
      Tests that a non-string key is not accepted by SharedDict.
    """
    tested_dict = self.getMemcachedDict()
    tested_key = tuple()
    tested_value = 'test_value'
    try:
      tested_dict[tested_key] = tested_value
    except TypeError:
      pass
    else:
      self.fail('No error was raised when assigning a value to a non-string key.')

if __name__ == '__main__':
  unittest.main()
