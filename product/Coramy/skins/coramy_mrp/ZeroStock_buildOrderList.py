## Script (Python) "ZeroStock_buildOrderList"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
if 1:
  # Delete all proposed orders
  for o in context.portal_catalog(simulation_state="auto_planned", parent_uid=[context.ordre_fabrication.getUid()]) :
    realo = o.getObject()
    realo.aq_parent.deleteContent(realo.getId())

  # Empty Zero Stock
  context.portal_simulation.zero_stock.deleteContent(context.portal_simulation.zero_stock.contentIds())

  # Expand Zero Stock as many times as needed (1 or 2 for the Coramy case)
  # for i in range(0,1):
  context.portal_simulation.zero_stock.expand()

# Collect movements in Zero Stock applied rule
zs_movement_list = context.portal_simulation.zero_stock.contentValues()

# keep only movements with a Modele resource
movement_list = []
for movement in zs_movement_list[0:100] :
  resource_value = movement.getResourceValue()
  if resource_value is not None:
    #if resource_value.getPortalType() == 'Modele' :
    movement_list.append(movement)

# Parse movements into a root group
root_group = context.portal_simulation.collectMovement(movement_list)
order_list = context.portal_simulation.buildOrderList(root_group)

# update produced orders
for order in order_list:
  order.autoPlan()
  order.purchase_order_apply_condition()

# reEmpty Zero Stock because we don't want to see the zero_stock quantities in the columns future_stock
context.portal_simulation.zero_stock.deleteContent(context.portal_simulation.zero_stock.contentIds())

request = context.REQUEST
redirect_url = '%s/view?%s' % ( context.absolute_url()
                                , 'portal_status_message=%s+propositions+OF+créés.' % len(order_list)
                                )

request[ 'RESPONSE' ].redirect( redirect_url )
