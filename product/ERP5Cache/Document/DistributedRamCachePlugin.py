from AccessControl import ClassSecurityInfo
from Products.CMFCore import CMFCorePermissions
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type import PropertySheet
from Products.ERP5Cache.PropertySheet.BaseCachePlugin import BaseCachePlugin
from Products.ERP5Cache.PropertySheet.DistributedRamCachePlugin import DistributedRamCachePlugin

class DistributedRamCachePlugin(XMLObject):
  """
  DistributedRamCachePlugin is a Zope (persistent) representation of 
  the Distributed RAM Cache real cache plugin object.
  """
  
  meta_type='ERP5 Distributed Ram Cache Plugin'
  portal_type='Distributed Ram Cache Plugin'
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
                    , DistributedRamCachePlugin 
                    )
