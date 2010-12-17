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

group_id_list_generator = getattr(context, \'ERP5Type_asSecurityGroupId\')\n
\n
security_category_dict = {}\n
# XXX This is a duplicate of logic present deep inside ERP5GroupManager.getGroupsForPrincipal()\n
# Please refactor into an accessible method so this code can be removed\n
def getDefaultSecurityCategoryMapping():\n
    return ((\n
              \'ERP5Type_getSecurityCategoryFromAssignment\',\n
              context.getPortalObject().getPortalAssignmentBaseCategoryList()\n
            ),)\n
getSecurityCategoryMapping = getattr(context, \'ERP5Type_getSecurityCategoryMapping\', getDefaultSecurityCategoryMapping)\n
# XXX end of code duplication\n
for method_id, base_category_list in getSecurityCategoryMapping():\n
  try:\n
    security_category_dict.setdefault(tuple(base_category_list), []).extend(\n
      getattr(context, method_id)(base_category_list, login, context, \'\'))\n
  except: # XXX: it is not possible to log message with traceback from python script\n
    print \'It was not possible to invoke method %s with base_category_list %s\'%(method_id, base_category_list)\n
\n
for base_category_list, category_value_list in security_category_dict.items():\n
  print \'base_category_list:\', base_category_list\n
  for category_dict in category_value_list:\n
    print \'-> category_dict:\', category_dict\n
    print \'-->\', group_id_list_generator(category_order=base_category_list,\n
                                        **category_dict)\n
return printed\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>login</string> </value>
        </item>
        <item>
            <key> <string>_proxy_roles</string> </key>
            <value>
              <tuple>
                <string>Manager</string>
                <string>Member</string>
              </tuple>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_viewSecurityMappingAsUser</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
