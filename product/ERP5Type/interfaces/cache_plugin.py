# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Nicolas Delaby <nicolas@nexedi.com>
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

from zope.interface import Interface

class ICachePlugin(Interface):
  """CachePlugin Interface Specification
  """

  def __init__(params={}):
    """Initialise default values
    """

  def clearCache():
    """Delete all caches
    """

  def clearCacheForScope(scope):
    """Delete all caches according to scope value
    """

  def initCacheStorage():
    """Make cache container usable
    """

  def getCacheStorage(**kw):
    """return cache container like dict,
    OOBTree, SQLConnector, ...
    """

  def get(cache_id, scope, default=None):
    """get the calculated value according to the cache_id and scope.
    raise KeyError if key does not exists and no default value provided.
    return CacheEntry or default
    """

  def set(cache_id, scope, value, cache_duration=None, calculation_time=0):
    """Store the cached value inside CacheEntry Wrapper
    """

  def delete(cache_id, scope):
    """delete cache entry according cache_id and given scope
    """

  def has_key(cache_id, scope):
    """return True if cache_id is set for according given scope
    """

  def getScopeList():
    """return the list of known scope values
    """

  def getScopeKeyList(scope):
    """return list of keys for given scope
    """

  def getCachePluginTotalMemorySize():
    """return memory size used by cache
    """
