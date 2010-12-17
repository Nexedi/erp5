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
            <value> <string>result = []\n
\n
for r in context.contentValues(portal_type= "Requirement", sort_on = ((\'int_index\',\'ascending\', \'int\'),)):\n
  if not r.getRequirementRelatedValueList():\n
    if not r.contentValues(portal_type= "Requirement", sort_on = ((\'int_index\',\'ascending\', \'int\'),)):\n
      result.append({\'requirement_reference\': r.Requirement_getDefaultReference(),\n
                     \'requirement_title\': r.getTitle(),\n
                     \'project_reference\': \'Not covered\',\n
                     \'project_title\': \'\',\n
                     \'stop_date\': None})\n
  else:\n
    for p in r.getRequirementRelatedValueList():\n
      result.append({\'requirement_reference\': r.Requirement_getDefaultReference(),\n
                     \'requirement_title\': r.getTitle(),\n
                     \'project_reference\': p.Project_getDefaultReference(),\n
                     \'project_title\': p.getTitle(),\n
                     \'stop_date\': p.getStopDate()})\n
  result.extend(r.RequirementDocument_getProjectCoverageList())\n
\n
return result\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>RequirementDocument_getOrderCoverageList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
