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
"""\n
N_ = context.Base_translateString\n
if len(uids):\n
  for alarm in context.portal_alarms.searchFolder(uid=uids):\n
    alarm.solve()\n
    # Invoke activiveSense a bit later\n
    alarm.activate().activeSense()\n
  portal_status_message = N_("Site Configuration is going to be fixed by Activities.")\n
else:\n
  portal_status_message = N_("No Site Configuration fix was request.")\n
\n
if enable_alarm:\n
  updated = False\n
  for alarm in context.portal_alarms.searchFolder(id="promise_%"):\n
    if not alarm.getEnabled():\n
      alarm.setEnabled(1)\n
      updated = True\n
  if updated:\n
    portal_status_message += N_("Consistency Check information will be periodically updated.")\n
\n
form_id = context.REQUEST.get("form_id", "")\n
\n
return context.Base_redirect(form_id, \n
                keep_items=dict(portal_status_message=portal_status_message))\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>enable_alarm=True, uids=[], **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ERP5Site_fixConfigurationConsistency</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
