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
  This script is used in parallel list fields\n
  to implement a new \'multi list field behaviour\' \n
  (it repeats category items\n
  in such way that it is possible to select multiple\n
  categories for the same document )\n
"""\n
# Initialise result\n
sub_field_list = []\n
\n
title = default_sub_field_property_dict[\'title\']\n
\n
# Maximum size of the MultiListField\n
default_sub_field_property_dict.update(title=\'&nbsp;\',\n
                                       key=\'default:list\',\n
                                       field_type=\'ListField\',\n
                                       size=1,\n
                                       item_list=[(\'\', \'\')] + item_list,\n
                                       value=None)\n
for value in value_list:\n
  new_dict = default_sub_field_property_dict.copy()\n
  new_dict[\'value\'] = value\n
  sub_field_list.append(new_dict)\n
\n
sub_field_list.append(default_sub_field_property_dict)\n
\n
sub_field_list[0][\'title\'] = title\n
return sub_field_list\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>item_list, value_list, default_sub_field_property_dict={}, is_right_display=0</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_hashCategoryList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
