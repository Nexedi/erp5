portal = context.getPortalObject()
operation = None
use_list = []
parameter_dict = {}

transient_output_item = None
context.checkConsistency(fixit=True)
initial_product = context.getSpecialiseValue(portal_type="Data Transformation").getResourceValue()
for analysis_line in sorted(context.objectValues(portal_type="Data Analysis Line"),
                           key=lambda x: x.getIntIndex()):
  resource = analysis_line.getResourceValue()
  if resource == initial_product:
    use_list = analysis_line.getUseList()
  if resource is not None:
    resource_portal_type = resource.getPortalType()
  else:
    resource_portal_type = ''
  if resource_portal_type == 'Data Operation':
    operation_analysis_line = analysis_line
    operation = analysis_line.getResourceValue()
  else:
    parameter = {}
    for portal_type in ["Data Array", "Data Array View", "Progress Indicator"] + \
                        list(portal.getPortalDataSinkTypeList()) + \
                        list(portal.getPortalDataDescriptorTypeList()):
      value = analysis_line.getAggregateValue(portal_type=portal_type)
      if value is not None:
        parameter[portal_type] = value
    if analysis_line.getQuantity() < 0 and "big_data/analysis/transient" in analysis_line.getUseList():
      # at the moment we only support transient data arrays
      parameter['Data Array'] = transient_input_item
    if analysis_line.getQuantity() > 0 and "big_data/analysis/transient" in analysis_line.getUseList():
      # at the moment we only support transient data arrays
      transient_output_item = portal.data_array_module.newContent(portal_type='Data Array',
                                                                  temp_object=True)
      parameter['Data Array'] = transient_output_item
    for base_category in analysis_line.getVariationRangeBaseCategoryList():
      parameter[base_category] = analysis_line.getVariationCategoryItemList(
                                   base_category_list=(base_category,))[0][0]
    reference = analysis_line.getReference()

    parameter["Start Date"] = analysis_line.getStartDate()
    parameter["Stop Date"] = analysis_line.getStopDate()
    parameter["causality_reference"] = analysis_line.getCausalityReference()
    parameter["causality_relative_url"] = analysis_line.getCausality()
    parameter["reference"] = analysis_line.getReference()
    # several lines with same reference wil turn the parameter into a list
    if reference in parameter_dict:
      if not isinstance(parameter_dict[reference], list):
        parameter_dict[reference] = [parameter_dict[reference]]
      parameter_dict[reference].append(parameter)
    else:
      parameter_dict[reference] = parameter
      
if transient_output_item is not None and not consuming_analysis_list:
  return

script_id = operation.getScriptId()
out = getattr(operation_analysis_line, script_id)(**parameter_dict)

for consuming_analysis in consuming_analysis_list:
  portal.restrictedTraverse(consuming_analysis).DataAnalysis_executeDataOperation(transient_input_item = transient_output_item)

if out == 1:
  context.activate(serialization_tag=str(context.getUid())).DataAnalysis_executeDataOperation(consuming_analysis_list)
else:
  # only stop batch ingestions
  if "big_data/ingestion/batch" in use_list:
    context.stop()
  # stop refresh
  if context.getRefreshState() == "refresh_started":
    context.stopRefresh()

return out
