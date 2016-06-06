<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="PythonScript" module="Products.PythonScripts.PythonScript"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>Script_magic</string> </key>
            <value> <int>3</int> </value>
        </item>
        <item>
            <key> <string>_bind_names</string> </key>
            <value>
              <object>
                <klass>
                  <global name="NameAssignments" module="Shared.DC.Scripts.Bindings"/>
                </klass>
                <tuple/>
                <state>
                  <dictionary>
                    <item>
                        <key> <string>_asgns</string> </key>
                        <value>
                          <dictionary>
                            <item>
                                <key> <string>name_container</string> </key>
                                <value> <string>container</string> </value>
                            </item>
                            <item>
                                <key> <string>name_context</string> </key>
                                <value> <string>context</string> </value>
                            </item>
                            <item>
                                <key> <string>name_m_self</string> </key>
                                <value> <string>script</string> </value>
                            </item>
                            <item>
                                <key> <string>name_subpath</string> </key>
                                <value> <string>traverse_subpath</string> </value>
                            </item>
                          </dictionary>
                        </value>
                    </item>
                  </dictionary>
                </state>
              </object>
            </value>
        </item>
        <item>
            <key> <string>_body</string> </key>
            <value> <string encoding="cdata"><![CDATA[

"""\n
Generic method called when submitting a form in dialog mode.\n
Responsible for validating form data and redirecting to the form action.\n
"""\n
from Products.ERP5Type.Log import log\n
\n
# XXX We should not use meta_type properly,\n
# XXX We need to discuss this problem.(yusei)\n
def isListBox(field):\n
  if field.meta_type==\'ListBox\':\n
    return True\n
  elif field.meta_type==\'ProxyField\':\n
    template_field = field.getRecursiveTemplateField()\n
    if template_field.meta_type==\'ListBox\':\n
      return True\n
  return False\n
\n
from Products.Formulator.Errors import FormValidationError\n
from ZTUtils import make_query\n
\n
request = container.REQUEST\n
request_form = request.form\n
error_message = \'\'\n
\n
# Make this script work alike wether called from another script or by a request\n
kw.update(request_form)\n
\n
# Exceptions for UI\n
if dialog_method == \'Base_configureUI\':\n
  return context.Base_configureUI(form_id=kw[\'form_id\'],\n
                                  selection_name=kw[\'selection_name\'],\n
                                  field_columns=kw[\'field_columns\'],\n
                                  stat_columns=kw[\'stat_columns\'])\n
# Exceptions for Sort\n
if dialog_method == \'Base_configureSortOn\':\n
  return context.Base_configureSortOn(form_id=kw[\'form_id\'],\n
                                      selection_name=kw[\'selection_name\'],\n
                                      field_sort_on=kw[\'field_sort_on\'],\n
                                      field_sort_order=kw[\'field_sort_order\'])\n
# Exceptions for Base_edit\n
# if dialog_method == \'Base_edit\':\n
#   return context.Base_edit(form_id=kw[\'form_id\'],\n
#                            dialog_id=dialog_id,\n
#                            selection_name=kw[\'selection_name\'])\n
# Exceptions for Workflow\n
if dialog_method == \'Workflow_statusModify\':\n
  value = context.Workflow_statusModify(form_id=kw[\'form_id\'],\n
                                        dialog_id=dialog_id)\n
  # XXX: This test is related to erp5_web and should not be present in configuration where it is not installed.\n
  #if not(getattr(context.REQUEST, \'ignore_layout\', 0)) and context.getApplicableLayout() :\n
  #  context.REQUEST.RESPONSE.redirect(context.WebSite_getDocumentPhysicalPath())\n
  return value\n
# Exception for edit relation\n
if dialog_method == \'Base_editRelation\':\n
  return context.Base_editRelation(form_id=kw[\'form_id\'],\n
                                   field_id=kw[\'field_id\'],\n
                                   selection_name=kw[\'list_selection_name\'],\n
                                   selection_index=kw[\'selection_index\'],\n
                                   uids=kw.get(\'uids\', ()),\n
                                   listbox_uid=kw.get(\'listbox_uid\', None),\n
                                   saved_form_data=kw[\'saved_form_data\'])\n
# Exception for create relation\n
if dialog_method == \'Base_createRelation\':\n
  return context.Base_createRelation(form_id=kw[\'form_id\'],\n
                                     selection_name=kw[\'list_selection_name\'],\n
                                     selection_index=kw[\'selection_index\'],\n
                                     base_category=kw[\'base_category\'],\n
                                     object_uid=kw[\'object_uid\'],\n
                                     catalog_index=kw[\'catalog_index\'],\n
                                     default_module=kw[\'default_module\'],\n
                                     dialog_id=dialog_id,\n
                                     portal_type=kw[\'portal_type\'],\n
                                     return_url=kw[\'cancel_url\'])\n
# Exception for folder delete\n
if dialog_method == \'Folder_delete\':\n
  return context.Folder_delete(form_id=kw[\'form_id\'],\n
                               selection_name=kw[\'selection_name\'],\n
                               md5_object_uid_list=kw[\'md5_object_uid_list\'])\n
\n
form = getattr(context, dialog_id)\n
\n
# form can be a python script that returns the form\n
if not hasattr(form, \'validate_all_to_request\'):\n
  form = form()\n
\n
# Validate the form\n
try:\n
  # It is necessary to force editable_mode before validating\n
  # data. Otherwise, field appears as non editable.\n
  # This is the pending of form_dialog.\n
  editable_mode = request.get(\'editable_mode\', 1)\n
  request.set(\'editable_mode\', 1)\n
  form.validate_all_to_request(request)\n
  request.set(\'editable_mode\', editable_mode)\n
except FormValidationError, validation_errors:\n
  # Pack errors into the request\n
  field_errors = form.ErrorFields(validation_errors)\n
  request.set(\'field_errors\', field_errors)\n
  return form(request)\n
\n
# Use REQUEST.redirect if possible. It will not be possible if at least one of these is true :\n
#  * we got an import_file,\n
#  * we got a listbox\n
#  * a value is None or [] or (), because this is not supported by make_query\n
can_redirect = 1\n
MARKER = [] # A recognisable default value. Use with \'is\', not \'==\'.\n
listbox_id_list = [] # There should not be more than one listbox - but this give us a way to check.\n
file_id_list = [] # For uploaded files.\n
for field in form.get_fields():\n
  k = field.id\n
  v = request.get(k, MARKER)\n
  if v is not MARKER:\n
    if isListBox(field):\n
      listbox_id_list.append(k)\n
    elif can_redirect and (v in (None, [], ()) or hasattr(v, \'read\')) : # If we cannot redirect, useless to test it again\n
      can_redirect = 0\n
\n
    # Cleanup my_ and your_ prefixes\n
    splitted = k.split(\'_\', 1)\n
    if len(splitted) == 2 and splitted[0] in (\'my\', \'your\'):\n
      if hasattr(v, \'as_dict\'):\n
        # This is an encapsulated editor\n
        # convert it\n
        kw.update(v.as_dict())\n
      else:\n
        kw[splitted[1]] = request_form[splitted[1]] = v\n
\n
    else:\n
      kw[k] = request_form[k] = v\n
\n
\n
if len(listbox_id_list):\n
  can_redirect = 0\n
  # Warn if there are more than one listbox in form ...\n
  if len(listbox_id_list) > 1:\n
    log(\'Base_callDialogMethod\', \'There are %s listboxes in form %s.\' % (len(listbox_id_list), form.id))\n
  # ... but handle them anyway.\n
  for listbox_id in listbox_id_list:\n
    listbox_line_list = []\n
    listbox = kw[listbox_id]\n
    listbox_keys = listbox.keys()\n
    listbox_keys.sort()\n
    for key in listbox_keys:\n
      listbox_line = listbox[key]\n
      listbox_line[\'listbox_key\'] = key\n
      listbox_line_list.append(listbox_line)\n
    listbox_line_list = tuple(listbox_line_list)\n
    kw[listbox_id] = request_form[listbox_id] = listbox_line_list\n
\n
\n
# Check if the selection changed\n
if hasattr(kw, \'previous_md5_object_uid_list\'):\n
  selection_list = context.portal_selections.callSelectionFor(kw[\'list_selection_name\'], context=context)\n
  if selection_list is not None:\n
    object_uid_list = map(lambda x:x.getObject().getUid(), selection_list)\n
    error = context.portal_selections.selectionHasChanged(kw[\'previous_md5_object_uid_list\'], object_uid_list)\n
    if error:\n
      error_message = context.Base_translateString("Sorry, your selection has changed.")\n
\n
# if dialog_category is object_search, then edit the selection\n
if dialog_category == "object_search" :\n
  context.portal_selections.setSelectionParamsFor(kw[\'selection_name\'], kw)\n
\n
# if we have checked line in listbox, modify the selection\n
listbox_uid = kw.get(\'listbox_uid\', None)\n
# In some cases, the listbox exists, is editable, but the selection name\n
# has no meaning, for example fast input dialogs.\n
# In such cases, we must not try to update a non-existing selection.\n
if listbox_uid is not None and kw.has_key(\'list_selection_name\'):\n
  uids = kw.get(\'uids\')\n
  selected_uids = context.portal_selections.updateSelectionCheckedUidList(\n
    kw[\'list_selection_name\'],\n
    listbox_uid, uids)\n
# Remove unused parameter\n
clean_kw = {}\n
for k, v in kw.items() :\n
  if v not in (None, [], ()) :\n
    clean_kw[k] = kw[k]\n
\n
# Handle deferred style, unless we are executing the update action\n
if dialog_method != update_method and clean_kw.get(\'deferred_style\', 0):\n
  clean_kw[\'deferred_portal_skin\'] = clean_kw.get(\'portal_skin\', None)\n
  # XXX Hardcoded Deferred style name\n
  clean_kw[\'portal_skin\'] = \'Deferred\'\n
  \n
  dialog_form = getattr(context, dialog_method)\n
  page_template = getattr(dialog_form, \'pt\', None)\n
  # If the action form has report_view as it\'s method, it \n
  if page_template != \'report_view\':\n
    # use simple wrapper\n
    clean_kw[\'deferred_style_dialog_method\'] = dialog_method\n
    kw[\'deferred_style_dialog_method\'] = dialog_method\n
    request.set(\'deferred_style_dialog_method\', dialog_method)\n
    dialog_method = \'Base_activateSimpleView\'\n
\n
\n
url_params_string = make_query(clean_kw)\n
\n
# XXX: We always redirect in report mode to make sure portal_skin\n
# parameter is taken into account by SkinTool.\n
# If url is too long, we do not redirect to avoid crash.\n
# XXX: 2000 is an arbitrary value resulted from trial and error.\n
if (not(can_redirect) or len(url_params_string) > 2000):\n
  if dialog_method != update_method:\n
    # When we are not executing the update action, we have to change the skin\n
    # manually,\n
    if \'portal_skin\' in clean_kw:\n
      new_skin_name = clean_kw[\'portal_skin\']\n
      context.getPortalObject().portal_skins.changeSkin(new_skin_name)\n
      request.set(\'portal_skin\', new_skin_name)\n
      deferred_portal_skin = clean_kw.get(\'deferred_portal_skin\')\n
      if deferred_portal_skin:\n
        request.set(\'deferred_portal_skin\', deferred_portal_skin)\n
    # and to cleanup formulator\'s special key in request\n
    # XXX unless we are in Folder_modifyWorkflowStatus which validates again !\n
    if dialog_method != \'Folder_modifyWorkflowStatus\':\n
      for key in list(request.keys()):\n
        if str(key).startswith(\'field\') or str(key).startswith(\'subfield\'):\n
          request.form.pop(key, None)\n
\n
  # If we cannot redirect, then call the form directly.\n
  dialog_form = getattr(context, dialog_method)\n
  # XXX: this is a hack that should not be needed anymore with the new listbox.\n
  # set the URL in request, so that we can immediatly call method\n
  # that depend on it (eg. Show All). This is really related to\n
  # current ListBox implementation which edit Selection\'s last_url\n
  # with the content of REQUEST.URL\n
  request.set(\'URL\', \'%s/%s\' % (context.absolute_url(), dialog_method))\n
  return dialog_form(**kw)\n
\n
dialog_method = getattr(context, dialog_method)\n
return dialog_method(**clean_kw)\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>dialog_method, dialog_id, dialog_category=\'\', update_method=None, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_callDialogMethod</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
