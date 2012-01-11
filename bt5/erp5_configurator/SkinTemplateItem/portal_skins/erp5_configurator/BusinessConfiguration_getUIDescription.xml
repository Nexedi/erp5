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
  Get all states and descriptions to present at the\n
  the form.\n
"""\n
\n
result = []\n
previous_state_list = []\n
workflow = business_configuration.getResourceValue()\n
state = workflow.getSourceValue()\n
\n
while state not in previous_state_list:\n
  transition = state.getDestinationValue()\n
  previous_state_list.append(state)\n
  if transition is None:\n
    break\n
\n
  state = transition.getDestinationValue()\n
  if state is None:\n
    break\n
\n
  if transition.getTransitionFormId() not in (None, ""):\n
     result.append({\'state\' : state.getTitle(), \n
                    \'description\' : state.getDescription(),\n
                    \'title\': state.getTitle()})\n
\n
return result\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>business_configuration</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>BusinessConfiguration_getUIDescription</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
