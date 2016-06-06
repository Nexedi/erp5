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
            <value> <string>from Products.PythonScripts.standard import Object\n
total_source_debit = 0\n
total_source_credit = 0\n
total_destination_debit = 0\n
total_destination_credit = 0\n
total_source_asset_debit = 0\n
total_source_asset_credit = 0\n
total_destination_asset_debit = 0\n
total_destination_asset_credit = 0\n
\n
source_section = context.getSourceSection()\n
destination_section = context.getDestinationSection()\n
for line in context.objectValues(\n
        portal_type = context.getPortalAccountingMovementTypeList()) :\n
  if line.getSource() and line.getSourceSection() == source_section:\n
    total_source_debit += line.getSourceDebit()\n
    total_source_asset_debit += line.getSourceInventoriatedTotalAssetDebit()\n
    total_source_credit += line.getSourceCredit()\n
    total_source_asset_credit += line.getSourceInventoriatedTotalAssetCredit()\n
  if line.getDestination()\\\n
      and line.getDestinationSection() == destination_section:\n
    total_destination_debit += line.getDestinationDebit()\n
    total_destination_asset_debit += line.getDestinationInventoriatedTotalAssetDebit()\n
    total_destination_credit += line.getDestinationCredit()\n
    total_destination_asset_credit += line.getDestinationInventoriatedTotalAssetCredit()\n
\n
return [Object(\n
          source_debit=total_source_debit,\n
          source_credit=total_source_credit,\n
          destination_debit=total_destination_debit,\n
          destination_credit=total_destination_credit,\n
          source_asset_debit=total_source_asset_debit,\n
          source_asset_credit=total_source_asset_credit,\n
          destination_asset_debit=total_destination_asset_debit,\n
          destination_asset_credit=total_destination_asset_credit,)]\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>**kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>InternalInvoiceTransaction_statInternalTransactionLineList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
