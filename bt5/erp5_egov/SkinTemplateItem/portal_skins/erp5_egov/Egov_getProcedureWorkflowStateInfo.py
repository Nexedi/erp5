if validation_state==None or workflow_id==None:
  return ''

portal_workflow = context.getPortalObject().portal_workflow
history_list = context.portal_workflow.getInfoFor(ob=context, 
                                          name='history', wf_id=workflow_id)
wf_detail={}
for history_line in history_list:
  if history_line.has_key('validation_state') and history_line['validation_state']==validation_state:
    wf_detail=history_line

return wf_detail
