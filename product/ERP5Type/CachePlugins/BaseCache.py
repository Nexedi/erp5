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
Base Cache plugin.
"""

import time

class CachedMethodError(Exception):
  pass

class CacheEntry(object):
  """ Cachable entry.  Used as a wrapper around real values stored in cache.
  value
  expires_at
  cache_hits
  calculation_time
  TODO: Based on above data we can have a different invalidation policy
  """

  def __init__(self, value, cache_duration=None, calculation_time=0):
    self.value = value
    if cache_duration in (None, 0):
      self.expires_at = None
    else:
      self.expires_at = time.time() + cache_duration
    self._cache_hit_count = 0
    self.calculation_time = calculation_time

  def isExpired(self):
    """ check cache entry for expiration """
    return self.expires_at < time.time() or self.expires_at is None

  def markCacheHit(self, delta=1):
    """ mark a read to this cache entry """
    self._cache_hit_count = self._cache_hit_count + delta 

  def getValue(self):
    """ return cached value """ 
    return getattr(self, 'value', None)

ACTIVATE_TRACKING = False

class BaseCache(object):
  """ Base Cache class """

  ## Time interval (s) to check for expired objects
  cache_expire_check_interval = 60

  def __init__(self, params={}):
    self._next_cache_expire_check_at = time.time()
    self._cache_hit_count = 0
    self._cache_miss_count = 0

  def markCacheHit(self, delta=1):
    """ Mark a read operation from cache """
    if ACTIVATE_TRACKING:
      self._cache_hit_count = self._cache_hit_count + delta

  def markCacheMiss(self, delta=1):
    """ Mark a write operation to cache """
    if ACTIVATE_TRACKING:
      self._cache_miss_count = self._cache_miss_count + delta

  def getCacheHitCount(self):
    """ get cache hits """
    return self._cache_hit_count

  def getCacheMissCount(self):
    """ get cache missess """
    return self._cache_miss_count

  def clearCache(self):
    """ Clear cache """
    self._cache_hit_list = 0
    self._cache_miss_count = 0
