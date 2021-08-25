"""
  Update Trade Condition with the appropriated Trade Condition.
"""
portal = context.getPortalObject()
if payment_mode is None and preserve:
  current_trade_condition = shopping_cart.getSpecialiseValue()
  if current_trade_condition is not None:
    payment_mode = current_trade_condition.getPaymentConditionPaymentMode()

reference='no_loyalty_reward'
# Loyalty is enabled and user want to use it
if context.REQUEST.get("loyalty_reward", "") == "enable" and context.getSiteLoyaltyExplanationTemplate():
  # this is double check.
  # a trade condition should properly configured for anonymous
  if context.ERP5Site_getAuthenticatedMemberPersonValue():
    reference= 'loyalty_reward'

if payment_mode:
  reference = '%s_%s' % (reference, payment_mode.lower())
sale_trade_condition = portal.portal_catalog.getResultValue(
  portal_type='Sale Trade Condition',
  reference='%' + reference + '%',
  validation_state='published',
  limit=1,
  sort_on=(('version', 'descending'),))

if sale_trade_condition:
  shopping_cart.setSpecialiseValue(sale_trade_condition.getObject())
else:
  shopping_cart.setSpecialise(context.WebSection_getDefaultTradeCondition())


portal.portal_sessions[container.REQUEST['session_id']].update(shopping_cart=shopping_cart)
