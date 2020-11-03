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


""" Cache Tool module for ERP5 """
import transaction
from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type import Permissions
from Products.ERP5Type.Globals import InitializeClass, DTMLFile, PersistentMapping
from Products.ERP5Type import _dtmldir
from Products.ERP5Type.Cache import CacheFactory
from Products.ERP5Type.Cache import CachingMethod
from Products.ERP5Type.Cache import DEFAULT_CACHE_FACTORY
from Products.ERP5Type.CachePlugins.RamCache import RamCache
from Products.ERP5Type.CachePlugins.DistributedRamCache import DistributedRamCache

class CacheTool(BaseTool):
  """ Caches tool wrapper for ERP5 """

  id = "portal_caches"
  meta_type = "ERP5 Cache Tool"
  portal_type = "Cache Tool"

  security = ClassSecurityInfo()
  manage_options = ({'label': 'Configure',
                                'action': 'cache_tool_configure',
                    },
                    {'label': 'Statistics',
                              'action': 'cache_tool_statistics',
                    },
                    ) + BaseTool.manage_options

  security.declareProtected( Permissions.ManagePortal, 'cache_tool_configure')
  cache_tool_configure = DTMLFile('cache_tool_configure', _dtmldir)

  security.declareProtected( Permissions.ManagePortal, 'cache_tool_statistics')
  cache_tool_statistics = DTMLFile('cache_tool_statistics', _dtmldir)

  security.declareProtected(Permissions.AccessContentsInformation, 'getCacheFactoryList')
  def getCacheFactoryList(self):
    """ Return available cache factories """

    def getRamCachePlugin(cp):
      cp_meta_type = cp.meta_type
      id = cp.getCacheId()
      if cp_meta_type == 'ERP5 Ram Cache':
        return RamCache(id)
      if cp_meta_type == 'ERP5 Distributed Ram Cache':
        ## even thougn we have such plugin in ZODB that doens't mean
        ## we have corresponding memcache module installed
        if getattr(cp, 'getSpecialiseValue', None) is not None:
          memcached_plugin = cp.getSpecialiseValue()
          if memcached_plugin is not None:
            server = memcached_plugin.getUrlString('')
            init_dict = {
              'server': server,
              'expiration_time': cf.getCacheDuration(),
              'server_max_key_length': memcached_plugin.getServerMaxKeyLength(),
              'server_max_value_length': memcached_plugin.getServerMaxValueLength(),
              'key_prefix': getattr(self, 'erp5_site_global_id', '')}
            return DistributedRamCache(id, init_dict)

    rd = {}
    for cf in self.objectValues('ERP5 Cache Factory'):
      cache_scope = cf.getCacheId()
      rd[cache_scope] = {}
      rd[cache_scope]['cache_plugins'] = []
      rd[cache_scope]['cache_params'] = {}
      for cp in cf.getCachePluginList():
        cache_obj = getRamCachePlugin(cp)
        if cache_obj is not None:
          ## set cache expire check interval
          cache_obj.cache_expire_check_interval = cp.getCacheExpireCheckInterval()
          rd[cache_scope]['cache_plugins'].append(cache_obj)
          rd[cache_scope]['cache_params']['cache_duration'] = cf.getCacheDuration()

      # support for cache bags which are like Cache Factory
      # i.e. provide Cache Plugins
      for cache_bag in cf.objectValues('ERP5 Cache Bag'):
        cache_scope = cache_bag.getCacheId()
        rd[cache_scope] = {}
        rd[cache_scope]['cache_plugins'] = []
        rd[cache_scope]['cache_params'] = {}
        for cp in cache_bag.getCachePluginList():
          cache_obj = getRamCachePlugin(cp)
          if cache_obj is not None:
            ## set cache expire check interval
            cache_obj.cache_expire_check_interval = cp.getCacheExpireCheckInterval()
            rd[cache_scope]['cache_plugins'].append(cache_obj)
            rd[cache_scope]['cache_params']['cache_duration'] = cf.getCacheDuration()

    return rd

  ##
  ## RAM cache structure
  ##
  security.declareProtected(Permissions.AccessContentsInformation, 'getRamCacheRoot')
  def getRamCacheRoot(self):
    """ Return RAM based cache root """
    return CachingMethod.factories

  security.declareProtected(Permissions.ModifyPortalContent, 'updateCache')
  def updateCache(self, REQUEST=None):
    """ Clear and update cache structure """
    for cf in CachingMethod.factories:
      for cp in CachingMethod.factories[cf].getCachePluginList():
        del cp
    CachingMethod.factories = {}
    ## read configuration from ZODB
    for key, item in self.getCacheFactoryList().items():
      #If there is no cache_plugins, do not create Cache Factory
      if item["cache_plugins"]:
        ## init cache backend storages
        for cp in item["cache_plugins"]:
          cp.initCacheStorage()
        CachingMethod.factories[key] = CacheFactory(item['cache_plugins'], item['cache_params'])
    if REQUEST is not None:
      self.REQUEST.RESPONSE.redirect('cache_tool_configure?manage_tabs_message=Cache updated.')

  security.declarePublic('clearAllCache')
  def clearAllCache(self):
    # Clear all cache factories. This method is public to be called from
    # scripts, but without docstring to prevent calling it from the URL
    ram_cache_root = self.getRamCacheRoot()
    for cf_key in ram_cache_root.keys():
      for cp in ram_cache_root[cf_key].getCachePluginList():
        cp.clearCache()

  security.declareProtected(Permissions.ManagePortal, 'manage_clearAllCache')
  def manage_clearAllCache(self, REQUEST=None):
    """Clear all cache factories."""
    self.clearAllCache()
    if REQUEST is not None:
      self.REQUEST.RESPONSE.redirect('cache_tool_configure?manage_tabs_message=All cache factories cleared.')

  security.declarePublic('clearCacheFactory')
  def clearCacheFactory(self, cache_factory_id):
    # Clear cache factory of given ID.
    # This method is public to be called from scripts, but without docstring to
    # prevent calling it from the URL
    ram_cache_root = self.getRamCacheRoot()
    if ram_cache_root.has_key(cache_factory_id):
      ram_cache_root[cache_factory_id].clearCache()

  security.declareProtected(Permissions.ManagePortal, 'manage_clearCacheFactory')
  def manage_clearCacheFactory(self, cache_factory_id, REQUEST=None):
    """ Clear only cache factory. """
    self.clearCacheFactory(cache_factory_id)
    if REQUEST is not None:
      self.REQUEST.RESPONSE.redirect('cache_tool_configure?manage_tabs_message=Cache factory %s cleared.' %cache_factory_id)

  security.declareProtected(Permissions.ModifyPortalContent, 'clearCache')
  def clearCache(self, cache_factory_list=(DEFAULT_CACHE_FACTORY,),
                 REQUEST=None, before_commit=False):
    """ Clear specified or default cache factory. """
    if before_commit:
      assert REQUEST is None
      transaction.get().addBeforeCommitHook(self.clearCache,
                                            (cache_factory_list,))
    ram_cache_root = self.getRamCacheRoot()
    for cf_key in cache_factory_list:
      self.clearCacheFactory(cf_key)
    if REQUEST is not None:
      self.REQUEST.RESPONSE.redirect('cache_tool_configure?manage_tabs_message=Cache cleared.')

  security.declareProtected(Permissions.ModifyPortalContent, 'clearCacheFactoryScope')
  def clearCacheFactoryScope(self, cache_factory_id, scope, REQUEST=None):
    """ Clear only cache factory. """
    ram_cache_root = self.getRamCacheRoot()
    if ram_cache_root.has_key(cache_factory_id):
      ram_cache_root[cache_factory_id].clearCacheForScope(scope)
    if REQUEST is not None:
      self.REQUEST.RESPONSE.redirect('cache_tool_configure?manage_tabs_message=Cache factory scope %s cleared.' %cache_factory_id)

  security.declareProtected(Permissions.AccessContentsInformation, 'getCacheTotalMemorySize')
  def getCacheTotalMemorySize(self, REQUEST=None):
    """ Calculate total size of memory used for cache.

        Note: this method will calculate RAM memory usage for 'local'
        (RamCache) cache plugins and will not include
        'shared' (DistributedRamCache) cache plugins."""
    stats = {}
    total_size = 0
    ram_cache_root = self.getRamCacheRoot()
    for cf_key, cf_value in ram_cache_root.items():
      for cp in cf_value.getCachePluginList():
        cp_total_size, cp_cache_keys_total_size = cp.getCachePluginTotalMemorySize()
        total_size += cp_total_size
        stats[cf_key] = dict(total = cp_total_size,
                             cp_cache_keys_total_size = cp_cache_keys_total_size)
    return dict(total_size = total_size, stats = stats)
