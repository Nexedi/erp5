portal = context.getPortalObject()

category_list = [
    c for c in [
        movement.getDestinationSection(base=True),
        movement.getDestinationPayment(base=True)
    ] if c
]

account = movement.getDestinationAccount()
if not account:
  # try to find from predicates, with fallback on the account
  # defined on the trade model path
  resource = movement.getResourceValue()
  if resource is not None:
    account = next(
        (
            predicate.getDestinationAccount()
            for predicate in portal.portal_domains.searchPredicateList(
                context=movement,
                portal_type='Purchase Supply Line',
            )
            if predicate.getDestinationAccount()), context.getDestination())
if account:
  category_list.append('destination/%s' % account)

return category_list
