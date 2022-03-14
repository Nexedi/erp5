portal = context.getPortalObject()

payment_mode_from_trade_condition = None
trade_condition = context.getSpecialiseValue()
if trade_condition is not None:
  payment_mode_from_trade_condition = trade_condition.getPaymentConditionPaymentMode()

return payment_mode_from_trade_condition or portal.portal_selections.getSelectionParamsFor(
    'accounting_create_related_payment_selection').get('payment_mode_for_related_payment')
