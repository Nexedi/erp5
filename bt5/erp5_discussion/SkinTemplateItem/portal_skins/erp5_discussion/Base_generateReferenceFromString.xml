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

"""\n
  Generate reference from a string by escaping all non ascii characters.\n
  XXX: add support for non-ascii characters using unidecode python library\n
"""\n
transliterate_list = [\'?\', \':\', \';\', \'/\', \'&\', \'=\', \'^\', \'@\', \'>\', \'<\', \']\', \'[\', \'^\', \'\\\\\']\n
\n
def removeNonAscii(s): \n
  return "".join(i for i in s if ord(i)>44 and ord(i)<123)\n
\n
# reference can be used for permanent URL so be friendly to spaces (SEO)\n
s = s.strip()\n
s =s.replace(\' \', \'-\')\n
\n
s = removeNonAscii(s)\n
for item in transliterate_list:\n
  s = s.replace(item, \'-\')\n
\n
return s.strip(\'-\')\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>s</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_generateReferenceFromString</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
