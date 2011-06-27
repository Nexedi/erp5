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
            <value> <string>"""Inspired by Event_getResourceItemList\n
Use Auditor proxy role to let anonymous users accessing resources.\n
"""\n
\n
from Products.ERP5Type.Cache import CachingMethod\n
portal = context.getPortalObject()\n
\n
sql_kw = {\'portal_type\': portal.getPortalResourceTypeList(),\n
          \'use_uid\': portal.portal_categories.getCategoryUid(portal.portal_preferences.getPreferredEventUse(), base_category=\'use\'),\n
          \'validation_state\': \'validated\',\n
          \'sort_on\': \'title\'}\n
\n
def getResourceItemList():\n
  return [(\'\', \'\')] + [(result.getTitle(), result.getRelativeUrl()) for result in portal.portal_catalog(**sql_kw)]\n
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
            <key> <string>_proxy_roles</string> </key>
            <value>
              <tuple>
                <string>Auditor</string>
              </tuple>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>WebSection_getEventResourceItemList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
