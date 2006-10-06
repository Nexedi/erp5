from AccessControl import ClassSecurityInfo
from Products.CMFCore import CMFCorePermissions
from Products.ERP5Type import Permissions
from Products.ERP5Type import PropertySheet
from Products.ERP5Cache.PropertySheet import CacheFactory
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.Cache import CachingMethod, CacheFactory

class CacheFactory(XMLObject):
  """
  CacheFactory is a collection of cache plugins. CacheFactory is an object which liv in ZODB.
  """
    
  meta_type = 'ERP5 Cache Factory'
  portal_type = 'Cache Factory'
  isPortalContent = 1 
  isRADContent = 1
  
  allowed_types = ('ERP5 Ram Cache Plugin', 
                   'ERP5 Distributed Ram Cache Plugin', 
                   'ERP5 SQL Cache Plugin',
                  )
    
  security = ClassSecurityInfo()
  security.declareProtected(CMFCorePermissions.ManagePortal,
                            'manage_editProperties',
                            'manage_changeProperties',
                            'manage_propertiesForm',
                            )

  property_sheets = ( PropertySheet.Base
                    , PropertySheet.SimpleItem
                    , PropertySheet.Folder
                    , PropertySheet.CacheFactory  
                    )
    
       
  def getCachePluginList(self):
    """ get ordered list of installed cache plugins in ZODB """
    cache_plugins = self.objectValues(self.allowed_types)
    cache_plugins = map(None, cache_plugins)
    cache_plugins.sort(lambda x,y: cmp(x.int_index, y.int_index))
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
