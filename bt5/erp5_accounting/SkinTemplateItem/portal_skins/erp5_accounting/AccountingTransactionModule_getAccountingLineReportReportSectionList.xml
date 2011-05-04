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
            <value> <string>from Products.ERP5Form.Report import ReportSection\n
portal = context.getPortalObject()\n
request = container.REQUEST\n
\n
selection_columns = (\n
  (\'title\', \'Title\',),\n
  (\'int_index\', \'Int Index\',),\n
  (\'parent_description\', \'Description\',),\n
  (\'parent_comment\', \'Comment\',),\n
  (\'parent_reference\', \'Invoice Number\',),\n
  (\'specific_reference\', \'Transaction Reference\',),\n
  (\'node_reference\', \'Account Code\',),\n
  (\'node_title\', \'Account Name\',),\n
  (\'node_account_type_title\', \'Account Type\',),\n
  (\'node_financial_section_title\', \'Financial Section\',),\n
  (\'section_title\', \'Section\',),\n
  (\'payment_title\', \'Section Bank Account\',),\n
  (\'payment_mode\', \'Payment Mode\',),\n
  (\'mirror_section_title\', \'Third Party\',),\n
  (\'mirror_payment_title\', \'Third Party Bank Account\',),\n
  (\'mirror_section_region_title\', \'Third Party Region\',),\n
  (\'function_reference\',\n
      \'%s Reference\' % context.AccountingTransactionLine_getFunctionBaseCategoryTitle()), \n
  (\'function_title\',\n
      context.AccountingTransactionLine_getFunctionBaseCategoryTitle()),\n
  (\'funding_reference\', \'Funding Reference\',),\n
  (\'funding_title\', \'Funding\',),\n
  (\'project_title\', \'Project\',),\n
  (\'product_line\', \'Product Line\'),\n
  (\'string_index\', \'String Index\'),\n
  (\'date\', \'Operation Date\'),\n
  (\'debit_price\', \'Converted Debit\'),\n
  (\'credit_price\', \'Converted Credit\'),\n
  (\'price\', \'Converted Net\'),\n
  (\'currency\', \'Accounting Currency\'),\n
  (\'debit\', \'Debit\'),\n
  (\'credit\', \'Credit\'),\n
  (\'quantity\', \'Net\'),\n
  (\'resource\', \'Transaction Currency\'),\n
  (\'translated_portal_type\', \'Line Type\'),\n
  (\'parent_translated_portal_type\', \'Transaction Type\'),\n
  (\'translated_simulation_state_title\', \'State\'),)\n
\n
\n
return [ReportSection(form_id=\'AccountingTransactionModule_viewAccountingLineReportReportSection\',\n
                      selection_columns=selection_columns,\n
                      path=context.getPhysicalPath())]\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>AccountingTransactionModule_getAccountingLineReportReportSectionList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
