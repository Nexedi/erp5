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
  Give an ICal status and percent-completed for a todo entry and status for a event entry.\n
  Return a tuple of (status, percent_complete).\n
  For todo status is one of: \'needs-action\', \'in-process\', \'completed\' and \'cancelled\' or nothing,\n
  then we\'ll assume it is \'needs-action\'.\n
  For event status is one of: \'cancelled\', \'confirmed\', \'tentative\' or nothing, \n
  then we\'ll assume it is \'tentative\'.\n
"""\n
status = \'\'\n
status_map_task = {\n
  \'draft\' : (\'needs-action\', 0),\n
  \'planned\' : (\'needs-action\', 33),\n
  \'ordered\' : (\'in-process\', 66),\n
  \'confirmed\' : (\'completed\', 100),\n
  \'cancelled\' : (\'cancelled\', 0)\n
}\n
\n
status_map_event = {\n
  \'CANCELLED\' : (\'expired\', \'deleted\', \'cancelled\'),\n
  \'CONFIRMED\' : (\'started\', \'responded\', \'delivered\', \'assigned\', \'acknowledged\'),\n
  \'TENTATIVE\' : (\'draft\', \'planned\', \'new\', \'ordered\')\n
}\n
\n
if brainObject is not None:\n
  real_context = brainObject\n
else:\n
  real_context = context\n
\n
portal_type = real_context.getPortalType()\n
if portal_type == \'Task\':\n
  return status_map_task.get(real_context.getSimulationState(), (\'\', 0))\n
elif portal_type in context.getPortalEventTypeList():\n
  for status_item in status_map_event:\n
    if real_context.getSimulationState() in status_map_event[status_item]:\n
      status = status_item\n
      break\n
return (status, 0)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>brainObject=None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_getICalStatusItem</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
