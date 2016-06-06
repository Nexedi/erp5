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
from Products.ERP5Form.Report import ReportSection\n
portal = context.getPortalObject()\n
  \n
request = container.REQUEST\n
section_category = request[\'section_category\']\n
section_category_strict = request[\'section_category_strict\']\n
simulation_state = request[\'simulation_state\']\n
account_type = request[\'account_type\']\n
period_list = [int(period) for period in request[\'period_list\']]\n
at_date = (request.get("at_date") or DateTime()).latestTime()\n
detailed = request[\'detailed\']\n
\n
selection_columns = [(\'mirror_section_title\', \'Third Party\'), ]\n
if detailed:\n
  selection_columns.extend([\n
                     (\'explanation_title\', \'Title\'),\n
                     (\'gap_id\', \'Account Number\'),\n
                     (\'reference\', \'Invoice Number\'),\n
                     (\'specific_reference\', \'Transaction Reference\'),\n
                     (\'date\', \'Operation Date\'),\n
                     (\'portal_type\', \'Transaction Type\'), ])\n
selection_columns.extend([\n
                     (\'total_price\', \'Balance\'),\n
                     (\'period_future\', \'Future\'), ] )\n
\n
editable_columns = [(\'date\', \'date\'), (\'period_future\', \'period_future\'),\n
                    (\'total_price\', \'total_price\')]\n
\n
previous_period = 0\n
for idx, period in enumerate(period_list):\n
  if idx != 0:\n
    previous_period = period_list[idx - 1]\n
  selection_columns.append((\'period_%s\' % idx, unicode(translateString(\n
      \'Period ${period_number} (from ${from} to ${to} days)\',\n
      mapping={\'period_number\': 1 + idx,\n
               \'from\': previous_period,\n
               \'to\': period} ))))\n
  editable_columns.append((\'period_%s\' % idx, \'\'))\n
\n
selection_columns.append((\'period_%s\' % (idx + 1),\n
  unicode(translateString(\'Older (more than ${day_count} days)\',\n
   mapping={\'day_count\': period_list[-1]}))))\n
editable_columns.append((\'period_%s\' % (idx + 1), \'\'))\n
\n
\n
return [ReportSection(form_id=(detailed and \n
                               \'AccountingTransactionModule_viewDetailedAgedBalanceReportSection\' or\n
                               \'AccountingTransactionModule_viewSummaryAgedBalanceReportSection\'),\n
                      path=context.getPhysicalPath(),\n
                      selection_columns=selection_columns,\n
                      selection_name=(detailed and\n
                                      \'accounting_transaction_module_detailed_aged_balance_selection\' or\n
                                      \'accounting_transaction_module_summary_aged_balance_selection\'),\n
                      selection_params=dict(section_category=section_category,\n
                                            section_category_strict=section_category_strict,\n
                                            account_type=account_type,\n
                                            editable_columns=editable_columns,\n
                                            simulation_state=simulation_state,\n
                                            period_list=period_list,\n
                                            at_date=at_date))]\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>AccountingTransactionModule_getAgedBalanceReportSectionList</string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
