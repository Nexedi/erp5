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
            <value> <string>Base_translateString = context.getPortalObject().Base_translateString\n
allowed_type_list = context.getVisibleAllowedContentTypeList()\n
\n
if not allowed_type_list:\n
  return context.ERP5Site_redirect(context.absolute_url(), keep_items={\'portal_status_message\': Base_translateString("You are not allowed to add new content in this context.")})\n
\n
# newContent will add the first allowed type when we do not specify portal_type=\n
new_object = context.newContent(portal_type=allowed_type_list[0])\n
\n
return context.ERP5Site_redirect(new_object.absolute_url(),\n
                                 keep_items={\'portal_status_message\': Base_translateString("Object created."),\n
                                             \'editable_mode\': 1})\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Folder_create</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
