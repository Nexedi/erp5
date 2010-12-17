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
  Create basic KM account using ERP5 credentials system.\n
"""\n
from Products.Formulator.Errors import ValidationError, FormValidationError\n
portal = context.getPortalObject()\n
translateString = context.Base_translateString\n
website = context.getWebSiteValue()\n
\n
# Call Base_edit\n
result, result_type = context.Base_edit(form_id, silent_mode=1, field_prefix=\'your_\')\n
\n
# Return if not appropriate\n
if result_type != \'edit\':\n
  return result\n
kw, encapsulated_editor_list = result\n
\n
# XXX: hard coded due to erp5_credentials requirement\n
kw[\'role_list\'] = [\'internal\']\n
kw.pop(\'password_confirm\', None)\n
default_email_text = reference = kw.pop(\'default_email_text\')\n
context.ERP5Site_newCredentialRequest(reference=reference, \\\n
                                      default_email_text=default_email_text, **kw)\n
\n
msg = translateString("Your account was successfully created. You will be notified by email how to proceed.")\n
return website.Base_redirect(form_id, keep_items=dict(portal_status_message=msg,\n
                             editable_mode=0))\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>form_id</string> </value>
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
            <value> <string>WebSite_createWebSiteAccount</string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>Create Web Site User Account</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
