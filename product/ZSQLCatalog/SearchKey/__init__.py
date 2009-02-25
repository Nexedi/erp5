# Automaticaly import all SearchKeys
import os
module_path = os.path.dirname(os.path.abspath(__file__))
global_dict = globals()
__relative_file__ = os.path.basename(__file__)
for filename in os.listdir(module_path):
  if filename.endswith('.py') and filename != __relative_file__:
    modulename = filename[:-3]
    try:
      module = __import__(modulename, global_dict, None, [])
    except ImportError:
      continue

