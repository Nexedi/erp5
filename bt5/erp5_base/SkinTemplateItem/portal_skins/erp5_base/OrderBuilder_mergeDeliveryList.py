"""
Script to be customized to merge deliveries
Here we pick the delivery that was created first
"""
for delivery_list in mergeable_delivery_list_list:
  delivery_list = sorted(
    delivery_list,
    key=lambda x: x.getCreationDate(),
  )
  main_delivery = delivery_list.pop(0)
  for delivery in delivery_list:
    cb_data = delivery.manage_cutObjects([x.getId() for x in delivery.objectValues()])
    _, = main_delivery.manage_pasteObjects(cb_data)
    delivery.cancel()
