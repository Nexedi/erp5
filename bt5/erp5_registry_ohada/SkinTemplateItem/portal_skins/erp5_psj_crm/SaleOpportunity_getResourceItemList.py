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
This script returns the list of items based on the preferred\n
resources for events. It is intended to be used\n
by ListField instances.\n
"""\n
\n
from Products.ERP5Type.Cache import CachingMethod\n
\n
def getResourceItemList():\n
  result = []\n
  url_list = context.portal_preferences.getPreferredSaleOpportunityResourceList()\n
  for url in url_list:\n
    resource_value = context.getPortalObject().restrictedTraverse(url)\n
    result.append((resource_value.getTranslatedTitle(), resource_value.getRelativeUrl()))\n
  return result\n
\n
getResourceItemList = CachingMethod(getResourceItemList, \n
      id=(script.id, context.Localizer.get_selected_language()), \n
      cache_factory=\'erp5_ui_long\')\n
                                 \n
return getResourceItemList()\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>SaleOpportunity_getResourceItemList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
