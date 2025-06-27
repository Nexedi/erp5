try:
  return context.Order_getRelatedOrderRequestValue() is not None
except UnboundLocalError:
  return False
