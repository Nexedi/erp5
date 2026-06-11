current_date=DateTime()
valid_assignment_list = []

# Keep consistency with Product.ERP5Security.ERP5UserManager.getValidAssignmentList
# except: checked_permission usage and no transaction
for assignment in context.contentValues(
    portal_type='Assignment',
    checked_permission="Access contents information"):
  if assignment.getValidationState() == 'open':
    if assignment.getStartDate() is not None and \
           assignment.getStartDate() >= current_date:
      continue
    if assignment.getStopDate() is not None and \
           assignment.getStopDate() <= current_date:
      continue
    valid_assignment_list.append(assignment)
return valid_assignment_list
