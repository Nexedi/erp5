"""Returns list of resources' inventories used in consumption for production
   Show only resources which are defined in transformation.
"""
movement_list = context.getMovementList()
portal = context.getPortalObject()
transformation_line_list_dict = {}
consumed_resource_list = []

resource_portal_type_list = kwargs.get("resource_portal_type")
if resource_portal_type_list is None:
  resource_portal_type_list = portal.getPortalResourceTypeList()
if isinstance(resource_portal_type_list, str):
  resource_portal_type_list = [resource_portal_type_list]
resource_portal_type_set = set(resource_portal_type_list)

for movement in movement_list:
  transformation = movement.getSpecialiseValue()
  if transformation is not None:
    transformation_line_list = transformation.objectValues()
    filtered_transformation_line_list = []
    for transformation_line in transformation_line_list:
      transformation_resource = transformation_line.getResourceValue()
      if transformation_resource is not None and transformation_resource.getPortalType() in resource_portal_type_set:
        filtered_transformation_line_list.append(transformation_line)
        consumed_resource_list.append(transformation_resource)
    transformation_line_list_dict[movement] = filtered_transformation_line_list
  else:
    transformation_line_list_dict[movement] = ()

if not consumed_resource_list:
  return ()

kwargs['resource_uid'] = [resource.getUid() for resource in consumed_resource_list]
kwargs['group_by_section'] = 0
kwargs['group_by_node'] = 1
kwargs['group_by_variation'] = 1
kwargs['section_uid'] = context.getDestinationSectionUid()

inventory_dict = {}
for inventory in portal.portal_simulation.getFutureInventoryList(*args,**kwargs):
  inventory_dict[inventory.resource_relative_url,
                 inventory.variation_text,
                 inventory.node_relative_url] = inventory

result_list = inventory_dict.values()
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

# sort result_list
transformation_allowed_content_type_list = context.portal_types['Transformation'].getTypeAllowedContentTypeList()
def compare(a, b):
    return cmp((consumption_dict.has_key(a.getUid()), a.portal_type in transformation_allowed_content_type_list),
               (consumption_dict.has_key(b.getUid()), b.portal_type in transformation_allowed_content_type_list),
               )
result_list.sort(cmp=compare, reverse=True)

context.REQUEST.set('consumption_dict', consumption_dict)
return result_list
