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
  user_id = context.Base_getLastUserIdByTransition(workflow_id=\'check_payment_workflow\', transition_id=\'deliver_action\')\n
  if user_id is not None:\n
    site_list = context.Baobab_getUserAssignedSiteList(user_id=user_id)\n
    source = context.getSource()\n
    for site in site_list:\n
      site_value = context.portal_categories.getCategoryValue(site)\n
      if site_value.getVaultType().endswith(\'guichet\') and source in site:\n
        source_trade = site + \'/encaisse_des_billets_et_monnaies/sortante\'\n
        # Save it only once we are sure that the document will not change any more\n
        # and that we will not have many users trying to do deliver_action\n
        if context.getSourceTrade() != source_trade:\n
          context.setSourceTrade(source_trade)\n
return source_trade\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>**kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>CheckPayment_getBaobabSource</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
