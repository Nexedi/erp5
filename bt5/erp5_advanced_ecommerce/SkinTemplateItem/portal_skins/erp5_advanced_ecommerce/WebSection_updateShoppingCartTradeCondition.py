"""
  Update Trade Condition with the appropriated Trade Condition.
"""
if payment_mode is None and preserve:
  current_trade_condition = shopping_cart.getSpecialiseValue()
  if current_trade_condition is not None:
    payment_mode = current_trade_condition.getPaymentConditionPaymentMode()

if context.REQUEST.get("loyalty_reward", "") != "disable":
  reference= 'loyalty_reward'
else:
  reference='no_loyalty_reward'

if payment_mode:
  reference = '%s_%s' % (reference, payment_mode.lower())

sale_trade_condition = context.portal_catalog.getResultValue(
  portal_type='Sale Trade Condition',
  reference=reference,
  validation_state='validated',
  limit=1,
  sort_on=(('version', 'descending'),))

if sale_trade_condition:
  shopping_cart.setSpecialiseValue(sale_trade_condition.getObject())
else:
  shopping_cart.setSpecialise(context.WebSection_getDefaultTradeCondition())
