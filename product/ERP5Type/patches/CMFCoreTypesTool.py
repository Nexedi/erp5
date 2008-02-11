from Products.CMFCore.TypesTool import TypeInformation
from zLOG import LOG, INFO

if getattr(TypeInformation, 'manage_main', None) is not None:
  LOG('ERP5Type/patches/CMFCoreTypesTool.py', INFO, 'This patch is no longer needed. Skipping.')
elif None in (getattr(TypeInformation, 'manage_propertiesForm__roles__', None),
              getattr(TypeInformation, 'manage_propertiesForm', None):
  LOG('ERP5Type/patches/CMFCoreTypesTool.py', INFO, 'manage_propertiesForm not found. Skipping.')
else:
  TypeInformation.manage_main__roles__ = TypeInformation.manage_propertiesForm__roles__
  TypeInformation.manage_main = TypeInformation.manage_propertiesForm
 
