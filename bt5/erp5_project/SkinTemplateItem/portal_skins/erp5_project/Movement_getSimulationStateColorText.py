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
            <value> <string># Define the color using the simulation state\n
if task.getPortalType() in task.getPortalCalendarPeriodTypeList():\n
  return \'#d3d3d3\'\n
\n
simulation_method = getattr(task, \'getSimulationState\', None)\n
if simulation_method is None:\n
  return \'#D1E8FF\'\n
\n
simulation_state = simulation_method()\n
\n
color_dict = {\n
  \'draft\': \'#a7d7ae\',\n
  \'planned\': \'#ffff00\',\n
  \'ordered\': \'#ff8e56\',\n
  \'confirmed\': \'#ff0000\',\n
  \'started\': \'#ff00ff\',\n
  \'stopped\': \'#00b8ff\',\n
  \'delivered\': \'#3deb3d\',\n
}\n
return color_dict.get(simulation_state, \'#D1E8FF\')\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>task=None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Movement_getSimulationStateColorText</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
