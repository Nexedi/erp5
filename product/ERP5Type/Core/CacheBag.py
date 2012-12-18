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


from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions
from Products.ERP5Type.Cache import DEFAULT_CACHE_SCOPE
from Products.ERP5Type.Core.CacheFactory import CacheFactory

class CacheBag(CacheFactory):
  """
  CacheBag is a special type of a CacheFactory that allows multi level caching
  in different backends describe by CachePlugin.

  CacheBag 1
     - Cache Plugin 1 (priority 0)
     - Cache Plugin 2 (priority 1)
  """

  meta_type = 'ERP5 Cache Bag'
  portal_type = 'Cache Bag'

  security = ClassSecurityInfo()

  security.declareProtected(Permissions.AccessContentsInformation, 'get')
  def get(self, cache_id, default=None):
    """
      Get value or return default.
    """
    ram_cache_factory_plugin_list = self.getRamCacheFactoryPluginList()

    for cache_plugin in ram_cache_factory_plugin_list:
      data_dict = cache_plugin.get(cache_id, DEFAULT_CACHE_SCOPE, default)
      if data_dict is not None:
        value = data_dict.getValue()
        if ram_cache_factory_plugin_list.index(cache_plugin) > 0:
          # update first plugin as it's the one to be used
          # XXX: JPS we can have different update policy here based on a project requirements.
          # c0 c1 c2....cN where c0 is filled from cN
          # c1.... cN-1 untouched then rotate i -> i+1
          # this way you can create "groups of caches" per date and trash old stuff
          # instead of using 2x more disk space, you can use 1/N more disk space
          cache_duration = self.getRamCacheFactory().cache_duration
          ram_cache_factory_plugin_list[0].set(cache_id, DEFAULT_CACHE_SCOPE, value, cache_duration)
        return value
    return default

  security.declareProtected(Permissions.AccessContentsInformation, 'set')
  def set(self, cache_id, value):
    """
      Set value.
    """
    cache_duration = self.getRamCacheFactory().cache_duration
    ram_cache_factory_plugin_list = self.getRamCacheFactoryPluginList()
    # set only in first plugin in sequence
    ram_cache_factory_plugin_list[0].set(cache_id, DEFAULT_CACHE_SCOPE, value, cache_duration)
