from Interface import Interface

class ICache(Interface):
  """ Cache interace """

  def get(self, key, default=None):
    """ Get key from cache """

  def set(self, key, value, timeout=None):
    """ Set key to cache """

  def delete(self, key):
    """ Delete key from cache """

  def has_key(self, key):
    """ Returns True if the key is in the cache and has not expired """

  def getScopeList(self):
    """ get available user scopes """
    
  def getScopeKeyList(self, scope):
    """ get keys for cache scope """
            
  def clearCache(self):
    """ Clear whole cache """

  def clearCacheForScope(self, scope):
    """ Clear cache for scope """
