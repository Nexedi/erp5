resource_value = context.Item_getResourceValue()
movement_value = context.getAggregateRelatedValue()

result_item_list = [('', '')]
if resource_value is not None:
  result_item_list.extend([(x.getTranslatedLogicalPath(), x.getCategoryRelativeUrl(base=0)) for x in resource_value.getQuantityUnitValueList()])
elif movement_value is not None:
  result_item_list.extend([(x.getTranslatedLogicalPath(), x.getCategoryRelativeUrl(base=0)) for x in movement_value.getQuantityUnitValueList()])

return result_item_list
