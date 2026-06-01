# For general purpose, get one valid member, so it can be used for validation
# or perform requests in behalf of the workgroup
from DateTime import DateTime
now = DateTime()
portal = context.getPortalObject()
workgroup = context

assignment_list = portal.portal_catalog(
  portal_type='Assignment',
  parent_portal_type='Person',
  validation_state='open',
  destination__uid=workgroup.getUid()
)

for assignment in assignment_list:
  if (not assignment.hasStartDate() or assignment.getStartDate() <= now)\
    and (not assignment.hasStopDate() or assignment.getStopDate() >= now):
    return assignment.getParentValue()

# We force raise, since this script should always return some person whenever
# it is called, else it must fail here.
raise ValueError('No user found.')
