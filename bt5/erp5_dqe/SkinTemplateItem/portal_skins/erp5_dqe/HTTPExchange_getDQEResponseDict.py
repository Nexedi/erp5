from json import loads

resource_value = context.getResourceValue()
if not resource_value.isMemberOf('http_exchange_resource/dqe'):
  return {}

try:
  response_dict = loads(context.getResponse('{}'))
except ValueError:
  return {}
# In all cases, the actual response is an inner dict that has key '1',
# apart from 'SIRETINFO' ('OrganisationData' resource for us) that it is just the dict
if resource_value == context.getPortalObject().portal_categories.http_exchange_resource.dqe.OrganisationData:
  return response_dict
return response_dict.get('1', {})
