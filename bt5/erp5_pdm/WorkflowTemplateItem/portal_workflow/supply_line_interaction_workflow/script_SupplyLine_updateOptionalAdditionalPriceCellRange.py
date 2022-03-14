supply_line = state_change['object']
price_parameter = 'additional_price'
base_id = 'path_optional_%s' % price_parameter
supply_line.updateQuantityPredicate(price_parameter)
supply_line.updateCellRange(base_id=base_id, option_variation=1)
