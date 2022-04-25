from six.moves import xrange
from Products.Formulator.Errors import FormValidationError
from Products.ERP5Type.Message import translateString
portal = context.getPortalObject()
request = context.REQUEST

target_context = portal.restrictedTraverse(choosen_action['relative_url'])
target_form = getattr(target_context, choosen_action['workflow_action'].split('/')[-1])

real_form = getattr(context, dialog_id)

# Validate the forms
for form in (real_form, target_form):
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
    return real_form(request)

  # XXX: this is a duplication from form validation code in Base_callDialogMethod
  # Correct fix is to factorise this script with Base_callDialogMethod, not to
  # fix XXXs here.
  do_action_for_param_dict = {}
  MARKER = []
  for f in form.get_fields():
    k = f.id
    v = getattr(request, k, MARKER)
    if v is not MARKER:
      if k.startswith('your_'):
        k=k[5:]
      elif k.startswith('my_'): # compat
        k=k[3:]
      do_action_for_param_dict[k] = v

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
    do_action_for_param_dict['listbox'] = listbox_line_list # XXX: hardcoded field name

assert 'workflow_action' in do_action_for_param_dict

# generate a random tag
tag = 'folder_workflow_action_%s' % random.randint(0, 1000)

# get the list of objects we are about to modify
selection_uid_list = portal.portal_selections.getSelectionCheckedUidsFor(selection_name)
selection_params = portal.portal_selections.getSelectionParamsFor(selection_name).copy()
selection_params[choosen_action['state_var']] = choosen_action['workflow_state']
selection_params['portal_type'] = choosen_action['portal_type']
selection_params['limit'] = None
if selection_uid_list:
  selection_params['uid'] = selection_uid_list

path_list = [brain.path for brain in
  portal.portal_selections.callSelectionFor(selection_name, params=selection_params)]

batch_size = 100 # XXX
# We want change state activities to have a lower priority that erp5_deferred_style reports
# not to prevent everybody from running report while a users change state of many documents.
priority = 3
path_list_len = len(path_list)

for i in xrange(0, path_list_len, batch_size):
  current_path_list = path_list[i:i+batch_size]
  context.activate(activity='SQLQueue', priority=priority, tag=tag).callMethodOnObjectList(
    current_path_list, 'Base_workflowStatusModify',  batch_mode=True, **do_action_for_param_dict)

# activate something on the module after everything, so that user can know that
# something is happening in the background
context.activate(after_tag=tag).getTitle()

# reset selection checked uids 
context.portal_selections.setSelectionCheckedUidsFor(selection_name, [])

return context.Base_redirect(form_id,
          keep_items=dict(portal_status_message=translateString("Workflow modification in progress.")))
