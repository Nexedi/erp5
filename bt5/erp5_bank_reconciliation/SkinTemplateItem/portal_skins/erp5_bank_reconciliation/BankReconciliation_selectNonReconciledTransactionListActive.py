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
            <value> <string>from Products.ERP5Type.Message import translateString\n
\n
context.getPortalObject().setPlacelessDefaultReindexParameters(activate_kw=dict(tag=tag))\n
\n
# XXX maybe we want to distribute this more.\n
# At the moment we cannot use searchAndActivate from Inventory API query\n
for line in context.BankReconciliation_getAccountingTransactionLineList():\n
  line.AccountingTransactionLine_setBankReconciliation(context, \n
      message=translateString("Select Non Reconciled Transactions"))\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>tag</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>BankReconciliation_selectNonReconciledTransactionListActive</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
