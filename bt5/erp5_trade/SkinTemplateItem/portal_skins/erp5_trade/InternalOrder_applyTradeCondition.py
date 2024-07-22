# This script searches for a trade condition matching the order
# and tries to complete some fields

order = context
Base_translateString = context.Base_translateString
trade_condition_portal_type_list = ('Internal Trade Condition',)

trade_condition_list = order.getSpecialiseValueList(
    portal_type=trade_condition_portal_type_list)

tested_base_category_list = [ ]
for base_category in ('source_section', 'source',
                      'destination_section', 'destination', ):
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
  destination_section_group = None
  destination_section = trade_condition.getDestinationSection()
  if destination_section:
    destination_section_group = trade_condition.getDestinationSectionValue().getGroup()
    if destination_section == context.getDestinationSection():
      rank -= 10
    else:
      rank += 2
  destination = trade_condition.getDestination()
  if destination:
    if destination == context.getDestination():
      rank -= 10
    else:
      rank += 2
  if trade_condition.getSourceSection():
    rank -= 1
    if destination_section_group:
      source_section_group = trade_condition.getSourceSectionValue().getGroup()
      if source_section_group:
        if source_section_group.startswith(destination_section_group) \
             or destination_section_group.startswith(source_section_group):
          # trade conditions where both sections are in the same group must have high priority
          rank -= 20
  if trade_condition.getSource():
    rank -= 1
  rank -= len(trade_condition.getSpecialiseList())
  if trade_condition.getValidationState() == 'validated':
    rank -= 2
  return rank

while count > 0 and len(trade_condition_list) == 0:
  count -= 1
  trade_condition_list = context.portal_domains.searchPredicateList(
      predicate_context, portal_type=trade_condition_portal_type_list,
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
  # set date
  if hasattr(order, 'getReceivedDate') and order.getReceivedDate() is None:
    context.setReceivedDate(DateTime())

  keep_items['portal_status_message'] = Base_translateString('Order updated.')

if not batch_mode:
  return context.Base_redirect(form_id, keep_items=keep_items)
