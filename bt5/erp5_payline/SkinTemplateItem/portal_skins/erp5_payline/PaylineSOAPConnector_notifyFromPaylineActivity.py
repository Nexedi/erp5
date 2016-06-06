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
container = portal.system_event_module\n
if object_id is not None and object_id in container:\n
  return\n
http_exchange = container.newContent(\n
  id=object_id,\n
  portal_type=\'HTTP Exchange\',\n
  request=request,\n
  response=response,\n
  resource_value=None if notification_type is None else getattr(portal.portal_categories.http_exchange_resource.payline.notification, notification_type),\n
  source_value=context,\n
)\n
# Notification ends in confirmed state, to be picked up by alarm (for security context switch)\n
http_exchange.confirm()\n
tag = script.id + \'-\' + http_exchange.getId()\n
http_exchange.reindexObject(activate_kw={\'tag\': tag})\n
portal.portal_alarms.handle_confirmed_http_exchanges.activate(after_tag=tag).activeSense()\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>object_id, notification_type, request, response=None</string> </value>
        </item>
        <item>
            <key> <string>_proxy_roles</string> </key>
            <value>
              <tuple>
                <string>Manager</string>
              </tuple>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>PaylineSOAPConnector_notifyFromPaylineActivity</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
