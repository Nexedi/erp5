"""
Local RAM based cache plugin.
"""


from BaseCache import *
import time

class RamCache(BaseCache):
  """ RAM based cache plugin."""
   
  _cache_dict = {}
  cache_expire_check_interval = 300
    
  def __init__(self, params={}):
    BaseCache.__init__(self)
            
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
      #print "EXPIRE ", self, self.cache_expire_check_interval
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
    self._cache_dict = {} 

  def clearCacheForScope(self, scope):
    try:
      self.getCacheStorage()[scope] = {}
    except KeyError:
      pass
