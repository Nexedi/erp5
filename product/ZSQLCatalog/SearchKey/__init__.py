# Automaticaly import all SearchKeys
import os, importlib
global_dict = globals()
__relative_file__ = os.path.basename(__file__)
for filename in os.listdir(os.path.dirname(os.path.abspath(__file__))):
  if filename.endswith('.py') and filename != __relative_file__:
    importlib.import_module("."+filename[:-3], "Products.ZSQLCatalog.SearchKey") # global_dict, None, [])
