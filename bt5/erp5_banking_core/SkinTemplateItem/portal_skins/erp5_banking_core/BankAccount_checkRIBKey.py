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
            <value> <string>d = {}\n
d[\'A\'] = d[\'J\'] = \'1\'\n
d[\'B\'] = d[\'K\'] = d[\'S\'] = \'2\'\n
d[\'C\'] = d[\'L\'] = d[\'T\'] = \'3\'\n
d[\'D\'] = d[\'M\'] = d[\'U\'] = \'4\'\n
d[\'E\'] = d[\'N\'] = d[\'V\'] = \'5\'\n
d[\'F\'] = d[\'O\'] = d[\'W\'] = \'6\'\n
d[\'G\'] = d[\'P\'] = d[\'X\'] = \'7\'\n
d[\'H\'] = d[\'Q\'] = d[\'Y\'] = \'8\'\n
d[\'I\'] = d[\'R\'] = d[\'Z\'] = \'9\'\n
\n
old_rib = account_nb[-2:]\n
\n
new_account_nb = ""\n
for nb in list(account_nb)[:-2]:\n
  if d.has_key(nb):\n
    new_account_nb += d[nb]\n
  else:\n
    new_account_nb += nb\n
\n
new_account_nb += "00"\n
new_account_nb = long(new_account_nb)\n
rib = 97 - new_account_nb % 97\n
\n
return (str(rib) == str(old_rib))\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>account_nb</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>BankAccount_checkRIBKey</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
