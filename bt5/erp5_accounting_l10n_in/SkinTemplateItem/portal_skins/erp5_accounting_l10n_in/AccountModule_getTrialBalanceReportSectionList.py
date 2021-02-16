"""
  Trial balance.
"""
from Products.ERP5Form.Report import ReportSection

request = context.REQUEST
portal  = context.portal_url.getPortalObject()

at_date              = request['at_date']
section_category     = request['transaction_section_category']
simulation_state     = request['transaction_simulation_state']
gap_root             = request['gap_root']
gap_list             = request.get('gap_list'            , [])
from_date            = request.get('from_date'           , None)
expand_accounts      = request.get('expand_accounts'     , False)
show_parent_accounts = request.get('show_parent_accounts', False)

# flat_mode is a boolean that indicate wether we should use a report tree
#   or a flat list of all accounts.
if request.get('tree_mode', False):
  raise ValueError('Tree mode no longer supported')

result = []
params = {
    'at_date'                             : at_date
  , 'from_date'                           : from_date
  , 'section_category'                    : section_category
  , 'section_category'                    : section_category
  , 'simulation_state'                    : simulation_state
  , 'accounting_transaction_line_currency': None
  , 'is_report_opened'                    : True
  , 'report_depth'                        : 5
  , 'gap_root'                            : gap_root
  , 'gap_list'                            : gap_list
  , 'show_parent_accounts'                : show_parent_accounts
  , 'expand_accounts'                     : expand_accounts
}

balance_columns = (
    ('title'          , 'Account')
  , ('opening_balance', 'Opening Balance')
  , ('debit_movement' , 'Debit Movements')
  , ('credit_movement', 'Credit Movements')
  , ('closing_balance', 'Closing Balance')
)

result.append( ReportSection(
                  path                 = portal.account_module.getPhysicalPath()
                  # FIXME: translate later (?)
                , title                = portal.Localizer.erp5_ui.gettext('Trial Balance').encode('utf8')
                , level                = 1
                , form_id              = 'AccountModule_viewAccountListForTrialBalance'
                , selection_name       = 'accounting_selection'
                , selection_params     = params
                , listbox_display_mode = 'FlatListMode'
                , selection_columns    = balance_columns
                ))

# Add a spacer
result.append( ReportSection( path    = portal.account_module.getPhysicalPath()
                            , title   = '\n'
                            , form_id = None
                            ))

# Add summary lines
result.append( ReportSection(
                  path                 = portal.account_module.getPhysicalPath()
                , title                = ''
                , form_id              = 'AccountModule_viewTrialBalanceSummary'
                , selection_name       = 'account_selection'
                , listbox_display_mode = 'FlatListMode'
                , selection_params     = params
                ))

return result
