name_designation_match = {
  'stop': 'Unimmobilisation',
  'start': 'Immobilisation',
  'annuity': 'Annuity',
  'correction': 'Correction' }

if transaction_line is None:
  transaction_line = context
if transaction_line.getPortalType() != 'Amortisation Transaction Line':
  return []


returned_dict = {}
delivery_related_list = transaction_line.getDeliveryRelatedValueList()

for simulation_movement in delivery_related_list:
  applied_rule = simulation_movement.getParentValue()
  item_value = applied_rule.getCausalityValue()
  item_uid = item_value.getUid()

  if returned_dict.get(item_uid, None) is None:
    returned_dict[item_uid] = []
  detail_list = returned_dict[item_uid]


  value = simulation_movement.getQuantity()
  debit, credit = 0, 0
  if value < 0:
    debit = - value
  else:
    credit = value
  debit = '%0.2f' % debit
  credit = '%0.2f' % credit

  operation = simulation_movement.getId().split('_')[0]
  designation = name_designation_match.get(operation, 'Unknown')

  detail_list.append( { 'item':item_value.getTitle(), 'designation':designation, 'debit':debit, 'credit':credit } )
  returned_dict[item_uid] = detail_list


returned_value = []
for item, data in list(returned_dict.items()):
  for detail in data:
    returned_value.append(detail)

return returned_value
