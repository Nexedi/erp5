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
            <value> <string># return site of the user and possible counter on wich user can be assigned\n
# XXX: this script should be named "Assignment_getPossibleSiteList", as it is not used anywhere else\n
destination_value = context.getDestinationValue()\n
if destination_value is None:\n
  # must have an organisation defined to limit site diplayed\n
  return [[\'\', \'\']]\n
\n
site_list = context.Delivery_getVaultItemList(\n
  user_site=0,\n
  vault_type=(\n
    \'site\',\n
    \'site/surface/banque_interne/guichet\',\n
    \'site/surface/gros_paiement/guichet\',\n
    \'site/surface/gros_versement/guichet\',\n
    \'site/surface/operations_diverses/guichet\',\n
  ),\n
  first_level=1,\n
  strict_membership=1,\n
  leaf_node=0,\n
  base_site=destination_value.getSite(),\n
)\n
return site_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Baobab_getPossibleUserAssignmentSiteList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
