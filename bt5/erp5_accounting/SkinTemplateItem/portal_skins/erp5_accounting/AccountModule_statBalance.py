portal = context.getPortalObject()
params = portal.ERP5Accounting_getParams(selection_name)
selection_params = context.portal_selections.getSelectionParamsFor(selection_name)

params['omit_asset_increase'] = omit_asset_increase
params['omit_asset_decrease'] = omit_asset_decrease
# For now, we omit simulation to be compatible with other reports.
params['omit_simulation'] = True

selection_domain = context.portal_selections.getSelectionDomainDictFor(selection_name)
if callable(selection_domain):
  selection_domain = selection_domain()
selection_report = context.portal_selections.getSelectionReportDictFor(selection_name)
if selection_domain:
  params['selection_domain'] = selection_domain
if selection_report:
  params['selection_report'] = selection_report
if kw.get('closed_summary'):
  params['closed_summary'] = kw['closed_summary']
if context.portal_selections.getSelectionInvertModeFor(selection_name):
  params['node_uid'] = context.portal_selections.getSelectionInvertModeUidListFor(selection_name)
elif 'title' in selection_params or \
   'preferred_gap_id' in selection_params or \
   'id' in selection_params or \
   'translated_validation_state_title' in selection_params:
  selection_params['ignore_unknown_columns'] = True
  # if list is filtered, apply the same filter here
  params['node_uid'] = [x.uid for x in
                        portal.portal_catalog(**selection_params)]
else:
  # make sure we only have Accounts as nodes
  params['node_category'] = ['account_type',]

# Remove params used internally by ERP5Accounting_getParams before passing to inventory API
params.pop("period_start_date", None)
params.pop("detailed_from_date_summary", None)

return portal.portal_simulation.getInventoryAssetPrice( **params )
