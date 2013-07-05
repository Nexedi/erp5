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
            <value> <string>error_counter = 0\n
for benchmark_result_line in context.contentValues(portal_type=\'Benchmark Result Line\'):\n
  error_counter += benchmark_result_line.getProperty(\'error_counter\')\n
\n
context.edit(error_counter=error_counter,\n
             error_message_list=error_message_list,\n
             string_index=\'FAIL\')\n
\n
context.stop()\n
context.setProperty(\'string_index\', result)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>result, error_message_list=[]</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>BenchmarkResult_completed</string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>Called at benchmark result completion</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
