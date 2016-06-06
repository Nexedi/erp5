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
            <value> <string>"""Find and returns Person object for current logged in user.\n
Returns None if no corresponding person, for example when not using ERP5Security.ERP5UserManager.\n
"""\n
portal = context.getPortalObject()\n
if user_name is None:\n
  user_name = portal.portal_membership.getAuthenticatedMember()\n
\n
from Products.ERP5Security.ERP5UserManager import getUserByLogin\n
found_user_list = getUserByLogin(portal, str(user_name))\n
if len(found_user_list) == 1:\n
  return found_user_list[0]\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>user_name = None</string> </value>
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
            <value> <string>ERP5Site_getAuthenticatedMemberPersonValue</string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>Get current logged in user\'s Person object</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
