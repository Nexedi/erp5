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
            <value> <string>return (\n
  (\'Movement_getNodeGapId\', \'Account Code\'),\n
  (\'node_translated_title\', \'Account Name\'),\n
  (\'section_title\', \'Section\'),\n
  (\'mirror_section_title\', \'Third Party\'),\n
  (\'date\', \'Operation Date\'),\n
  (\'modification_date\', \'Modification Date\'),\n
  (\'Movement_getSpecificReference\', \'Transaction Reference\'),\n
  (\'Movement_getExplanationTranslatedPortalType\', \'Type\'),\n
  (\'Movement_getExplanationTitle\', \'Title\'),\n
  (\'Movement_getExplanationReference\', \'Document Reference\'),\n
) + context.accounting_module.AccountModule_getAnalyticColumnList() + (\n
  (\'debit_price\', \'Debit\'),\n
  (\'credit_price\', \'Credit\'),\n
  (\'total_price\', \'Balance\'),\n
  (\'Movement_getSectionPriceCurrency\', \'Accounting Currency\'),\n
  \n
  (\'debit\', \'Transaction Currency Debit\'),\n
  (\'credit\', \'Transaction Currency Credit\'),\n
  (\'total_quantity\', \'Transaction Currency Balance\'),\n
  (\'resource_reference\', \'Transaction Currency\'),\n
  \n
  (\'Movement_getPaymentTitle\', \'Section Bank Account\',),\n
  (\'payment_mode_translated_title\', \'Payment Mode\',),\n
  \n
  (\'grouping_reference\', \'Grouping Reference\'),\n
  (\'grouping_date\', \'Grouping Date\'),\n
  (\'getTranslatedSimulationStateTitle\', \'State\'),\n
)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>AccountModule_getGeneralLedgerColumnItemList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
