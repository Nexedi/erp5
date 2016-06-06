<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <tuple>
        <global name="PythonScript" module="Products.PythonScripts.PythonScript"/>
        <tuple/>
      </tuple>
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

"""Valid line field input as email list"""\n
#We stop the hook if we get an error else no error\n
def hasError(email):\n
  email_parts = email.split(\'@\')\n
  if len(email_parts) != 2:\n
    return True\n
  \n
  suffix_parts = email_parts[1].split(\'.\')\n
  if len(suffix_parts) < 2:\n
    return True\n
\n
  if len(email_parts[0]) == 0:\n
    return True\n
\n
  if len(suffix_parts[0]) == 0 or len(suffix_parts[1]) == 0 :\n
    return True\n
\n
  return False\n
\n
for email in value:\n
  if hasError(email):\n
    break\n
else:\n
  return True\n
\n
\n
return False\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_code</string> </key>
            <value>
              <none/>
            </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>value, REQUEST</string> </value>
        </item>
        <item>
            <key> <string>errors</string> </key>
            <value>
              <tuple/>
            </value>
        </item>
        <item>
            <key> <string>func_code</string> </key>
            <value>
              <object>
                <klass>
                  <global name="FuncCode" module="Shared.DC.Scripts.Signature"/>
                </klass>
                <tuple/>
                <state>
                  <dictionary>
                    <item>
                        <key> <string>co_argcount</string> </key>
                        <value> <int>2</int> </value>
                    </item>
                    <item>
                        <key> <string>co_varnames</string> </key>
                        <value>
                          <tuple>
                            <string>value</string>
                            <string>REQUEST</string>
                            <string>hasError</string>
                            <string>_getiter_</string>
                            <string>email</string>
                            <string>True</string>
                            <string>False</string>
                          </tuple>
                        </value>
                    </item>
                  </dictionary>
                </state>
              </object>
            </value>
        </item>
        <item>
            <key> <string>func_defaults</string> </key>
            <value>
              <none/>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>LinesField_EmailsValidator</string> </value>
        </item>
        <item>
            <key> <string>warnings</string> </key>
            <value>
              <tuple/>
            </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
