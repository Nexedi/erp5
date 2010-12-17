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
            <value> <string># this script allows to create a new respond event for\n
# the current acknowledged event\n
\n
portal = state_change.getPortal()\n
portal_workflow = portal.portal_workflow\n
event = state_change[\'object\']\n
\n
follow_up_ticket_type = portal_workflow.getInfoFor(event,\n
                                                   \'follow_up_ticket_type\',\n
                                                   wf_id=\'event_workflow\')\n
\n
follow_up_ticket_title = portal_workflow.getInfoFor(event,\n
                                                    \'follow_up_ticket_title\',\n
                                                    wf_id=\'event_workflow\')\n
\n
create_event = portal_workflow.getInfoFor(event, \'create_event\',\n
                                          wf_id=\'event_workflow\')\n
\n
quote_original_message = portal_workflow.getInfoFor(event,\n
                                                    \'quote_original_message\',\n
                                                    wf_id=\'event_workflow\')\n
\n
follow_up = event.getFollowUp()\n
\n
if follow_up is None:\n
  if not (follow_up_ticket_type and follow_up_ticket_title):\n
    raise ValueError, \'Follow up must not empty when assign or acknowledge.\'\n
\n
if follow_up is None and follow_up_ticket_type and follow_up_ticket_title:\n
  event.Event_createFollowUpTicket(follow_up_ticket_title,\n
                                   follow_up_ticket_type)\n
\n
if create_event:\n
  new_event = portal.event_module.newContent(portal_type=event.portal_type,\n
                                             destination=event.getSource(),\n
                                             follow_up=event.getFollowUp(),\n
                                             causality=event.getRelativeUrl(),\n
                                             start_date=DateTime())\n
\n
  if quote_original_message:\n
    new_event.edit(content_type=event.getContentType(),\n
                   title=event.getReplySubject(),\n
                   text_content=event.getReplyBody())\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>state_change</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Event_createEventForAcknowledge</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
