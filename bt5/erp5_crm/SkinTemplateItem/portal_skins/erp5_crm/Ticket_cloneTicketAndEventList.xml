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
\n
new_ticket = context.Base_createCloneDocument(form_id=None, batch_mode=True)\n
\n
portal.portal_catalog.searchAndActivate(\n
  portal_type=portal.getPortalEventTypeList(),\n
  default_follow_up_uid=context.getUid(),\n
  method_id=\'Event_clone\',\n
  method_kw=dict(follow_up_relative_url=new_ticket.getRelativeUrl()))\n
\n
portal_status_message = portal.Base_translateString(\'Events are beeing cloned in the background.\')\n
keep_items = {\'portal_status_message\':portal_status_message}\n
new_ticket.Base_redirect(form_id=form_id, keep_items=keep_items)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>form_id=\'\'</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Ticket_cloneTicketAndEventList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
