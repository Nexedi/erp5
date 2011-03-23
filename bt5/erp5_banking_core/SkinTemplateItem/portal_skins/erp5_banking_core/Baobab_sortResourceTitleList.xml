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
            <value> <string>def currency_cmp(a, b):\n
  a_type = a[0][0]\n
  b_type = b[0][0]\n
  tmp_cmp = cmp(a_type, b_type)\n
  if tmp_cmp != 0:\n
    return tmp_cmp\n
  a_value = int(a[0].split()[2])\n
  b_value = int(b[0].split()[2])\n
  tmp_cmp= cmp(b_value, a_value)\n
  if tmp_cmp != 0:\n
    return tmp_cmp\n
  a_year = int(a[1])\n
  b_year = int(b[1])\n
  return cmp(a_year, b_year)\n
\n
list.sort(currency_cmp)\n
return list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>list</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Baobab_sortResourceTitleList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
