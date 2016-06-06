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
            <value> <string>portal = context.getPortalObject()\n
portal_types = portal.searchFolder(title=\'portal_types\')[0]\n
role_name_list = [\'Assignor\', \'Assignee\', \'Associate\', \'Auditor\', \'Author\']\n
role_category_list = [\'group/my_group\']\n
\n
role_list = [\'Product\', \'Product Module\', \'Person\', \'Person Module\', \n
                  \'Organisation\', \'Organisation Module\', \'Sale Trade Condition\',\n
                  \'Sale Trade Condition Module\', \'Web Page Module\', \'Sale Order Module\']\n
\n
\n
for role in role_list:\n
\n
  # Get portal type\n
  current_portal = portal_types.searchFolder(title={\'query\':role, \'key\':\'ExactMatch\'})[0]\n
\n
  # Delete existing role informations\n
  id_list =  [x.getId() for x in current_portal.searchFolder(portal_type=\'Role Information\')]\n
  current_portal.manage_delObjects(id_list)\n
\n
  # Create new role information\n
  current_portal.newContent(\n
                    portal_type = \'Role Information\',\n
                    title = \'Default\',\n
                    role_name_list = role_name_list,\n
                    role_category_list = role_category_list,\n
                    description = \'Configured by Scalability script\'\n
                   )\n
  # Update roles\n
  current_portal.updateRoleMapping()\n
\n
return 1\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>update_roles_scalability</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
