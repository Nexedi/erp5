'''
Creates a Data Acquisition Unit, as well as the corresponding Data Supply, with the provided CDN Access tag as reference.

This script returns a JSON response, as it is intended to be called by Wendelin Telecom slave instances
requested by CDNs Access in order to register themselves on the platform.
'''

import json

portal = context.getPortalObject()

response_dict = {}

# Check if CDN Access is already registered
data_acquisition_unit = context.portal_catalog.getResultValue(
  portal_type='Data Acquisition Unit',
  reference=fluentbit_tag,
  validation_state='validated'
)
if data_acquisition_unit:
  status = "ok"
  message = "CDN Access with tag %s already exists." % fluentbit_tag
  response_dict = dict(
    status=status,
    message=message
  )
  return json.dumps(response_dict)

# Check if the fluentbit tag has a valid format
fluentbit_tag_components = fluentbit_tag.split('_')
if len(fluentbit_tag_components) not in [4, 5]:
  status = "error"
  message = "Invalid CDN Access tag %s found" % fluentbit_tag
  response_dict = dict(
    status=status,
    message=message
  )
  return json.dumps(response_dict)

data_acquisition_unit = portal.data_acquisition_unit_module.newContent(
  portal_type='Data Acquisition Unit',
  reference=fluentbit_tag,
  data_unit_type='cdn'
)
data_acquisition_unit.validate()
data_supply = data_acquisition_unit.DataAcquisitionUnit_createCdnDataSupply(batch=1)

# Not automatic link to a project
#data_supply.setDestinationProject(destination_project)

status = "ok"
message = "CDN Access with tag %s successfully registered." % fluentbit_tag
response_dict = dict(
  status=status,
  message=message
)
return json.dumps(response_dict)
