# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2012 Nexedi SA and Contributors. All Rights Reserved.
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

from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions
from Products.ERP5Type.Cache import DEFAULT_CACHE_SCOPE

class CacheProviderMixIn:
  """
   Generic Cache Plugin set / get API implementation.
  """

  security = ClassSecurityInfo()

  def _getRamCachePlugin(self):
     """
       Get RAM based cache plugin for this ZODB cache plugin.
     """
     return self.getParentValue().getRamCacheFactory().getCachePluginById(self.getCacheId())

  security.declareProtected(Permissions.AccessContentsInformation, 'get')
  def get(self, cache_id, default=None):
    """
      Get value from cache plugin.
    """
    cache_plugin = self._getRamCachePlugin()
    value = cache_plugin.get(cache_id, DEFAULT_CACHE_SCOPE, default)
    if value is not None:
      value = value.getValue()
    return value

  security.declareProtected(Permissions.AccessContentsInformation, 'set')
  def set(self, cache_id, value):
    """
      Set value to cache plugin.
    """
    cache_duration = self.getParentValue().getRamCacheFactory().cache_duration
    cache_plugin = self._getRamCachePlugin()
    cache_plugin.set(cache_id, DEFAULT_CACHE_SCOPE, value, cache_duration)

  def getCacheId(self):
    """
      Get a common Cache Factory / Cache Bag ID in this
      case relative to portal_caches.
      It's required to use relative url (i.e. mainly ID) due
      to CachingMethod legacy.
    """
    relative_url = self.getRelativeUrl()
    assert relative_url[:14] == 'portal_caches/'
    return relative_url[14:]
