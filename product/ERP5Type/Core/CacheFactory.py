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

from Products.ERP5Type import PropertySheet
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.Cache import CachingMethod

class CacheFactory(XMLObject):
  """
  CacheFactory is a collection of cache plugins. CacheFactory is an object which lives in ZODB.
  """

  meta_type = 'ERP5 Cache Factory'
  portal_type = 'Cache Factory'

  allowed_types = ('ERP5 Ram Cache',
                   'ERP5 Distributed Ram Cache',
                  )

  security = ClassSecurityInfo()
  security.declareProtected(Permissions.ManagePortal,
                            'manage_editProperties',
                            'manage_changeProperties',
                            'manage_propertiesForm',
                            )

  property_sheets = ( PropertySheet.Base
                    , PropertySheet.SimpleItem
                    , PropertySheet.Folder
                    , PropertySheet.CacheFactory
                    , PropertySheet.SortIndex
                    )

  security.declareProtected(Permissions.AccessContentsInformation, 'getCacheId')
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

  security.declareProtected(Permissions.AccessContentsInformation, 'get')
  def get(self, cache_id, default=None):
    """
      Get value or return default from all contained Cache Bag
      or Cache Plugin.
    """
    cache_plugin_list = self.getCachePluginList(list(self.allowed_types) + ['ERP5 Cache Bag'])
    for cache_plugin in cache_plugin_list:
      value = cache_plugin.get(cache_id, default)
      if value is not None:
        return value
    return default

  security.declareProtected(Permissions.AccessContentsInformation, 'set')
  def set(self, cache_id, value):
    """
      Set value to all contained cache plugin or cache bag.
    """
    cache_plugin_list = self.getCachePluginList(list(self.allowed_types) + ['ERP5 Cache Bag'])
    for cache_plugin in cache_plugin_list:
      cache_plugin.set(cache_id, value)

  security.declareProtected(Permissions.AccessContentsInformation, 'getCachePluginList')
  def getCachePluginList(self, allowed_type_list=None):
    """ get ordered list of installed cache plugins in ZODB """
    if allowed_type_list is None:
      # fall back to default ones
      allowed_type_list = self.allowed_types
    cache_plugins = self.objectValues(allowed_type_list)
    cache_plugins = list(cache_plugins)
    cache_plugins.sort(key=lambda x: x.getIntIndex(0))
    return cache_plugins

  security.declareProtected(Permissions.AccessContentsInformation, 'getRamCacheFactory')
  def getRamCacheFactory(self):
    """ Return RAM based cache factory """
    cache_factory_name =  self.getCacheId()
    cache_tool = self.portal_caches
    cache_factory = CachingMethod.factories.get(cache_factory_name)
    #XXX This conditional statement should be remove as soon as
    #Broadcasting will be enable among all zeo clients.
    #Interaction which update portal_caches should interact with all nodes.
    if cache_factory is None and getattr(cache_tool, cache_factory_name, None) is not None:
      #ram_cache_root is not up to date for current node
      cache_tool.updateCache()
    return CachingMethod.factories[cache_factory_name]

  security.declareProtected(Permissions.AccessContentsInformation, 'getRamCacheFactoryPluginList')
  def getRamCacheFactoryPluginList(self):
    """ Return RAM based list of cache plugins for this factory """
    return self.getRamCacheFactory().getCachePluginList()

  def clearCache(self):
    """ clear cache for this cache factory """
    for cp in self.getRamCacheFactoryPluginList():
      cp.clearCache()
