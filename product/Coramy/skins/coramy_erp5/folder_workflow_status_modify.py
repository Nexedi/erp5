## Script (Python) "folder_workflow_status_modify"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=form_id,dialog_id,selection_name,md5_object_uid_list=None
##title=
##
from Products.Formulator.Errors import ValidationError, FormValidationError

request=context.REQUEST
error_message = ''

try:
  # Validate the form
  form = getattr(context,dialog_id)
  form.validate_all_to_request(request)
  kw = {}
  for f in form.get_fields():
    k = f.id
    k = k[3:]
    v = getattr(request,k,None)
    if v is not None:
      kw[k] = v
  selection_list = context.portal_selections.callSelectionFor(selection_name, context=context)
  # Check if the selection did not changed
  if md5_object_uid_list is not None:
    object_uid_list = map(lambda x:x.getObject().getUid(),selection_list)
    error = context.portal_selections.selectionHasChanged(md5_object_uid_list,object_uid_list)
    if error:
      error_message = 'Sorry+your+selection+has+changed'
  if error_message == '':
    for selection_item in selection_list:
      o = selection_item.getObject()
      workflow_action = kw['workflow_action']
      action_list = o.portal_workflow.getActionsFor(o)
      action_list = filter(lambda x:x.has_key('id'), action_list )
      action_id_list = map(lambda x:x['id'], action_list)
      # If the user is not allowed to do this transition, it will not be in action_list 
      if workflow_action in action_id_list:
        o.portal_workflow.doActionFor(
            o,
            workflow_action,
            wf_id=kw['workflow_id'],
            **kw)

     # We will check if there's an error_message
      history_data = None
      try:
        history_data = o.portal_workflow.getInfoFor(ob=o, name='history')
      except:
        pass
      redirect_url = None
      if history_data is not None:
        last_history_data = history_data[len(history_data)-1]
        this_error = last_history_data.get('error_message')
        if this_error != None and this_error != '':
          error_message += this_error + "-"
except FormValidationError, validation_errors:
  # Pack errors into the request
  field_errors = form.ErrorFields(validation_errors)
  request.set('field_errors', field_errors)
  return form(request)
except ValueError, value_error:
  # Pack errors into the request
  redirect_url = '%s/%s?%s%s' % ( context.absolute_url(), form_id
                                  , 'portal_status_message=',value_error
                                  )

  context.REQUEST[ 'RESPONSE' ].redirect( redirect_url )
else:
 
  if error_message != None and error_message != '':
    redirect_url = '%s/%s?%s' % ( context.absolute_url(), form_id
                                  , 'portal_status_message=%s' % error_message
                                  )
    pass
  if redirect_url is None:
    redirect_url = '%s/%s?%s' % ( context.absolute_url(), form_id
                                  , 'portal_status_message=Status+changed.'
                                  )

  context.REQUEST[ 'RESPONSE' ].redirect( redirect_url )
