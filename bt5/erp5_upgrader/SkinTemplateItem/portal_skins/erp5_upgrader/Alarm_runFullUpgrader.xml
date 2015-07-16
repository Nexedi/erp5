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
  Run upgrader\n
"""\n
portal = context.getPortalObject()\n
portal_alarms = portal.portal_alarms\n
\n
def launchUpgraderAlarm(alarm_id, after_tag=None):\n
  """ Get the alarm and use sense and solve """\n
  if after_tag is None:\n
    after_tag = []\n
  upgrader_alarm = getattr(portal_alarms, alarm_id, None)\n
  if upgrader_alarm is not None and (force or upgrader_alarm.sense()):\n
    # call solve method\n
    tag = alarm_id\n
    activate_kw = dict(tag=tag)\n
    activate_kw["after_tag"] = after_tag\n
    method_id = upgrader_alarm.getSolveMethodId()\n
    if method_id not in (None, \'\'):\n
      method = getattr(upgrader_alarm.activate(**activate_kw), method_id)\n
      method(force=force, activate_kw=activate_kw)\n
    return [tag] + after_tag\n
  return after_tag\n
\n
previous_tag = launchUpgraderAlarm(\'upgrader_check_pre_upgrade\')\n
\n
previous_tag = launchUpgraderAlarm(\'upgrader_check_upgrader\',\n
                                   after_tag=previous_tag)\n
\n
previous_tag = launchUpgraderAlarm(\'upgrader_check_post_upgrade\',\n
                                   after_tag=previous_tag)\n
\n
# Nothing else to do, so we can disable.\n
context.setEnabled(False)\n
return\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>force=0, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Alarm_runFullUpgrader</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
