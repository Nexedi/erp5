"""
Generic method called when submitting a form in dialog mode.
Responsible for validating form data and redirecting to the form action.

Please note that the new UI has deprecated use of Selections. Your scripts
will no longer receive `selection_name` nor `selection` in their arguments.

There are runtime values hidden in every form (injected by getHateoas Script):
  form_id - previous form ID (backward compatibility reasons)
  dialog_id - current form dialog ID
  dialog_method - method to be called - can be either update_method or dialog_method of the Dialog Form
"""

from Products.ERP5Type.Log import log, DEBUG, INFO, WARNING, ERROR
from Products.Formulator.Errors import FormValidationError, ValidationError
from ZTUtils import make_query
import json

def isFieldType(field, type_name):
  if field.meta_type == 'ProxyField':
    field = field.getRecursiveTemplateField()
  return field.meta_type == type_name

# Kato: I do not understand why we throw away REQUEST from parameters (hidden in **kw)
# and use container.REQUEST just to introduce yet another global state. Maybe because
# container.REQUEST is used in other places.
# Well, REQUEST from arguments is a different instance than container.REQUEST so it will create problems...
request = kw.get('REQUEST', None) or container.REQUEST

# request.form holds POST data thus containing 'field_' + field.id items
# such as 'field_your_some_field'
request_form = request.form
error_message = ''
translate = context.Base_translateString
portal = context.getPortalObject()

# Make this script work alike no matter if called by a script or a request
kw.update(request_form)

# Exceptions for UI
if dialog_method == 'Base_configureUI':
  return context.Base_configureUI(form_id=form_id,
                                  selection_name=kw['selection_name'],
                                  field_columns=kw['field_columns'],
                                  stat_columns=kw['stat_columns'])
# Exceptions for Sort
if dialog_method == 'Base_configureSortOn':
  return context.Base_configureSortOn(form_id=form_id,
                                      selection_name=kw['selection_name'],
                                      field_sort_on=kw['field_sort_on'],
                                      field_sort_order=kw['field_sort_order'])
# Exceptions for Workflow
if dialog_method == 'Workflow_statusModify':
  return context.Workflow_statusModify(form_id=form_id,
                                        dialog_id=dialog_id)

# Exception for edit relation
if dialog_method == 'Base_editRelation':
  return context.Base_editRelation(form_id=form_id,
                                   field_id=kw['field_id'],
                                   selection_name=kw['list_selection_name'],
                                   selection_index=kw['selection_index'],
                                   uids=kw.get('uids', ()),
                                   listbox_uid=kw.get('listbox_uid', None),
                                   saved_form_data=kw['saved_form_data'])
# Exception for create relation
# Not used in new UI - relation field implemented using JIO calls from JS
if dialog_method == 'Base_createRelation':
  return context.Base_createRelation(form_id=form_id,
                                     selection_name=kw['list_selection_name'],
                                     selection_index=kw['selection_index'],
                                     base_category=kw['base_category'],
                                     object_uid=kw['object_uid'],
                                     catalog_index=kw['catalog_index'],
                                     default_module=kw['default_module'],
                                     dialog_id=dialog_id,
                                     portal_type=kw['portal_type'],
                                     return_url=kw['cancel_url'])
# Exception for folder delete
if dialog_method == 'Folder_delete':
  return context.Folder_delete(form_id=kw['form_id'],
                               selection_name=kw['selection_name'],
                               md5_object_uid_list=kw['md5_object_uid_list'])

form = getattr(context, dialog_id)
extra_param = json.loads(extra_param_json or "{}")

# form can be a python script that returns the form
if not hasattr(form, 'validate_all_to_request'):
  form = form()

# Validate the form
try:
  # It is necessary to force editable_mode before validating
  # data. Otherwise, field appears as non editable.
  editable_mode = request.get('editable_mode', 1)
  request.set('editable_mode', 1)
  form.validate_all_to_request(request)
  request.set('editable_mode', editable_mode)

  default_skin = context.getPortalObject().portal_skins.getDefaultSkin()
  allowed_styles = ("ODT", "ODS", "Hal", "HalRestricted")
  if getattr(getattr(context, dialog_method), 'pt', None) == "report_view" and \
     request.get('your_portal_skin', default_skin) not in allowed_styles:
    # RJS own validation - only ODS/ODT and Hal* skins work for reports
    # Form is OK, it's just this field - style so we return back form-wide error
    # for which we don't have support out-of-the-box thus we manually craft it
    # XXX TODO: Form-wide validation errors
    return context.Base_renderMessage(
      translate('Only ODT, ODS, Hal and HalRestricted skins are allowed for reports '\
                'in Preferences - User Interface - Report Style'),
      level=WARNING)

except FormValidationError as validation_errors:
  # Pack errors into the request
  field_errors = form.ErrorFields(validation_errors)
  request.set('field_errors', field_errors)
  # Make sure editors are pushed back as values into the REQUEST object
  for f in form.get_fields():
    field_id = f.id
    if request.has_key(field_id):
      value = request.get(field_id)
      if callable(value):
        value(request)
  if kw.get('silent_mode', False): return context.ERP5Document_getHateoas(form=form, REQUEST=request, mode='form'), 'form'
  request.RESPONSE.setStatus(400)
  return context.ERP5Document_getHateoas(form=form, REQUEST=request, mode='form')


MARKER = [] # A recognisable default value. Use with 'is', not '=='.
listbox_id_list = [] # There should not be more than one listbox - but this give us a way to check.
file_id_list = [] # For uploaded files.
for field in form.get_fields():
  field_id = field.id
  field_value = request.get(field_id, MARKER)

  if field_value is not MARKER:
    if isFieldType(field, "ListBox"):
      listbox_id_list.append(field_id)

    # Cleanup my_ and your_ prefixes if present
    if field_id.startswith("my_") or field_id.startswith("your_"):
      _, field_name = field_id.split('_', 1)
      if hasattr(field_value, 'as_dict'):
        # This is an encapsulated editor - convert it
        kw.update(field_value.as_dict())
      else:
        kw[field_name] = request_form[field_name] = field_value

    else:
      kw[field_id] = request_form[field_id] = field_value


if len(listbox_id_list):
  # Warn if there are more than one listbox in form ...
  if len(listbox_id_list) > 1:
    log('Base_callDialogMethod', 'There are %s listboxes in form %s.' % (len(listbox_id_list), form.id))
  # ... but handle them anyway.
  for listbox_id in listbox_id_list:
    listbox_line_list = []
    listbox = kw[listbox_id]
    listbox_keys = listbox.keys()
    listbox_keys.sort()
    for key in listbox_keys:
      listbox_line = listbox[key]
      listbox_line['listbox_key'] = key
      listbox_line_list.append(listbox_line)
    listbox_line_list = tuple(listbox_line_list)
    kw[listbox_id] = request_form[listbox_id] = listbox_line_list


# Check if the selection changed
if hasattr(kw, 'previous_md5_object_uid_list'):
  selection_list = context.portal_selections.callSelectionFor(kw['list_selection_name'], context=context)
  if selection_list is not None:
    object_uid_list = map(lambda x:x.getObject().getUid(), selection_list)
    error = context.portal_selections.selectionHasChanged(kw['previous_md5_object_uid_list'], object_uid_list)
    if error:
      error_message = context.Base_translateString("Sorry, your selection has changed.")

# if dialog_category is object_search, then edit the selection
if dialog_category == "object_search" :
  context.portal_selections.setSelectionParamsFor(kw['selection_name'], kw)

# if we have checked line in listbox, modify the selection
listbox_uid = kw.get('listbox_uid', None)
# In some cases, the listbox exists, is editable, but the selection name
# has no meaning, for example fast input dialogs.
# In such cases, we must not try to update a non-existing selection.
if listbox_uid is not None and kw.has_key('list_selection_name'):
  uids = kw.get('uids')
  selected_uids = context.portal_selections.updateSelectionCheckedUidList(
    kw['list_selection_name'],
    listbox_uid, uids)
# Remove empty values for make_query.
clean_kw = dict((k, v) for k, v in kw.items() if v not in (None, [], ()))

# Add rest of extra param into arguments of the target method
kw.update(extra_param)

# Finally we will call the Dialog Method
# Handle deferred style, unless we are executing the update action
if dialog_method != update_method and clean_kw.get('deferred_style', 0):
  clean_kw['deferred_portal_skin'] = clean_kw.get('portal_skin', None)
  # XXX Hardcoded Deferred style name
  clean_kw['portal_skin'] = 'Deferred'

  page_template = getattr(getattr(context, dialog_method), 'pt', None)

  if page_template == 'report_view':
    # Limit Reports in Deferred style to known working styles
    if request_form.get('your_portal_skin', None) not in ("ODT", "ODS"):
      # RJS own validation - deferred option works here only with ODS/ODT skins
      return context.Base_renderMessage(
        translate('Deferred reports are possible only with preference '\
                  '"Report Style" set to "ODT" or "ODS"'),
        level=WARNING)

  # If the action form has report_view as it's method, it
  if page_template != 'report_view':
    # use simple wrapper
    clean_kw['deferred_style_dialog_method'] = dialog_method
    kw['deferred_style_dialog_method'] = dialog_method
    request.set('deferred_style_dialog_method', dialog_method)
    dialog_method = 'Base_activateSimpleView'

url_params_string = make_query(clean_kw)

# Never redirect in JSON style - do as much as possible here.
# At this point the 'dialog_method' should point to a form (if we are in report)
# if we are not in Deferred mode - then it points to `Base_activateSimpleView`

if True:
  if dialog_method != update_method:
    # When we are not executing the update action, we have to change the skin
    # manually,
    if 'portal_skin' in clean_kw:
      new_skin_name = clean_kw['portal_skin']
      context.getPortalObject().portal_skins.changeSkin(new_skin_name)
      request.set('portal_skin', new_skin_name)
      deferred_portal_skin = clean_kw.get('deferred_portal_skin')
      if deferred_portal_skin:
        # has to be either ODS or ODT because only those contain `form_list`
        request.set('deferred_portal_skin', deferred_portal_skin)
    # and to cleanup formulator's special key in request
    # XXX unless we are in Folder_modifyWorkflowStatus which validates again !
    if dialog_method != 'Folder_modifyWorkflowStatus':
      for key in list(request.keys()):
        if str(key).startswith('field') or str(key).startswith('subfield'):
          request.form.pop(key, None)

  # now get dialog_method after skin re-selection and dialog_method mingling
  dialog_form = getattr(context, dialog_method)
  # XXX: this is a hack that should not be needed anymore with the new listbox.
  # set the URL in request, so that we can immediatly call method
  # that depend on it (eg. Show All). This is really related to
  # current ListBox implementation which edit Selection's last_url
  # with the content of REQUEST.URL
  request.set('URL', '%s/%s' % (context.absolute_url(), dialog_method))

  # RJS: If we are in deferred mode - call the form directly and return
  # dialog method is now `Base_activateSimpleView` - the only script in
  # deferred portal_skins folder
  if clean_kw.get('deferred_style', 0):
    return dialog_form(**kw)  # deferred form should return redirect with a message

  # RJS: If skin selection is different than Hal* then ERP5Document_getHateoas
  # does not exist and we call form method directly
  # If update_method was clicked and the target is the original dialog form then we must not call dialog_form directly because it returns HTML
  if clean_kw.get("portal_skin", context.getPortalObject().portal_skins.getDefaultSkin()) not in ("Hal", "HalRestricted", "View"):
    return dialog_form(**kw)

  # dialog_form can be anything from a pure python function, class method to ERP5 Form or Python Script
  try:
    meta_type = dialog_form.meta_type
  except AttributeError:
    meta_type = ""

  if meta_type in ("ERP5 Form", "ERP5 Report"):
    return context.ERP5Document_getHateoas(REQUEST=request, form=dialog_form, mode="form")

  return dialog_form(**kw)

return getattr(context, dialog_method)(**kw)
