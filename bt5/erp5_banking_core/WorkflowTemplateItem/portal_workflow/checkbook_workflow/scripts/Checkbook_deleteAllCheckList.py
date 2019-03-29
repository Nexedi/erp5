checkbook = state_change['object']

for check in checkbook.objectValues():
  check.delete()
  if check.getSimulationState() != 'deleted':
    msg = Message(domain="ui", message="Sorry, no way to delete this check $id",
                  mapping = {'id' : check.getId()})
    raise ValueError(msg,)
