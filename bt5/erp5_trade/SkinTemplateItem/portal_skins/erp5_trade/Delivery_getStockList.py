def getOrderStr(movement_list, resource_value):
  order_str = ''
  sum_quantity = movement_idx = 0
  for movement_idx, movement in enumerate(movement_list):
    quantity = movement.getQuantity()
    quantity_unit_value = movement.getQuantityUnitValue()
    if quantity_unit_value is None:
      continue

    order_str += '%s%.f%s' % (movement_idx and ', ' or '', quantity,
                              quantity_unit_value.getShortTitle())

    converted_quantity = resource_value.convertQuantity(quantity,
                                                        movement.getQuantityUnit(),
                                                        resource_value.getDefaultQuantityUnit())

    if converted_quantity:
      sum_quantity += converted_quantity

  if not sum_quantity:
    return None
  elif movement_idx > 0:
    order_str += ' ' + context.Base_translateString('(${quantity}${quantity_unit} total)',
                                                    mapping={'quantity': sum_quantity,
                                                             'quantity_unit': resource_value.getShortTitle()})

  return order_str


movement_dict = {}
for movement in context.getMovementList():
  resource_value = movement.getResourceValue(portal_type=context.getPortalProductTypeList())
  if resource_value is not None:
    movement_dict_key = resource_value.getUid(), tuple(sorted(movement.getVariationCategoryList()))
    movement_dict.setdefault(movement_dict_key, []).append(movement)


line_list = []
order_dict = {}
for inventory in context.getFutureInventoryList(*args, **kwargs):
  resource_value = inventory.getResourceValue()
  dict_key = resource_value.getUid(), tuple(sorted(inventory.getVariationCategoryList()))

  try:
    movement_list = movement_dict[dict_key]
    del movement_dict[dict_key]
  except KeyError:
    pass
  else:
    order_dict[inventory.getUid()] = getOrderStr(movement_list, resource_value)

  line_list.append(inventory)

if movement_dict:
  for movement_list in list(movement_dict.values()):
    for movement in movement_list:
      resource_value = movement.getResourceValue()

      temp_movement = movement.asContext(getCurrentInventory=str,
                                         getAvailableInventory=str,
                                         inventory='')

      line_list.append(temp_movement)
      order_str = getOrderStr([movement], resource_value)
      if not order_str:
        continue

      order_dict[movement.getUid()] = order_str

context.REQUEST.set('order_dict', order_dict)

return line_list
