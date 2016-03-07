prevision = {}

if context.getDestinationAccount():
  prevision['destination'] = context.getDestinationAccount()

if context.getSourceAccount():
  prevision['source'] = context.getSourceAccount()

return prevision
