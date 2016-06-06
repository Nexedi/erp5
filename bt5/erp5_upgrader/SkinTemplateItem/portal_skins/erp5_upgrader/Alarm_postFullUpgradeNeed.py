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
            <value> <string>if REQUEST is not None:\n
  from zExceptions import Unauthorized\n
  raise Unauthorized("You can not call this script from the url")\n
\n
alarm_id_list = ("upgrader_check_pre_upgrade",\n
  "upgrader_check_upgrader",\n
  "upgrader_check_post_upgrade")\n
\n
portal = context.getPortalObject()\n
portal_alarms = portal.portal_alarms\n
message_list = []\n
\n
for alarm_id in alarm_id_list:\n
  alarm = getattr(portal_alarms, alarm_id, None)\n
  if alarm is not None and alarm.sense():\n
    last_active_process = alarm.getLastActiveProcess()\n
    result_list = last_active_process.getResultList()\n
    if result_list:\n
      detail = result_list[0].detail\n
    else:\n
      detail = ["Require solve %s" % alarm_id,]\n
    message_list.extend(detail)\n
\n
active_process = portal.restrictedTraverse(active_process)\n
if message_list:\n
  active_process.postActiveResult(\n
    summary=context.getTitle(),\n
    severity=1, detail=message_list)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>active_process, REQUEST=None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Alarm_postFullUpgradeNeed</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
