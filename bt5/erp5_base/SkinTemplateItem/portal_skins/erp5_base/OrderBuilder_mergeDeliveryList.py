"""
Script to be customized to merge deliveries
Here we pick the delivery that was created first
"""
portal = context.getPortalObject()
translateString = portal.Base_translateString
for delivery_list in mergeable_delivery_list_list:
  delivery_list = sorted(
    delivery_list,
    key=lambda x: x.getCreationDate(),
  )
  main_delivery = delivery_list.pop(0)
  for delivery in delivery_list:
    line_list = delivery.objectValues()
    if line_list:
      cb_data = delivery.manage_cutObjects([x.getId() for x in line_list])
      _, = main_delivery.manage_pasteObjects(cb_data)
    delivery.cancel(
      comment=translateString(
        "Merged with ${main_delivery_reference}",
        mapping={
          'main_delivery_reference': main_delivery.getReference()
        }
      )
    )
    portal.portal_workflow.doActionFor(
      main_delivery,
      'edit_action',
      comment=translateString(
        "${delivery_reference} was merged with this delivery",
        mapping={
          'delivery_reference': delivery.getReference()
        }
      )
    )
