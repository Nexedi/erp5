value = context.getProperty('resource_value')
if value is not None:
  return value.absolute_url()
