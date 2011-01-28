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
            <value> <string encoding="cdata"><![CDATA[

from Products.ERP5Form.Report import ReportSection\n
request = container.REQUEST\n
Base_translateString = container.Base_translateString\n
\n
portal_type = request[\'portal_type\']\n
simulation_state = request[\'simulation_state\']\n
hide_analytic = request[\'hide_analytic\']\n
project = request.get(\'project\', None)\n
at_date = request[\'at_date\'].latestTime()\n
from_date = request.get(\'from_date\') or at_date.earliestTime()\n
section_uid = context.Base_getSectionUidListForSectionCategory(\n
                                     request[\'section_category\'],\n
                                     request[\'section_category_strict\'])\n
payment_mode = request.get(\'payment_mode\')\n
payment = request.get(\'payment\')\n
gap_root = request.get(\'gap_root\')\n
\n
# Also get the currency, to know the precision\n
currency = context.Base_getCurrencyForSection(request[\'section_category\'])\n
precision = context.account_module.getQuantityPrecisionFromResource(currency)\n
# we set the precision in request, for formatting on editable fields\n
request.set(\'precision\', precision)\n
\n
selection_params = dict(portal_type=portal_type,\n
                        section_uid=section_uid,\n
                        precision=precision,\n
                        simulation_state=simulation_state,\n
                        at_date=at_date,\n
                        from_date=from_date,\n
                        payment_mode=payment_mode,\n
                        gap_root=gap_root,\n
                        payment=payment)\n
\n
if project:\n
  if project == \'None\':\n
    selection_params[\'project_uid\'] = project\n
  else:\n
    selection_params[\'project_uid\'] = \\\n
       context.getPortalObject().restrictedTraverse(project).getUid()\n
\n
analytic_column_list = ()\n
if hide_analytic:\n
  selection_params[\'group_by\'] = ( \'explanation_uid\',\n
                                   \'mirror_section_uid\',\n
                                   \'payment_uid\',\n
                                   \'node_uid\' )\n
else:\n
  analytic_column_list = context.accounting_module.AccountModule_getAnalyticColumnList()\n
  selection_params[\'analytic_column_list\'] = analytic_column_list\n
\n
selection_columns = (\n
    (\'specific_reference\', \'Transaction Reference\'),\n
    (\'date\', \'Date\'),\n
    (\'title\', \'Accounting Transaction Title\'),\n
    (\'parent_reference\', \'Document Reference\'),)\n
if len(portal_type) > 1:\n
  selection_columns += (\n
    (\'portal_type\', \'Journal Type\'), )\n
selection_columns += analytic_column_list + (\n
    (\'node_title\', \'Account\'),\n
    (\'mirror_section_title\', \'Third Party\'),\n
    (\'debit\', \'Debit\'),\n
    (\'credit\', \'Credit\'))\n
\n
return [ReportSection(\n
          path=context.getPhysicalPath(),\n
          title=Base_translateString(\'Transactions\'),\n
          selection_name=\'journal_selection\',\n
          form_id=\'AccountingTransactionModule_viewJournalSection\',\n
          selection_columns=selection_columns,\n
          selection_params=selection_params)]\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>AccountingTransactionModule_getJournalReportSectionList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
