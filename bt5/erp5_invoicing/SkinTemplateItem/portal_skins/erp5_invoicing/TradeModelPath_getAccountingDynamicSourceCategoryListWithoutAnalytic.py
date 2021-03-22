portal = context.getPortalObject()

category_list = [
    c for c in [
        movement.getSourceSection(base=True),
        movement.getSourcePayment(base=True)
    ] if c
]

account = movement.getSourceAccount()
if not account:
  # try to find from predicates, with fallback on the account
  # defined on the trade model path
  resource = movement.getResourceValue()
  if resource is not None:
    account = next(
        (
            predicate.getSourceAccount()
            for predicate in portal.portal_domains.searchPredicateList(
                context=movement,
                portal_type='Sale Supply Line',
            )
            if predicate.getSourceAccount()), context.getSource())
if account:
  category_list.append('source/%s' % account)

return category_list
