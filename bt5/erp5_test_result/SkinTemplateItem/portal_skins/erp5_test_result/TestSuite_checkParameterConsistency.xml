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

import json\n
\n
context.REQUEST.response.setHeader(\'Access-Control-Allow-Origin\', \'*\')\n
\n
error = []\n
#We should verify if the project actually exists\n
if context.getTitle() is None:\n
 error.append(\'ERROR: No project associated!\')\n
if context.getTestSuite() is None:\n
 error.append(\'ERROR: No test-suite associated!\')\n
if context.getTestSuiteTitle() is None:\n
 error.append(\'ERROR: No test-suite-title associated!\')\n
vcs_repository_list = context.objectValues(portal_type="Test Suite Repository")\n
if len(vcs_repository_list) == 0 :\n
 error.append("No vcs_repository_list! (minimum 1)")\n
else:\n
 profile_count = 0\n
 for vcs_list in vcs_repository_list: \n
   for property_name in [\'git_url\',\'buildout_section_id\',\'branch\']:\n
    property_value = vcs_list.getProperty(property_name)\n
    if property_value is None:\n
     error.append(\'ERROR: No \'+property_name+\'!\')\n
   if not(vcs_list.getProperty(\'profile_path\') is None):\n
    profile_count += 1\n
 if profile_count == 0:\n
    error.append(\'ERROR: No profile_path in any vcs_repository! (minimum 1)\')\n
\n
return len(error) >0\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
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
            <value> <string>TestSuite_checkParameterConsistency</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
