from json import loads

resource_value = context.getResourceValue()
if not resource_value.isMemberOf('http_exchange_resource/dqe'):
  return {}

try:
  response_dict = loads(context.getResponse('{}'))
except ValueError:
  return {}
# In all cases, the actual response is an inner dict that has key '1',
# apart from 'SIRETINFO' ('OrganisationData' resource for us)
# and 'ESTOCADE' ('RelocationData' resource for us)
# that it is just the dict
http_exchange_resource = context.getPortalObject().portal_categories.http_exchange_resource
if resource_value in (
  http_exchange_resource.dqe.OrganisationData,
  http_exchange_resource.dqe.RelocationData,
):
  return response_dict
return response_dict.get('1', {})
