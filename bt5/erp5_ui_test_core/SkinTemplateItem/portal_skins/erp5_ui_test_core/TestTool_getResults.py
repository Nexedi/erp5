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

portal_tests = container.portal_tests\n
if test_zuite_relative_url is not None:\n
  # we care for a specific test zuite\n
  portal_tests = portal_tests.restrictedTraverse(test_zuite_relative_url,\n
                                                 portal_tests)\n
\n
results = portal_tests.objectValues(\'Zuite Results\')\n
if not results:\n
  return None\n
\n
# Selenium results tests are just named "testTable.1", "testTable.2" and so forth.\n
# We replace this by the path of the test, this way we can easily see which test has failed.\n
html = results[len(results) - 1].index_html()\n
for idx, test_case in enumerate(portal_tests.listTestCases()):\n
  html = html.replace(\'>testTable.%s</a>\' % (idx + 1), \'>%s</a>\' % test_case[\'path\'])\n
\n
return html\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>test_zuite_relative_url=None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>TestTool_getResults</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
