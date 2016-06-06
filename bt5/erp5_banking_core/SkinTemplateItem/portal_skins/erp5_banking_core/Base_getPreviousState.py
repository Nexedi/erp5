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
            <value> <string># Get the id of the user which last passed given transition on given workflow.\n
workflow_item_list = context.Base_getWorkflowHistoryItemList(workflow_id, display=0)\n
workflow_item_list.reverse()\n
previous_state = None\n
found_given_state = 0\n
for workflow_item in workflow_item_list:\n
  current_state = workflow_item.getProperty(\'state\')\n
  if current_state == state:\n
    found_given_state = 1\n
    continue\n
  if found_given_state and (current_state != state):\n
    previous_state = current_state\n
    break\n
return previous_state\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>workflow_id, state</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_getPreviousState</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
