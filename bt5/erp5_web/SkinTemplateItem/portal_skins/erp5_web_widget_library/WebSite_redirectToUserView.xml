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
  Search for the current user and redirect to the default view.\n
  This code is a good example to show how to redirect to\n
  the appropriate object in the context of a Web Site.\n
\n
  TODO:\n
  - Implement a wholistic view on user information\n
    (documents, membership, etc.)\n
"""\n
translateString = context.Base_translateString\n
\n
# Return if anonymous\n
if context.portal_membership.isAnonymousUser():\n
  msg = translateString("Anonymous users do not have a personal profile.")\n
  return context.Base_redirect(form_id="view", \n
                               keep_items={\'portal_status_message\':msg})\n
\n
# Call generic erp5_base method to find user value  \n
person_object = context.ERP5Site_getAuthenticatedMemberPersonValue(user)\n
\n
# Return if no such user\n
if person_object is None:\n
  msg = translateString("This user has no personal profile.")\n
  return context.Base_redirect(form_id="view", keep_items={\'portal_status_message\':msg})\n
\n
return person_object.Base_redirect(form_id="view",\n
                                   keep_items={\'editable_mode\':editable_mode})\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>user=None, form_id="view", editable_mode=0</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>WebSite_redirectToUserView</string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>Redirect to user view</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
