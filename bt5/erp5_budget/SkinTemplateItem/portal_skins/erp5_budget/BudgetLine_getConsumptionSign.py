editable_property_list = list(zip(*context.BudgetLine_getEditablePropertyList()))[0]

if 'destination_credit' in editable_property_list:
  return -1
if 'destination_asset_credit' in editable_property_list:
  return -1
return 1
