## Script (Python) "test_jps"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
# Collect movements in Zero Stock applied rule
zs_movement_list = [context.portal_simulation.zero_stock['modele-137H401_coloris-modele-137H401-1_taille-adulte-52']]

# keep only movements with a Modele resource
movement_list = []
for movement in zs_movement_list :
  try :
    if movement.getResourceValue().getPortalType() == 'Modele' :
      movement_list.append(movement)
  except :
    pass

# Parse movements into a root group
root_group = context.portal_simulation.collectMovement(movement_list)
order_list = context.portal_simulation.buildOrderList(root_group)

# update produced orders
for order in order_list:
  order.autoPlan()
  order.purchase_order_apply_condition()

return "fait"
