shopping_cart = context.SaleOrder_getShoppingCart()
if shopping_cart is None:
  return default

trade_condition = shopping_cart.getSpecialiseValue()

if trade_condition is None:
  return default

current_payment_mode = trade_condition.getPaymentConditionPaymentMode()

if current_payment_mode in [None, ""]:
  up_trade_condition = trade_condition.getSpecialiseValue(portal_type="Sale Trade Condition")
  if up_trade_condition is not None:
    current_payment_mode = up_trade_condition.getPaymentConditionPaymentMode()

if current_payment_mode in [None, ""]:
  return default

return current_payment_mode
