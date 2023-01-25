"""
Return the earliest future date at which this Person security (security groups or global roles)
based on the current properties of the documents which involved in this computation.

May be overridden/extended in instances using non-generic conditions.
"""
now = DateTime()
result = None
for assignment_value in context.objectValues(portal_type='Assignment'):
  if assignment_value.getValidationState() == 'open':
    for assignment_date in (
      assignment_value.getStartDate(),
      assignment_value.getStopDate(),
    ):
      if assignment_date is not None and assignment_date > now and (
        result is None or
        result > assignment_date
      ):
        result = assignment_date
return result
