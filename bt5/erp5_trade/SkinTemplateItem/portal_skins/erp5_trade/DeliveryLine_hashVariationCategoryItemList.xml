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
item_list = filter(lambda x: x not in [(\'\',\'\'), [\'\',\'\']],\\\n
                   item_list)\n
sub_field_dict = {}\n
split_depth = 1\n
resource = context.getResourceValue()\n
if resource is not None:\n
  not_option_base_category_list = resource.getVariationBaseCategoryList(\n
                                                 omit_optional_variation=1)\n
else :\n
  not_option_base_category_list = ()\n
\n
del default_sub_field_property_dict[\'item_list\']\n
for item in item_list:\n
  # Get value of the item\n
  item_value = item[int(not is_right_display)]\n
  # Hash key from item_value\n
  item_split = string.split(item_value, \'/\')\n
  item_key = string.join(item_split[:split_depth] , \'/\' )\n
  base_category = item_split[0]\n
\n
  sub_field_property_dict = sub_field_dict.setdefault(item_key, default_sub_field_property_dict.copy())\n
\n
  sub_field_property_dict[\'key\'] = item_key\n
  sub_field_property_dict[\'required\'] = int(base_category in not_option_base_category_list)\n
  sub_field_property_dict[\'field_type\'] = \'ListField\'\n
  sub_field_property_dict[\'size\'] = 1\n
  sub_field_property_dict.setdefault(\'item_list\', [(\'\', \'\')]).extend([item])\n
  if item_value in value_list:\n
    # Only one value per variation\n
    sub_field_property_dict[\'value\'] = item_value\n
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
            <value> <string>DeliveryLine_hashVariationCategoryItemList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
