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
            <value> <string>test_result = context.getParentValue()\n
test_result_module = test_result.getParentValue()\n
\n
query_params = {\'delivery.start_date\': dict(query=test_result.getStartDate(), range=\'max\'),\n
                \'portal_type\': test_result.getPortalType(),\n
                \'title\': dict(query=test_result.getTitle(), key=\'ExactMatch\'),\n
                \'simulation_state\': \'stopped\',\n
                \'sort_on\': ((\'delivery.start_date\', \'descending\'),),}\n
\n
test_list = test_result_module.searchFolder(**query_params)\n
\n
redirect = container.REQUEST.RESPONSE.redirect\n
from ZTUtils import make_query\n
if test_list:\n
  previous_test_result = test_list[0].getObject()\n
  test_case_list = [tc for tc in previous_test_result.contentValues() if tc.getTitle() == context.getTitle()]\n
  if test_case_list:\n
    return redirect(\'%s/%s?%s\' % (\n
                  test_case_list[0].absolute_url(),\n
                  form_id, make_query(selection_name=selection_name,\n
                                      selection_index=selection_index,\n
                                      portal_status_message=\'Previous Test Result Line\')))\n
\n
return redirect(\'%s/%s?%s\' % (\n
                context.absolute_url(),\n
                form_id, make_query(selection_name=selection_name,\n
                                    selection_index=selection_index,\n
                                    portal_status_message=\'No Previous Test Result Line\')))\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>selection_name=\'\', selection_index=\'0\', form_id=\'view\', **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>TestResultLine_jumpToPreviousTestResultLine</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
