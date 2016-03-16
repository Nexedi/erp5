value = context.getProperty('order_value')
if value is not None:
  return value.absolute_url()
