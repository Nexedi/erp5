"Local RAM based cache"

from BaseCache import *
import time

class DummyCache(BaseCache):
  """ Dummy cache plugin. """
    
  def __init__(self, params):
    BaseCache.__init__(self)
 
  def __call__(self, callable_object, cache_id, cache_duration=None, *args, **kwd):
    ## Just calculate and return result - no caching 
    return callable_object(*args, **kwd)
        
  def getCacheStorage(self):
    pass
    
  def get(self, cache_id, scope, default=None):
    pass
       
  def set(self, cache_id, scope, value, cache_duration= None, calculation_time=0):
    pass

  def expireOldCacheEntries(self, forceCheck = False):
    pass
        
  def delete(self, cache_id, scope):
    pass
        
  def has_key(self, cache_id, scope):
    pass
        
  def getScopeList(self):
    pass
        
  def getScopeKeyList(self, scope):
    pass
        
  def clearCache(self):
    pass
        
  def clearCacheForScope(self, scope):
    pass
    
