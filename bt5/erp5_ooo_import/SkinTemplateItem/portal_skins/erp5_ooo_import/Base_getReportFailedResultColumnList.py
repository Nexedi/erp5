portal_object = context.getPortalObject()

if active_process_path is None:
  return []

active_process = context.getPortalObject().restrictedTraverse(active_process_path)
result_list = [[x.method_id, x.result] for x in active_process.getResultList()]

result_list.sort()

for [method_id, result] in result_list:
  if not result['success']:
    return [(x,x) for x in result['object'].keys()]

return []
