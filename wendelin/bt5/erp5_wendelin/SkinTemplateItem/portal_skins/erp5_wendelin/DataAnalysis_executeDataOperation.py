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
    reference = analysis_line.getReference()
    aggregate = analysis_line.getAggregateDataSinkValue() or \
                analysis_line.getAggregateDataArrayValue() or \
                analysis_line.getAggregateDataDescriptorValue()
    parameter_dict[reference] = aggregate
script_id = operation.getScriptId()
getattr(operation_analysis_line, script_id)(**parameter_dict)

# only stop batch ingestions
if use == "big_data/ingestion/batch":
  context.stop()
