now = DateTime()
return [
  x for x in context.objectValues(portal_type='Assignment')
    if x.getValidationState() == 'open'
      and (not x.hasStartDate() or x.getStartDate() <= now)
      and (not x.hasStopDate() or x.getStopDate() >= now)
]
