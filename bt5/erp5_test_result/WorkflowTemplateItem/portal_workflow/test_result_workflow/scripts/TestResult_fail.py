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
            <value> <string>test_result = sci[\'object\']\n
kw = sci[\'kwargs\']\n
stop_date = kw.get(\'date\') or DateTime()\n
test_result.setStopDate(stop_date)\n
if test_result.getPortalType() == \'Test Result Node\':\n
  cmdline = kw.get(\'command\', getattr(test_result, \'cmdline\', \'\'))\n
  edit_kw = {}\n
  if same_type(cmdline, []):\n
    cmdline = \' \'.join(map(repr, cmdline))\n
  if cmdline:\n
    edit_kw[\'cmdline\'] = cmdline\n
  for key in (\'stdout\', \'stderr\'):\n
    key_value = kw.get(key, getattr(test_result, key, \'\'))\n
    if key_value:\n
      edit_kw[key] = key_value\n
  test_result.edit(**edit_kw)\n
else:\n
  context.TestResult_complete(sci)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>sci</string> </value>
        </item>
        <item>
            <key> <string>_proxy_roles</string> </key>
            <value>
              <tuple>
                <string>Manager</string>
              </tuple>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>TestResult_fail</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
