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

if active_process_path is not None:\n
\n
  failed_line_count = len(context.Base_getReportFailedResultList(\n
                                       active_process_path=active_process_path))\n
  if failed_line_count > 0: \n
    return \'Import Report: %s line(s) failed over %s\' % \\\n
              (len(context.Base_getReportFailedResultList(active_process_path=active_process_path)), \n
               len(context.Base_getReportResultList(active_process_path=active_process_path)))\n
  else: \n
    return \'%s lines imported sucessfully\' % \\\n
                      len(context.Base_getReportResultList(active_process_path=active_process_path))\n
\n
raise AttributeError, \'Unable to get the active process\'\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>active_process_path=None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_getReportResultListTitle</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
