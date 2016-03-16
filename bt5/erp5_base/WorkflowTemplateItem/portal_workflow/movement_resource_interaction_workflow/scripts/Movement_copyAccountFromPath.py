'''Lookup source account & destination account from applicable paths and copy
them on this movement.
'''
movement = state_change['object']
searchPredicateList = movement.getPortalObject().portal_domains.searchPredicateList

resource = movement.getResourceValue()
if resource is not None:
  if not movement.getDestinationAccount():
    for predicate in searchPredicateList(
                      context=movement, portal_type='Purchase Supply Line'):
      if predicate.getDestinationAccount():
        movement.setDestinationAccount(predicate.getDestinationAccount())
        break
  if not movement.getSourceAccount():
    for predicate in searchPredicateList(
                      context=movement, portal_type='Sale Supply Line'):
      if predicate.getSourceAccount():
        movement.setSourceAccount(predicate.getSourceAccount())
        break
else:
  movement.setSourceAccount(None)
  movement.setDestinationAccount(None)
