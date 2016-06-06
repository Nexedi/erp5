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
portal = context.getPortalObject()\n
translateString = portal.Base_translateString\n
module = portal.getDefaultModule(portal_type)\n
\n
if not portal.Base_checkPermission(module.getId(), "Add portal content"):\n
  return context.Base_redirect(form_id,\n
                               keep_items=dict(\n
     portal_status_message=translateString("You do not have permission to add new event.")))\n
\n
# Create a new event\n
response = module.newContent(portal_type=portal_type,\n
                             source=source,\n
                             destination=destination,\n
                             resource=resource,\n
                             title=title,\n
                             text_content=text_content,\n
                             start_date=start_date,\n
                             follow_up_value=context,\n
                             content_type=content_type)\n
\n
if notification_message:\n
  response.Event_setTextContentFromNotificationMessage(\n
    reference=notification_message\n
  )\n
\n
if workflow_action:\n
  portal.portal_workflow.doActionFor(\n
    context,\n
    workflow_action,\n
  )\n
\n
message = translateString(\n
  "Created and associated a new ${portal_type} to the ticket.", \n
  mapping=dict(portal_type = translateString(portal_type)))\n
\n
if event_workflow_action == \'send\':\n
  response.start()\n
elif event_workflow_action == \'plan\':\n
  response.plan()\n
elif event_workflow_action == \'deliver\':\n
  response.deliver()\n
elif event_workflow_action == \'draft\':\n
  pass\n
else:\n
  raise NotImplementedError(\'Do not know what to do\')\n
return response.Base_redirect(\'view\', keep_items={\'portal_status_message\': message})\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>form_id=None, portal_type=None, resource=None,  title=None, text_content=None, start_date=None, event_workflow_action=None, notification_message=None, source=None, destination=None, content_type=None, workflow_action=None, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Ticket_newEvent</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
