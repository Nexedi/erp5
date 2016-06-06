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
            <value> <string># Proxy role Auditor to be able to check document existence in system_event_module\n
\n
# Note on flood: we mitigate flood effect by generating document id based on\n
# notification-received data. This means that it is not too complex to get ERP5\n
# to create many documents if one is able to call notification URL.\n
# Also, unknown values (notification type, type, ...) are accepted. The should\n
# probably be rejected instead, once we are confident enough that we do not loose\n
# important notifications.\n
\n
form_dict = REQUEST.form\n
context.log(repr(form_dict))\n
try:\n
  notification_type = form_dict[\'notificationType\'].upper()\n
  object_id = \'payline.\' + notification_type + \'_\' + form_dict[{\n
    \'WEBTRS\': \'token\',\n
    \'WEBWALLET\': \'token\',\n
    \'WALLET\': \'walletId\',\n
  }[notification_type]]\n
except KeyError:\n
  create_activity = True\n
  object_id = None\n
  notification_type = None\n
else:\n
  form_type = form_dict.get(\'type\')\n
  if notification_type == \'WALLET\' and form_type:\n
    object_id += \'_\' + form_type.lower()\n
  create_activity = object_id not in context.getPortalObject().system_event_module\n
if create_activity:\n
  context.activate(\n
    activity=\'SQLQueue\',\n
  ).PaylineSOAPConnector_notifyFromPaylineActivity(\n
    object_id,\n
    # Provide notificationType separately, so callee does not have to parse request just to store it\n
    notification_type=notification_type,\n
    request=context.Base_renderRequestForHTTPExchangeStorage(REQUEST),\n
  )\n
# Return a non-empty value, so an HTTP "200 OK" status is generated,\n
# and not a "204 No Content" as it is interpreted as an error by Payline.\n
return \' \'\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>REQUEST</string> </value>
        </item>
        <item>
            <key> <string>_proxy_roles</string> </key>
            <value>
              <tuple>
                <string>Auditor</string>
              </tuple>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>PaylineSOAPConnector_notifyFromPayline</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
