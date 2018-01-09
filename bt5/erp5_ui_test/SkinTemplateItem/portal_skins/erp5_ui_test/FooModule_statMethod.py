"""Compute stats from actual Foo Lines on a Foo object"""
column_list = ['getQuantity', 'id']
result = {c: 0.0 for c in column_list}

for line in context.contentValues(portal_type="Foo"):
  for column in column_list:
    value = getattr(line, column)
    if callable(value):
      value = value()
    result[column] = result[column] + float(value)

return [result, ]
