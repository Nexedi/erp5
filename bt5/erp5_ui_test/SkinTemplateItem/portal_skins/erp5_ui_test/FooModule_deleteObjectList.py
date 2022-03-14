"""Delete a range of sub objects"""
from builtins import str
from builtins import range
from DateTime import DateTime

for i in range(start, start + num):
  context.deleteContent(str(i))

return 'Deleted Successfully.'
