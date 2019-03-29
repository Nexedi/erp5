if related_simulation_movement_path_list is None:
  raise RuntimeError('related_simulation_movement_path_list is missing. Update ERP5 Product.')

open_sale_order = context.getCausalityValue()

open_sale_order_trade_condition = open_sale_order.getSpecialiseValue()
if open_sale_order_trade_condition is not None:
  context.setSpecialise(open_sale_order_trade_condition.getRelativeUrl())
  context.Order_applyTradeCondition(open_sale_order_trade_condition)
context.order(comment='Ordered by Open Sale Order')
