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
            <value> <string>for result_line, stdout in zip(result_line_list, stdout_list):\n
  context.newContent(portal_type=\'Benchmark Result Line\',\n
                     title=\'%s repeat with %s concurrent users\' % (repeat, concurrent_user),\n
                     concurrent_user=concurrent_user,\n
                     username=username,\n
                     repeat=repeat,\n
                     benchmark_suite_list=benchmark_suite_list,\n
                     result_header_list=result_header_list,\n
                     result_list=result_line,\n
                     error_counter=len([result for result in result_line if result == 0]),\n
                     stdout=stdout)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>username, repeat, concurrent_user, benchmark_suite_list, result_header_list, result_line_list, stdout_list</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>BenchmarkResult_addResultLineList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
