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
domain = context.getDefaultEventPathDestinationValue()\n
\n
if domain is None:\n
  message = \'Recipients must be defined\'\n
else:\n
  event_path = context.getDefaultEventPathValue(portal_type="Event Path")\n
  method_kw = {\'event_path\': event_path.getRelativeUrl(),\n
   \'keep_draft\': keep_draft}\n
  portal.portal_catalog.searchAndActivate("Entity_createEventFromDefaultEventPath",\n
    selection_domain={domain.getParentId(): (\'portal_domains\', domain.getRelativeUrl())},\n
    method_kw=method_kw)\n
  message = \'Events are being created in background\'\n
\n
return context.Base_redirect(keep_items={\'portal_status_message\': context.Base_translateString(message)})\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>keep_draft=False, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Ticket_createEventFromDefaultEventPath</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
