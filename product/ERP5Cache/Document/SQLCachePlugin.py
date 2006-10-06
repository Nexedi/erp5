from AccessControl import ClassSecurityInfo
from Products.CMFCore import CMFCorePermissions
from Products.ERP5Type.Base import Base
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type import PropertySheet
from Products.ERP5Cache.PropertySheet.BaseCachePlugin import BaseCachePlugin
from Products.ERP5Cache.PropertySheet.SQLCachePlugin import SQLCachePlugin

class SQLCachePlugin(XMLObject):
  """
  SQLCachePlugin is a Zope (persistent) representation of 
  the RAM based real SQL cache plugin object.
  """
  
  meta_type = 'ERP5 SQL Cache Plugin'
  portal_type = 'SQL Cache Plugin'
  isPortalContent = 1
  isRADContent = 1
  
  allowed_types = ()
    
  security = ClassSecurityInfo()
  security.declareProtected(CMFCorePermissions.ManagePortal,
                            'manage_editProperties',
                            'manage_changeProperties',
                            'manage_propertiesForm',
                            )

  property_sheets = ( PropertySheet.Base
                    , PropertySheet.SimpleItem
                    , PropertySheet.Folder
                    , BaseCachePlugin
                    , SQLCachePlugin 
                    )
