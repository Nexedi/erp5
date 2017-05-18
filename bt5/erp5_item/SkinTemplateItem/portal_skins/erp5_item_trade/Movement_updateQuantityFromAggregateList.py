if context.isMovement():
  movement_list = context,
else:
  movement_list = context.getCellValueList(base_id='movement')
for movement in movement_list:
  quantity = 0
  item_list = movement.getAggregateValueList()
  for item in item_list:
    if item.getQuantityUnit() != movement.getQuantityUnit():
      if len(item_list) > 1:
        raise NotImplementedError(
          'Quantity unit from the movement differs from quantity'
          ' unit on the item')
      else:
        movement.setQuantityUnit(item.getQuantityUnit())
    quantity += item.getQuantity(at_date=at_date)
  movement.setQuantity(quantity)
