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
            <value> <string>source_trade = context.getSourceTrade()\n
if source_trade is None or context.getSimulationState() != \'delivered\':\n
  destination = context.getDestination()\n
  if destination is None:\n
    return None\n
  user_id = context.Base_getLastUserIdByTransition(workflow_id=\'money_deposit_workflow\', transition_id=\'deliver_action\')\n
  if user_id is None:\n
    return None\n
  site_list = context.Baobab_getUserAssignedSiteList(user_id=user_id)\n
  for site in site_list:\n
    if context.portal_categories.getCategoryValue(site).getVaultType().endswith(\'guichet\') and destination in site:\n
      source_trade = site + \'/encaisse_des_billets_et_monnaies/entrante\'\n
      if context.getSourceTrade() != source_trade:\n
        context.setSourceTrade(source_trade)\n
      return source_trade\n
  from Products.ERP5Type.Message import Message\n
  message = Message(domain="ui", message="The owner is not assigned to the right vault.")\n
  raise ValueError,message\n
else:\n
  return source_trade\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>*args, **kw</string> </value>
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
            <value> <string>MoneyDeposit_getBaobabDestination</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
