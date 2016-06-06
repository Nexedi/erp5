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
            <value> <string># Remove empty items\n
item_list = filter(lambda x: x not in [(\'\',\'\'), [\'\',\'\']], \n
                   item_list)\n
\n
sub_field_dict = {}\n
split_depth = 1\n
\n
for item in item_list:\n
  # Get value of the item\n
  item_value = item[int(not is_right_display)]\n
  \n
  # Hash key from item_value\n
  item_split = string.split(item_value, \'/\')\n
  item_key = string.join(item_split[:split_depth] , \'/\' )\n
\n
  if not sub_field_dict.has_key(item_key):\n
    # Create property dict\n
    sub_field_property_dict = default_sub_field_property_dict.copy()\n
    sub_field_property_dict[\'key\'] = item_key\n
    sub_field_property_dict[\'required\'] = 1\n
    sub_field_property_dict[\'field_type\'] = \'ListField\'\n
    sub_field_property_dict[\'size\'] = 1\n
    sub_field_property_dict[\'item_list\'] = [(\'\',\'\')]\n
    sub_field_dict[item_key] = sub_field_property_dict\n
\n
  sub_field_dict[item_key][\'item_list\'] =\\\n
     sub_field_dict[item_key][\'item_list\'] + [item]\n
  if item_value in value_list:\n
    sub_field_dict[item_key][\'value\'] = item_value\n
\n
return sub_field_dict.values()\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>item_list, value_list, default_sub_field_property_dict={}, is_right_display=0</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Resource_hashVariationCategoryItemList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
