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
            <value> <string>from Products.CMFCore.WorkflowCore import WorkflowException\n
from Products.Formulator.Errors import FormValidationError\n
from Products.DCWorkflow.DCWorkflow import ValidationFailed\n
from Products.ERP5Type.Message import translateString\n
from Products.ERP5Type.Log import log\n
portal = context.getPortalObject()\n
request=context.REQUEST\n
\n
form = getattr(context, dialog_id)\n
\n
# Validate the form\n
# It is necessary to force editable_mode before validating\n
# data. Otherwise, field appears as non editable.\n
# This is the pending of form_dialog.\n
editable_mode = request.get(\'editable_mode\', 1)\n
request.set(\'editable_mode\', 1)\n
form.validate_all_to_request(request)\n
request.set(\'editable_mode\', editable_mode)\n
\n
# XXX: this is a duplication from form validation code in Base_callDialogMethod\n
# Correct fix is to factorise this script with Base_callDialogMethod, not to\n
# fix XXXs here.\n
doaction_param_list = {}\n
MARKER = []\n
for f in form.get_fields():\n
  k = f.id\n
  v = getattr(request, k, MARKER)\n
  if v is not MARKER:\n
    if k.startswith(\'your_\'):\n
      k=k[5:]\n
    elif k.startswith(\'my_\'): # compat\n
      k=k[3:]\n
    doaction_param_list[k] = v\n
\n
redirect_document = context.newContent(portal_type=doaction_param_list[\'portal_type\'])\n
\n
return redirect_document.Base_redirect()\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>form_id, dialog_id, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_newContentFromJS</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
