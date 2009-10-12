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

"""
Memcached based cache plugin.
"""
from threading import local
from zLOG import LOG, WARNING
from BaseCache import BaseCache
from BaseCache import CacheEntry
from Products.ERP5Type import interfaces
import zope.interface
from base64 import encodestring

try:
  import memcache
  from Products.ERP5Type.Tool.MemcachedTool import MemcachedDict, SharedDict
except ImportError:
  LOG('DistributedRamCache', 0, 'unable to import memcache')

## global ditionary containing connection objects
connection_pool = local()

_MARKER = []

class DistributedRamCache(BaseCache):
  """ Memcached based cache plugin. """

  zope.interface.implements(
        interfaces.ICachePlugin
    )

  def __init__(self, params={}):
    self._servers = params.get('server', '')
    self._server_max_key_length = params.get('server_max_key_length', 250)
    self._server_max_value_length = params.get('server_max_value_length', 1024*1024)
    self._debug_level = params.get('debug_level', 0)
    self._key_prefix = params.get('key_prefix', '')
    BaseCache.__init__(self)

  def initCacheStorage(self):
    """ Init cache storage """
    ## cache storage is a memcached server and no need to init it
    pass

  def getCacheStorage(self, **kw):
    ## if we use one connection object this causes 
    ## "MemCached: while expecting 'STORED', got unexpected response 'END'"
    ## messages in log files and can sometimes can block the thread. 
    ## For the moment we create a new conn object for every thread.
    try:
      dictionary = connection_pool.memcached_dict
    except AttributeError:
      dictionary = SharedDict(
        MemcachedDict(self._servers.split('\n'),
                      server_max_key_length=self._server_max_key_length,
                      server_max_value_length=self._server_max_value_length),
        prefix=self._key_prefix)
      connection_pool.memcached_dict = dictionary
    return dictionary

  def _getCacheId(self, cache_id, scope):
    return '%s_%s' % (scope, cache_id)

  def get(self, cache_id, scope, default=_MARKER):
    cache_storage = self.getCacheStorage()
    cache_id = self._getCacheId(cache_id, scope)
    cache_entry = cache_storage.get(cache_id)
    #Simulate the behaviour of a standard Dictionary
    if not isinstance(cache_entry, CacheEntry):
      if default is _MARKER:
        #Error to connect memcached server
        raise KeyError('Failed to retrieve value or to access memcached server: %s' % self._servers)
      else:
        return default
    # since some memcached-like products does not support expiration, we
    # check it by ourselves.
    if cache_entry.isExpired():
      del cache_storage[cache_id]
      return default
    self.markCacheHit()
    return cache_entry

  def set(self, cache_id, scope, value, cache_duration=None, calculation_time=0):
    cache_storage = self.getCacheStorage()
    cache_id = self._getCacheId(cache_id, scope)
    cache_entry = CacheEntry(value, cache_duration, calculation_time)
    cache_storage.set(cache_id, cache_entry)
    self.markCacheMiss()

  def expireOldCacheEntries(self, forceCheck = False):
    """ Memcache has its own built in expire policy """
    ## we can not use one connection to memcached server for time being of DistributedRamCache
    ## because if memcached is restarted for any reason our connection object will have its socket 
    ## to memcached server closed.
    ## The workaround of this problem is to create a new connection for every cache access
    ## but that's too much overhead or create a new connection when cache is to be expired. 
    ## This way we can catch memcached server failures. BTW: This hack is forced by the lack functionality in python-memcached 
    #self._cache = memcache.Client(self._servers.split('\n'), debug=self._debug_level) 
    pass

  def delete(self, cache_id, scope):
    cache_storage = self.getCacheStorage()
    cache_id = self._getCacheId(cache_id, scope)
    del cache_storage[cache_id]

  def has_key(self, cache_id, scope):
    cache_storage = self.getCacheStorage()
    cache_id = self._getCacheId(cache_id, scope)
    cache_entry = cache_storage.get(cache_id)
    to_return = False
    if isinstance(cache_entry, CacheEntry):
      if cache_entry.isExpired():
        del cache_storage[cache_id]
      else:
        to_return = True
    return to_return

  def getScopeList(self):
    ## memcached doesn't support namespaces (cache scopes) neither getting cached key list 
    return []

  def getScopeKeyList(self, scope):
    ## memcached doesn't support namespaces (cache scopes) neither getting cached key list 
    return []

  def clearCache(self):
    """This method is disabled because it clear unique storage shared by other
    client.
    Use expiration time instead.
    """
    BaseCache.clearCache(self)
    LOG('DistributedRamCache', WARNING, 'not allowed to clear memcache storage')

  def clearCacheForScope(self, scope):
    ## memcached doesn't support namespaces (cache scopes) neither getting cached key list.
    ## Becasue we've explicitly called this function instead of clearing specific cache 
    ## scope we have no choice but clear whole cache.
    self.clearCache()

  def getCachePluginTotalMemorySize(self):
    """ Calculate total RAM memory size of cache plugin. """
    return 0, {}
