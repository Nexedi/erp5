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
Local RAM based cache plugin.
"""
from __future__ import absolute_import

import time
from .BaseCache import BaseCache, CacheEntry
from Products.ERP5Type import interfaces
import zope.interface
import six

def calcPythonObjectMemorySize(i):
  """
  Returns the memory size of an object.
  (returns 0 if the required library is missing).
  """
  try:
    from pympler.asizeof import asizeof
    return asizeof(i)
  except ImportError:
    return 0

_MARKER = []
@zope.interface.implementer(
        interfaces.ICachePlugin)
class RamCache(BaseCache):
  """ RAM based cache plugin."""

  cache_expire_check_interval = 300

  def __init__(self, uid, params={}):
    self._cache_dict = {}
    BaseCache.__init__(self, uid)

  def initCacheStorage(self):
    """ Init cache storage """
    ## cache storage is a RAM based dictionary
    pass

  def getCacheStorage(self, **kw):
    return self._cache_dict

  def get(self, cache_id, scope, default=_MARKER):
    cache = self.getCacheStorage()
    cache_entry = cache.get((scope, cache_id), _MARKER)
    if cache_entry is not _MARKER:
      if not cache_entry.isExpired():
        #The value is well retrieved from cache storage
        self.markCacheHit()
        return cache_entry
      else:
        #Delete expired CacheEntry
        self.delete(cache_id, scope)
    if default is _MARKER:
      raise KeyError('CacheEntry for key %s not Found' % ((scope, cache_id),))
    return default

  def set(self, cache_id, scope, value, cache_duration=None, calculation_time=0):
    cache = self.getCacheStorage()
    cache[(scope, cache_id)] = CacheEntry(value, cache_duration, calculation_time)
    self.markCacheMiss()

  def expireOldCacheEntries(self, forceCheck=False):
    now = time.time()
    if forceCheck or (now > self._next_cache_expire_check_at):
      ## time to check for expired cache items
      self._next_cache_expire_check_at = now + self.cache_expire_check_interval
      cache = self.getCacheStorage()
      for key, value in cache.items():
        if value.isExpired():
          try:
            del cache[key]
          except KeyError:
            # The key might have disappeared, due to multi-threading.
            pass

  def delete(self, cache_id, scope):
    try:
      del self.getCacheStorage()[(scope, cache_id)]
    except KeyError:
      pass

  def has_key(self, cache_id, scope):
    cache = self.getCacheStorage()
    cache_entry = cache.get((scope, cache_id))
    to_return = False
    if isinstance(cache_entry, CacheEntry):
      if cache_entry.isExpired():
        #Delete expired CacheEntry
        self.delete(cache_id, scope)
      else:
        to_return = True
    return to_return

  def getScopeList(self):
    scope_set = set()
    for scope, cache_id in six.iterkeys(self.getCacheStorage()):
      scope_set.add(scope)
    return list(scope_set)

  def getScopeKeyList(self, scope):
    key_list = []
    for key in six.iterkeys(self.getCacheStorage()):
      if scope == key[0]:
        key_list.append(key[1])
    return key_list

  def clearCache(self):
    BaseCache.clearCache(self)
    self.getCacheStorage().clear()

  def clearCacheForScope(self, scope):
    cache = self.getCacheStorage()
    for key in cache.keys():
      if key[0] == scope:
        try:
          del cache[key]
        except KeyError:
          # The key might have disappeared, due to multi-threading.
          pass

  def getCachePluginTotalMemorySize(self):
    """ Calculate total RAM memory size of cache plugin.
        This function depends on mxBase python module:
        http://www.egenix.com/products/python/mxBase/
        """
    total_size = 0
    cache_keys_total_size = {}
    cache = self.getCacheStorage()
    for key, value in six.iteritems(cache):
      value_size = calcPythonObjectMemorySize(value)
      total_size += value_size
      cache_keys_total_size[key[1]] = value_size
    return total_size, cache_keys_total_size
