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
            <value> <string>template_tool = context.portal_templates\n
\n
matching = []\n
\n
for o in template_tool.contentValues(portal_type=\'Business Template\'):\n
  if portal_type in o.getTemplatePortalTypeIdList():\n
    matching.append(o.getUid())\n
  else:\n
    allowed_content_type_list = o.getTemplatePortalTypeAllowedContentTypeList()\n
    allowed_content_type_list = map(lambda x: x and x.split(\'|\')[1].strip(), allowed_content_type_list)\n
    if portal_type in allowed_content_type_list:\n
      matching.append(o.getUid())\n
\n
for o in template_tool.contentValues(portal_type=\'Business Template\'):\n
  if portal_type in o.getTemplatePortalTypeIdList():\n
    matching.append(o.getUid())\n
\n
return template_tool.Base_redirect(\'TemplateTool_viewBusinessTemplateList\', keep_items=dict(uid=matching, reset=1))\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>portal_type</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>TemplateTool_searchPortalType</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
