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
            <value> <string>def generic_sort(a,b):\n
  result = 0\n
  for k,v in sort_order:\n
    a_value = a.getProperty(k)\n
    b_value = b.getProperty(k)\n
    result = cmp(a_value,b_value)\n
    if result:\n
      if v in (\'DESC\', \'desc\', \'descending\', \'reverse\'):\n
        return -result\n
      else:\n
        return result\n
  return result \n
\n
unordered_list = map(lambda x: x.getObject(), unordered_list)\n
unordered_list.sort(generic_sort)\n
return unordered_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>unordered_list=[], sort_order=()</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_sortObjectListLikeSQL</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
