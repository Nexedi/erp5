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
  A core method that will return default image conversion arguments as a dict.\n
"""\n
portal = context.getPortalObject()\n
portal_preferences = portal.portal_preferences\n
image_argument_dict = {\'format\': portal_preferences.getPreferredImageFormat(),\n
                       \'quality\': portal_preferences.getPreferredImageQuality()}\n
\n
pre_converted_only = portal_preferences.getPreferredPreConvertedOnly()\n
if pre_converted_only:\n
  # only add if it\'s True as conversion machine assume that if it is missing\n
  # then conversion should happen "on the fly"\n
  image_argument_dict[\'pre_converted_only\'] = pre_converted_only\n
\n
if context.getPortalType() in (\'PDF\',):\n
  # PDF support frames\n
  image_argument_dict[\'frame\'] = 0\n
return image_argument_dict\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_getImageArgumentDict</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
