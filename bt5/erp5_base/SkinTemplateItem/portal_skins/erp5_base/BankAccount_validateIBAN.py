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
            <value> <string>"""External Validator for IBAN on bank account\n
"""\n
import string\n
if not editor:\n
  return True\n
\n
editor = editor.replace(\' \', \'\').upper()\n
country_code = editor[:2]\n
checksum = editor[2:4]\n
bban = editor[4:]\n
\n
iban_len_dict = {\n
 \'AD\': 24,\n
 \'AT\': 20,\n
 \'BA\': 20,\n
 \'BE\': 16,\n
 \'BG\': 22,\n
 \'CH\': 21,\n
 \'CY\': 28,\n
 \'CZ\': 24,\n
 \'DE\': 22,\n
 \'DK\': 18,\n
 \'EE\': 20,\n
 \'ES\': 24,\n
 \'FI\': 18,\n
 \'FO\': 18,\n
 \'FR\': 27,\n
 \'GB\': 22,\n
 \'GI\': 23,\n
 \'GL\': 18,\n
 \'GR\': 27,\n
 \'HR\': 21,\n
 \'HU\': 28,\n
 \'IE\': 22,\n
 \'IL\': 23,\n
 \'IS\': 26,\n
 \'IT\': 27,\n
 \'LI\': 21,\n
 \'LT\': 20,\n
 \'LU\': 20,\n
 \'LV\': 21,\n
 \'MA\': 24,\n
 \'MC\': 27,\n
 \'ME\': 22,\n
 \'MK\': 19,\n
 \'MT\': 31,\n
 \'NL\': 18,\n
 \'NO\': 15,\n
 \'PL\': 28,\n
 \'PT\': 25,\n
 \'RO\': 24,\n
 \'RS\': 22,\n
 \'SE\': 24,\n
 \'SI\': 19,\n
 \'SK\': 24,\n
 \'SM\': 27,\n
 \'TN\': 24,\n
 \'TR\': 26\n
}\n
\n
if len(editor) != iban_len_dict.get(country_code, -1):\n
  return False\n
\n
letter_code_dict = dict( zip(string.ascii_uppercase, range(10,36)) )\n
\n
iban_code = \'\'.join([str(letter_code_dict.get(x, x))\n
                for x in bban + country_code + checksum])\n
\n
try:\n
    iban_int = int(iban_code)\n
except ValueError:\n
    return False\n
\n
return iban_int % 97 == 1\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>editor, request</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>BankAccount_validateIBAN</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
