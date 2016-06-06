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
            <value> <string>"""Returns the item list of possible fundings to use on accounting lines.\n
"""\n
portal = context.getPortalObject()\n
\n
funding_base_category = portal.portal_preferences.getPreferredAccountingTransactionLineFundingBaseCategory()\n
if funding_base_category:\n
  return getattr(portal.portal_categories.restrictedTraverse(funding_base_category),\n
                  portal.portal_preferences.getPreference(\'preferred_category_child_item_list_method_id\',\n
                        \'getCategoryChildCompactLogicalPathItemList\'))(\n
                              local_sort_id=(\'int_index\', \'translated_title\'),\n
                              checked_permission=\'View\',\n
                              base=True) \n
\n
return ()\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>source=True</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>AccountingTransactionLine_getFundingItemList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
