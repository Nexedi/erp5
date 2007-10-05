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

"""
Local RAM based cache plugin.
"""
from Products.ERP5Type.Cache import DEFAULT_CACHE_SCOPE
from BaseCache import *
import time

def calcPythonObjectMemorySize(i):
  """ Recursive function that will 'walk' over complex python types and caclulate
      their RAM memory usage. """
  from mx.Tools import sizeof
  s = sizeof(i)
  if isinstance(i, dict):
    for k, v in i.items():
      s += calcPythonObjectMemorySize(k) + calcPythonObjectMemorySize(v)
  elif isinstance(i, list) or isinstance(i, tuple):
    for v in i:
      s += calcPythonObjectMemorySize(v)
  return s

class RamCache(BaseCache):
  """ RAM based cache plugin."""
   
  _cache_dict = {}
  cache_expire_check_interval = 300
    
  def __init__(self, params={}):
    BaseCache.__init__(self)
 
  def initCacheStorage(self):
    """ Init cache storage """
    ## cache storage is a RAM based dictionary
    pass
    
  def getCacheStorage(self):
    return self._cache_dict
    
  def get(self, cache_id, scope, default=None):
    cache = self.getCacheStorage()
    if self.has_key(cache_id, scope):
      cache_entry = cache[scope].get(cache_id, default)
      cache_entry.markCacheHit()
      self.markCacheHit()
      return cache_entry
    else:
      return default
            
  def set(self, cache_id, scope, value, cache_duration=None, calculation_time=0):
    cache = self.getCacheStorage()
    if not cache.has_key(scope):
      ## cache scope not initialized
      cache[scope] = {}
    cache[scope][cache_id] = CacheEntry(value, cache_duration, calculation_time)
    self.markCacheMiss()

  def expireOldCacheEntries(self, forceCheck = False):
    now = time.time()
    if forceCheck or (now > (self._last_cache_expire_check_at + self.cache_expire_check_interval)):
      ## time to check for expired cache items
      self._last_cache_expire_check_at = now
      cache = self.getCacheStorage()        
      for scope in cache.keys():
        for (cache_id, cache_item) in cache[scope].items():
          if cache_item.isExpired()==True:
            del cache[scope][cache_id]

  def delete(self, cache_id, scope):
    try:
      del self.getCacheStorage()[scope][cache_id]
    except KeyError:
      pass

  def has_key(self, cache_id, scope):
    cache = self.getCacheStorage()
    if not cache.has_key(scope):
      ## cache scope not initialized
      cache[scope] = {}
    return cache[scope].has_key(cache_id)

  def getScopeList(self):
    scope_list = []
    ## some cache scopes in RAM Cache can have no cache_ids keys but 
    ## they do exists. To have consistent behaviour with SQLCache plugin 
    ## where cache scope will not exists without its cache_ids we filter them.  
    for scope, item in self.getCacheStorage().items():
      if item!={}:
        scope_list.append(scope)
    return scope_list
    
  def getScopeKeyList(self, scope):
    return self.getCacheStorage()[scope].keys()
    
  def clearCache(self):
    BaseCache.clearCache(self)
    self._cache_dict = {DEFAULT_CACHE_SCOPE: {}} 
    
  def clearCacheForScope(self, scope):
    try:
      self.getCacheStorage()[scope] = {}
    except KeyError:
      pass
      
  def getCachePluginTotalMemorySize(self):
    """ Calculate total RAM memory size of cache plugin. 
        This function depends on mxBase python module:
        http://www.egenix.com/products/python/mxBase/
        """
    total_size = 0
    cache_keys_total_size = {}
    for cache_key, cache_value in self._cache_dict[DEFAULT_CACHE_SCOPE].items():
      cache_item_size = calcPythonObjectMemorySize(cache_value.getValue())
      total_size += cache_item_size
      cache_keys_total_size[cache_key] = cache_item_size
    return total_size, cache_keys_total_size      
