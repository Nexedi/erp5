from Products.ERP5Type.Message import translateString
tag = 'PaymentTransactionGroup_selectPaymentTransactionList'

context.serialize()

if context.getPortalObject().portal_activities.countMessageWithTag(tag,):
  return context.Base_redirect(form_id, keep_items=dict(portal_status_message=translateString(
    "Some payments are still beeing processed in the background, please retry later")))

context.activate(tag=tag).PaymentTransactionGroup_selectPaymentTransactionLineListActive(
  limit=limit,
  start_date_range_min=start_date_range_min,
  start_date_range_max=start_date_range_max,
  sign=sign,
  mode=mode,
  tag=tag)

return context.Base_redirect(form_id,
  keep_items=dict(portal_status_message=translateString('Payment selection in progress.')))
