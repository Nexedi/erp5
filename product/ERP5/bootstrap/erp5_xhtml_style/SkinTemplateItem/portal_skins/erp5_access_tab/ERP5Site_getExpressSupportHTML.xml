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
            <value> <string>language = context.Localizer.get_selected_language()\n
\n
SUPPORT_ENABLED = \'support_enabled\'\n
SUPPORT_DISABLED = \'support_disabled\'\n
ADVERTISEMENT_ENABLED = \'advertisement_enabled\'\n
\n
if express_mode==SUPPORT_ENABLED:\n
  # For Express users.\n
  proxy_path = \'web_site_module/express_frame/WebSite_viewExpressCustomerSupportMenu\'\n
elif express_mode==SUPPORT_DISABLED:\n
  return \'\'\n
else:\n
  # Advertisement\n
  # XXXX FIX THIS URL!!!\n
  proxy_path = \'web_site_module/express_frame/WebSite_viewDummyAdvertisement\'\n
\n
\n
# XXX we need to think about https\n
traverse_subpath = proxy_path.split(\'/\')\n
context.REQUEST.set(\'traverse_subpath\', traverse_subpath)\n
return context.portal_wizard.proxy()\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>express_mode</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ERP5Site_getExpressSupportHTML</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
