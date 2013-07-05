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
            <value> <string>previous_test = context.TestResult_getPrevious()\n
if previous_test is None:\n
  message = \'No Previous Test Result\'\n
else:\n
  context = previous_test\n
  message = \'Previous Test Result\'\n
\n
redirect = container.REQUEST.RESPONSE.redirect\n
from ZTUtils import make_query\n
return redirect(\'%s/%s?%s\' % (\n
                context.absolute_url_path(),\n
                form_id, make_query(selection_name=selection_name,\n
                                    selection_index=selection_index,\n
                                    portal_status_message=message)))\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>selection_name=\'\', selection_index=\'0\', form_id=\'view\', **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>TestResult_jumpToPreviousTestResult</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
