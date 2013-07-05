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
            <value> <string>form = context.REQUEST.form\n
test_result_file = form.get(\'filepath\')\n
test_report_id = form.get(\'test_report_id\', \'\')\n
\n
# find already created test result object\n
test_report = getattr(context, test_report_id)\n
\n
# parse test log file to get number of tests (successfull/failed)\n
all_test_results = context.parseTestSuiteResults(test_result_file)\n
\n
all_tests = 0\n
errors = 0\n
failures = 0\n
skips = 0\n
\n
# \'edit\' magic key is used to pass edit parameter from the external method to this script\n
# this is horrible XXX\n
edit_dict = all_test_results.pop(\'edit\', None)\n
if edit_dict:\n
  test_report.edit(**edit_dict)\n
\n
for test_id, test_result in all_test_results.items():\n
  # save log files\n
  log_files = test_result[\'files\']\n
\n
  all_tests += test_result[\'all_tests\']\n
  errors += test_result[\'errors\']\n
  failures += test_result[\'failures\']\n
  skips += test_result[\'skips\']\n
\n
  # save passed initial test state\n
  test_report.newContent(\n
            portal_type=\'Test Result Line\',\n
            id=test_id,\n
            title=test_result.get(\'test_case\'),\n
            string_index=test_result.get(\'result\'),\n
            all_tests=test_result.get(\'all_tests\'),\n
            html_test_result=test_result.get(\'html_test_result\'),\n
            errors=test_result.get(\'errors\'),\n
            failures=test_result.get(\'failures\'),\n
            skips=test_result.get(\'skips\'),\n
            duration=test_result.get(\'seconds\'),\n
            cmdline=log_files.get(\'cmdline\'),\n
            stdout=log_files.get(\'stdout\'),\n
            stderr=log_files.get(\'stderr\'),)\n
    \n
\n
test_report.edit(string_index=form.get(\'result\'),\n
                 all_tests=all_tests,\n
                 errors=errors,\n
                 failures=failures,\n
                 skips=skips)\n
\n
test_report.stop()\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>**kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>TestResultModule_reportCompleted</string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>Called at test finish</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
