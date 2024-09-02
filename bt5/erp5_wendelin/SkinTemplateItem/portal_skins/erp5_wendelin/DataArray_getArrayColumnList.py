# return columns from shape of axis 1 of ndarray
# if it is a structured array, set column names from dtype
# never return more than the first 100 columns
array = context.getArray()

if array is None:
  return []

else:
  if context.getArrayDtypeNames() is not None:
    return [('index', 'Index')] + [(str(i).replace(" ", "_"), str(i).replace(" ", "_")) for i in context.getArrayDtypeNames()]
  elif len(context.getArrayShape()) < 2:
    return [('index', 'Index'), ('1', '1')]
  else:
    return [('index', 'Index')] + [(str(i).replace(" ", "_"), str(i).replace(" ", "_")) for i in range(min(context.getArrayShape()[1], 100))]
