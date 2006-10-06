""" 
Base Cache plugin.
"""


#from Products.ERP5Cache.interfaces import ICache
import time

class CachedMethodError(Exception): 
  pass

class CacheEntry(object):
  """ Cachable entry.  Used as a wrapper around real values stored in cache.
  value
  cache_duration
  stored_at
  cache_hits
  calculation_time
  TODO: Based on above data we can have a different invalidation policy
  """
    
  def __init__(self, value, cache_duration=None, calculation_time=0):
    self.value = value
    self.cache_duration = cache_duration
    self.stored_at = int(time.time())
    self.cache_hits = 0
    self.calculation_time = calculation_time

       
  def isExpired(self):
    """ check cache entry for expiration """
    if self.cache_duration is None or self.cache_duration==0:
      ## cache entry can stay in cache forever until zope restarts
      return False
    now = int(time.time())
    if now > (self.stored_at + int(self.cache_duration)):
      return True
    else:
      return False
    
  def markCacheHit(self, delta=1):
    """ mark a read to this cache entry """
    self.cache_hits = self.cache_hits + delta 
    
  def getValue(self):
    """ return cached value """ 
    return getattr(self, 'value', None)


class BaseCache(object):
  """ Base Cache class """
    
  #__implements__ = (ICache,)
    
  ## Time interval (s) to check for expired objects
  cache_expire_check_interval = 60
    
  def __init__(self, params={}):
    self._last_cache_expire_check_at = time.time()
    self._cache_hits = 0
    self._cache_misses = 0
        
  def markCacheHit(self, delta=1):
    """ Mark a read operation from cache """
    self._cache_hits = self._cache_hits + delta

  def markCacheMiss(self, delta=1):
    """ Mark a write operation to cache """
    self._cache_misses = self._cache_misses + delta

  def getCacheHits(self):
    """ get cache hits """
    return self._cache_hits

  def getCacheMisses(self):
    """ get cache missess """
    return self._cache_misses
    
  def clearCache(self):
    """ Clear cache """
    self._cache_hits = 0
    self._cache_misses = 0
