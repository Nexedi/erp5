# ERP5Type has a specific __init__ file to circumvent circular references

# Hide internal implementation
from Globals import InitializeClass
import Folder as ERP5Folder
# Default constructor for Folder
# Can be overriden by adding a method addFolder in class Folder
def addFolder(folder, id, REQUEST=None, **kw):
  o = ERP5Folder.Folder(id)
  folder._setObject(id, o)
  if kw is not None: o.__of__(folder)._edit(force_update=1, **kw)
  # contentCreate already calls reindex 3 times ...
  # o.reindexObject()
  if REQUEST is not None:
      REQUEST['RESPONSE'].redirect( 'manage_main' )

InitializeClass(ERP5Folder.Folder)
