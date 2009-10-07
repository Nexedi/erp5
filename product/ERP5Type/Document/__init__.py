# ERP5Type has a specific __init__ file to circumvent circular references

## Hide internal implementation
#from Products.ERP5Type.Globals import InitializeClass
#import Products.ERP5Type.Core.Folder as ERP5Folder
## Default constructor for Folder
## Can be overriden by adding a method addFolder in class Folder
#def addFolder(folder, id, REQUEST=None, **kw):
  #o = ERP5Folder.Folder(id)
  #folder._setObject(id, o)
  #if kw is not None: o.__of__(folder)._edit(force_update=1, **kw)
  ## contentCreate already calls reindex 3 times ...
  ## o.reindexObject()
  #if REQUEST is not None:
      #REQUEST['RESPONSE'].redirect( 'manage_main' )

#InitializeClass(ERP5Folder.Folder)

from Products.ERP5Type.Base import TempBase
from Products.PythonScripts.Utility import allow_class
allow_class(TempBase)

def newTempBase(folder, id, REQUEST=None, **kw):
  o = TempBase(id)
  o = o.__of__(folder)
  if kw is not None: o._edit(force_update=1, **kw)
  return o

from AccessControl import ModuleSecurityInfo
ModuleSecurityInfo('Products.ERP5Type.Document').declarePublic('newTempBase',)
