from DateTime import DateTime

now = DateTime()
now_string = now.strftime('%Y%m%d-%H%M%S-%f')[:-3]

portal = context.getPortalObject()
portal_catalog = portal.portal_catalog

reference_separator = portal.getIngestionReferenceDictionary()["reference_separator"]
reference_end_single = portal.getIngestionReferenceDictionary()["single_end_suffix"]
none_extension = portal.getIngestionReferenceDictionary()["none_extension"]

try:
  # remove supplier, eof, size and hash from reference
  reference = reference_separator.join(reference.split(reference_separator)[1:-3])

  data_ingestion_reference = reference
  eof = movement_dict.get('eof', reference_end_single) if movement_dict.get('eof', reference_end_single) != "" else reference_end_single
  resource_reference = movement_dict.get('resource_reference', None)
  supplier = movement_dict.get('supplier', None)
  extension = movement_dict.get('extension', None)
  dataset_reference = movement_dict.get('dataset_reference', None)
  data_ingestion_id =  '%s_%s_%s_%s' %(supplier, dataset_reference, now_string, eof)
  size = movement_dict.get('size', None) if movement_dict.get('size', None) != "" else None
  hash_value = movement_dict.get('hash', None) if movement_dict.get('hash', None) != "" else None

  # search for applicable data ingestion
  data_ingestion = portal_catalog.getResultValue(
    portal_type = 'Data Ingestion',
    reference = data_ingestion_reference)

  if data_ingestion is not None:
    if data_ingestion.getSimulationState() != 'started':
      if eof == reference_end_single: # if not split (one single ingestion), invalidate old ingestion
        portal.ERP5Site_invalidateIngestionObjects(data_ingestion_reference)

  specialise_value_list = [x.getObject() for x in portal_catalog.searchResults(
    portal_type = 'Data Supply',
    reference = 'embulk',
    validation_state = 'validated')]

  # create a new data ingestion
  data_ingestion = portal.data_ingestion_module.newContent(
      id = data_ingestion_id,
      portal_type = "Data Ingestion",
      title = movement_dict.get('filename', data_ingestion_reference),
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
  for supply_line in composed.objectValues(portal_type = 'Data Supply Line'):
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

  if hash_value is None or eof != reference_end_single: # do not set hash if split, calculate when append
    hash_value = ""
  data_stream = portal.data_stream_module.newContent(
    portal_type = "Data Stream",
    id = data_ingestion_id,
    version = hash_value,
    title = "%s%s" % (data_ingestion.getTitle(), "."+extension if extension != none_extension else ""),
    reference = data_ingestion_reference)

  input_line.setDefaultAggregateValue(data_stream)

  if dataset_reference is not None:
    data_set = portal.data_set_module.get(dataset_reference)
    try:
      if data_set is None:
        data_set = portal.data_set_module.newContent(
          portal_type = "Data Set",
          title = "Data set " + dataset_reference,
          reference = dataset_reference,
          id = dataset_reference,
          description = "Default description.",
          version = "000"
        )
        data_set.validate()
    except:
      data_set = portal.data_set_module.get(dataset_reference)
    if portal.IsReferenceInvalidated(data_set):
      portal.RevalidateReference(data_set)
    if data_set.getValidationState() == "invalidated":
      data_set.validate()
    input_line.setDefaultAggregateValue(data_set)

  data_ingestion.start()

  data_operation = operation_line.getResourceValue()
  data_stream = input_line.getAggregateDataStreamValue()

  if eof == reference_end_single:
    data_stream.validate()

  return data_operation, {'data_stream': data_stream}
except Exception as e:
  context.logEntry(''.join(["[ERROR] Error during ingestion policy operation: ", str(e)]))
  raise e
