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
req = portal.erp5_sql_connection.manage_test\n
\n
security_uid_field_list = [x + ("_" if x != "" else "") + "security_uid" for x in portal.portal_catalog.getSQLCatalog().getSQLCatalogSecurityUidGroupsColumnsDict().keys()]\n
referenced_uid_set = set()\n
all_uid_set = set()\n
for security_uid_field in security_uid_field_list:\n
  referenced_uid_set.union({getattr(row, security_uid_field) for row in req("select distinct %s from catalog where %s is not NULL" % (security_uid_field, security_uid_field))})\n
\n
print(">> useless uids in roles_and_users table <<\\n")\n
if len(referenced_uid_set) > 0:\n
  for row in req("select * from roles_and_users where uid not in %s" + tuple(referenced_uid_set)):\n
    print row.uid, row.local_roles_group_id, row.allowedRolesAndUsers\n
\n
print("\\n>> uids that should be in roles_and_users table <<\\n")\n
all_uid_set = {row.uid for row in req("select uid from roles_and_users")}\n
\n
for security_uid_field in security_uid_field_list:\n
  for row in req("select %s, relative_url from catalog where %s not in %s" % (security_uid_field, security_uid_field, tuple(all_uid_set))):\n
    print security_uid_field, getattr(row, security_uid_field, None), row.relative_url\n
\n
print("\\n>> END <<")\n
return printed\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_dumpUnreferencedSecurityUid</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
