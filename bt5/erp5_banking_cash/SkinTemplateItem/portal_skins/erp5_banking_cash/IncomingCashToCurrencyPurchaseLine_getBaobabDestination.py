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
            <value> <string>currency = context.getResourceTitle()\n
encaisse_devise = "/encaisse_des_devises/%s/sortante" %(context.getParentValue().getResourceTitle(\'\').lower().replace(" ", "_"))\n
counter_site = context.getSource()\n
destination = counter_site + encaisse_devise\n
return destination\n
\n
\n
# OLD METHOD user logged in\n
#user_id = context.portal_membership.getAuthenticatedMember().getUserName()\n
\n
# NEW METHOD must use owner to know site letter\n
old_group_list = context.get_local_roles()\n
for group, role_list in old_group_list:\n
  if \'Owner\' in role_list:\n
    user_id = group\n
\n
\n
site_list = context.Baobab_getUserAssignedSiteList(user_id=user_id)\n
context.log(\'site_list\',site_list)\n
destination = None\n
for site in site_list:\n
  site_value = context.portal_categories.getCategoryValue(site)\n
  context.log(\'site_value\',site_value)\n
  if site_value.getVaultType().endswith(\'guichet\') and ((\'banque_interne\' in site) or (\'operations_diverses\' in site)):\n
    destination = site + encaisse_devise\n
    break\n
context.log(\'la_bonne_destination\',destination)\n
return destination\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>*args, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>IncomingCashToCurrencyPurchaseLine_getBaobabDestination</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
