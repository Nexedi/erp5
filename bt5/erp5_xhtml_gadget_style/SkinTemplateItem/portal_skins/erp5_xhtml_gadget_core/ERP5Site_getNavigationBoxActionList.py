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
            <key> <string>_Cacheable__manager_id</string> </key>
            <value> <string>http_cache</string> </value>
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
  Return action and modules links for ERP5\'s navigation\n
  box.\n
"""\n
from json import dumps\n
\n
portal= context.getPortalObject()\n
\n
def unLazyActionList(action_list):\n
  # convert to plain dict as list items are lazy calculated ActionInfo instances\n
  fixed_action_list = []\n
  for action in action_list:\n
    d = {}\n
    for k,v in action.items():\n
      if k in [\'url\', \'title\']:\n
        if k == \'url\':\n
          # escape \'&\' as not possible use it in a JSON string\n
          if type(v)!=type(\'s\'):\n
            # this is a tales expression so we need to calculate it\n
            v = str(context.execExpression(v))\n
        d[k] = v\n
    fixed_action_list.append(d)\n
  return fixed_action_list\n
\n
result = {}\n
module_list = portal.ERP5Site_getModuleItemList()\n
search_portal_type_list = portal.getPortalDocumentTypeList() + (\'Person\', \'Organisation\',)\n
language_list = portal.Localizer.get_languages_map()\n
actions = portal.portal_actions.listFilteredActionsFor(context)\n
ordered_global_actions = context.getOrderedGlobalActionList(actions[\'global\']);\n
user_actions = actions[\'user\']\n
\n
ordered_global_action_list = unLazyActionList(ordered_global_actions)\n
user_action_list = unLazyActionList(user_actions)\n
\n
result[\'favourite_dict\'] = {"ordered_global_action_list": ordered_global_action_list,\n
                            "user_action_list": user_action_list\n
                            }\n
result[\'module_list\'] = module_list\n
result[\'language_list\'] = language_list\n
result[\'search_portal_type_list\'] = [ [x,x] for x  in search_portal_type_list]\n
\n
return dumps(result)\n


]]></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ERP5Site_getNavigationBoxActionList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
