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
            <value> <string>"""\n
  Trial balance.\n
"""\n
from Products.ERP5Form.Report import ReportSection\n
\n
request = context.REQUEST\n
portal  = context.portal_url.getPortalObject()\n
\n
at_date              = request[\'at_date\']\n
section_category     = request[\'transaction_section_category\']\n
simulation_state     = request[\'transaction_simulation_state\']\n
gap_root             = request[\'gap_root\']\n
gap_list             = request.get(\'gap_list\'            , [])\n
from_date            = request.get(\'from_date\'           , None)\n
expand_accounts      = request.get(\'expand_accounts\'     , False)\n
show_parent_accounts = request.get(\'show_parent_accounts\', False)\n
\n
# flat_mode is a boolean that indicate wether we should use a report tree\n
#   or a flat list of all accounts.\n
if request.get(\'tree_mode\', False):\n
  raise \'Tree mode no longer supported\'\n
\n
result = []\n
params = {\n
    \'at_date\'                             : at_date\n
  , \'from_date\'                           : from_date\n
  , \'section_category\'                    : section_category\n
  , \'section_category\'                    : section_category\n
  , \'simulation_state\'                    : simulation_state\n
  , \'accounting_transaction_line_currency\': None\n
  , \'is_report_opened\'                    : True\n
  , \'report_depth\'                        : 5\n
  , \'gap_root\'                            : gap_root\n
  , \'gap_list\'                            : gap_list\n
  , \'show_parent_accounts\'                : show_parent_accounts\n
  , \'expand_accounts\'                     : expand_accounts\n
}\n
\n
balance_columns = (\n
    (\'title\'          , \'Account\')\n
  , (\'opening_balance\', \'Opening Balance\')\n
  , (\'debit_movement\' , \'Debit Movements\')\n
  , (\'credit_movement\', \'Credit Movements\')\n
  , (\'closing_balance\', \'Closing Balance\')\n
)\n
\n
result.append( ReportSection(\n
                  path                 = portal.account_module.getPhysicalPath()\n
                  # FIXME: translate later (?)\n
                , title                = portal.Localizer.erp5_ui.gettext(\'Trial Balance\').encode(\'utf8\')\n
                , level                = 1\n
                , form_id              = \'AccountModule_viewAccountListForTrialBalance\'\n
                , selection_name       = \'accounting_selection\'\n
                , selection_params     = params\n
                , listbox_display_mode = \'FlatListMode\'\n
                , selection_columns    = balance_columns\n
                ))\n
\n
# Add a spacer\n
result.append( ReportSection( path    = portal.account_module.getPhysicalPath()\n
                            , title   = \'\\n\'\n
                            , form_id = None\n
                            ))\n
\n
# Add summary lines\n
result.append( ReportSection(\n
                  path                 = portal.account_module.getPhysicalPath()\n
                , title                = \'\'\n
                , form_id              = \'AccountModule_viewTrialBalanceSummary\'\n
                , selection_name       = \'account_selection\'\n
                , listbox_display_mode = \'FlatListMode\'\n
                , selection_params     = params\n
                ))\n
\n
return result\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>AccountModule_getTrialBalanceReportSectionList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
