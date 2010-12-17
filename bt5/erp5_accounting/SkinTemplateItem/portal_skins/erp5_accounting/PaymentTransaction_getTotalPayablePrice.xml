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
            <value> <string>if brain is not None:\n
  transaction = brain.getObject()\n
else:\n
  transaction = context\n
    \n
def getTotalPrice(transaction_path):\n
  is_source = transaction.AccountingTransaction_isSourceView()\n
  total_price = 0\n
  for mvt in transaction.getMovementList(\n
         portal_type=context.getPortalAccountingMovementTypeList()):\n
    if is_source:\n
      node = mvt.getSourceValue()\n
      if node is not None and node.isMemberOf(\'account_type/asset/cash\'):\n
        total_price -= mvt.getSourceInventoriatedTotalAssetPrice() or 0\n
    else:\n
      node = mvt.getDestinationValue()\n
      if node is not None and  node.isMemberOf(\'account_type/asset/cash\'):\n
        total_price -= mvt.getDestinationInventoriatedTotalAssetPrice() or 0\n
  return total_price\n
\n
return getTotalPrice(transaction.getPath())\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>brain=None, selection=None, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>PaymentTransaction_getTotalPayablePrice</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
