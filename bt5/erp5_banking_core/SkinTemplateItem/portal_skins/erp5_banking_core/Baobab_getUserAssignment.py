if user_id is None:
  user_id = context.portal_membership.getAuthenticatedMember().getUserName()
person_list = context.acl_users.erp5_users.getUserByLogin(user_id)
if not person_list:
  return None
assignment_list = person_list[0].contentValues(filter={'portal_type': 'Assignment'})
if not assignment_list:
  return None
valid_assignment = None
now = DateTime()
for assignment in assignment_list:
  if assignment.getValidationState() == 'open':
    stop = assignment.getStopDate()
    start = assignment.getStartDate()
    if (stop is None or stop > now) and (start is None or start < now):
      if valid_assignment is not None:
        raise ValueError('There are too many valid assignments for user %r' % (user_id, ))
      valid_assignment = assignment
return valid_assignment
