"""Create objects with given parameters"""
from builtins import str
from builtins import range
for i in range(start, start + num):
  context.newContent(id = 'foo_' + str(i), title = 'Foo Title %d' % i, portal_type='Foo')
for i in range(start, start + num):
  context.newContent(id = 'bar_' + str(i), title = 'Bar Title %d' % i, portal_type='Bar')

return 'Created Successfully.'
