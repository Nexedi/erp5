cell_range = []
# Those value are define on property sheet of portal type
resource = context.getDefaultResourceValue()
if resource is None: # When we have a supply line in the resource
  resource = context.getParentValue()

base_category_list = resource.getVariationBaseCategoryList()

for c in base_category_list:
  # try to display line first, then column, and finally others
  if matrixbox==1:
    # XXX matrixbox is right_display (not as listfield) => invert display and value in item
    cell_range.append(map(lambda x: (x[1], x[0]),
                          resource.getVariationCategoryItemList(
                                 base_category_list=(c,),
                                 display_base_category=display_base_category,
                                 omit_individual_variation=0, sort_id='id')))
  else:
    cell_range.append(
             resource.getVariationCategoryList(base_category_list=(c,),
                                               omit_individual_variation=0, sort_id='id'))


predicate_list = context.contentValues(
                              filter={'portal_type':'Predicate Group'})
pred_ids = []
if predicate_list != []:
  if matrixbox == 1:
    pred_ids = list(map(lambda x: (x.getRelativeUrl(), x.getTitle()),
                                   predicate_list))
  else:
    pred_ids = list(map(lambda x: x.getRelativeUrl(), predicate_list))

# Insert predicat list for display in columns
cell_range.insert(1, pred_ids)

# Remove empty range
cell_range = filter(lambda x: x!=[], cell_range)

return cell_range
