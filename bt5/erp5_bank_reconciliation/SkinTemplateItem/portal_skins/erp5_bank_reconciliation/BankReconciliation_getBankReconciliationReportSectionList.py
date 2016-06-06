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
request = container.REQUEST\n
\n
if context.getSourcePayment():\n
  # As we are showing quantities and not asset prices, we use the precision\n
  # from this bank account currency.\n
  request.set(\'precision\',\n
      context.getQuantityPrecisionFromResource(\n
        context.getSourcePaymentValue().getPriceCurrency()))\n
\n
report_section_list = [\n
  ReportSection(form_id=\'BankReconciliation_view\',\n
                path=context.getPhysicalPath()),\n
]\n
\n
if request.get(\'show_reconcilied\', True):\n
  report_section_list.append(\n
    ReportSection(form_id=\'BankReconciliation_viewBankReconciliationReportSection\',\n
                  path=context.getPhysicalPath(),\n
                  selection_name="bank_reconciliation_report_selection",\n
                  selection_params={\'title\': \'Reconciled Transactions\',\n
                                    \'mode\': \'unreconcile\'}))\n
if request.get(\'show_non_reconcilied\', True):\n
  report_section_list.append(\n
    ReportSection(form_id=\'BankReconciliation_viewBankReconciliationReportSection\',\n
                  selection_name="bank_reconciliation_report_selection",\n
                  path=context.getPhysicalPath(),\n
                  selection_params={\'title\': \'Not Reconciled Transactions\',\n
                                    \'mode\': \'reconcile\'}))\n
\n
return report_section_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>BankReconciliation_getBankReconciliationReportSectionList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
