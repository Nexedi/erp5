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
            <value> <string># When validating a user preference, we invalidate other user preferences.\n
\n
from Products.ERP5Type.Message import translateString\n
\n
portal = context.getPortalObject()\n
\n
\n
if context.getPriority() != 3: # XXX 3 is Priority.USER\n
  return\n
\n
for preference in portal.portal_preferences.searchFolder(\n
    owner={\'query\': str(portal.portal_membership.getAuthenticatedMember()), \'key\': \'ExactMatch\'},\n
    portal_type=context.getPortalType()):\n
  preference = preference.getObject()\n
  assert portal.portal_membership.getAuthenticatedMember().allowed(preference, [\'Owner\', ]), preference\n
\n
  if preference != context and \\\n
      preference.getPreferenceState() == \'enabled\' and \\\n
      preference.getPriority() == context.getPriority():\n
    preference.disable(\n
      comment=translateString(\n
        \'Automatically disabled when enabling ${preference_title}.\',\n
        mapping={\'preference_title\': context.getTitle()}))\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Preference_disableOtherPreferences</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
