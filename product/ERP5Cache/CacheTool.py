""" Cache Tool module for ERP5 """
from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type import Permissions
from Globals import InitializeClass, DTMLFile, PersistentMapping
from Products.ERP5Cache import _dtmldir
from Products.ERP5Type.Cache import CachingMethod, CacheFactory
from Products.ERP5Cache.CachePlugins.RamCache import RamCache
from Products.ERP5Cache.CachePlugins.DistributedRamCache import DistributedRamCache
from Products.ERP5Cache.CachePlugins.SQLCache import SQLCache

##try:
##  from Products.TimerService import getTimerService
##except ImportError:
##  def getTimerService(self):
##    pass


class CacheTool(BaseTool):
  """ Caches tool wrapper for ERP5 """
    
  id = "portal_caches"
  meta_type = "ERP5 Cache Tool"
  portal_type = "Cache Tool"

  security = ClassSecurityInfo()
  manage_options = ({'label': 'Configure',
                                'action': 'cache_tool_configure',
                    },) + BaseTool.manage_options

  security.declareProtected( Permissions.ManagePortal, 'cache_tool_configure')
  cache_tool_configure = DTMLFile( 'cache_tool_configure', _dtmldir )
  
  def __init__(self):
    BaseTool.__init__(self)

  security.declareProtected(Permissions.AccessContentsInformation, 'getCacheFactoryList')
  def getCacheFactoryList(self):
    """ Return available cache factories """
    rd ={}
    for cf in self.objectValues('ERP5 Cache Factory'):
      cache_scope = cf.getId()
      rd[cache_scope] = {}
      rd[cache_scope]['cache_plugins'] = []
      rd[cache_scope]['cache_params'] = {}
      for cp in cf.getCachePluginList():
        cp_meta_type = cp.meta_type
        if cp_meta_type == 'ERP5 Ram Cache Plugin':
          cache_obj = RamCache()
        elif cp_meta_type == 'ERP5 Distributed Ram Cache Plugin':
          cache_obj = DistributedRamCache({'server':cp.getServer()})
        elif cp_meta_type == 'ERP5 SQL Cache Plugin':
          ## use connection details from 'erp5_sql_transactionless_connection' ZMySLQDA object
          connection_string = self.erp5_sql_transactionless_connection.connection_string
          kw = self.parseDBConnectionString(connection_string)
          kw['cache_table_name'] = cp.getCacheTableName()
          cache_obj = SQLCache(kw)
        ## set cache expire check interval
        cache_obj.cache_expire_check_interval = cp.getCacheExpireCheckInterval() 
        rd[cache_scope]['cache_plugins'].append(cache_obj)
        rd[cache_scope]['cache_params']['cache_duration'] = cf.getCacheDuration() #getattr(cf, 'cache_duration', None)
    return rd

  ##
  ## DB structure
  ##
  security.declareProtected(Permissions.ModifyPortalContent, 'createDBCacheTable')
  def createDBCacheTable(self, cache_table_name="cache", REQUEST=None):
    """ create in MySQL DB cache table """
    my_query = SQLCache.create_table_sql %cache_table_name
    try:
      self.erp5_sql_transactionless_connection.manage_test("DROP TABLE %s" %cache_table_name)
    except:
      pass
    self.erp5_sql_transactionless_connection.manage_test(my_query)
    if REQUEST:
      self.REQUEST.RESPONSE.redirect('cache_tool_configure?portal_status_message=Cache table successfully created.')

  security.declareProtected(Permissions.AccessContentsInformation, 'parseDBConnectionString')
  def parseDBConnectionString(self, connection_string):
    """ Parse given connection string. Code "borrowed" from ZMySLQDA.db """
    kwargs = {}
    items = connection_string.split()
    if not items: 
      return kwargs
    lockreq, items = items[0], items[1:]
    if lockreq[0] == "*":
      db_host, items = items[0], items[1:]
    else:
      db_host = lockreq
    if '@' in db_host:
      db, host = split(db_host,'@',1)
      kwargs['db'] = db
      if ':' in host:
        host, port = split(host,':',1)
        kwargs['port'] = int(port)
      kwargs['host'] = host
    else:
      kwargs['db'] = db_host
    if kwargs['db'] and kwargs['db'][0] in ('+', '-'):
      kwargs['db'] = kwargs['db'][1:]
    if not kwargs['db']:
      del kwargs['db']
    if not items: 
      return kwargs
    kwargs['user'], items = items[0], items[1:]
    if not items: 
      return kwargs
    kwargs['passwd'], items = items[0], items[1:]
    if not items: 
      return kwargs
    kwargs['unix_socket'], items = items[0], items[1:]
    return kwargs
    
  ##
  ## RAM cache structure
  ##
  security.declareProtected(Permissions.AccessContentsInformation, 'getRamCacheRoot')
  def getRamCacheRoot(self):
    """ Return RAM based cache root """
    erp5_site_id = self.getPortalObject().getId()
    return CachingMethod.factories[erp5_site_id]

  security.declareProtected(Permissions.ModifyPortalContent, 'updateCache')
  def updateCache(self, REQUEST=None):
    """ Clear and update cache structure """
    erp5_site_id = self.getPortalObject().getId()
    for cf in CachingMethod.factories[erp5_site_id]:
      for cp in  CachingMethod.factories[erp5_site_id][cf].getCachePluginList():
        del cp
    CachingMethod.factories[erp5_site_id] = {}
    ## read configuration from ZODB
    for key,item in self.getCacheFactoryList().items():
      if len(item['cache_plugins'])!=0:
        CachingMethod.factories[erp5_site_id][key] = CacheFactory(item['cache_plugins'], item['cache_params'])    
    if REQUEST:
      self.REQUEST.RESPONSE.redirect('cache_tool_configure?portal_status_message=Cache updated.')
    
  security.declareProtected(Permissions.ModifyPortalContent, 'clearCache')
  def clearCache(self, REQUEST=None):
    """ Clear whole cache structure """
    ram_cache_root = self.getRamCacheRoot()
    for cf in ram_cache_root:
      for cp in ram_cache_root[cf].getCachePluginList():
        cp.clearCache()
    if REQUEST:
      self.REQUEST.RESPONSE.redirect('cache_tool_configure?portal_status_message=Cache cleared.')

  security.declareProtected(Permissions.ModifyPortalContent, 'clearCacheFactory')
  def clearCacheFactory(self, cache_factory_id, REQUEST=None):
    """ Clear only cache factory. """
    ram_cache_root = self.getRamCacheRoot()
    if ram_cache_root.has_key(cache_factory_id):
      ram_cache_root[cache_factory_id].clearCache()
    if REQUEST:
      self.REQUEST.RESPONSE.redirect('cache_tool_configure?portal_status_message=Cache factory %s cleared.' %cache_factory_id)

  
  # Timer - checks for cache expiration triggered by Zope's TimerService
##  def isSubscribed(self):
##      """
##      return True, if we are subscribed to TimerService.
##      Otherwise return False.
##      """
##      service = getTimerService(self)
##      if not service:
##          LOG('AlarmTool', INFO, 'TimerService not available')
##          return False
##
##      path = '/'.join(self.getPhysicalPath())
##      if path in service.lisSubscriptions():
##          return True
##      return False
##
##  security.declareProtected(Permissions.ManageProperties, 'subscribe')
##  def subscribe(self):
##    """
##      Subscribe to the global Timer Service.
##    """
##    service = getTimerService(self)
##    if not service:
##      LOG('AlarmTool', INFO, 'TimerService not available')
##      return
##    service.subscribe(self)
##    return "Subscribed to Timer Service"
##
##  security.declareProtected(Permissions.ManageProperties, 'unsubscribe')
##  def unsubscribe(self):
##    """
##      Unsubscribe from the global Timer Service.
##    """
##    service = getTimerService(self)
##    if not service:
##      LOG('AlarmTool', INFO, 'TimerService not available')
##      return
##    service.unsubscribe(self)
##    return "Usubscribed from Timer Service"
##
##  def manage_beforeDelete(self, item, container):
##    self.unsubscribe()
##    BaseTool.inheritedAttribute('manage_beforeDelete')(self, item, container)
##
##  def manage_afterAdd(self, item, container):
##    self.subscribe()
##    BaseTool.inheritedAttribute('manage_afterAdd')(self, item, container)
##
##  security.declarePrivate('process_timer')
##  def process_timer(self, interval, tick, prev="", next=""):
##    """
##      This method is called by TimerService in the interval given
##      in zope.conf. The Default is every 5 seconds. This method will
##      try to expire cache entries.
##    """
##    ram_cache_root = self.getRamCacheRoot()
##    for cf_id, cf_obj in ram_cache_root.items():
##      cf_obj.expire()
