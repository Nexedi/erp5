"""
  A sample usage of how ical categories can be used
  (here to group tasks related to the same project
  or events related to the same sale opportunity)
"""
project = None

if brainObject is not None:
  real_context = brainObject
else:
  real_context = context

portal_type = real_context.getPortalType()
if portal_type == 'Task':
  project = real_context.getSourceProjectValue()
elif portal_type in context.getPortalEventTypeList():
  project = real_context.getFollowUpValue()

if project is not None:
  # we have to tweak here because not all object have references
  if hasattr(project, 'getReference'):
    return project.getReference() or project.getTitle()
  else:
    return project.getTitle()
return ''
