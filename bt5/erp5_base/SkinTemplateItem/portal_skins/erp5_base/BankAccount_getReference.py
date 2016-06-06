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
            <value> <string>reference = \'\'\n
if context.getBankCountryCode():\n
  reference = \' \'.join((context.getBankCountryCode(),\n
                   context.getBankCode() or \'\',\n
                   context.getBranch() or \'\',\n
                   context.getBankAccountNumber() or \'\',\n
                   context.getBankAccountKey() or \'\'))\n
else:\n
  reference = \' \'.join((context.getBankCode() or \'\',\n
                   context.getBranch() or \'\',\n
                   context.getBankAccountNumber() or \'\',\n
                   context.getBankAccountKey() or \'\'))\n
\n
if not reference.strip():\n
  return default or context.getTitleOrId()\n
\n
return reference\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>default=None, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>BankAccount_getReference</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
