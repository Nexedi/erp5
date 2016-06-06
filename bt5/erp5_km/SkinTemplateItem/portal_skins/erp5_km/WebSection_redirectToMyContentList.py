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
  This script redirects to the page which displays all documents\n
  owned by the current user.\n
\n
  TODO:\n
    - make search_area value configurable\n
    - explain the role of \'search_section\' ?\n
"""\n
web_site = context.getWebSiteValue()\n
search_area_web_section_id = web_site.getLayoutProperty(\'search_area_web_section_id\',\n
                                                        default=None)\n
if search_area_web_section_id:\n
  search_section = web_site[search_area_web_section_id]\n
else:\n
  search_section = web_site\n
\n
search_section.Base_redirect(\n
                form_id=\'WebSection_viewMyContentList\', \n
                keep_items=dict(reset=1,\n
                                search_section_path=context.getRelativeUrl()))\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>WebSection_redirectToMyContentList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
