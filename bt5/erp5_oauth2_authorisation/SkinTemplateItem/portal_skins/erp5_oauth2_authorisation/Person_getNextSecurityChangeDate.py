"""
Return the earliest future date at which this Person security (security groups or global roles)
based on the current properties of the documents which involved in this computation.

May be overridden/extended in instances using non-generic conditions.
"""
now = DateTime()
result = None
for assignment_value in context.objectValues(portal_type='Assignment'):
  if assignment_value.getValidationState() == 'open':
    for assignent_date in (
      assignment_value.getStartDate(),
      assignment_value.getStopDate(),
    ):
      if assignent_date is not None and assignent_date > now and (
        result is None or
        result > assignent_date
      ):
        result = assignent_date
return result
