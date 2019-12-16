from Products.CMFCore.WorkflowCore import WorkflowException
from Products.Formulator.Errors import FormValidationError
from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import translateString
from Products.ERP5Type.Log import WARNING

portal = context.getPortalObject()
request = REQUEST or context.REQUEST

form = getattr(context, dialog_id)

# Validate the form
try:
  # It is necessary to force editable_mode before validating
  # data. Otherwise, field appears as non editable.
  # This is the pending of form_dialog.
  editable_mode = request.get('editable_mode', 1)
  request.set('editable_mode', 1)
  form.validate_all_to_request(request)
  request.set('editable_mode', editable_mode)
except FormValidationError, validation_errors:
  # Pack errors into the request
  field_errors = form.ErrorFields(validation_errors)
  request.set('field_errors', field_errors)
  request.RESPONSE.setStatus(400)
  return context.Base_renderForm(dialog_id)

# XXX: this is a duplication from form validation code in Base_callDialogMethod
# Correct fix is to factorise this script with Base_callDialogMethod, not to
# fix XXXs here.
doaction_param_list = {}
MARKER = []
for f in form.get_fields():
  k = f.id
  v = getattr(request, k, MARKER)
  if v is not MARKER:
    if k.startswith('your_'):
      k=k[5:]
    elif k.startswith('my_'): # compat
      k=k[3:]
    doaction_param_list[k] = v

listbox = request.get('listbox') # XXX: hardcoded field name
if listbox is not None:
  listbox_line_list = []
  for key, value in sorted(listbox.iteritems()):
    value['listbox_key'] = key
    listbox_line_list.append(value)
  doaction_param_list['listbox'] = tuple(listbox_line_list)

execution_date = doaction_param_list.pop('execution_date', None)
if execution_date is not None:
  context.activate(
    activity='SQLQueue',
    at_date=execution_date,
  ).Base_workflowStatusModify(
    workflow_action=doaction_param_list.pop('next_workflow_action'),
    comment=doaction_param_list.get('comment', ''),
    batch=True,
  )
  doaction_param_list['comment'] = translateString(
    'Scheduled for execution at $time',
    mapping={
      'time': str(execution_date),
    },
  )
try:
  portal.portal_workflow.doActionFor(
    context,
    doaction_param_list['workflow_action'],
    **doaction_param_list)
except ValidationFailed, error_message:
  if getattr(error_message, 'msg', None):
    # use of Message class to store message+mapping+domain
    message = error_message.msg
    if same_type(message, []):
      message = '. '.join('%s' % x for x in message)
    else:
      message = str(message)
  else:
    message = str(error_message)
  return context.Base_renderMessage(message, WARNING, request)
except WorkflowException as error_message:
  if str(error_message) == "No workflow provides the '${action_id}' action.":
    message = translateString("Workflow state may have been updated by other user. Please try again.")
    return context.Base_renderMessage(message, WARNING, request)
  else:
    raise
else:
  message = request.get('portal_status_message')
  if message is None:
    message = translateString('Status changed.')

# Allow to redirect to another document
redirect_document_path = request.get('redirect_document_path', None)
if redirect_document_path:
  redirect_document = portal.restrictedTraverse(redirect_document_path)
  form_id = 'view'
else:
  redirect_document = context

return redirect_document.Base_redirect(form_id,
                keep_items={'portal_status_message': message})
