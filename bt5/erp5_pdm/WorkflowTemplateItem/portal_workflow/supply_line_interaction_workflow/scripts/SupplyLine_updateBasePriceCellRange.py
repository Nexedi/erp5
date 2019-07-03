supply_line = state_change['object']
price_parameter = 'base_price'
base_id = 'path'
supply_line.updateQuantityPredicate(price_parameter)
supply_line.updateCellRange(base_id=base_id)
