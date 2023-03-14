"""Returns the date when the `deliver` transaction was passed"""
portal = context.getPortalObject()
getInfoFor = portal.portal_workflow.getInfoFor

for wf_id in context.getTypeInfo().getTypeWorkflowList():
  for item in getInfoFor(context, 'history', wf_id=wf_id, default=[]):
    if item['action'] == 'deliver':
      return item['time']

return context.getModificationDate()
