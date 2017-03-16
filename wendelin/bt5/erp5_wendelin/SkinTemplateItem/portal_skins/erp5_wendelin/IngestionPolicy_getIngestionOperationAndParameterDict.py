from DateTime import DateTime

now = DateTime()
today_string = now.strftime('%Y%m%d')
portal = context.getPortalObject()
portal_catalog = portal.portal_catalog

data_ingestion_reference = movement_dict.get('reference', reference)
data_ingestion_id =  "%s-%s" %(today_string, data_ingestion_reference)
resource_reference = movement_dict.get('resource_reference', None)
specialise_reference = movement_dict.get('specialise_reference', None)
  
# first search for applicable data ingestion
data_ingestion = portal_catalog.getResultValue(
  portal_type = 'Data Ingestion',
  simulation_state = 'started',
  reference =data_ingestion_reference)
  
if data_ingestion is None:
  document = portal.data_ingestion_module.get(data_ingestion_id)
  if (document is not None) and document.getSimulationState() == 'started':
    data_ingestion = document

if data_ingestion is None:
  specialise_value_list = [x.getObject() for x in portal_catalog.searchResults(
    portal_type = 'Data Supply',
    reference = specialise_reference,
    validation_state = 'validated')]
  
  # if we do not find a validated data supply, we look for a default data supply
  if not specialise_value_list:
    specialise_value_list = [x.getObject() for x in portal_catalog.searchResults(
      portal_type = 'Data Supply',
      reference = specialise_reference,
      validation_state = 'default')]
      
  # create a new data ingestion
  data_ingestion = portal.data_ingestion_module.newContent(
      id = data_ingestion_id,
      portal_type = "Data Ingestion",
      reference = data_ingestion_reference,
      start_date = now,
      specialise_value_list = specialise_value_list)
      
  property_list = ["title",
                   "source",
                   "source_section",
                   "source_project",
                   "destination",
                   "destination_section",
                   "destination_project",
                   "specialise"]
  
  composed = data_ingestion.asComposedDocument()
  data_ingestion.edit(**{p: composed.getProperty(p) for p in property_list})

  # create ingestion lines from specialise lines and assign input line
  # and operation line
  input_line = None
  operation_line = None
  for supply_line in composed.objectValues(
      portal_type = 'Data Supply Line'):
    current_line = data_ingestion.newContent(
      portal_type = "Data Ingestion Line",
      title = supply_line.getTitle(),
      aggregate = supply_line.getAggregateList(),
      int_index = supply_line.getIntIndex(),
      quantity = supply_line.getQuantity(),
      reference = supply_line.getReference(),
      resource = supply_line.getResource(),
    )
    if current_line.getResourceReference() == resource_reference:
      input_line = current_line
    elif current_line.getResourceValue().getPortalType() == "Data Operation":
      operation_line = current_line
    else:
      # we set quantity=0 for the empty line
      current_line.setQuantity(0)

  # copy device and configuration from operation line to input line
  input_line.setAggregateSet(
    input_line.getAggregateList() + operation_line.getAggregateList())
  
  # Check if we have a batch referece
  data_ingestion_batch_reference =  movement_dict.get(
                                    'aggregate_data_ingestion_batch_reference',
                                    None)
  data_ingestion_batch_id =  "%s-%s" %(today_string,
                                       data_ingestion_batch_reference)

  data_sink = None
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
        data_sink = previous_data_ingestion_line\
          .getAggregateDataSinkValue()

    input_line.setDefaultAggregateValue(data_ingestion_batch)

  
  data_product = portal.portal_catalog.getResultValue(
    portal_type = "Data Product",
    reference = resource_reference)
    
  data_sink_type = data_product.getAggregatedPortalType()
  
  if data_sink is None:
    data_sink = portal.getDefaultModule(data_sink_type).newContent(
      portal_type = data_sink_type,
      reference = data_ingestion_reference)
    data_sink.validate()
  
  input_line.setDefaultAggregateValue(data_sink)
  data_ingestion.start()

else:
  # find ingestion line for current resource
  for line in data_ingestion.objectValues(portal_type="Data Ingestion Line"):
    if line.getResourceReference() == resource_reference:
      input_line = line
    elif line.getResourceValue().getPortalType() == "Data Operation":
      operation_line = line

data_operation = operation_line.getResourceValue()
parameter_dict = {
   input_line.getReference(): input_line.getAggregateDataSinkValue(),
  'bucket_reference': movement_dict.get('bucket_reference', None)}

return data_operation, parameter_dict
