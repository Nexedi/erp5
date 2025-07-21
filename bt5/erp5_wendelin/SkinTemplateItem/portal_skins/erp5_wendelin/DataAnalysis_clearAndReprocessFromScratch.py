# only refresh if causalility analysis is not refreshing
for data_analysis in context.getCausalityValueList(portal_type="Data Analysis"):
  if data_analysis.getRefreshState() in ("refresh_planned", "refresh_started"):
    return "Refresh not started because causality analysis refresh not finished"

for line in context.objectValues(portal_type="Data Analysis Line"):
  if line.getResourceValue().getPortalType() == "Data Product" and line.getQuantity() == -1:
    progress_indicator = line.getAggregateProgressIndicatorValue()
    if progress_indicator is not None:
      progress_indicator.setIntOffsetIndex(0)
      progress_indicator.setStringOffsetIndex('')
  if line.getResourceValue().getPortalType() == "Data Product" and line.getQuantity() == 1:
    data_array = line.getAggregateDataArrayValue()
    if data_array is not None:
      data_array.setArray(None)
      data_array.setStartDate(None)
      data_array.manage_delObjects(list(data_array.keys()))

if context.getRefreshState() != "refresh_started":
  context.startRefresh()
context.activate(serialization_tag=str(context.getUid())).DataAnalysis_executeDataOperation()
