# -*- coding: utf-8 -*-
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
import os

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from Products.ERP5Type.tests.utils import installRealMemcachedTool
from Products.ERP5Type.tests.ERP5TypeTestCase import\
    _getVolatileMemcachedServerDict
import time

class TestMemcachedTool(ERP5TypeTestCase):
  """
    Test MemcachedTool.
    Note : When writing tests, keep in mind that the test must not give false
           positive or negative if the value already exists in an existing
           memcached server.
  """

  expiration_time = 10 # second

  def getBusinessTemplateList(self):
    return tuple()

  def getTitle(self):
    return "MemcachedTool"

  def setUp(self): # pylint: disable=method-hidden
    super(TestMemcachedTool, self).setUp()
    installRealMemcachedTool(self.portal)
    memcached_tool = self.portal.portal_memcached
    #create Memcache Plugin
    url_string = "%(hostname)s:%(port)s" % _getVolatileMemcachedServerDict()
    if getattr(memcached_tool, 'default_memcached_plugin', None) is None:
      memcached_tool.newContent(id='default_memcached_plugin',
                                portal_type='Memcached Plugin',
                                int_index=0,
                                url_string=url_string)
    if getattr(memcached_tool, 'memcached_plugin_with_expiration', None) is None:
      memcached_tool.newContent(id='memcached_plugin_with_expiration',
                                portal_type='Memcached Plugin',
                                int_index=1,
                                expiration_time=self.expiration_time,
                                url_string=url_string)

    self.tic()

  def afterSetUp(self):
    uf = self.portal.acl_users
    uf._doAddUser('vincent', self.newPassword(), ['Manager'], [])
    user = uf.getUserById('vincent').__of__(uf)
    newSecurityManager(None, user)

  def getMemcachedDict(self):
    return self.portal.portal_memcached.getMemcachedDict(key_prefix='unit_test',
                                                              plugin_path='portal_memcached/default_memcached_plugin')

  def getMemcachedDictWithExpiration(self):
    return self.portal.portal_memcached.getMemcachedDict(
                                                        key_prefix='unit_test',
               plugin_path='portal_memcached/memcached_plugin_with_expiration')


  def test_00_MemcachedToolIsEnabled(self):
    """
      Check if MemcachedTool is enabled without USE_MEMCACHED_TOOL file.
    """
    from Products.ERP5Type import product_path
    memcached_tool_enable_path = '%s%s%s' % (product_path, os.sep,
                                             'USE_MEMCACHED_TOOL')
    self.assertFalse(os.access(memcached_tool_enable_path, os.F_OK),
                     'A static file %s is obsolete. Please remove it and retry this unit test.' % memcached_tool_enable_path)
    memcached_tool = self.portal.portal_memcached
    try:
      import memcache
      del memcache
    except ImportError:
      # MemcachedTool should be disabled
      self.assertRaises(RuntimeError, memcached_tool.getMemcachedDict)

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
    self.commit()
    # After a commit, check that the value is commited and grabbed from memcached
    # again. Its value must not change, but the instance is not the same anymore.
    self.assertTrue(tested_dict[tested_key] is not tested_value)
    self.assertTrue(tested_dict[tested_key] == tested_value)

  def test_04_deleteValue(self):
    """
      Tests that deleting a value works.
    """
    tested_dict = self.getMemcachedDict()
    tested_key = 'test_key'
    tested_value = 'test_value'
    tested_dict[tested_key] = tested_value
    self.assertTrue(tested_dict[tested_key] == tested_value)
    del tested_dict[tested_key]
    self.assertRaises(KeyError, tested_dict.__getitem__, tested_key)

  def test_05_deleteValueAndCommit(self):
    """
      Tests that deleted values are actually deleted in memcached.
    """
    tested_dict = self.getMemcachedDict()
    tested_key = 'test_key'
    tested_value = 'test_value'
    tested_dict[tested_key] = tested_value
    self.assertTrue(tested_dict[tested_key] == tested_value)
    del tested_dict[tested_key]
    self.commit()
    self.assertRaises(KeyError, tested_dict.__getitem__, tested_key)

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

  def test_07_checkExpirationTimeOfMemcachedDict(self):
    """
    Test that expiration time parameter is well handle by memcached tool
    """
    tested_dict = self.getMemcachedDictWithExpiration()
    key = 'my_key'
    value = 'a'*100
    tested_dict[key] = value
    self.commit()
    self.assertEqual(tested_dict.get(key), value)
    self.commit()
    # Sleep epliration_time + 1 second to be sure that it is well expired
    time.sleep(self.expiration_time + 1)
    # now value should have expired
    self.assertRaises(KeyError, tested_dict.__getitem__, key)

if __name__ == '__main__':
  unittest.main()
