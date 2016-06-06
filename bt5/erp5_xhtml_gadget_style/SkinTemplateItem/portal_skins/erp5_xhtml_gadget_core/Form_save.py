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
            <value> <string>"""\n
  Save form on context.\n
"""\n
from json import dumps\n
from Products.Formulator.Errors import FormValidationError\n
from Products.CMFActivity.Errors import ActivityPendingError\n
\n
request = context.REQUEST\n
\n
# Prevent users who don\'t have rights to edit the object from\n
# editing it by calling the Base_edit script with correct\n
# parameters directly.\n
# XXX: implement it (above)\n
\n
# Get the form\n
form = getattr(context,form_id)\n
edit_order = form.edit_order\n
try:\n
  # Validate\n
  form.validate_all_to_request(request, key_prefix=key_prefix)\n
except FormValidationError, validation_errors:\n
  # Pack errors into the request\n
  result = {}\n
  result[\'field_errors\'] = {}\n
  field_errors = form.ErrorFields(validation_errors)\n
  for key, value in field_errors.items():\n
    result[\'field_errors\'][key] = value.error_text\n
  return dumps(result)\n
\n
(kw, encapsulated_editor_list), action = context.Base_edit(form_id, silent_mode=1)\n
\n
context.log(kw)\n
context.edit(REQUEST=request, edit_order=edit_order, **kw)\n
for encapsulated_editor in encapsulated_editor_list:\n
  encapsulated_editor.edit(context)\n
\n
# XXX: consider some kind of protocol ?\n
return dumps({})\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>form_id, key_prefix = None, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Form_save</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
