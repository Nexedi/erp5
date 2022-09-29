from Products.ERP5Type.Utils import cartesianProduct
portal = context.getPortalObject()

tracking_parameters = {
    'node_uid': context.getSourceUid(),
    'resource_uid': context.getResourceUid(),
    'at_date': context.getStartDate(),
    'output': 1,

    'item_catalog_title': kw.get('title') or '',
    'item_catalog_reference': kw.get('reference') or '',
    'item_catalog_portal_type': kw.get('portal_type') or '',
    'item_catalog_validation_state': kw.get('validation_state') or '',
}


check_variation = bool(context.getVariationCategoryList())
acceptable_variation_category_list = \
      cartesianProduct(context.getCellRange(base_id='movement'))

result_list = []
for tracking_brain in portal.portal_simulation.getCurrentTrackingList(
                            **tracking_parameters):
  item = tracking_brain.getObject()

  # XXX can this be done in SQL ?
  # it could, by computing all variation texts, but I don't think this is
  # really necessary.
  if check_variation and \
      item.Item_getVariationCategoryList(at_date=context.getStartDate())\
      not in acceptable_variation_category_list:
    continue

  result_list.append(item)

return result_list
