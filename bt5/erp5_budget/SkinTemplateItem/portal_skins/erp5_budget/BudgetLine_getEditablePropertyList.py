item_list = []

# FIXME: it's not so good to use a category here ...

if context.isMemberOf('budget_line_type/quantity'):
  item_list.append(('quantity', 'quantity'))
if context.isMemberOf('budget_line_type/destination_debit'):
  item_list.append(('destination_debit', 'destination_debit'))
if context.isMemberOf('budget_line_type/destination_credit'):
  item_list.append(('destination_credit', 'destination_credit'))

if not item_list:
  # by default we use quantity
  item_list = [('quantity', 'quantity')]

item_list.append(
 ('membership_criterion_category_list',
  'membership_criterion_category_list'))
return item_list
