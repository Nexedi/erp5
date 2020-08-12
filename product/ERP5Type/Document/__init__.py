# ERP5Type has a specific __init__ file to circumvent circular references

from Products.ERP5Type.Base import TempBase
from Products.PythonScripts.Utility import allow_class
allow_class(TempBase)

def newTempBase(folder, id, REQUEST=None, **kw):
  from Products.ERP5Type.Base import TempBase
  o = TempBase(id)
  o = o.__of__(folder)
  if kw is not None: o._edit(force_update=1, **kw)
  return o

from AccessControl import ModuleSecurityInfo
ModuleSecurityInfo('Products.ERP5Type.Document').declarePublic('newTempBase',)
