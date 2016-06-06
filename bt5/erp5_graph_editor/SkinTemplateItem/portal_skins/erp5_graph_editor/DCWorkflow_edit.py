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
            <value> <string>from Products.ERP5Type.Message import translateString\n
from Products.Formulator.Errors import FormValidationError\n
request = container.REQUEST\n
\n
form = getattr(context, form_id)\n
edit_order = form.edit_order\n
try:\n
  # Validate\n
  form.validate_all_to_request(request, key_prefix=\'my_\')\n
except FormValidationError, validation_errors:\n
  # Pack errors into the request\n
  result = {}\n
  result[\'field_errors\'] = {}\n
  field_errors = form.ErrorFields(validation_errors)\n
  for key, value in field_errors.items():\n
    result[\'field_errors\'][key] = value.error_text\n
  return form()\n
\n
(kw, encapsulated_editor_list), action = context.Base_edit(form_id, silent_mode=1)\n
assert not encapsulated_editor_list\n
\n
context.setProperties(\n
  title=kw[\'title\'],\n
  description=kw[\'description\'],\n
  manager_bypass=context.manager_bypass)\n
marker = []\n
if context.getProperty("jsplumb_graph", marker) is marker:\n
  context.manage_setProperty("jsplumb_graph", kw["jsplumb_graph"])\n
else:\n
  context.manage_changeProperties({\'jsplumb_graph\': kw["jsplumb_graph"]})\n
\n
# XXX handle workflow edition here.\n
\n
return context.Base_redirect(form_id, \n
                             keep_items={\'portal_status_message\': translateString("Data updated.")})\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>form_id, *args, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>DCWorkflow_edit</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
