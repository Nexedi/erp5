from Products.ERP5Type.Document import newTempBase
portal = context.getPortalObject()
catalog = portal.portal_catalog.getResultValue
if current:
  method = portal.portal_simulation.getCurrentTrackingList
else:
  method = portal.portal_simulation.getTrackingList

uid = context.getUid()

history_list = []

simulation_state = portal.getPortalCurrentInventoryStateList() \
                                  + portal.getPortalTransitInventoryStateList() \
                                  + portal.getPortalReservedInventoryStateList()

kw['item.simulation_state'] = simulation_state
for res in method(aggregate_uid=uid, **kw):
  history = newTempBase(context, str(len(history_list)))
  explanation = catalog(uid=res.delivery_uid)
  node_value = catalog(uid=res.node_uid)
  section_value = catalog(uid=res.section_uid)
  resource_value = catalog(uid=res.resource_uid) 
  history.edit(
      #uid = catalog(uid=res.uid).getTitle(),
      date=res.getDate(),
      node_title=node_value is not None and node_value.getTitle() or None,
      source_title=explanation.getSourceTitle(),
      section_title=section_value is not None and section_value.getTitle() or None,
      resource_title=resource_value is not None and resource_value.getTitle() or None,
      explanation=explanation.getTitle(),
      translated_portal_type = explanation.getTranslatedPortalType(),
      quantity = explanation.getQuantity(),
      url=explanation.absolute_url(),
      item_quantity = context.getQuantity(at_date=res.getDate()), 
      variation_category_item_list = [x[0] for x in explanation.getVariationCategoryItemList()],
      simulation_state=explanation.getTranslatedSimulationStateTitle(),
  )
 
  history_list.append(history)
  
return history_list
