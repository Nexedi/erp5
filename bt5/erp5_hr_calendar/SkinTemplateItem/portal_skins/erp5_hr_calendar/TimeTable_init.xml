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
            <value> <string># Create a first line to retrieve list of days\n
int_index = 0\n
line = context.newContent(int_index=int_index)\n
day_list = line.getWeekDayList()\n
line.edit(day_of_week=day_list[0])\n
tag = "%s_reindex" % context.getRelativeUrl()\n
\n
# Create other lines\n
for day in day_list[1:]:\n
  int_index+=1\n
  context.newContent(int_index=int_index, day_of_week=day,\n
                     activate_kw={"tag": tag})\n
# after indexing, make sure to update periodicity stop date\n
context.getPortalObject().portal_alarms.update_time_table_end_periodicity.activate(\n
  after_tag=tag, priority=5).activeSense()\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>*args, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>TimeTable_init</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
