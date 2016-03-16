# Override InventoryLine_asCellRange from erp5_trade for backward compatibility
return context.CashDetail_asCellRange(base_category=base_category, base_id=base_id, matrixbox=matrixbox, **kw)
