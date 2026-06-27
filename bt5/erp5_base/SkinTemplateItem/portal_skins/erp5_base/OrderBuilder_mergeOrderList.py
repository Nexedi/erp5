"""
Script to be customized to merge deliveries
Here we pick the order that was created first
"""
portal = context.getPortalObject()
translateString = portal.Base_translateString
for order_list in mergeable_order_list_list:
  order_list = sorted(
    order_list,
    key=lambda x: x.getCreationDate(),
  )
  main_order = order_list.pop(0)
  for order in order_list:
    line_list = order.objectValues()
    if line_list:
      cb_data = order.manage_cutObjects([x.getId() for x in line_list])
      main_order.manage_pasteObjects(cb_data)
    order.cancel(
      comment=translateString(
        "Merged with ${main_order_reference}",
        mapping={
          'main_order_reference': main_order.getReference()
        }
      )
    )
    portal.portal_workflow.doActionFor(
      main_order,
      'edit_action',
      comment=translateString(
        "${order_reference} was merged with this order",
        mapping={
          'order_reference': order.getReference()
        }
      )
    )
