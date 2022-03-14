from builtins import str
from builtins import range
portal =  context.getPortalObject()

"""Delete objects we are about to create """
for i in range(start, start + num):
  if getattr(portal.bug_module, 'bug_' + str(i), None) is not None:
    portal.bug_module.deleteContent('bug_' + str(i))

"""Create objects with given parameters"""
for i in range(start, start + num):
  portal.bug_module.newContent(id = 'bug_' + str(i), title = 'Super Bug %d' % i, portal_type='Bug')

return 'Created Successfully.'
