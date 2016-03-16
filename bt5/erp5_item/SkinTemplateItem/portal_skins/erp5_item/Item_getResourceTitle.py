resource = context.Item_getResourceValue(**kw)
if resource is not None:
  return resource.getTitle()
return None
