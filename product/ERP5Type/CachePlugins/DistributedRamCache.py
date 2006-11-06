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
Memcached based cache plugin.
"""

from BaseCache import *
from time import time
from zLOG import LOG

try:
  import memcache
  MEMCACHED_SERVER_MAX_KEY_LENGTH = memcache.SERVER_MAX_KEY_LENGTH
except ImportError:
  LOG('DistributedRamCache',0,'unable to import memcache')

## number of seconds before creating a new connection to memcached server
##KEEP_ALIVE_MEMCACHED_CONNECTION_INTERVAL = 30  
 
class DistributedRamCache(BaseCache):
  """ Memcached based cache plugin. """

  def __init__(self, params):
    self._servers = params.get('server', '')
    self._debugLevel = params.get('debugLevel', 7)
    self._last_cache_conn_creation_time = time()
    BaseCache.__init__(self)
        
  def getCacheStorage(self):
    ## if we use one connection object this causes  "MemCached: while expecting 'STORED', got unexpected response 'END'"
    ## messages in log files and thus sometimes can block the thread. For the moment we create
    ## a new conn object for every memcache access which in turns means another socket. 
    ## See  addiionaly expireOldCacheEntries() comments for one or many connections.
    try:
      from Products.ERP5Type.Utils import get_request
      request = get_request()
    except ImportError:
      request = None
      
    if request is not None:
      ## Zope/ERP5 environment
      memcache_conn = request.get('_erp5_memcache_connection', None)
      if not memcache_conn:
        ## we have not memcache_conn for this request
        memcache_conn = memcache.Client(self._servers.split('\n'), debug=self._debugLevel)
        request.set('_erp5_memcache_connection', memcache_conn)
        return memcache_conn      
      else:
        ## we have memcache_conn for this request
        return memcache_conn
    else:
      ## run from unit tests
      return  memcache.Client(self._servers.split('\n'), debug=self._debugLevel)
       
  def checkAndFixCacheId(self, cache_id, scope):
    ## memcached doesn't support namespaces (cache scopes) so to "emmulate"
    ## such behaviour when constructing cache_id we add scope in front
    cache_id = "%s.%s" %(scope, cache_id) 
    ## memcached will fail to store cache_id longer than MEMCACHED_SERVER_MAX_KEY_LENGTH.
    if len(cache_id) > MEMCACHED_SERVER_MAX_KEY_LENGTH:
      cache_id = cache_id[:MEMCACHED_SERVER_MAX_KEY_LENGTH]
    return cache_id
    
  def get(self, cache_id, scope, default=None):
    cache_storage = self.getCacheStorage()
    cache_id = self.checkAndFixCacheId(cache_id, scope)
    cache_entry = cache_storage.get(cache_id)
    self.markCacheHit()
    return cache_entry
       
  def set(self, cache_id, scope, value, cache_duration= None, calculation_time=0):
    cache_storage = self.getCacheStorage()
    cache_id = self.checkAndFixCacheId(cache_id, scope)
    if not cache_duration:
      ## what should be default cache_duration when None is specified?
      ## currently when 'None' it means forever so give it  big value of 100 hours
      cache_duration = 360000
    cache_entry = CacheEntry(value, cache_duration, calculation_time)
    cache_storage.set(cache_id, cache_entry, cache_duration)
    self.markCacheMiss()
   
  def expireOldCacheEntries(self, forceCheck = False):
    """ Memcache has its own built in expire policy """
    ## we can not use one connection to memcached server for time being of DistributedRamCache
    ## because if memcached is restarted for any reason our connection object will have its socket 
    ## to memcached server closed.
    ## The workaround of this problem is to create a new connection for every cache access
    ## but that's too much overhead or create a new connection when cache is to be expired. 
    ## This way we can catch memcached server failures. BTW: This hack is forced by the lack functionality in python-memcached 
    #self._cache = memcache.Client(self._servers.split('\n'), debug=self._debugLevel) 
    pass    
        
  def delete(self, cache_id, scope):
    cache_storage = self.getCacheStorage()
    cache_id = self.checkAndFixCacheId(cache_id, scope)
    cache_storage.delete(cache_id)
        
  def has_key(self, cache_id, scope):
    if self.get(cache_id, scope):
      return True
    else:
      return False

  def getScopeList(self):
    ## memcached doesn't support namespaces (cache scopes) neither getting cached key list 
    return []
    
  def getScopeKeyList(self, scope):
    ## memcached doesn't support namespaces (cache scopes) neither getting cached key list 
    return []

  def clearCache(self):
    BaseCache.clearCache(self)
    cache_storage = self.getCacheStorage()
    cache_storage.flush_all()
    
  def clearCacheForScope(self, scope):
    ## memcached doesn't support namespaces (cache scopes) neither getting cached key list 
    pass       
