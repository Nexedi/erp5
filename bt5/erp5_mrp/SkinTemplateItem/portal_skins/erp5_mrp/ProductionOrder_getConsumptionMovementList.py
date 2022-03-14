"""Returns list of resources' inventories used in consumption for production
   Show only resources which are defined in transformation.
"""
movement_list = context.getMovementList()
portal = context.getPortalObject()
transformation_line_list_dict = {}

resource_portal_type_list = kwargs.get("resource_portal_type")
if resource_portal_type_list is None:
  resource_portal_type_list = portal.getPortalResourceTypeList()
if isinstance(resource_portal_type_list, str):
  resource_portal_type_list = [resource_portal_type_list]
resource_portal_type_set = set(resource_portal_type_list)

consumed_resource_set = set()
consumed_resource_and_varation_set = set()
for movement in movement_list:
  amount_list = [x for x in movement.asComposedDocument().getAggregatedAmountList() \
                 if x.getResourceValue().getPortalType() in resource_portal_type_set]
  for amount in amount_list:
    consumed_resource_set.add(amount.getResourceValue())
    consumed_resource_and_varation_set.add(
      (amount.getResourceRelativeUrl(), amount.getVariationText()))
  transformation_line_list_dict[movement] = amount_list

if not consumed_resource_set:
  return ()

kwargs['resource_uid'] = [resource.getUid() for resource in consumed_resource_set]
kwargs['group_by_section'] = 0
kwargs['group_by_node'] = 1
kwargs['group_by_variation'] = 1
kwargs['section_uid'] = context.getDestinationSectionUid()

inventory_dict = {}
for inventory in portal.portal_simulation.getFutureInventoryList(*args,**kwargs):
  if (inventory.resource_relative_url, inventory.variation_text) in consumed_resource_and_varation_set:
    inventory_dict[inventory.resource_relative_url,
                 inventory.variation_text,
                 inventory.node_relative_url] = inventory

result_list = list(inventory_dict.values())
consumption_dict = {}
for movement in movement_list:
  for material in transformation_line_list_dict[movement]:
    material_resource = material.getResource()
    if material_resource is None:
      continue

    inventory_dict_key = (material_resource,
                          '\n'.join(sorted(material.getVariationCategoryList())),
                          movement.getDestination())

    quantity = material.getQuantity()

    try:
      obj = inventory_dict[inventory_dict_key]
    except KeyError:
      obj = material
      result_list.append(obj)
    else:
      inventory_quantity_unit = obj.getQuantityUnit()
      quantity_unit = material.getQuantityUnit()
      if quantity_unit != inventory_quantity_unit:
        quantity = material.getResourceValue().convertQuantity(quantity,
                                                               quantity_unit,
                                                               inventory_quantity_unit)

    if quantity:
      consumption_dict[obj.getUid()] = consumption_dict.get(obj.getUid(), 0) + \
                       quantity * (movement.getQuantity() or 0)

result_list.sort(key=lambda x: (x.getProperty("resource_title"), "".join([y[0] for y in x.getVariationCategoryItemList()])))
context.REQUEST.set('consumption_dict', consumption_dict)

return result_list
