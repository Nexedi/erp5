portal = context.getPortalObject()

category_list = [
    c for c in [
        movement.getSourceSection(base=True),
        movement.getSourcePayment(base=True)
    ] if c
]

account = movement.getSourceAccount() or context.getSource()
if not account:
  # try to find from predicates
  resource = movement.getResourceValue()
  if resource is not None:
    account = next(
        (
            predicate.getSourceAccount()
            for predicate in portal.portal_domains.searchPredicateList(
                context=movement,
                portal_type='Sale Supply Line',
            )
            if predicate.getSourceAccount()), None)
if account:
  category_list.append('source/%s' % account)

return category_list
