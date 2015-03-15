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
            <value> <string>ticket = sci[\'object\']\n
kw = sci[\'kwargs\']\n
\n
event = ticket.Ticket_getCausalityValue()\n
event.Event_createResponse(\n
  response_event_portal_type=kw[\'response_event_portal_type\'],\n
  response_event_resource=kw[\'response_event_resource\'],\n
  response_event_title=kw.get(\'response_event_title\'),\n
  response_event_text_content=kw.get(\'response_event_text_content\'),\n
  response_event_start_date=kw[\'response_event_start_date\'],\n
  response_workflow_action=kw[\'response_workflow_action\'],\n
  response_event_notification_message=kw[\'response_event_notification_message\'],\n
  default_destination=kw[\'default_destination\'],\n
  response_event_content_type=kw[\'response_event_content_type\'])\n
\n
ticket.invalidate()\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>sci</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>createResponseAndInvalidate</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
