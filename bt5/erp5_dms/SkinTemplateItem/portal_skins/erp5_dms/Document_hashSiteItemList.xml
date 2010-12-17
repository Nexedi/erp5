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
  This script repeats site category items\n
  in such way that it is possible to select multiple\n
  site categories for the same document\n
"""\n
# Initialise result\n
sub_field_list = []\n
\n
# Maximum size of the MultiListField\n
default_sub_field_property_dict.update({\n
  \'required\': 0,\n
  \'field_type\': \'ListField\',\n
  \'size\': 1,\n
  \'item_list\': [(\'\', \'\')] + item_list,\n
  \'value\': None,\n
})\n
\n
z = 0\n
for i in range(1):\n
  new_dict = default_sub_field_property_dict.copy()\n
  new_dict[\'title\'] = \'&nbsp;\'\n
  new_dict[\'key\'] = str(z)\n
  z += 1\n
  sub_field_list.append(new_dict)\n
\n
# WARNING This code is very dangerous and ad hoc\n
# But it was the only way to make parallel list field\n
# work in this case \n
section_list = context.aq_parent.aq_parent.getSiteList()\n
section_list.reverse()\n
for value in section_list:\n
  new_dict = default_sub_field_property_dict.copy()\n
  new_dict[\'value\'] = value\n
  new_dict[\'title\'] = \'&nbsp;\'\n
  new_dict[\'key\'] = str(z)\n
  z += 1\n
  sub_field_list.append(new_dict)\n
\n
new_dict[\'title\'] = default_sub_field_property_dict[\'title\']\n
sub_field_list.reverse()\n
return sub_field_list\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>item_list, value_list, default_sub_field_property_dict={}, is_right_display=0</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Document_hashSiteItemList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
