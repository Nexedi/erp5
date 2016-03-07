quantity = 0.0

for p in context.contentValues(portal_type = "Project Line"):
  quantity += p.ProjectLine_getAggregatedQuantity()

# By default, take the total of children
if quantity: return quantity

# if children define nothing, use our own value
# This is compatible with spreadsheet calculation
return context.getQuantity()
