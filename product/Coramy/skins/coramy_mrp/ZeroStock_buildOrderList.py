## Script (Python) "ZeroStock_buildOrderList"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
return   context.portal_simulation.zero_stock.deleteContent(context.portal_simulation.zero_stock.contentIds())

if 0:
  # Delete all proposed orders
  #production_list = context.portal_catalog(simulation_state="auto_planned", parent_uid=[context.ordre_fabrication.getUid()])
  #context.ordre_fabrication.deleteContent(map(lambda b:b.id, production_list))
  buy_list = context.portal_catalog(simulation_state="auto_planned", parent_uid=[context.commande_achat.getUid()])
  #return map(lambda b:b.id, buy_list)
  #context.commande_achat.deleteContent(map(lambda b:b.id, buy_list))

  # Empty Zero Stock
  context.portal_simulation.zero_stock.deleteContent(context.portal_simulation.zero_stock.contentIds())

  context.portal_simulation.commitTransaction() # Release any SQL locks

  # Expand Zero Stock as many times as needed (1 or 2 for the Coramy case)
  # for i in range(0,1):
  context.portal_simulation.portal_simulation.zero_stock.expand()

# Collect movements in Zero Stock applied rule
zs_movement_list = context.portal_simulation.zero_stock.contentValues()
#return len(zs_movement_list )
#context.portal_simulation.commitTransaction() # Release any SQL locks

# keep only movements with a Modele resource
movement_list = []
for movement in zs_movement_list:
  resource_value = movement.getResourceValue()
  if resource_value is not None:
    movement_list.append(movement)

# Parse movements into a root group
root_group = context.portal_simulation.collectMovement(movement_list)
order_list = context.portal_simulation.buildOrderList(root_group)

# update produced orders
for order in order_list:
  order.autoPlan()
  order.purchase_order_apply_condition()

context.portal_simulation.commitTransaction() # Release any SQL locks
return "Done"

# reEmpty Zero Stock because we don't want to see the zero_stock quantities in the columns future_stock
context.portal_simulation.zero_stock.deleteContent(context.portal_simulation.zero_stock.contentIds())

request = context.REQUEST
redirect_url = '%s/view?%s' % ( context.absolute_url()
                                , 'portal_status_message=%s+propositions+OF+créés.' % len(order_list)
                                )

request[ 'RESPONSE' ].redirect( redirect_url )
