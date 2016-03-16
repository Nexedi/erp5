portal = context.getPortalObject()
for path in path_list:
  document = portal.restrictedTraverse(path)
  # Useful to reproduce Ingestion process from beginning
  # All properties of object are considered as user input
  input_parameter_dict = {'portal_type': document.getPortalType()}
  for property_id in document.propertyIds():
    if property_id not in ('portal_type', 'uid', 'id',) \
      and document.hasProperty(property_id):
      input_parameter_dict[property_id] = document.getProperty(property_id)
  filename = document.getFilename()

  # Now starts metadata discovery process
  document.activate().discoverMetadata(filename=filename, input_parameter_dict=input_parameter_dict)
