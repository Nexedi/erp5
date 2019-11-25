"""
Generic method called when submitting a form in dialog mode.
Responsible for validating form data and redirecting to the form action.
"""
from Products.ERP5Type.Log import log

# XXX We should not use meta_type properly,
# XXX We need to discuss this problem.(yusei)
def isFieldType(field, type_name):
  if field.meta_type == 'ProxyField':
    field = field.getRecursiveTemplateField()
  return field.meta_type == type_name
def isListBox(field):
  return isFieldType(field, 'ListBox')

from Products.Formulator.Errors import FormValidationError
from ZTUtils import make_query

request = container.REQUEST
request_form = request.form
error_message = ''

# Make this script work alike wether called from another script or by a request
kw.update(request_form)

# Exceptions for UI
if dialog_method == 'Base_configureUI':
  return context.Base_configureUI(form_id=kw['form_id'],
                                  selection_name=kw['selection_name'],
                                  field_columns=kw['field_columns'],
                                  stat_columns=kw['stat_columns'])
# Exceptions for Sort
if dialog_method == 'Base_configureSortOn':
  return context.Base_configureSortOn(form_id=kw['form_id'],
                                      selection_name=kw['selection_name'],
                                      field_sort_on=kw['field_sort_on'],
                                      field_sort_order=kw['field_sort_order'])
# Exceptions for Base_edit
# if dialog_method == 'Base_edit':
#   return context.Base_edit(form_id=kw['form_id'],
#                            dialog_id=dialog_id,
#                            selection_name=kw['selection_name'])
# Exceptions for Workflow
if dialog_method == 'Workflow_statusModify':
  value = context.Workflow_statusModify(form_id=kw['form_id'],
                                        dialog_id=dialog_id)
  # XXX: This test is related to erp5_web and should not be present in configuration where it is not installed.
  #if not(getattr(context.REQUEST, 'ignore_layout', 0)) and context.getApplicableLayout() :
  #  context.REQUEST.RESPONSE.redirect(context.WebSite_getDocumentPhysicalPath())
  return value
# Exception for edit relation
if dialog_method == 'Base_editRelation':
  return context.Base_editRelation(form_id=kw['form_id'],
                                   field_id=kw['field_id'],
                                   selection_name=kw['list_selection_name'],
                                   selection_index=kw['selection_index'],
                                   uids=kw.get('uids', ()),
                                   listbox_uid=kw.get('listbox_uid', None),
                                   saved_form_data=kw['saved_form_data'])
# Exception for create relation
if dialog_method == 'Base_createRelation':
  return context.Base_createRelation(form_id=kw['form_id'],
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

# form can be a python script that returns the form
if not hasattr(form, 'validate_all_to_request'):
  form = form()

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
  return form(request)

# Use REQUEST.redirect if possible. It will not be possible if at least one of these is true :
#  * we got an import_file,
#  * we got a listbox
#  * a value is None or [] or (), because this is not supported by make_query
can_redirect = 1
MARKER = [] # A recognisable default value. Use with 'is', not '=='.
listbox_id_list = [] # There should not be more than one listbox - but this give us a way to check.
for field in form.get_fields():
  k = field.id
  v = request.get(k, MARKER)
  if v is not MARKER:
    if isListBox(field):
      listbox_id_list.append(k)
    elif can_redirect and (v in (None, [], ()) or hasattr(v, 'read') or 'password' in k or isFieldType(field, 'PasswordField')) : # If we cannot redirect, useless to test it again
      can_redirect = 0

    # Cleanup my_ and your_ prefixes
    splitted = k.split('_', 1)
    if len(splitted) == 2 and splitted[0] in ('my', 'your'):

      if hasattr(v, 'as_dict'):
        # This is an encapsulated editor
        # convert it
        kw.update(v.as_dict())
      else:
        kw[splitted[1]] = request_form[splitted[1]] = v

    else:
      kw[k] = request_form[k] = v

if len(listbox_id_list):
  can_redirect = 0
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
    object_uid_list = [x.getObject().getUid() for x in selection_list]
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
  context.portal_selections.updateSelectionCheckedUidList(
    kw['list_selection_name'],
    listbox_uid, uids)
# Remove values which doesn't work with make_query.
clean_kw = {}
for k, v in kw.items() :
  if v not in (None, [], ()) :
    clean_kw[k] = kw[k]

# Handle deferred style, unless we are executing the update action
if dialog_method != update_method and clean_kw.get('deferred_style', 0):
  clean_kw['previous_skin_selection'] = context.getPortalObject().portal_skins.getCurrentSkinName()
  clean_kw['deferred_portal_skin'] = clean_kw.get('portal_skin', None)
  # XXX Hardcoded Deferred style name
  clean_kw['portal_skin'] = 'Deferred'
  
  dialog_form = getattr(context, dialog_method)
  page_template = getattr(dialog_form, 'pt', None)
  # If the action form has report_view as it's method, it 
  if page_template != 'report_view':
    # use simple wrapper
    clean_kw['deferred_style_dialog_method'] = dialog_method
    kw['deferred_style_dialog_method'] = dialog_method
    request.set('deferred_style_dialog_method', dialog_method)
    dialog_method = 'Base_activateSimpleView'

url_params_string = make_query(clean_kw)

# XXX: We always redirect in report mode to make sure portal_skin
# parameter is taken into account by SkinTool.
# If url is too long, we do not redirect to avoid crash.
# XXX: 2000 is an arbitrary value resulted from trial and error.
if (not(can_redirect) or len(url_params_string) > 2000):
  if dialog_method != update_method:
    # When we are not executing the update action, we have to change the skin
    # manually,
    if 'portal_skin' in clean_kw:
      new_skin_name = clean_kw['portal_skin']
      context.getPortalObject().portal_skins.changeSkin(new_skin_name)
      request.set('portal_skin', new_skin_name)
      deferred_portal_skin = clean_kw.get('deferred_portal_skin')
      if deferred_portal_skin:
        request.set('deferred_portal_skin', deferred_portal_skin)
    # and to cleanup formulator's special key in request
    # XXX unless we are in Folder_modifyWorkflowStatus which validates again !
    if dialog_method != 'Folder_modifyWorkflowStatus':
      for key in list(request.keys()):
        if str(key).startswith('field') or str(key).startswith('subfield'):
          request.form.pop(key, None)

  # If we cannot redirect, then call the form directly.
  dialog_form = getattr(context, dialog_method)
  # XXX: this is a hack that should not be needed anymore with the new listbox.
  # set the URL in request, so that we can immediatly call method
  # that depend on it (eg. Show All). This is really related to
  # current ListBox implementation which edit Selection's last_url
  # with the content of REQUEST.URL
  request.set('URL', '%s/%s' % (context.absolute_url(), dialog_method))
  return dialog_form(**kw)

if error_message != '':
  redirect_url = '%s/%s?%s' % ( context.absolute_url()
                              , dialog_method
                              , 'portal_status_message=%s' % error_message
                              )
elif url_params_string != '':
  redirect_url = '%s/%s?%s' % ( context.absolute_url()
                              , dialog_method
                              , url_params_string
                              )

else:
  redirect_url = '%s/%s' % ( context.absolute_url()
                            , dialog_method
                            )

return request.RESPONSE.redirect(redirect_url)

# vim: syntax=python
