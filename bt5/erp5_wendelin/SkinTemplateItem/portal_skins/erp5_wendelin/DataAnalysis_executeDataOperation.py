portal = context.getPortalObject()
operation = None
use = None
parameter_dict = {}
initial_product = context.getSpecialiseValue().getResourceValue()
for analysis_line in context.objectValues(portal_type="Data Analysis Line"):
  resource = analysis_line.getResourceValue()
  if resource == initial_product():
    use = analysis_line.getUse()
  if resource is not None:
    resource_portal_type = resource.getPortalType()
  else:
    resource_portal_type = ''
  if resource_portal_type == 'Data Operation':
    operation_analysis_line = analysis_line
    operation = analysis_line.getResourceValue()
  else:
    parameter = {}
    for portal_type in ["Data Array", "Progress Indicator"] + \
                        list(portal.getPortalDataSinkTypeList()) + \
                        list(portal.getPortalDataDescriptorTypeList()):
      value = analysis_line.getAggregateValue(portal_type=portal_type)
      if value is not None:
        parameter[portal_type] = value

    for base_category in analysis_line.getVariationRangeBaseCategoryList():
      parameter[base_category] = analysis_line.getVariationCategoryItemList(
                                   base_category_list=(base_category,))[0][0]
    reference = analysis_line.getReference()
    # several lines with same reference wil turn the parameter into a list
    if reference in parameter_dict:
      if not isinstance(parameter_dict[reference], list):
        parameter_dict[reference] = [parameter_dict[reference]]
      parameter_dict[reference].append(parameter)
    else:
      parameter_dict[reference] = parameter
script_id = operation.getScriptId()
out = getattr(operation_analysis_line, script_id)(**parameter_dict)

# only stop batch ingestions
if use == "big_data/ingestion/batch":
  context.stop()

return out
