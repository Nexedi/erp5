"""Returns a dictionnary of dependant variation categories for this budget
line.
This can be used to know if a budget cell aggregates the values from other
budget cells.
For example, the returned dictionnary can be:
  { 'function/f': ['function/f/f1', 'function/f/f2'],
    'source/account_type/asset': ['source/account_type/asset/cash'], }
As we can see on the example, only individual categories are returned, not cell
coordinates.
"""
# look on the budget model to see which base categories are used for non strict
# membership. We will only update summaries for thoses axis
non_strict_base_category_set = {}
budget_model = context.getParentValue().getSpecialiseValue()
if budget_model is not None:
  for budget_variation in budget_model.contentValues(
        portal_type=context.getPortalBudgetVariationTypeList()):
    if budget_variation.isMemberOf('budget_variation/budget_cell') \
        and budget_variation.getInventoryAxis() in (
            'movement',
            'node_category',
            'mirror_node_category',
            'section_category',
            'mirror_section_category',
            'function_category',
            'project_category',
            'payment_category',):

      non_strict_base_category_set[
          budget_variation.getProperty('variation_base_category')] = True

# build a dict of dependant dimensions
dependant_dimensions_dict = {}
for bc in non_strict_base_category_set.keys():
  vcl = reversed(context.getVariationCategoryList(base_category_list=(bc,)))
  for vc in vcl:
    dependant_vc_list = [other_vc for other_vc in vcl
                          if other_vc.startswith('%s/' % vc)
                          and other_vc not in dependant_dimensions_dict]
    if dependant_vc_list:
      dependant_dimensions_dict[vc] = dependant_vc_list

return dependant_dimensions_dict
