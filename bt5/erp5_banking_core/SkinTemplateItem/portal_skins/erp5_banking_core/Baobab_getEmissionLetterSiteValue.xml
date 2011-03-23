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
            <value> <string># We will take the emission letter and find what is the right site\n
# for it and the return the result\n
\n
site_item_list = context.Delivery_getVaultItemList(vault_type=(\'site\',),user_site=0,\n
                                                  with_base=0,strict_membership=1,\n
                                                  leaf_node=0)\n
site_path_list = [x[1] for x in site_item_list if x[1]!=\'\' and \'principale\' in x[1]]\n
site_base_category = context.portal_categories.site\n
for site_path in site_path_list:\n
  site = site_base_category.restrictedTraverse(site_path)\n
  if site.getCodification()[:1].lower()==emission_letter:\n
    return site\n
return None\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>emission_letter=None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Baobab_getEmissionLetterSiteValue</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
