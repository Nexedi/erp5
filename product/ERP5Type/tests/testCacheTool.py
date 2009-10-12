# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                     Ivan Tyagov <ivan@nexedi.com>
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

import time
import unittest

from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.CachePlugins.DummyCache import DummyCache
from AccessControl.SecurityManagement import newSecurityManager
from zLOG import LOG
import transaction

class TestingCache(DummyCache):
  """A dummy cache that mark cache miss, so that you can later count access
  using getCacheMisses() """
  def __init__(self, params):
    DummyCache.__init__(self, params)

  def __call__(self, callable_object, cache_id, scope, cache_duration=None,
                *args, **kwd):
    self.markCacheMiss(1)
    return callable_object(*args, **kwd)

class TestCacheTool(ERP5TypeTestCase):

  def getTitle(self):
    return "Cache Tool"

  def getBusinessTemplateList(self):
      """
        Return the list of business templates.
      """
      return ('erp5_base',)

  def afterSetUp(self):
    self.login()
    self.checkCacheTool()
    self.checkPortalTypes()
    self.createPersistentMemcachedPlugin()
    self.createCacheFactories()
    self.createCachedMethod()
    transaction.commit()

  def login(self):
    uf = self.getPortal().acl_users
    uf._doAddUser('admin', '', ['Manager'], [])
    uf._doAddUser('ERP5TypeTestCase', '', ['Manager'], [])
    user = uf.getUserById('admin').__of__(uf)
    newSecurityManager(None, user)

  def checkCacheTool(self):
    portal = self.getPortal()
    self.assertNotEqual(None, getattr(portal, 'portal_caches', None))

  def checkPortalTypes(self):
    portal = self.getPortal()
    portal_types = portal.portal_types
    typeinfo_names = ("Cache Factory",
                      "Ram Cache",
                      "Distributed Ram Cache",
                      )
    for typeinfo_name in typeinfo_names:
      portal_type = getattr(portal_types, typeinfo_name, None)
      self.assertNotEqual(None, portal_type)

  def createPersistentMemcachedPlugin(self):
    portal_memcached = self.getPortal().portal_memcached
    memcached_plugin_id = 'flare'
    if getattr(portal_memcached, memcached_plugin_id, None) is None:
      portal_memcached.newContent(portal_type='Memcached Plugin',
                                  id=memcached_plugin_id,
                                  url_string='127.0.0.1:12121',
                                  server_max_key_length=0,
                                  server_max_value_length=0,
                                  priority=1)

  def createCacheFactories(self):
    portal = self.getPortal()
    portal_caches = portal.portal_caches

    # Cache plugins are organised into 'Cache factories' so we create
    # factories first ram_cache_factory (to test Ram Cache Plugin) 
    if getattr(portal_caches, 'ram_cache_factory', None) is None:
      ram_cache_factory = portal_caches.newContent(portal_type="Cache Factory",
                                                   id='ram_cache_factory',
                                                   container=portal_caches)
      ram_cache_plugin = ram_cache_factory.newContent(portal_type="Ram Cache")
      ram_cache_plugin.setIntIndex(0)

    if getattr(portal_caches, 'another_ram_cache_factory', None) is None:
      cache_factory = portal_caches.newContent(portal_type="Cache Factory",
                                                   id='another_ram_cache_factory',
                                                   container=portal_caches)
      cache_plugin = cache_factory.newContent(portal_type="Ram Cache")
      cache_plugin.setIntIndex(0)

    if getattr(portal_caches, 'distributed_ram_cache_factory', None) is None:
      ## distributed_ram_cache_factory (to test Distributed Ram Cache Plugin) 
      dram_cache_factory = portal_caches.newContent(portal_type="Cache Factory",
                                                    id='distributed_ram_cache_factory',
                                                    container=portal_caches)
      dram_cache_plugin = dram_cache_factory.newContent(
              portal_type="Distributed Ram Cache", specialise='portal_memcached/default_memcached_plugin' )
      dram_cache_plugin.setIntIndex(0)

    if getattr(portal_caches, 'distributed_persistent_cache_factory', None) is None:
      ## distributed_ram_cache_factory (to test Distributed Ram Cache Plugin) 
      dram_cache_factory = portal_caches.newContent(portal_type="Cache Factory",
                                                    id='distributed_persistent_cache_factory',
                                                    container=portal_caches)
      dram_cache_plugin = dram_cache_factory.newContent(
              portal_type="Distributed Ram Cache", specialise='portal_memcached/flare' )
      dram_cache_plugin.setIntIndex(0)

    if getattr(portal_caches, 'erp5_user_factory', None) is None:

      ## erp5_user_factory (to test a combination of all cache plugins)
      erp5_user_factory = portal_caches.newContent(portal_type="Cache Factory",
                                                   id="erp5_user_factory")

      ram_cache_plugin = erp5_user_factory.newContent(portal_type="Ram Cache")
      ram_cache_plugin.setIntIndex(0)
      dram_cache_plugin = erp5_user_factory.newContent(portal_type="Distributed Ram Cache",
                                                       specialise='portal_memcached/default_memcached_plugin')
      dram_cache_plugin.setIntIndex(1)
    ## update Ram Cache structure
    portal_caches.updateCache()

    from Products.ERP5Type.Cache import CachingMethod

    ## do we have the same structure we created above?
    self.assert_('ram_cache_factory' in CachingMethod.factories)
    self.assert_('another_ram_cache_factory' in CachingMethod.factories)
    self.assert_('distributed_ram_cache_factory' in CachingMethod.factories)
    self.assert_('distributed_persistent_cache_factory' in CachingMethod.factories)
    self.assert_('erp5_user_factory' in CachingMethod.factories)

  def createCachedMethod(self):
    portal = self.getPortal()
    if getattr(portal, 'testCachedMethod', None) is not None:
      return
    ## add test cached method
    py_script_id = "testCachedMethod"
    py_script_params = "value=10000, portal_path=('','erp5')"
    py_script_body = """
def veryExpensiveMethod(value):
 ## do something expensive for some time
 ## no 'time.sleep()' available in Zope
 ## so concatenate strings
 s = ""
 for i in range(0, value):
   s = str(value*value*value) + s
 return value

result = veryExpensiveMethod(value)
return result
"""
    portal.manage_addProduct['PythonScripts'].manage_addPythonScript(
                                                id=py_script_id)
    py_script_obj = getattr(portal, py_script_id)
    py_script_obj.ZPythonScript_edit(py_script_params, py_script_body)

  def test_01_CacheFactoryOnePlugin(self):
    """ Test cache factory containing only one cache plugin. """
    portal = self.getPortal()
    from Products.ERP5Type.Cache import CachingMethod
    py_script_id = "testCachedMethod"
    py_script_obj = getattr(portal, py_script_id)
    for cf_name, clear_allowed in (('ram_cache_factory', True),
                    ('distributed_ram_cache_factory', False),
                    ('distributed_persistent_cache_factory', False),
                   ):
      my_cache = CachingMethod(py_script_obj,
                               'py_script_obj',
                               cache_factory=cf_name)
      self._cacheFactoryInstanceTest(my_cache, cf_name, clear_allowed)

  def test_02_CacheFactoryMultiPlugins(self):
    """ Test a cache factory containing multiple cache plugins. """
    portal = self.getPortal()
    from Products.ERP5Type.Cache import CachingMethod
    py_script_id = "testCachedMethod"
    py_script_obj = getattr(portal, py_script_id)
    cf_name = 'erp5_user_factory'
    my_cache = CachingMethod(py_script_obj,
                             'py_script_obj',
                             cache_factory=cf_name)
    self._cacheFactoryInstanceTest(my_cache, cf_name, clear_allowed=False)

  def _cacheFactoryInstanceTest(self, my_cache, cf_name, clear_allowed):
    portal = self.getPortal()
    print 
    print "="*40
    print "TESTING:", cf_name

    # if the test fails because your machine is too fast, increase this value.
    nb_iterations = 30000

    portal.portal_caches.clearCacheFactory(cf_name)
    ## 1st call
    start = time.time()
    original =  my_cache(nb_iterations, portal_path=('', portal.getId()))
    end = time.time()
    calculation_time = end-start
    print "\n\tCalculation time (1st call)", calculation_time

    ## 2nd call - should be cached now
    start = time.time()
    cached =  my_cache(nb_iterations, portal_path=('', portal.getId()))
    end = time.time()
    calculation_time = end-start
    print "\n\tCalculation time (2nd call)", calculation_time

    # check if cache works by getting calculation_time for last cache
    # operation even remote cache must have access time less than a second.
    # if it's greater than method wasn't previously cached and was calculated
    # instead
    self.assert_(1.0 > calculation_time)

    ## check if equal.
    self.assertEquals(original, cached)

    ## OK so far let's clear cache
    if clear_allowed:
      portal.portal_caches.clearCacheFactory(cf_name)

      ## 1st call
      start = time.time()
      original =  my_cache(nb_iterations, portal_path=('', portal.getId()))
      end = time.time()
      calculation_time = end-start
      print "\n\tCalculation time (after cache clear)", calculation_time

      ## Cache  cleared shouldn't be previously cached
      self.assert_(1.0 < calculation_time)

  def test_03_cachePersistentObjects(self):
    # storing persistent objects in cache is not allowed, but this check is
    # only performed in unit tests.
    from Products.ERP5Type.Cache import CachingMethod
    def func():
      # return a persistent object
      return self.portal
    cached_func = CachingMethod(func, 'cache_persistent_obj')
    self.assertRaises(TypeError, cached_func)

    def func():
      # return a method bound on a persistent object
      return self.portal.getTitle
    cached_func = CachingMethod(func, 'cache_bound_method')
    self.assertRaises(TypeError, cached_func)

  def test_04_CheckConcurrentRamCacheDict(self):
    """Check that all RamCache doesn't clear the same cache_dict
    """
    print 
    print "="*40
    print "TESTING: Concurrent RamCache" 
    portal = self.getPortal()
    nb_iterations = 30000
    from Products.ERP5Type.Cache import CachingMethod
    py_script_id = "testCachedMethod"
    py_script_obj = getattr(portal, py_script_id)

    ram_cached_method = CachingMethod(py_script_obj,
                             'py_script_obj',
                             cache_factory='ram_cache_factory')

    portal.portal_caches.clearCache(cache_factory_list=('ram_cache_factory', 'another_ram_cache_factory',))
    #First call, fill the cache
    start = time.time()
    ram_cached_method(nb_iterations, portal_path=('', portal.getId()))
    end = time.time()
    calculation_time = end-start
    print "\n\tCalculation time (1st call)", calculation_time

    ## 2nd call - should be cached now
    start = time.time()
    cached = ram_cached_method(nb_iterations, portal_path=('', portal.getId()))
    end = time.time()
    calculation_time = end-start
    print "\n\tCalculation time (2nd call)", calculation_time
    self.assert_(1.0 > calculation_time)

    #Clear only another_ram_cache_factory
    portal.portal_caches.clearCacheFactory('another_ram_cache_factory')
    #Call conversion for ram_cache_factory
    start = time.time()
    cached = ram_cached_method(nb_iterations, portal_path=('', portal.getId()))
    end = time.time()
    calculation_time = end-start
    print "\n\tCalculation time (3rd call)", calculation_time
    self.assert_(1.0 > calculation_time)

  def test_99_CachePluginInterface(self):
    """Test Class against Interface
    """
    from Products.ERP5Type.CachePlugins.DistributedRamCache import DistributedRamCache
    from Products.ERP5Type.CachePlugins.RamCache import RamCache
    from Products.ERP5Type.interfaces.cache_plugin import ICachePlugin
    from zope.interface.verify import verifyClass
    verifyClass(ICachePlugin, DistributedRamCache)
    verifyClass(ICachePlugin, RamCache)

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestCacheTool))
  return suite

