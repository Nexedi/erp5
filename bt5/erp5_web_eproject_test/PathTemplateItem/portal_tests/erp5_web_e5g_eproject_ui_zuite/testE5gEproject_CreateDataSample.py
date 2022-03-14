from builtins import str
from builtins import range
portal =  context.getPortalObject()

"""Delete objects we are about to create """
for i in range(start, start + num):
  if getattr(portal.project_module, 'project_' + str(i), None) is not None:
    portal.project_module.deleteContent('project_' + str(i))
  if getattr(portal.task_module, 'task_' + str(i), None) is not None:
    portal.task_module.deleteContent('task_' + str(i))

"""Create objects with given parameters"""
for i in range(start, start + num):
  portal.project_module.newContent(id = 'project_' + str(i), title = 'Super Project %d' % i, reference = 'Super Project %d' % i, portal_type='Project')
  portal.task_module.newContent(id = 'task_' + str(i), title = 'Super Task %d' % i, portal_type='Task')

return 'Created Successfully.'
