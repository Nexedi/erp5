translateString = context.Base_translateString

portal_type = 'Payment Transaction Group'
removed = False
for line in context.getMovementList(
        portal_type=context.getPortalAccountingMovementTypeList()):

  payment_transaction_group = line.getAggregateValue(portal_type=portal_type)
  if payment_transaction_group is not None and \
       payment_transaction_group.getValidationState() not in ('delivered',):
    line.setAggregateValue(None, portal_type=portal_type)
    removed = True

message = translateString('No valid payment transaction group found')
if removed:
  message = translateString('Removed from payment transaction group')

return context.Base_redirect('view', keep_items=dict(portal_status_message=message))
