kwd = context.ERP5Site_getAccountingSelectionParameterDict(selection_name)
# cleanup unsupported catalog parameters
kwd.pop('period_start_date', None)
kwd.pop('detailed_from_date_summary', None)

if kw.get('stat'):
  selection_params = context.portal_selections.getSelectionParamsFor(selection_name)
  selection_domain = context.portal_selections.getSelectionDomainDictFor(selection_name)
  if callable(selection_domain):
    selection_domain = selection_domain()
  selection_report = context.portal_selections.getSelectionReportDictFor(selection_name)
  if selection_domain:
    kwd['selection_domain'] = selection_domain
  if selection_report:
    kwd['selection_report'] = selection_report
  if context.portal_selections.getSelectionInvertModeFor(selection_name):
    kwd['stock.node_uid'] = context.portal_selections.getSelectionInvertModeUidListFor(selection_name)
  # is list filtered ?
  elif 'title' in selection_params or \
      'preferred_gap_id' in selection_params or\
      'id' in selection_params or \
      'translated_validation_state_title' in selection_params:
    selection_params['ignore_unknown_columns'] = True
    # if yes, apply the same filter here
    kwd['stock.node_uid'] = [x.uid for x in
                         context.portal_catalog(**selection_params)]
  else:
    kwd['portal_type'] = context.getPortalAccountingMovementTypeList()
  return context.portal_simulation.getInventoryStat( **kwd )[0]['stock_uid']

kwd['stock.node_uid'] = brain.uid

return context.portal_simulation.getInventoryStat( **kwd )[0]['stock_uid']
# vim: syntax=python
