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
            <value> <string>from Products.ERP5Type.Cache import CachingMethod\n
\n
cachedMethod = CachingMethod(context.ConfigurationTemplate_readOOCalcFile, script.getId())\n
result = {}\n
filename = "standard_default_accounts.ods"\n
object_list = cachedMethod(filename)\n
\n
for item in object_list:\n
  for k in item.keys():\n
    if k.startswith(\'gap_\'):\n
      gap_id = k[len(\'gap_\'):]\n
      account_list = result.setdefault(gap_id, [])\n
      new_item = item.copy()\n
      new_item[\'gap\'] = new_item.pop(k)\n
      if (\'title_%s\' % gap_id) in new_item:\n
        new_item[\'title\'] = new_item[\'title_%s\' % gap_id]\n
      \n
      # clean all localisation columns\n
      for k in list(new_item.keys()):\n
        if k.startswith(\'gap_\') or k.startswith(\'title_\'):\n
          new_item.pop(k)\n
\n
      account_list.append(new_item)\n
      continue\n
\n
return result\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>BusinessConfiguration_getDefaultAccountList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
