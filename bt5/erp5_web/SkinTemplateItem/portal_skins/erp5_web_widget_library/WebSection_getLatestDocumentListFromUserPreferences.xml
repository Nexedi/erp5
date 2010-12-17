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
            <value> <string>web_section = None\n
box_relative_url = context.REQUEST.get(\'box_relative_url\', None)\n
if box_relative_url is not None:\n
  box = context.restrictedTraverse(box_relative_url)\n
  preferences = box.KnowledgeBox_getDefaultPreferencesDict()\n
  # check if in preferences we explicitly define the section we want \n
  if preferences.get(\'preferred_section_relative_url\', None) is not None:\n
    web_section_relative_url = preferences[\'preferred_section_relative_url\']\n
    web_section = context.restrictedTraverse(web_section_relative_url, None)\n
  elif context.REQUEST.get(\'current_web_section\', None) is not None:\n
    web_section =  context.REQUEST[\'current_web_section\']\n
  # if current context is a Web Section or Web Site ..\n
  if web_section is None and not getattr(context, \'isDocument\', 1):\n
    web_section = context\n
\n
# fall back to site\n
if web_section is None:\n
  web_section = context.getWebSiteValue()\n
return web_section.getDocumentValueList(**kw)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>**kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>WebSection_getLatestDocumentListFromUserPreferences</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
