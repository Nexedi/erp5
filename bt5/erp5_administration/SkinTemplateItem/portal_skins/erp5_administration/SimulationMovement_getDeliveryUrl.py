value = context.getProperty('delivery_value')
if value is not None:
  return value.absolute_url()
