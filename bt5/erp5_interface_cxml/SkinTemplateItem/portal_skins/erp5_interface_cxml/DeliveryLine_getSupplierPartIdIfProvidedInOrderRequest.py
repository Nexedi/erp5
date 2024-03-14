# If SupplierPartId in cmxl OrderRequest is empty we are
# not allowed to transmit our SupplierPartId
order = context.getParentValue().Order_getRelatedOrderRequestValue()
line_dict = order.getLinePropertyDict()[context.getIntIndex()]
if line_dict.get('resource_reference'):
  return context.getResourceReference()
else:
  return ''
