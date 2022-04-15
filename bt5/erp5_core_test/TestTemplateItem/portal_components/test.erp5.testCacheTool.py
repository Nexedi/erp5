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

from __future__ import print_function
import time
import unittest

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import _getPersistentMemcachedServerDict
from Products.ERP5Type.CachePlugins.DummyCache import DummyCache
from AccessControl.SecurityManagement import newSecurityManager
from Products.ERP5Type.Cache import CachingMethod, DEFAULT_CACHE_SCOPE

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

  cache_duration = 10 # second
  python_script_id = "testCachedMethod"
  nb_iterations = 60000

  def getTitle(self):
    return "Cache Tool"

  def afterSetUp(self):
    self.login()
    self.checkCacheTool()
    self.checkPortalTypes()
    self.createPersistentMemcachedPlugin()
    self.createCacheFactories()
    self.createCachedMethod()
    self.commit()

  def login(self): # pylint:disable=arguments-differ
    uf = self.portal.acl_users
    uf._doAddUser('admin', '', ['Manager'], [])
    uf._doAddUser('ERP5TypeTestCase', '', ['Manager'], [])
    user = uf.getUserById('admin').__of__(uf)
    newSecurityManager(None, user)

  def checkCacheTool(self):
    self.assertIsNot(None, self.portal.portal_caches)

  def checkPortalTypes(self):
    portal_types = self.portal.portal_types
    typeinfo_names = ("Cache Factory",
                      "Ram Cache",
                      "Distributed Ram Cache",
                      )
    for typeinfo_name in typeinfo_names:
      portal_type = getattr(portal_types, typeinfo_name, None)
      self.assertNotEqual(None, portal_type)

  def createPersistentMemcachedPlugin(self):
    portal_memcached = self.portal.portal_memcached
    # setup persistent memcached
    memcached_plugin_id = 'flare'
    if getattr(portal_memcached, memcached_plugin_id, None) is None:
      connection_dict = _getPersistentMemcachedServerDict()
      url_string = '%(hostname)s:%(port)s' % connection_dict
      portal_memcached.newContent(portal_type='Memcached Plugin',
                                  id=memcached_plugin_id,
                                  url_string=url_string,
                                  server_max_key_length=0,
                                  server_max_value_length=0,
                                  priority=1)

  def createCacheFactories(self):
    portal_caches = self.portal.portal_caches

    # Cache plugins are organised into 'Cache factories' so we create
    # factories first ram_cache_factory (to test Ram Cache Plugin)
    if getattr(portal_caches, 'ram_cache_factory', None) is None:
      ram_cache_factory = portal_caches.newContent(portal_type="Cache Factory",
                                            id='ram_cache_factory',
                                            container=portal_caches,
                                            cache_duration=self.cache_duration)
      ram_cache_plugin = ram_cache_factory.newContent(portal_type="Ram Cache")
      ram_cache_plugin.setIntIndex(0)

    if getattr(portal_caches, 'another_ram_cache_factory', None) is None:
      cache_factory = portal_caches.newContent(portal_type="Cache Factory",
                                            id='another_ram_cache_factory',
                                            container=portal_caches,
                                            cache_duration=self.cache_duration)
      cache_plugin = cache_factory.newContent(portal_type="Ram Cache")
      cache_plugin.setIntIndex(0)

    if getattr(portal_caches, 'distributed_ram_cache_factory', None) is None:
      ## distributed_ram_cache_factory (to test Distributed Ram Cache Plugin)
      dram_cache_factory = portal_caches.newContent(portal_type="Cache Factory",
                                            id='distributed_ram_cache_factory',
                                            container=portal_caches,
                                            cache_duration=self.cache_duration)
      dram_cache_plugin = dram_cache_factory.newContent(
                        portal_type="Distributed Ram Cache",
                        specialise='portal_memcached/default_memcached_plugin')
      dram_cache_plugin.setIntIndex(0)

    if getattr(portal_caches, 'distributed_persistent_cache_factory', None) is None:
      ## distributed_ram_cache_factory (to test Distributed Ram Cache Plugin)
      dram_cache_factory = portal_caches.newContent(portal_type="Cache Factory",
                                      id='distributed_persistent_cache_factory',
                                      container=portal_caches,
                                      cache_duration=self.cache_duration)
      dram_cache_plugin = dram_cache_factory.newContent(
                                           portal_type="Distributed Ram Cache",
                                           specialise='portal_memcached/flare')
      dram_cache_plugin.setIntIndex(0)

    if getattr(portal_caches, 'erp5_user_factory', None) is None:

      ## erp5_user_factory (to test a combination of all cache plugins)
      erp5_user_factory = portal_caches.newContent(portal_type="Cache Factory",
                                            id="erp5_user_factory",
                                            cache_duration=self.cache_duration)

      ram_cache_plugin = erp5_user_factory.newContent(portal_type="Ram Cache")
      ram_cache_plugin.setIntIndex(0)
      dram_cache_plugin = erp5_user_factory.newContent(
                        portal_type="Distributed Ram Cache",
                        specialise='portal_memcached/default_memcached_plugin')
      dram_cache_plugin.setIntIndex(1)
    ## update Ram Cache structure
    portal_caches.updateCache()

    ## do we have the same structure we created above?
    self.assertTrue('ram_cache_factory' in CachingMethod.factories)
    self.assertTrue('another_ram_cache_factory' in CachingMethod.factories)
    self.assertTrue('distributed_ram_cache_factory' in CachingMethod.factories)
    self.assertTrue('distributed_persistent_cache_factory' in CachingMethod.factories)
    self.assertTrue('erp5_user_factory' in CachingMethod.factories)

  def createCachedMethod(self):
    portal = self.portal
    if getattr(portal, self.python_script_id, None) is not None:
      portal.manage_delObjects(ids=[self.python_script_id])
    ## add test cached method
    py_script_params = "value=10000, portal_path=('','erp5'), result=''"
    py_script_body = """
portal = context.getPortalObject()
portal.newCacheCookie('cache_tool_test')

return result
"""
    portal.manage_addProduct['PythonScripts'].manage_addPythonScript(
                                                id=self.python_script_id)
    py_script_obj = getattr(portal, self.python_script_id)
    py_script_obj.ZPythonScript_edit(py_script_params, py_script_body)
    return

  def test_01_CacheFactoryOnePlugin(self):
    """ Test cache factory containing only one cache plugin. """
    portal = self.portal
    py_script_obj = getattr(portal, self.python_script_id)
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
    py_script_obj = getattr(self.portal, self.python_script_id)
    cf_name = 'erp5_user_factory'
    my_cache = CachingMethod(py_script_obj,
                             'py_script_obj',
                             cache_factory=cf_name)
    self._cacheFactoryInstanceTest(my_cache, cf_name, clear_allowed=False)


  def _getCacheCookieValue(self):
    return self.portal.getCacheCookie('cache_tool_test')

  def _callCache(self, my_cache, real_calculation=False, result=""):
    before_cookie_value = self._getCacheCookieValue()
    start = time.time()
    cached =  my_cache(self.nb_iterations,
                        portal_path=('', self.portal.getId()),
                        result=result)
    end = time.time()
    calculation_time = end-start
    self.assertEqual(cached, result)
    after_cookie_value = self._getCacheCookieValue()
    # if there is cache miss, then real calculation is done,
    # then the cookie is increased with a value 1
    self.assertEqual(after_cookie_value-before_cookie_value,
                      int(real_calculation))
    return calculation_time

  def _cacheFactoryInstanceTest(self, my_cache, cf_name, clear_allowed):
    portal = self.portal
    print
    print "="*40
    print "TESTING:", cf_name

    result = 'a short value'
    #portal.portal_caches.clearCacheFactory(cf_name)

    def clearCache():
      my_cache.delete(self.nb_iterations,
                    portal_path=('', portal.getId()),
                    result=result)
      self.commit()

    # Make sure we do not have values in cache
    clearCache()

    # redefine callCache to avoid passing parameters all the time
    def callCache(real_calculation=True):
      return self._callCache(my_cache, real_calculation=real_calculation,
                             result=result)
    ## 1st call
    calculation_time = callCache(real_calculation=True)
    print "\n\tCalculation time (1st call)", calculation_time
    self.commit()

    ## 2nd call - should be cached now
    calculation_time = callCache(real_calculation=False)
    print "\n\tCalculation time (2nd call)", calculation_time
    self.commit()

    ## OK so far let's clear cache
    if clear_allowed:
      portal.portal_caches.clearCacheFactory(cf_name)

      ## 1st call
      calculation_time = callCache(real_calculation=True)
      print "\n\tCalculation time (after cache clear)", calculation_time

    # Test delete method on CachingMethod
    print "\n\tCalculation time (3rd call)", calculation_time
    # make sure cache id filled
    calculation_time = callCache(real_calculation=False)

    # Purge the Caching Method
    clearCache()

    # Check that result is computed
    calculation_time = callCache(real_calculation=True)
    print "\n\tCalculation time (4th call)", calculation_time
    self.commit()

  def test_03_cachePersistentObjects(self):
    # storing persistent objects in cache is not allowed, but this check is
    # only performed in unit tests.
    def cache_persistent_obj_func():
      # return a persistent object
      return self.portal
    cached_func = CachingMethod(cache_persistent_obj_func, 'cache_persistent_obj')
    self.assertRaises(TypeError, cached_func)

    def cache_bound_method_func():
      # return a method bound on a persistent object
      return self.portal.getTitle
    cached_func = CachingMethod(cache_bound_method_func, 'cache_bound_method')
    self.assertRaises(TypeError, cached_func)

  def test_04_CheckConcurrentRamCacheDict(self):
    """Check that all RamCache doesn't clear the same cache_dict
    """
    print
    print "="*40
    print "TESTING: Concurrent RamCache"
    portal = self.portal
    result = 'Something short'

    py_script_obj = getattr(portal, self.python_script_id)

    ram_cached_method = CachingMethod(py_script_obj,
                             'py_script_obj',
                             cache_factory='ram_cache_factory')

    portal.portal_caches.clearCache(cache_factory_list=('ram_cache_factory',
                                                 'another_ram_cache_factory',))
    # First call, fill the cache
    start = time.time()
    cached = ram_cached_method(self.nb_iterations,
                               portal_path=('', portal.getId()),
                               result=result)
    end = time.time()
    calculation_time = end-start
    print "\n\tCalculation time (1st call)", calculation_time
    self.assertEqual(cached, result)
    self.commit()

    ## 2nd call - should be cached now
    start = time.time()
    cached = ram_cached_method(self.nb_iterations,
                               portal_path=('', portal.getId()),
                               result=result)
    end = time.time()
    calculation_time = end-start
    print "\n\tCalculation time (2nd call)", calculation_time
    self.assertTrue(1.0 > calculation_time, "1.0 <= %s" % calculation_time)
    self.assertEqual(cached, result)
    self.commit()

    # Clear only another_ram_cache_factory
    portal.portal_caches.clearCacheFactory('another_ram_cache_factory')
    # Call conversion for ram_cache_factory
    start = time.time()
    cached = ram_cached_method(self.nb_iterations,
                               portal_path=('', portal.getId()),
                               result=result)
    end = time.time()
    calculation_time = end-start
    print "\n\tCalculation time (3rd call)", calculation_time
    self.assertTrue(1.0 > calculation_time, "1.0 <= %s" % calculation_time)
    self.assertEqual(cached, result)
    self.commit()

  def test_05_CheckLongKeysAndLargeValues(self):
    """Check that persistent distributed Cache Plugin can handle keys
    more than 250 bytes and values more than 1024 bytes.
    """
    print
    print '=' * 40
    print 'TESTING: Long Keys and Large values'
    portal = self.portal
    # import the local and clear it
    from Products.ERP5Type.CachePlugins.DistributedRamCache import\
                                                                connection_pool
    getattr(connection_pool, 'local_dict', {}).clear()

    python_script_id = 'ERP5Site_getLargeStringValue'
    portal.manage_addProduct['PythonScripts'].manage_addPythonScript(
                                                           id=python_script_id)
    # Edit python script which return large value ie: 25 MB string
    py_script_obj = getattr(portal, python_script_id)
    py_script_params = "value=10000, long_parameter=''"
    py_script_body = """
def veryExpensiveMethod(value):
  # do something expensive for some time
  # no 'time.sleep()' available in Zope
  # so concatenate strings
  s = ''
  for i in range(0, value):
    s = str(value * value * value) + s
  return value

veryExpensiveMethod(value)
return 'a' * 1024 * 1024 * 25
"""
    py_script_obj.ZPythonScript_edit(py_script_params, py_script_body)
    result = 'a' * 1024 * 1024 * 25 # 25 MB
    long_parameter = 'a' * 1024

    py_script_obj = getattr(portal, python_script_id)

    # First, call a ram based distributed cache to
    # trig a bug which fill in the MemcachedDict connection pool
    # with the first created instance.
    # If later another CachePlugin try to access its own memcached_connection
    # The first one is returned event if the configuration is different.
    def myLocalFunction(**kw):
      return None
    cached_method = CachingMethod(myLocalFunction,
                                  'py_script_obj',
                           cache_factory='distributed_ram_cache_factory')
    cached_method()
    # Check that Cache plugin create new connection in pool
    self.assertEqual(1, len(connection_pool.local_dict))

    # Now test long keys and large values
    cached_method = CachingMethod(py_script_obj,
                                  'py_script_obj',
                          cache_factory='distributed_persistent_cache_factory')

    #First call, fill the cache
    start = time.time()
    cached = cached_method(self.nb_iterations,
                           long_parameter=long_parameter)
    end = time.time()
    calculation_time = end-start
    print "\n\tCalculation time (1st call)", calculation_time
    self.assertEqual(cached, result)
    self.commit()

    # Check that Cache plugin create a second connection in pool
    self.assertEqual(2, len(connection_pool.local_dict))

    ## 2nd call - should be cached now
    start = time.time()
    cached = cached_method(self.nb_iterations,
                           long_parameter=long_parameter)
    end = time.time()
    calculation_time = end-start
    print "\n\tCalculation time (2nd call)", calculation_time
    self.assertTrue(1.0 > calculation_time, "1.0 <= %s" % calculation_time)
    self.assertEqual(cached, result)
    self.commit()

  def test_06_CheckCacheExpiration(self):
    """Check that expiracy is well handle by Cache Plugins
    """
    print
    print "="*40
    print "TESTING: Cache Expiration Time"

    py_script_obj = getattr(self.portal, self.python_script_id)

    cache_factory_list = ('ram_cache_factory', 'distributed_ram_cache_factory',
                          'distributed_persistent_cache_factory')
    for cache_factory in cache_factory_list:
      print '\n\t==> %s' % cache_factory
      my_cache = CachingMethod(py_script_obj,
                               'py_script_obj',
                               cache_factory=cache_factory)

      # First call, fill the cache
      calculation_time = self._callCache(my_cache, real_calculation=True)
      print "\n\tCalculation time (1st call)", calculation_time

      ## 2nd call - should be cached now
      calculation_time = self._callCache(my_cache, real_calculation=False)
      print "\n\tCalculation time (2nd call)", calculation_time

      # Wait expiration period then check that value is computed
      # .1 is an additional epsilon delay to work around time precision issues
      time_left_to_wait = .1 + self.cache_duration
      print "\n\tSleep %.2f seconds to wait expiration time" % time_left_to_wait
      time.sleep(time_left_to_wait)

      # Call conversion for ram_cache_factory
      calculation_time = self._callCache(my_cache, real_calculation=True)
      print "\n\tCalculation time (3rd call)", calculation_time

  def test_06_CheckCacheBag(self):
    """
      Check Cache Bag
    """
    portal_caches = self.portal.portal_caches
    cache_factory = portal_caches.newContent(portal_type="Cache Factory",
                                         cache_duration=3600)
    cache_bag = cache_factory.newContent(portal_type="Cache Bag",
                                         cache_duration=3600)

    cache_plugin1 = cache_bag.newContent(portal_type="Ram Cache")
    cache_plugin1.setIntIndex(0)

    cache_plugin2 = cache_bag.newContent(portal_type="Ram Cache")
    cache_plugin2.setIntIndex(1)
    self.tic()
    portal_caches.updateCache()

    # test proper init
    ram_cache_factory_plugin_list = cache_bag.getRamCacheFactoryPluginList()
    self.assertEqual(2, len(ram_cache_factory_plugin_list))

    # test get / set API
    cache_bag.set('x', 'value_fox_x')
    self.assertEqual('value_fox_x', cache_bag.get('x'))

    # test that only first cache plugin is used to set
    self.assertEqual('value_fox_x',
                     ram_cache_factory_plugin_list[0].get('x',DEFAULT_CACHE_SCOPE).getValue())
    self.assertRaises(KeyError, ram_cache_factory_plugin_list[1].get, 'x', DEFAULT_CACHE_SCOPE)

    # check hot copy happens from second in order plugin to first
    ram_cache_factory_plugin_list[1].set('y', DEFAULT_CACHE_SCOPE, 'value_for_y', cache_bag.cache_duration)
    self.assertEqual('value_for_y', cache_bag.get('y'))
    self.assertEqual('value_for_y', ram_cache_factory_plugin_list[0].get('y',DEFAULT_CACHE_SCOPE).getValue())

  def test_07_CheckCacheFactory(self):
    """
      Check Cache Factory set and get API.
    """
    portal_caches = self.portal.portal_caches

    cache_factory = portal_caches.newContent(portal_type="Cache Factory",
                                         cache_duration=3600)

    cache_plugin1 = cache_factory.newContent(portal_type="Ram Cache")
    cache_plugin1.setIntIndex(0)

    cache_bag1 = cache_factory.newContent(portal_type="Cache Bag",
                                         cache_duration=3600)
    cache_bag1.setIntIndex(1)
    cache_bag1.newContent(portal_type="Ram Cache")
    cache_bag1.newContent(portal_type="Ram Cache")
    self.tic()
    portal_caches.updateCache()

    # test get / set API
    cache_factory.set('x', 'value_for_x')
    self.assertEqual('value_for_x', cache_factory.get('x'))

    # test that all cache plugin have this set
    self.assertEqual('value_for_x', cache_plugin1.get('x'))
    self.assertEqual('value_for_x', cache_bag1.get('x'))

    # test set on individual cache plugin as this cache plugin has highest priority
    # it will affect what root Cache Factory returns
    cache_plugin1.set('x', 'new_value_for_x')
    self.assertEqual('new_value_for_x', cache_plugin1.get('x'))
    self.assertEqual('new_value_for_x', cache_factory.get('x'))
    # others cache plugins will remain with old value until ...
    self.assertEqual('value_for_x', cache_bag1.get('x'))
    # .. root Cache Factory set will update all
    cache_factory.set('x', 'new_value_for_x')
    self.assertEqual(cache_factory.get('x'), cache_plugin1.get('x'))
    self.assertEqual(cache_plugin1.get('x'), cache_bag1.get('x'))
    self.assertEqual('new_value_for_x', cache_factory.get('x'))

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

