portal = context.getPortalObject()
Base_translateString = portal.Base_translateString

cell_range = []
add_predicate = 1


# Get base category list
if option_variation:
  # Get option base category list
  add_predicate = 0
  no_option_base_category_list = context.getVariationRangeBaseCategoryList(
                                                 omit_option_base_category=1)
  base_category_list = context.getVariationRangeBaseCategoryList()
  option_base_category_list = [x for x in base_category_list \
                               if x not in no_option_base_category_list]
  if not option_base_category_list:
    base_category_list_list = []
  else:
    base_category_list_list = [option_base_category_list]
else:
  # Compatibility with ERP5 Shop
  if base_id == 'reference':
    add_predicate = 0
  # Get base categories selected by the user
  if base_id in ('path', 'reference'):
    # XXX Compatibility
    selected_base_category_list = context.getPVariationBaseCategoryList()
    if not selected_base_category_list:
      # XXX Compatibility...
      if context.getParentValue().getPortalType() in \
                                  context.getPortalResourceTypeList():
        selected_base_category_list = context.getParentValue().\
                                        getPVariationBaseCategoryList()
  else:
    property_id = '%s_variation_base_category_list' % base_id[len('path_'):]
    selected_base_category_list = context.getProperty(property_id)
  base_category_list_list = [[x] for x in selected_base_category_list]

# Generate cell range
for base_category_list in base_category_list_list:
  if matrixbox:
    # XXX matrixbox is right_display (not as listfield)
    # => invert display and value in item
    cell_range.append([(x[1], x[0]) for x in
                          context.getVariationRangeCategoryItemList(
                                 base_category_list=base_category_list,
                                 display_base_category=display_base_category,
                                 sort_id='id')])
  else:
    cell_range.append(
              context.getVariationRangeCategoryList(
                                     base_category_list=base_category_list,
                                     sort_id='id'))
# If no option, don't display quantity range
if option_variation:
  if cell_range != []:
    add_predicate = 1
# Do we need to add predicate ?
if add_predicate:
  # Get quantity step
  # XXX Dirty, use the same quantity range for option/no option matrix
  if base_id == 'path':
    # XXX Compatibility
    price_parameter = 'base_price'
  else:
    price_parameter = base_id[len('path_'):]
    option_base_id_begin_with = 'optional_'
    if price_parameter.startswith(option_base_id_begin_with):
      price_parameter = price_parameter[len(option_base_id_begin_with):]
  predicate_list = context.getQuantityPredicateValueList(price_parameter)

  if matrixbox:
#     pred_ids = [(x.getRelativeUrl(), x.getTitle()) for x in predicate_list]
    # Translate the matrixbox ranges
    pred_ids = []
    for predicate in predicate_list:
      predicate_criterion_list = predicate.getCriterionList()
      predicate_title = ''
      for criterion in predicate_criterion_list:
        if criterion.property == 'quantity':
          min_qty = criterion.min
          max_qty = criterion.max
          if min_qty is None:
            predicate_title = Base_translateString("Quantity < ${max_quantity}",
                                                   mapping={'max_quantity': max_qty})
          elif max_qty is None:
            predicate_title = Base_translateString("${min_quantity} <= Quantity",
                                                   mapping={'min_quantity': min_qty})
          else:
            predicate_title = Base_translateString("${min_quantity} <= Quantity < ${max_quantity}",
                                                   mapping={'min_quantity': min_qty,
                                                            'max_quantity': max_qty})
          break
      pred_ids.append((predicate.getRelativeUrl(), predicate_title))
  else:
    pred_ids = [x.getRelativeUrl() for x in predicate_list]
  # Insert predicat list for display in columns
  cell_range.insert(1, pred_ids)
# Remove empty range
cell_range = [x for x in cell_range if x!=[]]
return cell_range
