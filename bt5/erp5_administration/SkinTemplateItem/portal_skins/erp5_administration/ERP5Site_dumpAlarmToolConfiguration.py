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
            <value> <string>alarm_tool = context.getPortalObject().portal_alarms\n
periodicity_list = [\n
  \'periodicity_day_frequency\',\n
  \'periodicity_hour\',\n
  \'periodicity_hour_frequency\',\n
  \'periodicity_minute\',\n
  \'periodicity_minute_frequency\',\n
  \'periodicity_month\',\n
  \'periodicity_month_day\',\n
  \'periodicity_month_frequency\',\n
  \'periodicity_start_date\',\n
  \'periodicity_stop_date\',\n
  \'periodicity_week\',\n
  \'periodicity_week_day\',\n
  \'periodicity_week_frequency\',\n
]\n
result_list = [\'Alarm;Enabled;ReportMethodId;ActiveSenseMethodId;SenseMethodId;SolveMethodId;\' + \';\'.join(periodicity_list)]\n
for alarm in alarm_tool.contentValues():\n
  in_list = [\n
    alarm.getRelativeUrl(),\n
    str(alarm.getEnabled()),\n
    str(alarm.getReportMethodId()),\n
    str(alarm.getActiveSenseMethodId()),\n
    str(alarm.getSenseMethodId()),\n
    str(alarm.getSolveMethodId())\n
  ]\n
  for periodicity_id in periodicity_list:\n
    in_list.append(str(getattr(alarm, periodicity_id, None)))\n
  result_list.append(\';\'.join(in_list))\n
result_list.sort()\n
return \'\\n\'.join(result_list)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ERP5Site_dumpAlarmToolConfiguration</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
