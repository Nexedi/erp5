from DateTime import DateTime

now = DateTime()
today_string = now.strftime('%Y%m%d')
portal = context.getPortalObject()
portal_catalog = portal.portal_catalog

data_ingestion_reference = movement_dict.get('reference', reference)
resource_reference = movement_dict.get('resource_reference', None)
specialise_reference = movement_dict.get('specialise_reference', None)
destination_section_reference = movement_dict.get('destination_section_reference', None)
data_ingestion_id =  "%s-%s-%s" %(today_string, destination_section_reference, data_ingestion_reference)

data_ingestion_query_kw = dict(
  portal_type = 'Data Ingestion',
  simulation_state = ['started', 'stopped'],
  reference = data_ingestion_reference)

if destination_section_reference is not None:
  data_ingestion_query_kw["destination_section_reference"] = destination_section_reference

# first search for applicable data ingestion
data_ingestion = portal_catalog.getResultValue(**data_ingestion_query_kw)

def init_input_line(input_line, operation_line):
  # copy device and configuration from operation line to input line
  input_line.setAggregateSet(
    input_line.getAggregateList() + operation_line.getAggregateList())

  # Check if we have a batch referece
  data_ingestion_batch_reference =  movement_dict.get(
                                    'aggregate_data_ingestion_batch_reference',
                                    None)
  data_ingestion_batch_id =  "%s-%s" %(today_string,
                                       data_ingestion_batch_reference)

  data_sink_type_list = []
  data_sink_list = []
  data_product = None
  if data_ingestion_batch_reference is not None:
    data_ingestion_batch = portal_catalog.getResultValue(
      portal_type = "Data Ingestion Batch",
      reference = data_ingestion_batch_reference)

    if data_ingestion_batch is None:
      data_ingestion_batch = portal.data_ingestion_batch_module.get(
                                                        data_ingestion_batch_id)
    if data_ingestion_batch is None:
      data_ingestion_batch = portal.data_ingestion_batch_module.newContent(
        id = data_ingestion_batch_id,
        portal_type = "Data Ingestion Batch",
        reference = data_ingestion_batch_reference)

    else:
      previous_data_ingestion_line = portal_catalog.getResultValue(
        portal_type = "Data Ingestion Line",
        resource_reference = resource_reference,
        aggregate_uid = data_ingestion_batch.getUid())

      if previous_data_ingestion_line is not None:
        data_product = previous_data_ingestion_line.getResourceValue()
        data_sink_type_list = data_product.getAggregatedPortalTypeList()
        data_sink_list = previous_data_ingestion_line\
                         .getAggregateValueList(portal_type=data_sink_type_list)

    input_line.setDefaultAggregateValue(data_ingestion_batch)

  if not data_sink_list:
    if not data_sink_type_list:
      if data_product is None:
        data_product = portal.portal_catalog.getResultValue(
          portal_type = "Data Product",
          reference = resource_reference)
      data_sink_type_list = data_product.getAggregatedPortalTypeList()

    for data_sink_type in data_sink_type_list:
      # This should be more generic
      if data_sink_type not in ("Progress Indicator", "Data Ingestion Batch"):
        # first try to find existing validated data sink
        # with same device, project, resource (but can be different source)
        data_sink = portal.portal_catalog.getResultValue(
          portal_type=data_sink_type,
          validation_state="validated",
          item_device_relative_url=operation_line.getAggregateDevice(),
          item_project_relative_url=input_line.getDestinationProject(),
          item_resource_uid=input_line.getResourceUid())

        if data_sink is None:
          data_sink = portal.getDefaultModule(data_sink_type).newContent(
            portal_type = data_sink_type,
            reference = "%s-%s" %(data_ingestion_reference, resource_reference))
          data_sink.validate()
        data_sink_list.append(data_sink)

  input_line.setAggregateValueList(
                            input_line.getAggregateValueList() + data_sink_list)
  input_line.setQuantity(1)

if data_ingestion is None:
  document = portal.data_ingestion_module.get(data_ingestion_id)
  if (document is not None) and document.getSimulationState() in ('started', 'stopped'):
    data_ingestion = document

if modify and data_ingestion is None:
  specialise_query_kw = dict(portal_type = 'Data Supply',
    reference = specialise_reference,
    validation_state = 'validated')
  if destination_section_reference is not None:
    specialise_query_kw["destination_section_reference"] = destination_section_reference

  specialise_list = [x.getRelativeUrl() for x in portal_catalog(**specialise_query_kw)]

  # if we do not find a validated data supply, we look for a default data supply
  if not specialise_list:
    specialise_query_kw["validation_state"] = 'default'
    specialise_list = [x.getRelativeUrl() for x in portal_catalog(**specialise_query_kw)]

  # create a new data ingestion
  data_ingestion = portal.ERP5Site_createDataIngestion(specialise_list,
                                                       data_ingestion_reference,
                                                       data_ingestion_id)

# find ingestion line for current resource
for line in data_ingestion.objectValues(portal_type="Data Ingestion Line"):
  if line.getResourceReference() == resource_reference:
    input_line = line
  elif line.getResourceValue().getPortalType() == "Data Operation":
    operation_line = line

if modify and input_line.getQuantity() == 0:
  init_input_line(input_line, operation_line)

data_operation = operation_line.getResourceValue()
parameter_dict = {
   input_line.getReference(): \
     {v.getPortalType(): v for v in input_line.getAggregateValueList()}}
bucket_reference = movement_dict.get('bucket_reference', None)
if bucket_reference is not None:
  parameter_dict['bucket_reference'] = bucket_reference

return data_operation, parameter_dict
