import json

portal = context.getPortalObject()

dummy_response = portal.restrictedTraverse(response_id)

description = dummy_response.getDescription()

if description:
  result = json.loads(description)
  result['status'] = 'done'
  return json.dumps(result)

return json.dumps({'status': 'pending'})
