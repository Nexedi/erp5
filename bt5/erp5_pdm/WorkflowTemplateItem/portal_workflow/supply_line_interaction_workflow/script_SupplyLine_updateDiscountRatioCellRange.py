supply_line = state_change['object']
price_parameter = 'discount_ratio'
base_id = 'path_discount_ratio'
supply_line.updateQuantityPredicate(price_parameter)
supply_line.updateCellRange(base_id=base_id)
