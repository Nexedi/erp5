from erp5.component.module.MovementCollectionDiff import getPropertyAndCategoryList

portal = context.getPortalObject()
for path in path_list:
  document = portal.restrictedTraverse(path)
  # Useful to reproduce Ingestion process from beginning
  # All properties of object are considered as user input
  input_parameter_dict = {'portal_type': document.getPortalType()}
  input_parameter_dict.update(getPropertyAndCategoryList(document))
  filename = document.getFilename()

  # Now starts metadata discovery process
  document.activate().discoverMetadata(filename=filename, input_parameter_dict=input_parameter_dict)
