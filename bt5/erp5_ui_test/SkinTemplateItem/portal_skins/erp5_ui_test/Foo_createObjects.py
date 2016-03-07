"""Create sub object for Foo"""
from DateTime import DateTime
date = DateTime('2009/01/01')
for i in range(start, start + num):
  context.newContent(id = str(i), title = 'Title %d' % i, start_date = date)
  date += 1

return 'Created Successfully.'
