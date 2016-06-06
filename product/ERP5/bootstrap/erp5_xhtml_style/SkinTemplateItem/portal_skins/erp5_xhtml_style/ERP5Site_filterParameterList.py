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
            <value> <string>kept_names = (\'editable_mode\', \'ignore_layout\',            # erp5_web\n
              \'selection_name\', \'selection_index\',         # list mode\n
              \'selection_key\',                             # list mode\n
              \'bt_list\',                                   # business template installation system\n
              \'ignore_hide_rows\',\n
             )\n
# Dialog mode is absent from the kept_name list on purpose :\n
# none of its variable should ever get transmited because\n
# it\'s the deepest level of navigation.\n
# Cancel url is always overwritten, except when rendering\n
# a dialog. So this is safe to propagate it.\n
\n
return dict((item for item in parameter_list.items() if item[0] in kept_names))\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>parameter_list</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ERP5Site_filterParameterList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
