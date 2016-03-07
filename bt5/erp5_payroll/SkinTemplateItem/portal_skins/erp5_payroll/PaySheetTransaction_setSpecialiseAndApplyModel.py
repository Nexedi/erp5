context.setSpecialiseValueList(relation_value_list, portal_type=portal_type)

if relation_value_list:
  context.PaySheetTransaction_applyModel(force=1)
