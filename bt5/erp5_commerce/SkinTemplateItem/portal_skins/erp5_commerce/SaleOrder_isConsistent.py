if context.SaleOrder_isShippingRequired() and context.SaleOrder_getSelectedShippingResource() is None:
  ## shipping is required but not selected
  return False
return True
