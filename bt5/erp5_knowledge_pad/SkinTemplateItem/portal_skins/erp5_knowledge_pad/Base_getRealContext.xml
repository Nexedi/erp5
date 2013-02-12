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
            <value> <string>real_context = context\n
if real_context.isTempObject():\n
  real_context = real_context.getParentValue()\n
\n
web_site_value = real_context.getWebSiteValue()\n
if web_site_value is not None and web_site_value.isTempObject():\n
  real_web_site_value = web_site_value.getParentValue()\n
  while real_web_site_value.isTempObject():\n
    real_web_site_value = real_web_site_value.getParentValue()\n
  web_site_url = web_site_value.getRelativeUrl()\n
  web_site_url_without_language = real_web_site_value.getRelativeUrl()\n
  real_context_url = real_context.getRelativeUrl()\n
  real_context_url_without_language = real_context_url.replace(web_site_url, web_site_url_without_language, 1)\n
  real_context = context.getPortalObject().restrictedTraverse(real_context_url_without_language)\n
\n
return real_context\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_getRealContext</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
