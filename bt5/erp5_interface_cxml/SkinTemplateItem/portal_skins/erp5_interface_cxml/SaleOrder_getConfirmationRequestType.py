# if some lines are missing, use "detail" type:
for line in context.objectValues(portal_type="Sale Order Line"):
  if not line.SaleOrderLine_isConfirmationItem():
    return "detail"

if context.hasCxmlChanges():
  return "detail"
else:
  return "accept"
