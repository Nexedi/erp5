request = context.REQUEST
resource = request.get('resource',None)
if resource in (None,'None'):
  resource = request.get('field_my_resource',None)
item_model = context.getPortalObject().restrictedTraverse(resource)

variation_list = item_model.getVariationRangeCategoryItemList(display_id='title',display_base_category=0)

# The 50 one is the default one
def sort_variation_list(a, b):
  if a[0] == '50':
    return -1
  return cmp(a[0], b[0])

variation_list.sort(sort_variation_list)
return variation_list
