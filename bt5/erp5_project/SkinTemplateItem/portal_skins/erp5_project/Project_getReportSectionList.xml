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
            <value> <string>from Products.ERP5Form.Report import ReportSection\n
\n
result = []\n
\n
params = {}\n
\n
portal = context.portal_url.getPortalObject()\n
\n
for project_line in [x.getObject() for x in context.searchFolder(sort_id=\'int_index\')]:\n
\n
  result.append(\n
                 ReportSection(path=project_line.getPhysicalPath(),    \n
                               form_id=\'ProjectLine_viewReport\',\n
                               selection_name=\'project_line_selection\',\n
                               selection_params=params,\n
                               #listbox_display_mode=\'ReportTreeMode\',\n
                               \n
                               )             \n
               )\n
\n
\n
return result\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>*args,**kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Project_getReportSectionList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
