#from Products.ERP5Type.Log import log
import traceback
import cPickle
import types
import importlib

class ImportInfo(object):
  def __init__(self, module_name):
    self.module_name = module_name

def ClusterDataNotebookLine_execute(self):
  self.ERP5Site_assertClusterDataNotebookEnabled()
  data_notebook = self.getParentValue()

  # restore previous call information
  pickle = data_notebook.getPickle()
  if pickle is not None:
    unpickled = cPickle.loads(pickle)
  else:
    unpickled = {}
  filler = {}
  for k, v in unpickled.items():
    if isinstance(v, ImportInfo):
      filler[k] = importlib.import_module(v.module_name)
    else:
      filler[k] = v
  new_pickle = {}
  try:
    result, func_locals = self.getDefaultCodeValue()._exec_with_fill(filler)
  except Exception:
    result = traceback.format_exc()
  else:
    # store in pickle for next run
    for k,v in func_locals.items():
      if isinstance(v, types.ModuleType):
        new_pickle[k] = ImportInfo(v.__name__)
      else:
        new_pickle[k] = v
    data_notebook.edit(pickle=cPickle.dumps(new_pickle))

  if result is not None:
    result = str(result)
  # store textual representation to send it over the wire
  self.edit(result=result)
