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
            <value> <string>if not ean13_code:\n
  return True\n
\n
ean13_code = [x for x in ean13_code if x.isalnum()]\n
\n
if len(ean13_code) != 13:\n
  return False\n
\n
key = 0\n
coeff = 1\n
for c in ean13_code[:12]:\n
  key += int(c) * coeff\n
  coeff = 4 - coeff # coeff value alternates between 1 and 3\n
key = (10 - key) % 10\n
\n
if key != int(ean13_code[12]):\n
  return False\n
\n
return True\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>ean13_code, REQUEST</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_validateEan13Code</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
