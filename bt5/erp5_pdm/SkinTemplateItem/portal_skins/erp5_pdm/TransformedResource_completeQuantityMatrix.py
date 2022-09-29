consumption_list = context.getSpecialiseValueList()
# convert string to float
reference_quantity = float( reference_quantity )

cell_key_list = context.getCellKeyList( base_id = 'quantity')

for cell_key in cell_key_list:

  # If cell exists, do not modify it
  if not context.hasCell(base_id='quantity', *cell_key ):
    ratio = 1
    consumption_applied = 0

    # XXX This part can be really improve, but it works
    for reference_variation_category in reference_variation_category_list:
      for consumption in consumption_list:
        for key in cell_key:
          consumption_ratio = consumption.getQuantityRatio(reference_variation_category, key )
          if consumption_ratio is not None:
            ratio = ratio * consumption_ratio
            consumption_applied = 1

    # If no consumption applied, do not do anything
    if consumption_applied:
      cell = context.newCell(base_id='quantity', *cell_key)
      cell.edit(mapped_value_property_list = ['quantity'],
                quantity = ratio * reference_quantity
      )
      cell.setMembershipCriterionCategoryList( cell_key )
      cell.setMembershipCriterionBaseCategoryList( context.getQVariationBaseCategoryList() )

return context.Base_redirect(form_id, keep_item={'portal_status_message': 'Consumption applied.'})
