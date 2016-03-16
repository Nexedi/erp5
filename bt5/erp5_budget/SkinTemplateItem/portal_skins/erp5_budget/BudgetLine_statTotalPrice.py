portal = context.getPortalObject()
params = portal.portal_selections.getSelectionParamsFor(selection_name)
cell_index = params.get('cell_index')
engaged_budget = params.get('engaged_budget')

query_dict = context.BudgetLine_getInventoryQueryDictForCellIndex(
                  cell_index=cell_index,
                  engaged_budget=engaged_budget)

return portal.portal_simulation.getInventoryAssetPrice(**query_dict)
