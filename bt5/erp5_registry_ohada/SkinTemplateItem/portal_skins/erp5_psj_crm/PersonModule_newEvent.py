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
            <value> <string encoding="cdata"><![CDATA[

"""\n
  This script creates a new event with given metadata and\n
  attaches it to the current ticket.\n
"""\n
translateString = context.Base_translateString\n
module = context.getDefaultModule(portal_type)\n
\n
# Build selection\n
person_list = context.portal_selections.getSelectionCheckedValueList(selection_name)\n
if not person_list:\n
  person_list = context.portal_selections.getSelectionValueList(selection_name)\n
\n
# Find authenticated user\n
user = context.portal_membership.getAuthenticatedMember()\n
user_person = context.portal_catalog.getResultValue(portal_type=\'Person\', reference=user)\n
\n
# For every person, create an event\n
if not single_event:\n
  count = 0\n
  for person in person_list:\n
    # Create a new event\n
    event = module.newContent(portal_type=portal_type, \n
                            description=description, \n
                            title=title, \n
                            follow_up=follow_up,\n
                            text_content=text_content) # text_format is set by Event_init\n
    count += 1\n
    # Trigger appropriate workflow action\n
    if direction == \'incoming\':\n
      event.setSourceValue(person)\n
      event.setDestinationValue(user_person)\n
      event.receive()\n
    else:\n
      event.plan()\n
      event.setDestinationValue(person)\n
      event.setSourceValue(user_person)\n
else:\n
  if direction == \'incoming\' and len(person_list) > 1:\n
    # This case is not possible\n
    portal_status_message = translateString("The Single Event option can only be used with outgoing messages",\n
                                    mapping = dict(portal_type = portal_type, count=count))\n
    return context.Base_redirect(form_id, keep_items = dict(portal_status_message=portal_status_message, selection_name=selection_name, selection_index=selection_index), **kw)\n
  # Proceed to event creation\n
  event = module.newContent(portal_type=portal_type, \n
                            description=description, \n
                            title=title, \n
                            follow_up=follow_up,\n
                            text_content=text_content) # text_format is set by Event_init\n
  event.plan()\n
  event.setDestinationValueList(person_list)\n
  event.setSourceValue(user_person)\n
  count = 1\n
\n
# Redirect to the event module (but is this the best place to go since events are not yet indexed ?)\n
portal_status_message = translateString("Created and associated ${count} new ${portal_type}(s) to the selected ticket.", \n
                                    mapping = dict(portal_type = portal_type, count=count))\n
context.Base_redirect(form_id, keep_items = dict(portal_status_message=portal_status_message, selection_name=selection_name, selection_index=selection_index), **kw)\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>portal_type, title, description, direction, selection_name, selection_index, follow_up, single_event=0, text_content=None, form_id=None, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>PersonModule_newEvent</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
