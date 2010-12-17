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
            <value> <string>section_value = context.getSourceSectionValue()\n
\n
if section_value is None or \\\n
   section_value.getProperty(\'price_currency\', None) is None:\n
  # If no section defined, no way to convert currencies\n
  return 0\n
\n
transaction_currency = context.getResource()\n
if transaction_currency is not None and\\\n
   transaction_currency != section_value.getProperty(\'price_currency\', None):\n
  return 1\n
\n
for line in context.getMovementList(\n
   portal_type=context.getPortalAccountingMovementTypeList()):\n
  if ((line.getSourceCredit() !=\n
       line.getSourceInventoriatedTotalAssetCredit()) or (\n
       line.getSourceDebit() !=\n
       line.getSourceInventoriatedTotalAssetDebit())):\n
   return 1\n
\n
return 0\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>AccountingTransaction_isSourceCurrencyConvertible</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
