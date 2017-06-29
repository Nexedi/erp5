portal = context.getPortalObject()
params = portal.ERP5Site_getAccountingSelectionParameterDict(selection_name)
params['omit_asset_increase'] = omit_asset_increase
params['omit_asset_decrease'] = omit_asset_decrease
# For now, we omit simulation to be compatible with other reports.
params['omit_simulation'] = True

# Remove params used internally by ERP5Site_getAccountingSelectionParameterDict before passing to inventory API
params.pop("period_start_date", None)
params.pop("detailed_from_date_summary", None)

return portal.portal_simulation.getInventoryAssetPrice(
                                          node_uid=brain.uid,
                                          **params )
