from Products.CMFCore.WorkflowCore import WorkflowException
from Products.Formulator.Errors import FormValidationError
from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import translateString
from Products.ERP5Type.Log import log
portal = context.getPortalObject()
request=context.REQUEST

form = getattr(context, dialog_id)

# Validate the form
# It is necessary to force editable_mode before validating
# data. Otherwise, field appears as non editable.
# This is the pending of form_dialog.
editable_mode = request.get('editable_mode', 1)
request.set('editable_mode', 1)
form.validate_all_to_request(request)
request.set('editable_mode', editable_mode)

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

redirect_document = context.newContent(portal_type=doaction_param_list['portal_type'])

return redirect_document.Base_redirect(keep_items={'portal_status_message': 'Document created.'})
