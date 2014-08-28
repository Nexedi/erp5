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
Return all previous test result line for the same test, same\n
test suite, but for older revisions.\n
\n
Note that creation_date is used, but it could be nicer to use\n
the start date. However for now it is more convenient from a\n
catalog point of view\n
"""\n
\n
test_result = context.getParentValue()\n
\n
query_params = {\'creation_date\' : dict(query=context.getCreationDate(), range=\'ngt\'),\n
                \'portal_type\': \'Test Result\',\n
                \'limit\': limit,\n
                \'title\': dict(query=test_result.getTitle(), key=\'ExactMatch\'),\n
                \'simulation_state\': (\'stopped\', \'public_stopped\', \'failed\'),\n
                \'sort_on\': ((\'creation_date\', \'descending\'),),}\n
\n
result_list = []\n
expected_id = context.getId()\n
expected_title = context.getTitle()\n
\n
for tr in context.portal_catalog(**query_params):\n
  line_found = False\n
  tr = tr.getObject()\n
  \n
  # Optimisation: the test result line probably have the same id in the previous\n
  # test result.\n
  line = getattr(tr, expected_id, None)\n
  if line is not None and line.getTitle() == expected_title \\\n
      and line.getSimulationState() in (\'stopped\', \'public_stopped\', \'failed\'):\n
    result_list.append(line)\n
    line_found = True\n
  else:\n
    for line in tr.contentValues(portal_type=\'Test Result Line\'):\n
      if line.getTitle() == context.getTitle() \\\n
         and line.getSimulationState() in (\'stopped\', \'public_stopped\', \'failed\'):\n
        result_list.append(line)\n
        line_found = True\n
        # next time, the test result line will likely have the same id as this one.\n
        expected_id = line.getId()\n
\n
  # This test result line was not executed in this test. We had a line "Not executed",\n
  # mainly because we have a count method that counts test results, so we need to\n
  # return as many test result line as the count method returns.\n
  if not line_found:\n
    result_list.append(tr.asContext(string_index=\'NOT_EXECUTED\'))\n
    \n
return result_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>limit, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>TestResultLine_getResultHistoryList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
