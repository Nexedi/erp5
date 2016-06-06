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
            <value> <string>kw = dict(limit=15)\n
\n
if starts_with is not None and search_catalog_key is not None:\n
  kw[search_catalog_key] = "%s%%" % starts_with\n
\n
if search_portal_type is not None:\n
  kw["portal_type"] = search_portal_type\n
\n
result_dict_list = []\n
for brain in context.portal_catalog(**kw):\n
  obj = brain.getObject()\n
\n
  # There may be objects with different Portal Types, so the only way seems\n
  # to call the script for each object... The returned dict should only contains\n
  # \'label\' (first line displayed) and \'description\' (optional: second line displayed)\n
  result_dict = obj.getTypeBasedMethod(\'getCompletionDict\',\n
                                       fallback_script_id=\'Base_getCompletionDict\')(obj)\n
\n
  result_dict[\'value\'] = obj.getProperty(search_catalog_key)\n
  result_dict_list.append(result_dict)\n
\n
from json import dumps\n
return dumps(result_dict_list, indent=4)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>starts_with=None, search_catalog_key=None, search_portal_type=None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ERP5Site_getCompletionDictList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
