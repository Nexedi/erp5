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
            <value> <string>try:\n
  return container.REQUEST.other[script.id]\n
except KeyError:\n
  pass\n
\n
if not role_list:\n
  return []\n
\n
portal = context.getPortalObject()\n
\n
if not portal_type:\n
  portal_type = portal.getPortalNodeTypeList()\n
\n
role_uid = [portal.portal_categories.resolveCategory(role).getUid()\n
              for role in role_list]\n
\n
result = container.REQUEST.other[script.id] = [(\'\', \'\')] + [\n
      (x.getTitle(), x.getRelativeUrl()) for x in \n
            context.portal_catalog.searchResults(\n
               portal_type=portal_type,\n
               default_role_uid=role_uid,\n
               validation_state=validation_state,\n
               sort_on=((\'portal_type\', \'asc\'),\n
                        (\'title\', \'asc\'))) ]\n
\n
return result\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>role_list, validation_state=\'validated\', portal_type=None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_getEntityItemList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
