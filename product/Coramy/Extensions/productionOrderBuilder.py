def productionOrderBuilder(self):

  context = self

  # Delete all proposed orders
  for o in context.portal_catalog(simulation_state = "auto_planned", parent_uid=[context.ordre_fabrication.getUid()]) :
    realo = o.getObject()
    realo.aq_parent._delObject(o.id)

  # Empty Zero Stock
  for mid in  context.portal_simulation.zero_stock.contentIds():
    context.portal_simulation.zero_stock._delObject(mid)

  # Expand Zero Stock as many times as needed (1 or 2 for the Coramy case)
  # for i in range(0,1):
  context.portal_simulation.zero_stock.expand()

  # Collect movements in Zero Stock applied rule
  zs_movement_list = context.portal_simulation.zero_stock.contentValues()

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

  # Look at result
  # return map(lambda x:x.getRelativeUrl(), order_list)
  for order in order_list:
    order.autoPlan()
    order.purchase_order_apply_condition()

  request = context.REQUEST
  redirect_url = '%s/view?%s' % ( context.absolute_url()
                                  , 'portal_status_message=%s+propositions+OF+créés.' % len(order_list)
                                  )

  request[ 'RESPONSE' ].redirect( redirect_url )
