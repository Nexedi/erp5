from Products.ERP5Type.Utils import cartesianProduct
from Products.ERP5Type.Message import translateString

updated_cell_count = 0

dependant_dimensions_dict = context.BudgetLine_getSummaryDimensionKeyDict()
cell_key_list = context.getCellKeyList()

# we iterate in reversed order to update the deepest cells first
for cell_key in reversed(cartesianProduct(context.getCellRange())):
  for idx, dimension in enumerate(cell_key):
    if dimension in dependant_dimensions_dict:
      dependant_cell_list = []
      matching_cell_key = list(cell_key)
      for key in dependant_dimensions_dict[dimension]:
        matching_cell_key[idx] = key
        for other_cell_key in cell_key_list:
          if matching_cell_key == other_cell_key:
            cell = context.getCell(*other_cell_key)
            if cell is not None:
              dependant_cell_list.append(cell)

      if dependant_cell_list:
        cell = context.getCell(*cell_key)
        if cell is None:
          # if summary cell does not exist, we create it.
          cell = context.newCell(*cell_key)
          cell.edit(
            membership_criterion_base_category_list
              =[bc for bc in context.getVariationBaseCategoryList() if bc not
                in context.getMembershipCriterionBaseCategoryList()],
            membership_criterion_category_list=cell_key,
            mapped_value_property_list=('quantity', ))
        cell.setQuantity(sum([dependant_cell.getQuantity() for dependant_cell
                                in dependant_cell_list]))
        updated_cell_count += 1
      break

return context.Base_redirect(form_id,
     keep_items=dict(portal_status_message=translateString(
      "${updated_cell_count} budget cells updated.",
      mapping=dict(updated_cell_count=updated_cell_count))))
