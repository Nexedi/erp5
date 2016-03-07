"""Returns the quantity divided by the max quantity"""
q = context.getQuantity()
max_q = 0.0
for x in context.getParentValue().contentValues():
  max_q += x.getTotalQuantity()

try:
  return q/max_q
except ZeroDivisionError:
  # This means that the Quantity and the max quantity  are 0
  return 1.0
