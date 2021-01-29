now = DateTime()

return (
  context.getValidationState() == 'open'
  and (not context.hasStartDate() or context.getStartDate() <= now)
  and (not context.hasStopDate() or context.getStopDate() >= now)
)
