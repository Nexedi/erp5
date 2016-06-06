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

\'\'\'\n
This script remove accents and spaces and other things from the text to generate a new login\n
\'\'\'\n
\n
inc = 1\n
\n
# XXX here it should be possible to use a regular expression\n
login = text.lower()\n
login = login.replace(\' \', \'_\')\n
login = login.replace(\'é\', \'e\')\n
login = login.replace(\'è\', \'e\')\n
login = login.replace(\'à\', \'a\')\n
login = login.replace(\'ç\', \'c\')\n
\n
new_login = login\n
\n
# search if the login already exists\n
result = context.portal_catalog(reference=login)\n
\n
while len(result) > 0:\n
\n
  if new_login.rfind(\'-\'):\n
    # if a number has already been added to the end of the login, increase it\n
    if new_login[new_login.rfind(\'-\')+1:].isdigit():\n
      inc = int(new_login[new_login.rfind(\'-\')+1:]) + 1\n
\n
  new_login = \'%s-%s\' % (login, inc)\n
  result = context.portal_catalog(reference=new_login)\n
\n
return new_login\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>text</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>generateNewLogin</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
