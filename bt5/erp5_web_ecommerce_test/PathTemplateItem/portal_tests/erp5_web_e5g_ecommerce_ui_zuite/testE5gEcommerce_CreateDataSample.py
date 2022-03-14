from builtins import str
from builtins import range
portal =  context.getPortalObject()

"""Delete objects we are about to create """
for i in range(start, start + num):
  if getattr(portal.product_module, 'product_' + str(i), None) is not None:
    portal.product_module.deleteContent('product_' + str(i))

"""Create objects with given parameters"""
for i in range(start, start + num):
  portal.product_module.newContent(id = 'product_' + str(i), title = 'Super Product %d' % i, portal_type='Product')

return 'Created Successfully.'
