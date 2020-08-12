# ERP5Type has a specific __init__ file to circumvent circular references.
# Eventhough this is a dynamic module created by initializeLegacyDocumentDynamicModule
# the module is defined, because newTempBase is imported from several places.

from Products.ERP5Type.Base import TempBase
from Products.PythonScripts.Utility import allow_class
allow_class(TempBase)

def newTempBase(folder, id, REQUEST=None, **kw):
  # reimport TempBase, because this module is replaced by a dynamic module
  # and references to globals are not kept
  from Products.ERP5Type.Base import TempBase
  o = TempBase(id)
  o = o.__of__(folder)
  if kw is not None: o._edit(force_update=1, **kw)
  return o

from AccessControl import ModuleSecurityInfo
ModuleSecurityInfo('Products.ERP5Type.Document').declarePublic('newTempBase',)
