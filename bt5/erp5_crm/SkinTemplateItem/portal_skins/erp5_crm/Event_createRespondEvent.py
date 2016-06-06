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
 TODO: This script does not work now. This needs proxy role, but if proxified, then this script can be a security hole.\n
       Because anyone can create an email and send to everywhere. (Yusei)\n
"""\n
\n
# this script allows to create a new follow up ticket for a given event\n
event_object = context\n
event_module = context.getPortalObject().getDefaultModule(respond_event_portal_type)\n
# Create the outgoing\n
respond_event = event_module.newContent(\n
      portal_type=respond_event_portal_type,\n
      title=respond_event_title,\n
      resource=respond_event_resource,\n
      start_date=DateTime(),\n
      source=context.getDefaultDestination(),\n
      destination=context.getDefaultSource(),\n
      causality=context.getRelativeUrl(),\n
      follow_up=context.getFollowUp(),\n
      text_content=respond_event_text_content,\n
      content_type=context.getContentType()\n
      )\n
\n
# Change the state to posted\n
respond_event.start()\n
\n
if respond_event.portal_type==\'Mail Message\' and respond_event.getSource():\n
  respond_event.send()\n
else:\n
  respond_event.send(from_url=context.portal_preferences.getPreferredEventSenderEmail())\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>respond_event_portal_type, respond_event_title, respond_event_resource, respond_event_text_content</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Event_createRespondEvent</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
