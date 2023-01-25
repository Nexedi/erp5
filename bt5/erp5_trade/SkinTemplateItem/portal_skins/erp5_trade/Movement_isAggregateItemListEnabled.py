"""This script is an helper to replace complex TALES expression
for Base_viewTradeFieldLibrary/my_view_mode_aggregate_title_list.enable
"""

# If the resource accepts items, and the context is a movements (ie. not a line
# already containing cells or line that has variations but not cells yet)
if context.getResource() and context.getResourceValue().getAggregatedPortalTypeList()\
   and context.isMovement()\
   and (('Cell' in context.getPortalType()) or not context.getVariationCategoryList()):
  return True

# If the movement already has an aggregate, display it.
if context.getAggregate():
  return True

# If there's not resource yet, we give a chance to set an item.
if context.getResource() is None and context.getPortalItemTypeList():
  return True

return False
