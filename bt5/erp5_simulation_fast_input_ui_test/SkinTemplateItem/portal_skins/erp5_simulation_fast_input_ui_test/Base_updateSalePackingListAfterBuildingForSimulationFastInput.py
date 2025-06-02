portal = context.getPortalObject()
movement_and_corresponding_simulation_movement_list_dict = {}
for simulation_movement in [portal.restrictedTraverse(path) for path in related_simulation_movement_path_list]:
  movement = simulation_movement.getDeliveryValue()
  if not movement in movement_and_corresponding_simulation_movement_list_dict:
    movement_and_corresponding_simulation_movement_list_dict[movement] = []
  movement_and_corresponding_simulation_movement_list_dict[movement].append(simulation_movement)

delivery_dict = {}
for movement in movement_and_corresponding_simulation_movement_list_dict:
  delivery = movement.getRootDeliveryValue()
  for simulation_movement in movement_and_corresponding_simulation_movement_list_dict[movement]:
    order_simulation_movement = simulation_movement.getParentValue().getParentValue()
    order = order_simulation_movement.getDeliveryValue().getRootDeliveryValue()
  if not delivery in delivery_dict:
    delivery_dict[delivery] = set()
  delivery_dict[delivery].add(order)

for delivery in delivery_dict:
  delivery.setCausalityValueList(list(delivery_dict[delivery]))
  delivery.confirm()
