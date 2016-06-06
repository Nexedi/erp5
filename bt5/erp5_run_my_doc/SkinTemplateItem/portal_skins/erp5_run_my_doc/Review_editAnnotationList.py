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

annotation_list = context.getAnnotation().split(\'\\n\');\n
user_name = context.getPortalObject().portal_membership.getAuthenticatedMember()\n
for uid in listbox_uid:\n
  i = int(uid)\n
  old_comment, locator, context_url, author, color = annotation_list[i][1:-1].split("},{");\n
  new_comment = context.REQUEST[\'field_listbox_title_\' + uid]\n
  #print(\'Old title: \' + old_comment + \' -> \' + new_comment)\n
  if old_comment != new_comment:\n
    author = user_name\n
    annotation_list[i] = "{" + str(new_comment) + "},{" + str(locator) + "},{" + str(context_url) + "},{" + str(author) + "},{" + str(color) + \'}\'\n
    annotation_list[i] = annotation_list[i]\n
\n
context.setAnnotation("\\n".join(annotation_list))\n
\n
translateString = context.Base_translateString\n
portal_status_message = translateString(\'Data updated.\')\n
context.Base_redirect(\'Review_viewAnnotationList\', keep_items = dict(portal_status_message=portal_status_message))\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>listbox_uid</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Review_editAnnotationList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
