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
            <value> <string>attachement_method = getattr(context, \'PDFDocument_getApplicationIncomeDict\')\n
attachement_type_dict = attachement_method()\n
\n
type_list = map(lambda x: x.getId(), context.allowedContentTypes())\n
viewable_content_list = context.contentValues(portal_type=type_list, checked_permission=\'View\')\n
\n
content_title_list = []\n
for content in viewable_content_list:\n
  content_title_list.append(content.getTitle())\n
\n
requirement = 0\n
\n
for title in attachement_type_dict.keys():\n
  if attachement_type_dict[title][\'requirement\'] == \'Required\':\n
    if title not in content_title_list:\n
      requirement = requirement + 1\n
\n
return requirement\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>PDFDocument_getRequirementCount</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
