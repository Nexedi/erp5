from Products.ERP5Type.Document import newTempBase

if context.getArray() is None:
  return []

class SequenceSliceMap():
  def __init__(self, sequence_slice, usual_slice_length, total_length):
    self.sequence_slice = sequence_slice
    self.length = usual_slice_length
    self.total_length = total_length

  def __repr__(self):
    return repr(list(self))

  def __len__(self):
    return self.total_length

  def __getitem__(self, index):
    return self.sequence_slice[index % self.length]

def createTempBase(nr, row):
  def getElementFromArray(array, index):
    return array[index]

  def getElementFromScalar(scalar, index=None):
    return scalar

  column_list = [col for col in context.DataArray_getArrayColumnList() if col[0] != 'index']
  column_iterator = enumerate(column_list)
  if len(column_list) == 1:
    getElement = getElementFromScalar
  else:
    getElement = getElementFromArray
  return newTempBase(context.getPortalObject(),
                     str(id(row)),
                     index = nr,
                     **{col[0]: str(getElement(row, i)) for i, col in column_iterator})


length = context.getArrayShape()[0]

# never access more than 1000 lines at once
list_lines = min(list_lines, limit, 1000)

if context.REQUEST.has_key("limit"):
  list_start = limit[0]
  list_lines = limit[1] - limit[0]

orig_list_start = list_start
if orig_list_start + list_lines > length:
  orig_list_start = length - length - (length % list_lines)

list_start = max(length - list_start - list_lines, 0)
if abs(orig_list_start) < list_lines and orig_list_start != 0:
  list_end = abs(orig_list_start)
else:
  list_end = max(list_start + list_lines, 0)
#list_end = max(list_start + list_lines, 0)

if list_start == list_end:
  array_slice = [context.getArrayIndex(list_start)]
else:
  array_slice = context.getArraySlice(list_start, list_end)

temp_base_list = list(reversed([createTempBase(nr + list_start, row) for nr, row in enumerate(array_slice)]))

# return lazy sequence of temp objects
return SequenceSliceMap(temp_base_list, list_lines, length)
