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
from Products.ERP5Type.PropertySheet.CacheFactory import CacheFactory
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.Cache import CachingMethod

class CacheFactory(XMLObject):
  """
  CacheFactory is a collection of cache plugins. CacheFactory is an object which lives in ZODB.
  """
    
  meta_type = 'ERP5 Cache Factory'
  portal_type = 'Cache Factory'
  isPortalContent = 1 
  isRADContent = 1
  
  allowed_types = ('ERP5 Ram Cache', 
                   'ERP5 Distributed Ram Cache', 
                   'ERP5 SQL Cache',
                   'ERP5 Zodb Cache',
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
                    , CacheFactory  
                    )
    
       
  def getCachePluginList(self):
    """ get ordered list of installed cache plugins in ZODB """
    cache_plugins = self.objectValues(self.allowed_types)
    cache_plugins = map(None, cache_plugins)
    cache_plugins.sort(key=lambda x: x.getIntIndex(0))
    return  cache_plugins
    
  security.declareProtected(Permissions.AccessContentsInformation, 'getRamCacheFactory')
  def getRamCacheFactory(self):
    """ Return RAM based cache factory """
    erp5_site_id = self.getPortalObject().getId()
    return CachingMethod.factories[erp5_site_id][self.cache_scope]
    
  security.declareProtected(Permissions.AccessContentsInformation, 'getRamCacheFactoryPluginList')
  def getRamCacheFactoryPluginList(self):
    """ Return RAM based list of cache plugins for this factory """
    return self.getRamCacheFactory().getCachePluginList()
  
  def clearCache(self):
    """ clear cache for this cache factory """
    for cp in self.getRamCacheFactory().getCachePluginList():
      cp.clearCache()
