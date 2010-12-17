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
            <value> <string>from AccessControl import getSecurityManager\n
from Products.ERP5Type.Message import translateString\n
\n
request = context.REQUEST\n
new_password = request.get("new_password")\n
former_password = request.get("current_password")\n
password_confirm = request.get("password_confirm")\n
\n
user = getSecurityManager().getUser()\n
persons = context.acl_users.erp5_users.getUserByLogin(user)\n
person = persons[0]\n
\n
if not person.checkPassword(former_password):\n
  msg = translateString("Current password is wrong.")\n
elif new_password != password_confirm:\n
  msg = translateString("Confirmation failed, passwords are not equals.")\n
  return context.Base_redirect(form_id=\'EGov_viewChangePasswordForm\', keep_items = {\'portal_status_message\' : msg})\n
else:\n
  msg = translateString("Password changed.")\n
  person.setPassword(new_password)\n
\n
# clear erp5_content_short cache (see _authenticateCredentials in Products.ERP5Security.ERP5UserManager)\n
context.portal_caches.clearCache((\'erp5_content_short\',))\n
return context.WebSite_logout()\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>form_id=\'view\', **kw</string> </value>
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
            <value> <string>EGov_setNewPassword</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
