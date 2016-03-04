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
            <value> <string>portal = context.getPortalObject()\n
updateRelatedCategory = portal.portal_categories.updateRelatedCategory\n
\n
new_category_list = []\n
object_category_list = context.getCategoriesList()\n
\n
new_category_name = kw[\'new_category_name\']\n
old_category_name = kw[\'old_category_name\']\n
\n
for category in object_category_list:\n
  new_category = updateRelatedCategory(category, old_category_name, new_category_name)\n
  new_category_list.append(new_category)\n
\n
if new_category_list != object_category_list:\n
  context.setCategoriesList(new_category_list)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>fixit=0, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_updateRelatedCategory</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
