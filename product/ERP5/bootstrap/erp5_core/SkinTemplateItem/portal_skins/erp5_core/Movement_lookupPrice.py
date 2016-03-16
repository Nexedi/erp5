resource = context.getResourceValue()
if resource is not None:
  return resource.getPrice(context=context)
else:
  return None
