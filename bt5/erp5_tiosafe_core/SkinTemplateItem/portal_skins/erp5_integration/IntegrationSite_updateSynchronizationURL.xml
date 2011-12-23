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
            <value> <string>url = context.getPortalObject().absolute_url()\n
portal_object = context.getPortalObject()\n
acl_users = portal_object.acl_users\n
if not acl_users.getUserById(\'tiosafe_sync_user\'):\n
  acl_users.zodb_users.manage_addUser(\n
      user_id=\'tiosafe_sync_user\',\n
      login_name=\'tiosafe_sync_user\',\n
      password=\'tiosafe_sync_user\',\n
      confirm=\'tiosafe_sync_user\',\n
  )\n
  acl_users.zodb_roles.assignRoleToPrincipal(\'Manager\', \'tiosafe_sync_user\')\n
\n
\n
for im in context.objectValues(portal_type="Integration Module"):\n
  sub = im.getDestinationSectionValue()\n
  pub = im.getSourceSectionValue()\n
  pub.edit(url_string=url)\n
  sub.edit(url_string=url, subscription_url_string=url, user_id=\'tiosafe_sync_user\', password="tiosafe_sync_user")\n
\n
message = context.Base_translateString("Synchronization update to url ${url}.", mapping=dict(url=url))\n
return context.Base_redirect(keep_items=dict(portal_status_message=message))\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>IntegrationSite_updateSynchronizationURL</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
