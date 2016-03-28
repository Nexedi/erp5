# return columns from shape of axis 1 of ndarray
# never return more than the first 100 columns
array = context.getArray()

if array is None:
  return []

else:
  if len(context.getArrayShape()) < 2:
    return [('index', 'Index'), ('1', '1')]
  else:
    return [('index', 'Index')] + [(str(i), str(i)) for i in range(min(context.getArrayShape()[1], 100))]
