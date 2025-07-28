portal = context.getPortalObject()

error_list = []

data_movement = context

data_delivery = data_movement.getParentValue()
data_transformation = data_delivery.getSpecialiseValue(portal_type='Data Transformation')
if data_transformation is None:
  return error_list

data_transformation_line = portal.portal_catalog.getResultValue(
  parent_uid=data_transformation.getUid(),
  reference=data_movement.getReference(),
  resource_relative_url=data_movement.getResource()
)
if data_transformation_line is None:
  return error_list

aggregate_type_set = set([
  aggregate.getPortalType() for aggregate in data_movement.getAggregateValueList()
])
item_type_list = data_transformation_line.getAggregatedPortalTypeList()

for item_type in item_type_list:
  if item_type not in aggregate_type_set and item_type != 'Data Array Line':
    error_list.append("Item Type %s is missing" % item_type)

return error_list
