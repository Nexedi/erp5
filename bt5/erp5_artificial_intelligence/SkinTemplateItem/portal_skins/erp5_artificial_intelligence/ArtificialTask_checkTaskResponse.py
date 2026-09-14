import json

portal = context.getPortalObject()

active_process = portal.restrictedTraverse(response_id)

description = active_process.getDescription()

if description:
  result = json.loads(description)
  result['status'] = 'done'
  return json.dumps(result)

return json.dumps({'status': 'pending'})
