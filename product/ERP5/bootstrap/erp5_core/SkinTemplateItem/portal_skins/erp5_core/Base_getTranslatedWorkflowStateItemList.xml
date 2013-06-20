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
            <value> <string>"""Returns the state item list of a given workflow.\n
wf_id : the id of workflow. It can be string, list or tuple.\n
\n
This script is deprecated, it is much recommended to use\n
ERP5Site_getWorkflowStateItemList by passing the portal type instead.\n
"""\n
\n
Base_translateString = context.Base_translateString\n
\n
if same_type(wf_id, []) or same_type(wf_id, ()):\n
  workflow_id_list = wf_id\n
else:\n
  workflow_id_list = [wf_id]\n
\n
result = []\n
for state_title, state_id in context.Base_getWorkflowStateItemList(workflow_id_list=workflow_id_list):\n
  translated_state_title = Base_translateString(state_title)\n
  result.append((translated_state_title, state_id))\n
\n
return result\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>wf_id</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_getTranslatedWorkflowStateItemList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
