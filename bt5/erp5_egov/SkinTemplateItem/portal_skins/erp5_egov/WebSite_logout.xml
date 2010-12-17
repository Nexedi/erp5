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
            <value> <string>"""\n
  Default logout handler, overwritten to give website specific portal status message.\n
"""\n
portal = context.getPortalObject()\n
N_ = portal.Base_translateString\n
website = context.getWebSiteValue()\n
form_id=\'EGov_viewLoginForm\'\n
\n
REQUEST = context.REQUEST\n
if REQUEST.has_key(\'portal_skin\'):\n
   context.portal_skins.clearSkinCookie()\n
REQUEST.RESPONSE.expireCookie(\'__ac\', path=\'/\')\n
msg = N_(\'You have been logged out. Thank you for using this website.\')\n
return website.Base_redirect(form_id, keep_items = {\'portal_status_message\' : msg},\n
                             editable_mode=editable_mode, **kw)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>dialog_id=None, editable_mode=0, **kw</string> </value>
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
            <value> <string>WebSite_logout</string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>Logout handler</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
