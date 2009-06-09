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

import random
import unittest
import time
import os

from Products.ERP5Type.CachePlugins.RamCache import RamCache
from Products.ERP5Type.CachePlugins.DistributedRamCache import\
                                              DistributedRamCache
from Products.ERP5Type.CachePlugins.BaseCache import CacheEntry
from Products.ERP5Type.Tool.CacheTool import CacheTool


class Foo:
  my_field = (1,2,3,4,5)

class TestRamCache(unittest.TestCase):
  quiet = 1

  def getTitle(self):
    return "Cache"

  def setUp(self):
    self.cache_plugins = (RamCache(),
                          DistributedRamCache({'server': '127.0.0.1:11211',
                                                 'debugLevel': 7,}),
                        )

  def testScope(self):
    """ test scope functions """
    ## create some sample scopes
    iterations = 10
    test_scopes = []
    for i in range(0, iterations):
        test_scopes.append("my_scope_%s" %i)
    test_scopes.sort()
    
    ## remove DistributedRamCache since it's a flat storage
    filtered_cache_plugins = filter(
        lambda x: not isinstance(x, DistributedRamCache), self.cache_plugins)
    
    for cache_plugin in filtered_cache_plugins:
      if not self.quiet:
        print "TESTING (scope): ", cache_plugin

      ## clear cache for this plugin
      cache_plugin.clearCache()
      
      ## should exists no scopes in cache
      self.assertEqual([], cache_plugin.getScopeList())
      
      ## set some sample values 
      for scope in test_scopes:
        cache_id = '%s_cache_id' %scope
        cache_plugin.set(cache_id, scope, scope*10)
        
        ## we set ONLY one value per scope -> check if we get the same cache_id
        self.assertEqual([cache_id], cache_plugin.getScopeKeyList(scope))
        if not self.quiet:
          print "\t", cache_id, scope, "\t\tOK"
      
      ## get list of scopes which must be the same as test_scopes since we clear cache initially
      scopes_from_cache = cache_plugin.getScopeList()
      scopes_from_cache.sort()
      self.assertEqual(test_scopes, scopes_from_cache)
      
      ## remove scope one by one
      count = 1 
      for scope in test_scopes:
        cache_plugin.clearCacheForScope(scope)
        ## .. and check that  we should have 1 less cache scope 
        scopes_from_cache = cache_plugin.getScopeList()
        self.assertEqual(iterations - count, len(scopes_from_cache))
        count = count + 1
        
      ## .. we shouldn't have any cache scopes 
      scopes_from_cache = cache_plugin.getScopeList()
      self.assertEqual([], scopes_from_cache)

      
  def testSetGet(self):
    """ set value to cache and then get it back """
    for cache_plugin in self.cache_plugins:
      self.generaltestSetGet(cache_plugin, 100)
    
  def testExpire(self):
    """ Check expired by setting a key, wit for its timeout and check if in
    cache"""
    for cache_plugin in self.cache_plugins:
      self.generalExpire(cache_plugin, 2)

            
  def generalExpire(self, cache_plugin, iterations):
    if not self.quiet:
      print "TESTING (expire): ", cache_plugin
    base_timeout = 1
    values = self.prepareValues(iterations)
    scope = "peter"
    count = 0
    for value in values:
      count = count +1
      cache_timeout = base_timeout + random.random()*2
      cache_id = "mycache_id_to_expire_%s" %(count)
      if not self.quiet:
        print "\t", cache_id, " ==> timeout (s) = ", cache_timeout,

      ## set to cache
      cache_plugin.set(cache_id, scope, value, cache_timeout)
        
      ## sleep for timeout +1
      time.sleep(cache_timeout + 1)
        
      ## should remove from cache expired cache entries 
      cache_plugin.expireOldCacheEntries(forceCheck=True)
        
      ##  check it, we MUST NOT have this key any more in cache
      self.assertEqual(False, cache_plugin.has_key(cache_id, scope))
      if not self.quiet:
        print "\t\tOK"
     
  def generaltestSetGet(self, cache_plugin, iterations):
    if not self.quiet:
      print "TESTING (set/get/has/del): ", cache_plugin
    values = self.prepareValues(iterations)
    cache_duration = 30
    scope = "peter"
    count = 0
    for value in values:
      count = count +1
      cache_id = "mycache_id_to_set_get_has_del_%s" %(count)
        
      ## set to cache
      cache_plugin.set(cache_id, scope, value, cache_duration)
      if not self.quiet:
        print "\t", cache_id,
        
      ## check has_key()
      self.assertEqual(True, cache_plugin.has_key(cache_id, scope))
        
      ## check get()
      cache_entry = cache_plugin.get(cache_id, scope)
      if isinstance(value, Foo):
        ## when memcached or sql cached we have a new object created for user
        ## just compare one field from it
        self.assertEqual(value.my_field, cache_entry.getValue().my_field)
      else:
        ## primitive types, direct comparision
        self.assertEqual(value, cache_entry.getValue())
        
      ## is returned result proper cache entry?
      self.assertEqual(True, isinstance(cache_entry, CacheEntry))
        
      ## is returned result proper type?
      self.assertEqual(type(value), type(cache_entry.getValue()))
        
      ## check delete(), key should be removed from there
      cache_plugin.delete(cache_id, scope)
      self.assertEqual(False, cache_plugin.has_key(cache_id, scope))
        
      if not self.quiet:
        print "\t\tOK"
    
  def prepareValues(self, iterations):
    """ generate a big list of values """
    values = []
    my_text = "".join(map(chr, range(50,200))) * 10 ## long string (150*x)
    for i in range(0, iterations):
      values.append(random.random()*i)
      values.append(random.random()*i/1000)
      values.append(my_text)
      values.append(Foo())
    return values

if __name__ == '__main__':
  unittest.main()
