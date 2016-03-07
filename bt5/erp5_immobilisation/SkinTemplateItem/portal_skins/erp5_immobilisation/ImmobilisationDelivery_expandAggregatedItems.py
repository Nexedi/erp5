item_list = []
movement_list = context.getImmobilisationMovementList()
#context.log('movement_list %s' % context.getRelativeUrl(),[m.getPath() for m in movement_list])
movemement_path_list = []
for movement in movement_list:
  movemement_path_list.append(movement.getPath())
  for item in movement.getAggregateValueList():
    if item not in item_list:
      item_list.append(item)
for item in item_list:
  item.activate(tag='expand_amortisation', after_path_and_method_id=(movemement_path_list, ('immediateReindexObject', 'recursiveImmediateReindexObject', 'updateImmobilisationState',) )).expandAmortisation()
