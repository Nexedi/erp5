supply_line = state_change['object']
price_parameter = 'surcharge_ratio'
base_id = 'path_%s' % price_parameter
supply_line.updateQuantityPredicate(price_parameter)
supply_line.updateCellRange(base_id=base_id)
