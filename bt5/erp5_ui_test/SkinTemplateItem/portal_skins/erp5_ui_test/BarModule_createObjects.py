"""Create objects with given parameters"""
for i in range(start, start + num):
  context.newContent(id=str(i), title='Title %d' % i, portal_type='Bar')

return 'Created Successfully.'
