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
            <value> <string>data = {}\n
\n
for d, sql in [(\'SQLDict\',context.ActivityTool_getCurrentActivities(table=\'message\')),\n
               (\'SQLQueue\',context.ActivityTool_getCurrentActivities(table=\'message_queue\'))]:\n
  data[d] = {\'line_list\':[]}\n
  for line in sql:\n
    tmp = {}\n
    for k in [\'message\',\'method_id\',\'processing\',\'node\',\'min_pri\',\'max_pri\']:\n
      tmp[k] = line[k]\n
    data[d][\'line_list\'].append(tmp)\n
\n
for d, sql in [(\'SQLDict2\',context.ActivityTool_getSQLActivities(table=\'message\')),\n
               (\'SQLQueue2\',context.ActivityTool_getSQLActivities(table=\'message_queue\'))]:\n
  data[d] = {\'line_list\':[]}\n
  for line in sql:\n
    tmp = {\'pri\':line[\'pri\']}\n
    for k in [\'min\',\'avg\',\'max\']:\n
      tmp[k] = str(line[k])\n
    data[d][\'line_list\'].append(tmp)\n
\n
import json\n
return json.dumps(data)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ActivityTool_getSqlStatisticList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
