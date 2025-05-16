'''
Creates a Data Acquisition Unit, as well as the corresponding Data Supply, with the provided ORS tag as reference.

This script returns a JSON response, as it is intended to be called by Wendelin Telecom slave instances
requested by ORSs in order to register themselves on the platform.
'''

import json

portal = context.getPortalObject()

response_dict = {}

# Check if ORS is already registered
data_acquisition_unit = context.portal_catalog.getResultValue(
  portal_type='Data Acquisition Unit',
  reference=fluentbit_tag,
  validation_state='validated'
)
if data_acquisition_unit:
  status = "ok"
  message = "ORS with tag %s already exists." % fluentbit_tag
  response_dict = dict(
    status=status,
    message=message
  )
  return json.dumps(response_dict)

# Check if the fluentbit tag has a valid format
fluentbit_tag_components = fluentbit_tag.split('_')
if len(fluentbit_tag_components) not in [2, 3]:
  status = "error"
  message = "Invalid ORS tag %s found" % fluentbit_tag
  response_dict = dict(
    status=status,
    message=message
  )
  return json.dumps(response_dict)

ors_hostname, ors_comp_id = fluentbit_tag_components[0], fluentbit_tag_components[1]
fluentbit_tag_prefix = '%s_%s' % (ors_hostname, ors_comp_id)

# Detect the case where an existing ORS has changed the last component of its tag (i.e. its radio ID):
# Search for all validated Data Acquisition Units with the same first two tag components
# and get their related destination_project
related_data_acquisition_unit_list = [
  related_data_acquisition_unit for related_data_acquisition_unit \
  in portal.data_acquisition_unit_module.searchFolder(
    portal_type='Data Acquisition Unit',
    validation_state='validated'
  ) \
  if related_data_acquisition_unit.getReference() is not None \
  and related_data_acquisition_unit.getReference().startswith(fluentbit_tag_prefix)
]
destination_project = None
if related_data_acquisition_unit_list:
  related_destination_project_list = []
  for related_data_acquisition_unit in related_data_acquisition_unit_list:
    related_data_supply = related_data_acquisition_unit.DataAcquisitionUnit_getOrsDataSupply()
    # Non-standard ORS
    if related_data_supply is None:
      continue
    related_destination_project = related_data_supply.getDestinationProject()
    if related_destination_project:
      related_destination_project_list.append(related_destination_project)

  # If there is only one destination_project found, link the new Data Acquisition Unit to it
  # Else, do not do anything automatically: this case will have to be resolved manually
  related_destination_project_set = set(related_destination_project_list)
  if len(related_destination_project_set) == 1:
    destination_project = related_destination_project_set.pop()

data_acquisition_unit = portal.data_acquisition_unit_module.newContent(
  portal_type='Data Acquisition Unit',
  reference=fluentbit_tag
)
data_acquisition_unit.validate()
data_supply = data_acquisition_unit.DataAcquisitionUnit_createOrsDataSupply(batch=1)
data_supply.setDestinationProject(destination_project)

status = "ok"
message = "ORS with tag %s successfully registered." % fluentbit_tag
response_dict = dict(
  status=status,
  message=message
)
return json.dumps(response_dict)
