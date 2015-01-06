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

portal = context.getPortalObject()\n
security_uid_field_list = [x + ("_" if x != "" else "") + "security_uid" for x in portal.portal_catalog.getSQLCatalog().getSQLCatalogSecurityUidGroupsColumnsDict().keys()]\n
security_uid_set_list = []\n
for security_uid_field in security_uid_field_list:\n
  security_uid_set_list.append({getattr(x, security_uid_field) for x in context.z_get_referenced_security_uid_set_for(security_uid_field=security_uid_field)})\n
security_uid_set = reduce(lambda p, v: p.union(v), security_uid_set_list)\n
filtered_set = context.Base_filterSecurityUidDict(\n
  portal.portal_catalog.getSQLCatalog(catalog_id).security_uid_dict,\n
  security_uid_set\n
)\n
if len(filtered_set) > 0:\n
  context.z_delete_from_roles_and_users(uid=filtered_set)\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>catalog_id=None</string> </value>
        </item>
        <item>
            <key> <string>guard</string> </key>
            <value>
              <persistent> <string encoding="base64">AAAAAAAAAAI=</string> </persistent>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_cleanupRolesAndUsersTable</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
  <record id="2" aka="AAAAAAAAAAI=">
    <pickle>
      <global name="Guard" module="Products.DCWorkflow.Guard"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>roles</string> </key>
            <value>
              <tuple>
                <string>Manager</string>
              </tuple>
            </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
