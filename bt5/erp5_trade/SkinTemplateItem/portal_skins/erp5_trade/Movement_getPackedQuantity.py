movement = context
delivery_uid = movement.getExplanationUid()
resource_uid = movement.getResourceUid()
variation_text = movement.getVariationText()
packed_quantity = 0

sql_list = movement.Movement_zGetPackedQuantity(
                       explanation_uid=delivery_uid,
                       resource_uid=resource_uid,
                       variation_text=variation_text)

if len(sql_list)>0 :
  if sql_list[0].quantity is not None :
    return float(sql_list[0].quantity)

return packed_quantity
