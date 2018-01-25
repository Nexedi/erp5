item_list = []
movement_list = context.getImmobilisationMovementList()
#context.log('movement_list %s' % context.getRelativeUrl(),[m.getPath() for m in movement_list])
movemement_path_list = []
tag = script.id + '_' + context.getPath()
for movement in movement_list:
  # XXX: Tagged reindexation added to replace after_path_and_method_id. May be unnecessary.
  movement.recursiveReindexObject(activate_kw={'tag': tag})
  movemement_path_list.append(movement.getPath())
  for item in movement.getAggregateValueList():
    if item not in item_list:
      item_list.append(item)
for item in item_list:
  item.activate(tag='expand_amortisation', after_tag=tag, after_path_and_method_id=(movemement_path_list, ('updateImmobilisationState',) )).expandAmortisation()
