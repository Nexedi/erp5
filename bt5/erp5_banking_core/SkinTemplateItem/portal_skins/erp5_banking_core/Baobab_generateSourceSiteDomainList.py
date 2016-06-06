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
            <value> <string encoding="cdata"><![CDATA[

domain_list = []\n
i = 0\n
vault_list = context.Delivery_getVaultItemList(leaf_node=0, vault_type=\'site\')\n
\n
# get depth\n
depth = len(parent.getPath().split(\'/\')[3:])\n
\n
for vault in vault_list:\n
  if vault[0] != \'\':\n
    if len(vault[0].split(\'/\')) == depth:\n
      if depth > 1:\n
        path_length = len(vault[0].split(\'/\')) - 1\n
        parent_path = \'/\'.join(parent.getPath().split(\'/\')[-path_length:])\n
        if \'/\'.join(vault[0].split(\'/\')[:-1]) != parent_path:\n
          # only add those from parent\n
          continue\n
      domain = parent.generateTempDomain(id=vault[0].split(\'/\')[-1])\n
      domain.edit(title=vault[0].split(\'/\')[-1], membership_criterion_base_category=(\'source\',), membership_criterion_category=(\'source/%s\' %(vault[1]),), domain_generator_method_id=script.id)\n
      i+=1\n
      domain_list.append(domain)\n
\n
return domain_list\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>depth, parent, **kw</string> </value>
        </item>
        <item>
            <key> <string>_proxy_roles</string> </key>
            <value>
              <tuple>
                <string>Manager</string>
              </tuple>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Baobab_generateSourceSiteDomainList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
