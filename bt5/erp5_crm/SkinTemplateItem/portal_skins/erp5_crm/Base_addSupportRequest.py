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
            <value> <string>portal = context.getPortalObject()\n
logged_in_user_value = portal.ERP5Site_getAuthenticatedMemberPersonValue()\n
now = DateTime()\n
\n
if support_request_template:\n
  support_request_template = portal.restrictedTraverse(support_request_template)\n
  # Note: temlate\'s reference is first event\'s Portal Type for such template.\n
  # This is not so clean, but is far cheaper than creating a\n
  # "first_event_portal_type" base category, adding it to Support Request and\n
  # then cleaning up such category on instance creation from template.\n
  event_portal_type = support_request_template.getReference()\n
  container = portal.support_request_module\n
  support_request = container[\n
    container.manage_pasteObjects(\n
      support_request_template.getParentValue().manage_copyObjects(\n
        ids=[support_request_template.getId()],\n
      ),\n
    )[0][\'new_id\']\n
  ]\n
  support_request.makeTemplateInstance()\n
else:\n
  support_request = portal.support_request_module.newContent(\n
    portal_type=\'Support Request\',\n
    title=title,\n
    resource=support_request_resource,\n
  )\n
support_request.edit(\n
  source_value=logged_in_user_value,\n
  source_section=portal.portal_preferences.getPreferredSection(),\n
  destination_decision_value=context,\n
  start_date=now,\n
)\n
\n
context_portal_type = context.getPortalType()\n
if context_portal_type == \'Person\':\n
  source = context\n
  source_section = context.getSubordinationValue()\n
elif context_portal_type == \'Organisation\':\n
  source = source_section = context\n
else:\n
  source = source_section = None\n
\n
event = portal.getDefaultModule(portal_type=event_portal_type).newContent(\n
  portal_type=event_portal_type,\n
  title=support_request.getTitle(),\n
  resource=resource,\n
  source_value=source,\n
  source_section_value=source_section,\n
  destination_value=logged_in_user_value,\n
  destination_section_value=None if logged_in_user_value is None else logged_in_user_value.getSubordinationValue(),\n
  start_date=now,\n
  follow_up_value=support_request,\n
  text_content=text_content,\n
  content_type=\'text/html\' if portal.portal_preferences.getPreferredTextEditor() else \'text/plain\',\n
)\n
support_request.setCausalityValue(event)\n
# Note: workflow can be event_workflow or event_simulation_workflow.\n
# The former allows "deliver" from "started" only, so use this state.\n
event.start()\n
event.deliver()\n
\n
for method_id in {\n
      \'submitted\': (\'submit\', ),\n
      \'validated\': (\'validate\', ),\n
      \'suspended\': (\'validate\', \'suspend\'),\n
      \'invalidated\': (\'validate\', \'invalidate\'),\n
    }[support_request_state]:\n
  getattr(support_request, method_id)()\n
\n
support_request.Base_redirect(\n
  keep_items={\n
    \'portal_status_message\': portal.Base_translateString(\n
      \'New ${portal_type} created.\',\n
      mapping={\n
        \'portal_type\': \'Support Request\',\n
      },\n
    ),\n
  },\n
)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>event_portal_type, resource, support_request_resource, support_request_state, support_request_template, text_content, title, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_addSupportRequest</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
