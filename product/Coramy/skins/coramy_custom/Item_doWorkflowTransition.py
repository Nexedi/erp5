## Script (Python) "Item_doWorkflowTransition"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=workflow_action='', workflow_id=''
##title=
##
# A shorter version of of workflow_status_modify and folder_workflow_status_modify ...

error_message = ''

action_list = context.portal_workflow.getActionsFor(context)
action_list = filter(lambda x:x.has_key('id'), action_list )
action_id_list = map(lambda x:x['id'], action_list)
  
# If the user is not allowed to do this transition, it will not be in action_list 
if workflow_action in action_id_list:
  context.portal_workflow.doActionFor(
        context,
        workflow_action,
        wf_id=workflow_id
  )

# We will check if there's an error_message
history_data = None
try:
  history_data = context.portal_workflow.getInfoFor(ob=context, name='history')
except:
  pass
  redirect_url = None
  if history_data is not None:
    last_history_data = history_data[len(history_data)-1]
    this_error = last_history_data.get('error_message')
    if this_error != None and this_error != '':
      error_message += this_error + "-"
    
return error_message
