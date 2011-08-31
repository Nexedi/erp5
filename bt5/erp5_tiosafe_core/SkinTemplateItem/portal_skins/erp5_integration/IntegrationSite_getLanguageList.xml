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
            <value> <string>from Products.ERP5Type.Cache import CachingMethod\n
\n
\n
def getLanguageList(site):\n
  language_list = [(\'\', \'\'),]\n
  # First check if there is a specific method\n
  if getattr(site, "IntegrationSite_getPluginLanguageList", None):\n
    language_list += [(l.title,l.id) for l in getattr(site, \'IntegrationSite_getPluginLanguageList\')()]\n
  else:\n
    # Otherwise use list from localizer\n
    language_list += [(x["name"], x["code"]) for x in site.Localizer.get_all_languages()]\n
  return language_list\n
\n
\n
getLanguageList = CachingMethod(getLanguageList, \\\n
                                id = \'IntegrationSite_getLanguageList\', \\\n
                                cache_factory = \'erp5_ui_long\')\n
\n
\n
return getLanguageList(context)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>IntegrationSite_getLanguageList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
