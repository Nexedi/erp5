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
            <value> <string># return counter list for a given site and a given vault type\n
\n
if vault_type is None:\n
  vault_type = (\'site/surface/banque_interne\', \'site/surface/gros_paiement\', \'site/surface/gros_versement\', \'site/surface/operations_diverses\')\n
\n
\n
vault_list = context.Delivery_getVaultItemList(vault_type=vault_type, strict_membership = 0, leaf_node=0, user_site=1, with_base=0)\n
counter_dict = {}\n
for vault in vault_list:\n
  if len(vault[0].split("/")) == 4:\n
    counter = \'/\'.join(vault[0].split("/")[:3])\n
    if not counter_dict.has_key(counter):\n
      if not \'siege\' in vault[1]:\n
        counter_dict[counter] = \'/\'.join(vault[1].split("/")[:6])\n
      else:\n
        counter_dict[counter] = \'/\'.join(vault[1].split("/")[:5])\n
             \n
\n
list = counter_dict.items()\n
list.sort()\n
return list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>vault_type=None, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Baobab_getCounterList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
