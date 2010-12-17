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
            <value> <string>context.getPortalObject().portal_skins.changeSkin(\'ODS\')\n
request = container.REQUEST\n
request.set(\'portal_skin\', \'ODS\') # Some TALES expressions checks this\n
\n
if target_language:\n
  request[\'AcceptLanguage\'].set(target_language, 10)\n
\n
if print_mode == \'list_view\' or print_mode == \'list_view_separate_sheet\':\n
  if print_mode == \'list_view_separate_sheet\':\n
    request.set(\'sheet_per_report_section\', 1)\n
  return context.Folder_viewContentListAsODSReport()\n
\n
return getattr(context, form_id)()\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>form_id=\'\', target_language=\'\', print_mode=\'\', **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_viewAsODS</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
