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
            <value> <string># this script allows to create a new follow up ticket for\n
# the current event if the event isn\'t already linked with\n
# an existing ticket\n
\n
event = state_change[\'object\']\n
\n
if not(len(event.getFollowUpValueList())):\n
  history = event.portal_workflow.getInfoFor(event, \'history\', wf_id=\'event_workflow\')\n
\n
  for history_item in history[::-1]:\n
    if history_item[\'action\'] == \'assign_action\':\n
      follow_up_ticket_type = history_item[\'follow_up_ticket_type\']\n
      follow_up_ticket_title = history_item[\'follow_up_ticket_title\']\n
      break\n
\n
  event.Event_createFollowUpTicket(follow_up_ticket_title, follow_up_ticket_type)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>state_change</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Event_createFollowUpTicket</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
