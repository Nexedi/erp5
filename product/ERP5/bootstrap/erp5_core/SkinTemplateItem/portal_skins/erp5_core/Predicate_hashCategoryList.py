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
            <value> <string>"""\n
  This script is used in parallel list fields in Predicate_view\n
"""\n
# Initialise result\n
sub_field_list = []\n
\n
# use MultiListField\n
default_sub_field_property_dict.update({\'field_type\':\'MultiListField\'})\n
\n
z = 0\n
category_list = []\n
for x in item_list:\n
  base_category = x[1].split(\'/\', 1)[0]\n
  if base_category and base_category not in category_list:\n
    category_list.append(base_category)\n
\n
for category in category_list:\n
  new_dict = default_sub_field_property_dict.copy()\n
  new_dict[\'value\'] = [x for x in value_list if x.startswith(\'%s/\' % category)]\n
  if z == 0:\n
    new_dict[\'title\'] = \'%s (%s)\' % (default_sub_field_property_dict[\'title\'], category)\n
  else:\n
    new_dict[\'title\'] = \'(%s)\' % category\n
  new_dict[\'item_list\'] = [[\'\', \'\']] + [x for x in item_list if x[1].startswith(\'%s/\' % category)]\n
  new_dict[\'key\'] = str(z)\n
  if len(new_dict[\'item_list\']) == 1:\n
    continue\n
  z += 1\n
  sub_field_list.append(new_dict)\n
\n
request = context.REQUEST\n
\n
return sub_field_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>item_list, value_list, default_sub_field_property_dict={}, is_right_display=0</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Predicate_hashCategoryList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
