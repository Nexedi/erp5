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
            <value> <string>from Products.Formulator.Errors import FormValidationError\n
from Products.ERP5Type.Message import translateString\n
portal = context.getPortalObject()\n
request = context.REQUEST\n
\n
target_context = portal.restrictedTraverse(choosen_action[\'relative_url\'])\n
target_form = getattr(target_context, choosen_action[\'workflow_action\'].split(\'/\')[-1])\n
\n
real_form = getattr(context, dialog_id)\n
\n
# Validate the forms\n
for form in (real_form, target_form):\n
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
    return real_form(request)\n
\n
  # XXX: this is a duplication from form validation code in Base_callDialogMethod\n
  # Correct fix is to factorise this script with Base_callDialogMethod, not to\n
  # fix XXXs here.\n
  do_action_for_param_dict = {}\n
  MARKER = []\n
  for f in form.get_fields():\n
    k = f.id\n
    v = getattr(request, k, MARKER)\n
    if v is not MARKER:\n
      if k.startswith(\'your_\'):\n
        k=k[5:]\n
      elif k.startswith(\'my_\'): # compat\n
        k=k[3:]\n
      do_action_for_param_dict[k] = v\n
\n
  listbox = request.get(\'listbox\') # XXX: hardcoded field name\n
  if listbox is not None:\n
    listbox_line_list = []\n
    listbox = getattr(request,\'listbox\',None) # XXX: hardcoded field name\n
    listbox_keys = listbox.keys()\n
    listbox_keys.sort()\n
    for key in listbox_keys:\n
      listbox_line = listbox[key]\n
      listbox_line[\'listbox_key\'] = key\n
      listbox_line_list.append(listbox[key])\n
    listbox_line_list = tuple(listbox_line_list)\n
    do_action_for_param_dict[\'listbox\'] = listbox_line_list # XXX: hardcoded field name\n
\n
assert \'workflow_action\' in do_action_for_param_dict\n
\n
# generate a random tag\n
tag = \'folder_workflow_action_%s\' % random.randint(0, 1000)\n
\n
# get the list of objects we are about to modify\n
selection_uid_list = portal.portal_selections.getSelectionCheckedUidsFor(selection_name)\n
selection_params = portal.portal_selections.getSelectionParamsFor(selection_name).copy()\n
selection_params[choosen_action[\'state_var\']] = choosen_action[\'workflow_state\']\n
selection_params[\'portal_type\'] = choosen_action[\'portal_type\']\n
selection_params[\'limit\'] = None\n
if selection_uid_list:\n
  selection_params[\'uid\'] = selection_uid_list\n
\n
path_list = [brain.path for brain in\n
  portal.portal_selections.callSelectionFor(selection_name, params=selection_params)]\n
\n
batch_size = 100 # XXX\n
priority = 2 # XXX\n
path_list_len = len(path_list)\n
\n
for i in xrange(0, path_list_len, batch_size):\n
  current_path_list = path_list[i:i+batch_size]\n
  context.activate(activity=\'SQLQueue\', priority=priority, tag=tag).callMethodOnObjectList(\n
    current_path_list, \'Base_workflowStatusModify\',  batch_mode=True, **do_action_for_param_dict)\n
\n
# activate something on the module after everything, so that user can know that\n
# something is happening in the background\n
context.activate(after_tag=tag).getTitle()\n
\n
# reset selection checked uids \n
context.portal_selections.setSelectionCheckedUidsFor(selection_name, [])\n
\n
return context.Base_redirect(form_id,\n
          keep_items=dict(portal_status_message=translateString("Workflow modification in progress.")))\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>form_id, dialog_id, selection_name, choosen_action, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Folder_modifyWorkflowStatus</string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
