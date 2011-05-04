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
            <value> <string># When the parent document (Mutilated Banknote) is finished or delivered, the mutilated banknotes must not be put in the "caisse_coutante/billets_mutiles"\n
# In reality, they are moved to "caisse_courante/billets_mutiles" with "canceled" status.\n
# To do this, the "mutilated" from "caisse_courante/billets_mutiles" are destroyed from erp5 point of view and new ones with state "canceled" are added to "caisse_courante/encaisse_des_billets_et_monnaies".\n
# See ExchangedMutilatedBanknoteLine_getBaobabDestination (those lines are created at "planned" state).\n
\n
mutilated_banknote = context.getParentValue()\n
if mutilated_banknote.getSimulationState() == \'stopped\':\n
  return mutilated_banknote.getDestination()\n
return None\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>*args, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>IncomingMutilatedBanknoteLine_getBaobabDestination</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
