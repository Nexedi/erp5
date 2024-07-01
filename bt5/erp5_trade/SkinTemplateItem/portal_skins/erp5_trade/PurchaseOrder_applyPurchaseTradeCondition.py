# This script searches for a trade condition matching the order
# and tries to complete some fields

order = context
Base_translateString = context.Base_translateString
trade_condition_portal_type = 'Purchase Trade Condition'

trade_condition_list = order.getSpecialiseValueList(
    portal_type=trade_condition_portal_type)

tested_base_category_list = [ ]
for base_category in ('destination_section', 'destination',
                      'source_section', 'source', ):
  if context.getProperty(base_category):
    tested_base_category_list.append(base_category)

count = len(tested_base_category_list) + 1

# if no date is defined, use today's date to retrieve predicate that define start_date_range_min/max
if order.getStartDate() is None:
  predicate_context = order.asContext(start_date=DateTime())
else:
  predicate_context = order

def rank_method(trade_condition):
  rank = 0
  source_section = trade_condition.getSourceSection()
  if source_section:
    if source_section == context.getSourceSection():
      rank -= 10
    else:
      rank += 2
  source = trade_condition.getSource()
  if source:
    if source == context.getSource():
      rank -= 10
    else:
      rank += 2
  if trade_condition.getDestinationSection():
    rank -= 1
  if trade_condition.getDestination():
    rank -= 1
  rank -= len(trade_condition.getSpecialiseList())
  if trade_condition.getValidationState() == 'validated':
    rank -= 2
  return rank

while count > 0 and len(trade_condition_list) == 0:
  count -= 1
  trade_condition_list = context.portal_domains.searchPredicateList(
      predicate_context, portal_type=trade_condition_portal_type,
      tested_base_category_list=tested_base_category_list[:count],
      sort_key_method=rank_method)

keep_items = {}
if len(trade_condition_list ) == 0 :
  keep_items['portal_status_message'] = Base_translateString('No trade condition.')
  keep_items['portal_status_level'] = 'error'

else :
  # if more than one trade condition is found, simply apply the first one
  trade_condition=trade_condition_list[0].getObject()

  order.Order_applyTradeCondition(trade_condition, force=force)

  keep_items['portal_status_message'] = Base_translateString('Order updated.')

if not batch_mode:
  return context.Base_redirect(form_id, keep_items=keep_items)
