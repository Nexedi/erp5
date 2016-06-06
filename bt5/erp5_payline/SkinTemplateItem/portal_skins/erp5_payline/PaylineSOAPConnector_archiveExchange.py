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
Called right after a Payline call is made, before response is returned to caller.\n
\n
Archive exchange\'s raw data in system_event_module as an HTTP Exchange document.\n
"""\n
# TODO: remove manaer proxy role\n
portal = context.getPortalObject()\n
\n
def getdoc(document, identifier):\n
  # For consistency with how suds looks functions up.\n
  if identifier is None:\n
    if len(document) > 1:\n
      raise ValueError(\n
        \'Ambiguous document lookup: %r has more than one child\' % (\n
          document.getPath(),\n
        )\n
      )\n
    return document.values()[0]\n
  return getattr(document, identifier)\n
\n
exchange = portal.system_event_module.newContent(\n
  portal_type=\'HTTP Exchange\',\n
  request=raw_request, # XXX: this is not HTTP, but a SOAP message\n
  response=raw_response, # XXX: this is not HTTP, but a SOAP message\n
  # Note: it is important to use an ObjectManager method to retrieve final\n
  # category (get, __getattr__, __getitem__), as their name may clash with\n
  # method names (__getattr__) or properties (getProperty, __getattr__).\n
  # So "get" it is.\n
  resource_value=getdoc(\n
    getdoc(\n
      portal.portal_categories.http_exchange_resource.payline.query,\n
      service,\n
    ),\n
    port,\n
  ).get(name),\n
  follow_up_value=archive_kw[\'follow_up_value\'],\n
)\n
exchange.confirm()\n
# This is a call we initiated, value returned is sufficient to finalise this exchange.\n
exchange.acknowledge()\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>service, port, name, raw_request, raw_response, archive_kw</string> </value>
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
            <value> <string>PaylineSOAPConnector_archiveExchange</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
