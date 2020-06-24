portal = context.getPortalObject()

category_list = [
    c for c in [
        movement.getDestinationSection(base=True),
        movement.getDestinationPayment(base=True)
    ] if c
]

account = movement.getDestinationAccount() or context.getDestination()
if not account:
  # try to find from predicates
  resource = movement.getResourceValue()
  if resource is not None:
    account = next(
        (
            predicate.getDestinationAccount()
            for predicate in portal.portal_domains.searchPredicateList(
                context=movement,
                portal_type='Purchase Supply Line',
            )
            if predicate.getDestinationAccount()), None)

if account:
  category_list.append('destination/%s' % account)

function = movement.getDestinationFunction(
    base=True) or context.getDestinationFunction(base=True)
if function:
  category_list.append(function)

funding = movement.getDestinationFunding(
    base=True) or context.getDestinationFunding(base=True)
if funding:
  category_list.append(funding)

project = movement.getDestinationProject(
    base=True) or context.getDestinationProject(base=True)
if project:
  category_list.append(project)

return category_list
