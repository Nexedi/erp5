order = context

# copy categories
category_list = [
  'source', 'source_section', 'source_decision',
  'source_administration', 'source_payment', 'source_project',
  'source_carrier', 'source_referral', 'source_function',
  'source_trade',
  'destination', 'destination_section', 'destination_decision',
  'destination_administration', 'destination_payment', 'destination_project',
  'destination_carrier', 'destination_referral', 'destination_function',
  'destination_trade',
  'price_currency', 'incoterm', 'delivery_mode',
]
new_category_dict = {}


def getPropertyFromTradeCondition(trade_condition, property_name):
  """Get a property from the trade condition, or from a specialised trade
  condition
  """
  v = trade_condition.getProperty(property_name)
  if v:
    return v
  for specialised_trade_condition in trade_condition.getSpecialiseValueList():
    v = getPropertyFromTradeCondition(
              specialised_trade_condition, property_name)
    if v:
      return v

if not reverse_arrow_category:
  for category in category_list:
    if force or not order.getPropertyList(category):
      v = getPropertyFromTradeCondition(trade_condition, category)
      if v:
        new_category_dict[category] = v
        # for accounting transactions, we also initialize resource with the price
        # currency
        if category == 'price_currency' and \
            context.getPortalType() in \
            context.getPortalAccountingTransactionTypeList():
          new_category_dict['resource'] = v
else:
  # Reverse source and destination
  # This is useful for Returned Sale/Purchase XXX types.
  reverse_dict = {
    'source':'destination',
    'source_section':'destination_section',
    'source_decision':'destination_decision',
    'source_administration':'destination_administration',
    'source_payment':'destination_payment',
    'source_project':'destination_project',
    'source_carrier':'destination_carrier',
    'source_referral':'destination_referral',
    'source_function':'destination_function',
    'destination':'source',
    'destination_section':'source_section',
    'destination_decision':'source_decision',
    'destination_administration':'source_administration',
    'destination_payment':'source_payment',
    'destination_project':'source_project',
    'destination_carrier':'source_carrier',
    'destination_referral':'source_referral',
    'destination_function':'source_function',
    }
  for category in category_list:
    if force or not order.getPropertyList(category):
      if category in reverse_dict:
        trade_condition_category = reverse_dict[category]
      else:
        trade_condition_category = category
      v = getPropertyFromTradeCondition(trade_condition, trade_condition_category)
      if v:
        new_category_dict[category] = v
        # for accounting transactions, we also initialize resource with the price
        # currency
        if category == 'price_currency' and \
            context.getPortalType() in \
            context.getPortalAccountingTransactionTypeList():
          new_category_dict['resource'] = v


def copyPaymentCondition(order, trade_condition):
  filter_dict = {'portal_type': 'Payment Condition'}
  to_copy = trade_condition.contentIds(filter=filter_dict)
  if len(to_copy) > 0 :
    copy_data = trade_condition.manage_copyObjects(ids=to_copy)
    order.manage_pasteObjects(copy_data)
  for other_trade_condition in trade_condition.getSpecialiseValueList():
    copyPaymentCondition(order, other_trade_condition)

filter_dict = {'portal_type': 'Payment Condition'}
if force:
  order.manage_delObjects(list(order.contentIds(filter=filter_dict)))
if len(order.contentIds(filter=filter_dict)) == 0:
  copyPaymentCondition(order, trade_condition)

# set specialise
new_category_dict['specialise'] = trade_condition.getRelativeUrl()

order.edit(**new_category_dict)
