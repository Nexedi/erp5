from DateTime import DateTime

if data_ingestion_id is None:
  now = DateTime()
  today_string = now.strftime('%Y%m%d')
  data_ingestion_id =  "%s-%s" %(today_string, data_ingestion_reference)

portal = context.getPortalObject()
data_ingestion = portal.data_ingestion_module.newContent(
    id = data_ingestion_id,
    portal_type = "Data Ingestion",
    reference = data_ingestion_reference,
    specialise_list = specialise_list)

composed = data_ingestion.asComposedDocument()

property_list = ["title",
                 "source",
                 "source_section",
                 "source_project",
                 "destination",
                 "destination_section",
                 "destination_project",
                 "specialise"]

property_dict = {p: composed.getProperty(p) for p in property_list}
property_dict["start_date"] = composed.getEffectiveDate()
property_dict["stop_date"] = composed.getExpirationDate()

data_ingestion.edit(**property_dict)


# create ingestion lines from specialise lines
for supply_line in composed.objectValues(
    portal_type = 'Data Supply Line'):

  current_line = data_ingestion.newContent(
    portal_type = "Data Ingestion Line",
    title = supply_line.getTitle(),
    aggregate = supply_line.getAggregateDeviceList(),
    int_index = supply_line.getIntIndex(),
    quantity = supply_line.getQuantity(),
    reference = supply_line.getReference(),
    resource = supply_line.getResource(),
    use = supply_line.getUse()
  )
  if current_line.getResourceValue().getPortalType() == "Data Product":
    # we set quantity=0 for the data product lines
    current_line.setQuantity(0)

# start ingestion only if data supply is validated
data_supply_validated = True
for specialise_path in specialise_list:
  specialise = portal.restrictedTraverse(specialise_path)
  if specialise.getPortalType() == "Data Supply":
    if specialise.getValidationState() != "validated":
      data_supply_validated = False
if data_supply_validated:
  data_ingestion.start()

return data_ingestion
