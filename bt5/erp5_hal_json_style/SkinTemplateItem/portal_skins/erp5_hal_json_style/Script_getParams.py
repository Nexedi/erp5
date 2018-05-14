try:
  if "Script" in context.meta_type:
    return context.params()
  return None
except AttributeError:
  return None
