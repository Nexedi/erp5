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
 Applies all the configuration necessary to have UNG working.\n
"""\n
portal = context.getPortalObject()\n
isTransitionPossible = portal.portal_workflow.isTransitionPossible\n
\n
# enable the ung_preference\n
ung_preference = getattr(portal.portal_preferences, \'ung_preference\', None)\n
if ung_preference is not None:\n
 if  isTransitionPossible(ung_preference, \'enable\'):\n
   ung_preference.enable()\n
\n
# publish the ung web site\n
ung_web_site = getattr(portal.web_site_module, \'ung\', None)\n
if ung_web_site is not None:\n
  if isTransitionPossible(ung_web_site, \'publish\', None):\n
    ung_web_site.publish()\n
    for web_section in ung_web_site.contentValues(portal_types=\'Web Section\'):\n
      if isTransitionPossible(web_section, \'publish\', None):\n
        web_section.publish()\n
\n
# configure system preference\n
ung_system_preference = getattr(portal.portal_preferences, \'ung_system_preference\', None)\n
if ung_system_preference is None:\n
  ung_system_preference = portal.portal_preferences.newContent(portal_type=\'System Preference\',\n
                                                               id=\'ung_system_preference\',\n
                                                               title=\'UNG System Preference\')\n
  ung_system_preference.setPreferredOoodocServerAddress(\'localhost\')\n
  ung_system_preference.setPreferredOoodocServerPortNumber(\'8008\')\n
  ung_system_preference.enable()\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Alarm_configureUng</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
