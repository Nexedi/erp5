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
            <value> <string>portal = state_change.getPortal()\n
\n
# invalidate the cache for security\n
portal.portal_caches.clearCache(cache_factory_list=(\'erp5_content_short\',))\n
\n
# Using PAS removes the need of anything else in this script\n
if portal.acl_users.meta_type == \'Pluggable Auth Service\':\n
  return\n
\n
# Get the assignment object and its parent\n
assignment_object = state_change[\'object\']\n
person_object     = assignment_object.getParentValue()\n
\n
# Call the script if available\n
person_security_script = getattr(person_object, \'Person_updateUserSecurityGroup\', None)\n
\n
if person_security_script is not None:\n
  person_security_script()\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>state_change</string> </value>
        </item>
        <item>
            <key> <string>_proxy_roles</string> </key>
            <value>
              <tuple>
                <string>Manager</string>
              </tuple>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Assignment_updateUserSecurityGroup</string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>This script use Proxy Role(Manager)</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
