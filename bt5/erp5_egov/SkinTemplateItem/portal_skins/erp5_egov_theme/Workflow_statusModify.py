from Products.Formulator.Errors import FormValidationError
from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import translateString
portal = context.getPortalObject()
request=context.REQUEST

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
except FormValidationError as validation_errors:
  # Pack errors into the request
  field_errors = form.ErrorFields(validation_errors)
  request.set('field_errors', field_errors)
  return form(request)

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
  listbox = getattr(request,'listbox',None) # XXX: hardcoded field name
  listbox_keys = listbox.keys()
  listbox_keys.sort()
  for key in listbox_keys:
    listbox_line = listbox[key]
    listbox_line['listbox_key'] = key
    listbox_line_list.append(listbox[key])
  listbox_line_list = tuple(listbox_line_list)
  doaction_param_list['listbox'] = listbox_line_list # XXX: hardcoded field name

try:
  context.portal_workflow.doActionFor(
    context,
    doaction_param_list['workflow_action'],
    **doaction_param_list)
except ValidationFailed as error_message:
  if getattr(error_message, 'msg', None):
    # use of Message class to store message+mapping+domain
    message = error_message.msg
    if same_type(message, []):
      message = '. '.join('%s' % x for x in message)
    else:
      message = str(message)
  else:
    message = str(error_message)
  return context.ERP5Site_redirect(
                  '%s/view' % context.absolute_url(),
                  keep_items={'portal_status_message': message}, **kw)

portal_status_message = request.get('portal_status_message', translateString('Status changed.'))

# Allow to redirect to another document
redirect_document_path = request.get('redirect_document_path', context.getRelativeUrl())
redirect_document = context.restrictedTraverse(redirect_document_path)

return context.ERP5Site_redirect(
                '%s/view' % (redirect_document.absolute_url()),
                keep_items={'portal_status_message': portal_status_message})
