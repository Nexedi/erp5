#For Cloudooo : Proxify it to allow anonymous user to discover metadata of uploaded file
current_date=DateTime()
assignment_list = []
for assignment in context.contentValues(portal_type='Assignment'):
  if assignment.getValidationState() == 'open':
    start_date = assignment.getStartDate()
    stop_date = assignment.getStopDate()
    if start_date is not None and stop_date is not None and start_date <= current_date < stop_date:
      assignment_list.append(assignment)
    elif start_date is not None and stop_date is None and start_date <= current_date:
      assignment_list.append(assignment)
    elif stop_date is not None and start_date is None and current_date < stop_date:
      assignment_list.append(assignment)
    elif start_date is None and stop_date is None:
      assignment_list.append(assignment)
return assignment_list
