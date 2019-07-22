from Products.ERP5Type.Document import newTempBase
portal = context.getPortalObject()
if current:
  method = portal.portal_simulation.getCurrentTrackingList
else:
  method = portal.portal_simulation.getTrackingList

# tracking list is much more readable if locations are sorted by dates.
kw.setdefault('sort_on', (('date', 'ascending',),))

history_list = []
for brain in method(aggregate_uid=context.getUid(), **kw):
  explanation = brain.getExplanationValue()
  history = newTempBase(explanation.getParentValue(), explanation.getId())
  date = brain.getDate()
  history.edit(
      date=date,
      node_title=brain.node_title,
      source_title=explanation.getSourceTitle(),
      section_title=brain.section_title,
      resource_title=brain.resource_title,
      explanation=explanation.getTitle(),
      translated_portal_type=explanation.getTranslatedPortalType(),
      quantity=explanation.getQuantity(),
      # item_quantity=context.getQuantity(at_date=date),
      variation_category_item_list=[x[0] for x in explanation.getVariationCategoryItemList()],
      simulation_state=explanation.getTranslatedSimulationStateTitle(),
  )

  history_list.append(history)

return history_list
