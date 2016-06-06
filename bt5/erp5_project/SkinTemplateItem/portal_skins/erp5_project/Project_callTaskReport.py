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
            <value> <string>use_ods_style = 1\n
if getattr(context.portal_skins, \'erp5_ods_style\', None) is None:\n
  use_ods_style = 0\n
\n
request = container.REQUEST\n
if use_ods_style:\n
  context.getPortalObject().portal_skins.changeSkin(\'ODS\')\n
  request.set(\'portal_skin\', \'ODS\') # Some TALES expressions checks this\n
  request.set(\'reset\', 1) # Some TALES expressions checks this\n
\n
if target_language:\n
  request[\'AcceptLanguage\'].set(target_language, 10)\n
\n
form_report = getattr(context, print_mode)\n
return form_report(**kw)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>form_id=\'\', target_language=\'\', print_mode=\'\', **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Project_callTaskReport</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
