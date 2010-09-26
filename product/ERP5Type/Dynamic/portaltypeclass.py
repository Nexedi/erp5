from zLOG import LOG, ERROR, BLATHER

def resetDynamicDocuments(context, slave=False):
  """
  Allow resetting all classes to ghost state, most likely done after
  adding and removing mixins on the fly

  Nodes just trying to catch up with state of classes without wanting
  to invalidate them globally should set slave=True.
  """
  LOG("ERP5Type.Dynamic", 0, "Resetting dynamic classes")
  # stub
  return
