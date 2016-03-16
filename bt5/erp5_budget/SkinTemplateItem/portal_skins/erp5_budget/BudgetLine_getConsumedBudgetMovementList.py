if not cell_index:
  return []

kw.update(context.BudgetLine_getInventoryQueryDictForCellIndex(
            cell_index=cell_index,
            engaged_budget=engaged_budget))

return context.getPortalObject().portal_simulation.getMovementHistoryList(**kw)
