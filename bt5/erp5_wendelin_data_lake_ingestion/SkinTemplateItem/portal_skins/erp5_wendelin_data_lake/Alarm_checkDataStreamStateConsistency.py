# Consistency state alarm that checks and fixes (changes state) that
# all published Data Sets have their linked Data Stream(s) matching its state.

for data_set in context.portal_catalog(portal_type = "Data Set",
                               validation_state = "published"):
  data_ingestion_line_list = context.portal_catalog(
                             portal_type = "Data Ingestion Line",
                             aggregate_uid = data_set.getUid())
  for data_ingestion_line in data_ingestion_line_list:
    data_stream = data_ingestion_line.getAggregateValue(portal_type = "Data Stream")
    if data_stream and data_stream.getValidationState() == "validated":
      data_stream.publish()
