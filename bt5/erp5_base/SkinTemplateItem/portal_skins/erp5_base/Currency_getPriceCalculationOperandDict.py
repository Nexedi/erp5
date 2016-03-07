"""
Search for all predicates that corresponds to this particular context
and returns the base price of the resource
This script derives form getPriceCalculationOperandDict and is invoked by getPrice.

  movement -- transaction line

  **kw -- dictionary containing all information of the transaction

"""

def sort_key(exchange_line):
  if exchange_line.getPortalType() == 'Currency Exchange Cell':
    exchange_line = exchange_line.getParentValue()
  start_date_range_min = exchange_line.getStartDate()
  start_date_range_max = exchange_line.getStopDate()
  if start_date_range_min and start_date_range_max:
    return start_date_range_max - start_date_range_min
  return 2**16

# If getPrice is directly called on a resource, call directly
# Resource_getPriceCalculationOperandDict on the resource
if movement is None:
  return context.Resource_getPriceCalculationOperandDict(**kw)
else:
  if validation_state is None:
    validation_state = 'validated'
  kw.setdefault('portal_type', 'Currency Exchange Line')

  # discard `categories` that might have been passed by Movement_getPriceCalculationOperandDict
  # and that searchPredicateList does not accept.
  kw.pop('categories', None)

  predicate_list = context.portal_domains.searchPredicateList(
      context=movement,
      validation_state=validation_state,
      test=True,
      **kw)

  predicate_list.sort(key=sort_key)
  # For each predicate(i.e: Currency Exchange Line) found, get the exchange rate
  # with the reference currency
  for predicate in predicate_list:
    price = predicate.getPrice() or predicate.getBasePrice()
    if price:
      return dict(price=price)
