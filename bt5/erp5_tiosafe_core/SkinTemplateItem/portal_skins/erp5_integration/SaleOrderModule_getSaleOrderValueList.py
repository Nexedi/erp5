sale_order_list = []
if gid:
  return []

if not id:
  while context_document.getParentValue().getPortalType() != "Synchronization Tool":
    context_document = context_document.getParentValue()

  site = context_document.Base_getRelatedObjectList(portal_type="Integration Module")[0].getObject().getParentValue()
  params = {'delivery.start_date' : {'query' : site.getStartDate(), 'range' : "min"},
            'delivery.stop_date' : {'query' : site.getStopDate(), 'range' : "max"},
            'default_specialise_uid' : site.getSourceTradeUid()}
  sale_order_list = [x.getObject() for x in context.portal_catalog(portal_type='Sale Order',
                                                                   simulation_state='confirmed',
                                                                   **params)]
else:
  # work on defined sale order (id is not None)
  sale_order = getattr(context.sale_order_module, id)
  if sale_order.getSimulationState() != 'confirmed':
    sale_order_list.append(sale_order)

return sale_order_list
