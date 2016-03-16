packing_list_content = context

for simulation_movement in packing_list_content.getDeliveryRelatedValueList():
  simulation_movement.reindexObject()
