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
            <value> <string>"""\n
  Script customized to UNG to don\'t check the preference permission\n
"""\n
\n
if REQUEST is not None:\n
  from zExceptions import Unauthorized\n
  raise Unauthorized(script.getId())\n
\n
portal = context.getPortalObject()\n
\n
if not context.getReference():\n
  # noop in case if invoked on non loggable object\n
  return\n
\n
from Products.ERP5Type.Message import translateString\n
preference = portal.portal_preferences.createPreferenceForUser(\n
                                  context.getReference(), enable=True)\n
\n
preference.setTitle(translateString(\'Preference for ${name}\',\n
                     mapping=dict(name=context.getTitle().decode(\'utf-8\'))))\n
\n
for assignment in context.contentValues(portal_type=\'Assignment\'):\n
  group = assignment.getGroup(base=True)\n
  if group:\n
    preference.setPreferredSectionCategory(group)\n
    preference.setPreferredAccountingTransactionSectionCategory(group)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>REQUEST=None</string> </value>
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
            <value> <string>Person_createUserPreference</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
