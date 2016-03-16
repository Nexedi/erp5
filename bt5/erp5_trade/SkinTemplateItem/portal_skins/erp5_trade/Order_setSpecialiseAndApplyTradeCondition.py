context.setSpecialiseValueList(relation_value_list, portal_type=portal_type)

if relation_value_list:
  context.Order_applyTradeCondition(context.getSpecialiseValue(), force=1)
