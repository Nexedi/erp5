data_delivery = context

error_list = []

current_data_supply_list = data_delivery.getSpecialiseList(portal_type='Data Supply')
if len(current_data_supply_list) > 1:
  error_list.append("More than one Data Supply linked to Data Delivery")
  return error_list

causality_data_supply_set = set()
for causality in data_delivery.getCausalityValueList():
  causality_data_supply_set.update(causality.getSpecialiseList(portal_type='Data Supply'))

missing_data_supply_list = []
for data_supply in causality_data_supply_set:
  if data_supply not in current_data_supply_list:
    missing_data_supply_list.append(data_supply)
for data_supply in missing_data_supply_list:
  error_list.append("Missing Data Supply: %s" % data_supply)

return error_list
