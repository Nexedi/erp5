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
            <value> <string>"""Returns the event that caused this ticket.\n
\n
Either defined explictly through causality relation or simply the first event.\n
"""\n
portal = context.getPortalObject()\n
\n
causality = context.getCausalityValue(portal_type=portal.getPortalEventTypeList())\n
if causality is not None:\n
  return causality\n
\n
# XXX for folder workflow action dialog\n
if context.isTempObject():\n
  context = portal.restrictedTraverse(context.getRelativeUrl())\n
\n
event_list = portal.portal_catalog(\n
  portal_type=portal.getPortalEventTypeList(),\n
  default_follow_up_uid=context.getUid(),\n
  limit=1,\n
  sort_on=((\'delivery.start_date\', \'ASC\'),),\n
)\n
if event_list:\n
  return event_list[0].getObject()\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Ticket_getCausalityValue</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
