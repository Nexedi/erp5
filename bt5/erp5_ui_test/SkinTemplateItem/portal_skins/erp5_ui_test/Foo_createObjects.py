"""Create sub object for Foo"""
from builtins import str
from builtins import range
from DateTime import DateTime
date = DateTime('2009/01/01')
for i in range(start, start + num):
  document = context.newContent(id = str(i), title = 'Title %d' % i, start_date = date)
  if (editable == 0):
    document.manage_permission('Modify portal content', [], 0)
  date += 1

return 'Created Successfully.'
