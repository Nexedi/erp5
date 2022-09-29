from Products.ERP5Type.Utils import cartesianProduct
from Products.ERP5Form.Report import ReportSection

REQUEST = context.REQUEST
variation_category_list = REQUEST.get('variation_category_list', [])
if len(variation_category_list):
  reference_variation_category_list = variation_category_list
elif reference_variation_category_list == []:
  reference_variation_category_list = context.getVariationCategoryList()

result = []

# Separate reference_variation_category_list by base category
variation_category_dict = {}
for variation_category in reference_variation_category_list:
  base_category = variation_category.split('/',1)[0]
  if base_category in variation_category_dict:
    variation_category_dict[base_category].append( variation_category )
  else:
    variation_category_dict[base_category] = [variation_category]

variation_key_list = cartesianProduct( variation_category_dict.values() )


for variation_key in variation_key_list:
  params =  {
    'reference_variation_category_list' : variation_key,
  }

  result.append(
    # Context is report form
    ReportSection(path=context.getPhysicalPath(),
                  title='Resource variation',
                  level=1,
                  form_id='Transformation_viewExpanded',
                  selection_name='transformation_expanded_selection',
                  selection_params=params,
#                  selection_columns="Id",
                  listbox_display_mode='FlatListMode'
    )
  )

return result
