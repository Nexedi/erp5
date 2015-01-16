'''Lookup source function & destination function from applicable paths and copy
them on this movement.
'''
movement = state_change['object']
searchPredicateList = movement.getPortalObject().portal_domains.searchPredicateList

resource = movement.getResourceValue()
if resource is not None:
  if not movement.getDestinationFunction():
    for predicate in searchPredicateList(
                      context=movement, portal_type='Purchase Supply Line'):
      if predicate.getDestinationFunction():
        movement.setDestinationFunction(predicate.getDestinationFunction())
        break
  if not movement.getSourceFunction():
    for predicate in searchPredicateList(
                      context=movement, portal_type='Sale Supply Line'):
      if predicate.getSourceFunction():
        movement.setSourceFunction(predicate.getSourceFunction())
        break
else:
  movement.setSourceFunction(None)
  movement.setDestinationFunction(None)
