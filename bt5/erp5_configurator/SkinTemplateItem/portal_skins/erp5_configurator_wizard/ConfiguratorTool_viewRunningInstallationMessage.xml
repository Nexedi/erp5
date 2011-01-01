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

# different part of the configuration process in estimatd percentages\n
# values for machine with pystones =(1.3600000000000012, 36764.705882352908)\n
building_bt5_part_percentage = 15.0\n
installation_bt5_part_percentage = 26.0\n
activity_part_percentage = 59.0\n
calc_percentage = 0.0\n
is_activities_running = len(installation_status[\'activity_list\'])!=0\n
is_bt5_building_running = installation_status[\'bt5\'][\'all\']==0 and \\\n
                          not is_activities_running\n
is_bt5_installation_running = installation_status[\'bt5\'][\'all\']!=0 and \\\n
                              not is_activities_running \n
\n
if not is_bt5_building_running:\n
  all_bt5s = float(installation_status[\'bt5\'][\'all\'])\n
  current_bt5s = float(installation_status[\'bt5\'][\'current\'])\n
  bt5_percent_of_total = current_bt5s / all_bt5s\n
  calc_percentage = calc_percentage + building_bt5_part_percentage + \\\n
                    bt5_percent_of_total*installation_bt5_part_percentage\n
\n
if is_activities_running:\n
  activity_list = installation_status[\'activity_list\']\n
  all_activities = float(max(activity_list))\n
  current_activities = float(activity_list[-1])\n
  activity_percent_of_total = (all_activities - current_activities)/all_activities\n
  calc_percentage += activity_percent_of_total*activity_part_percentage\n
  #context.log(\'%s\\nLast:%s\\nAll:%s\\-->%s\' %(activity_list, current_activities, all_activities, activity_percent_of_total))\n
\n
return context.ConfiguratorTool_viewRunningInstallationMessageRenderer(percentage=int(calc_percentage))\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>installation_status</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ConfiguratorTool_viewRunningInstallationMessage</string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>Calculate percentages and show installation message</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
