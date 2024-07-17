"""
  Returns a group category based on career
  and or assignments in such way that the returned
  value describes the most accurately the default group
  which a person has been assigned to.

  Default implementation considers the list of
  valid assigned groups, if any, and returns the most recent
  one. Else, it returns the career group.

  Implementation is based on Person_getAssignedGroupList.
  (to be implemented).
"""

if REQUEST is not None:
  # This script has proxy roles, so we don't allow users to call it directly
  from AccessControl import getSecurityManager
  from zExceptions import Unauthorized
  if not 'Manager' in getSecurityManager().getUser().getRoles():
    raise Unauthorized(script)

from DateTime import DateTime
now = DateTime()

existing_group_set = {}
for assignment in context.contentValues(portal_type='Assignment'):
  if assignment.getGroup() \
      and assignment.getValidationState() == 'open' \
      and ( assignment.getStartDate() is None or
            assignment.getStartDate() <= now <= assignment.getStopDate()):
    existing_group_set[assignment.getGroup()] = 1

# If we have multiple groups defined on assignments, this scripts does not
# try to guess, and fallback to the default career's group
if len(existing_group_set.keys()) == 1:
  return list(existing_group_set.keys())[0]

# no group found on open assignments, returns the default group
# (on a person document this is acquired on the default career's subordination)
return context.getGroup()
