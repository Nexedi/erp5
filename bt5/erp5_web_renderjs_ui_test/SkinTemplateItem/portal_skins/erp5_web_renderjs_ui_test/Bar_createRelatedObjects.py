module = context.getParentValue()

for i in range(0, num):
  module.newContent(title='Related %d' % i, portal_type='Bar', successor_value=context)

return 'Created Successfully.'
