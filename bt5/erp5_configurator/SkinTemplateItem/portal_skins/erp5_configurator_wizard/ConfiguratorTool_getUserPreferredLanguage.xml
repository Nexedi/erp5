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
            <value> <string>REQUEST = context.REQUEST\n
\n
# First, find a cookie already made before.\n
COOKIE_NAME = \'configurator_user_preferred_language\'\n
user_preferred_language = REQUEST.cookies.get(COOKIE_NAME, None)\n
if user_preferred_language is not None:\n
  # user already have explicitly selected language\n
  return user_preferred_language\n
\n
# use language from browser\'s settings\n
configuration_language_list = []\n
for item in context.ConfiguratorTool_getConfigurationLanguageList():\n
  configuration_language_list.append(item[1])\n
http_accept_language = REQUEST.get(\'HTTP_ACCEPT_LANGUAGE\', \'en\')\n
\n
for language_set in http_accept_language.split(\',\'):\n
  language_tag = language_set.split(\';\')[0]\n
  language = language_tag.split(\'-\')[0]\n
  if language in configuration_language_list:\n
    return language\n
return \'en\'\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ConfiguratorTool_getUserPreferredLanguage</string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>Get user preferred language from browser</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
