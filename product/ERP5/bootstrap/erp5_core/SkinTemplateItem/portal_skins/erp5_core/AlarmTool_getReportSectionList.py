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
  Returns a list of all alarms in \n
  the form of report sections.\n
\n
  TODO: cache this result in RAM \n
  on a per transaction level.\n
"""\n
REQUEST = context.REQUEST\n
if display_success is None: display_success = REQUEST.form.get(\'display_success\')\n
if display_raw_result is None: display_raw_result = REQUEST.form.get(\'display_raw_result\')\n
\n
from Products.ERP5Form.Report import ReportSection\n
result = []\n
\n
for alarm in context.contentValues():\n
  if alarm.isEnabled() and \\\n
    (display_success or alarm.sense()) and\\\n
    (display_raw_result or alarm.getReportMethodId()):\n
    if alarm.getReportMethodId():\n
      form_id = alarm.getReportMethodId()\n
    else:\n
      form_id = \'Alarm_viewReport\'\n
    result.append(\n
      ReportSection(\n
        title=alarm.getTitle(),\n
        path=alarm.getPhysicalPath(),\n
        level=1,\n
        form_id=form_id,\n
        listbox_display_mode=\'FlatListMode\')\n
      )\n
\n
return result\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>display_success=None, display_raw_result=None, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>AlarmTool_getReportSectionList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
