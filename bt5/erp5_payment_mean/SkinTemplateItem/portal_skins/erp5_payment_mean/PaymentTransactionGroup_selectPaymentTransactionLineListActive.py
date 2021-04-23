batch_size = 100
priority = 1

activate_kw = dict(tag=tag, priority=priority)

aggregate = context.getRelativeUrl()

payment_relative_url_list = [brain.relative_url for brain
  in context.PaymentTransactionGroup_getGroupablePaymentTransactionLineList(
      limit=limit,
      start_date_range_min=start_date_range_min,
      start_date_range_max=start_date_range_max,
      sign=sign,
      mode=mode,)]

if mode == 'stopped_or_delivered':
  method_id = 'AccountingTransactionLine_setAggregate'
else:
  assert mode == 'planned_or_confirmed', "Unknown mode, %r" % mode
  method_id = 'AccountingTransactionLine_stopAndSetAggregate'


object_list_len = len(payment_relative_url_list)
activate = context.getPortalObject().portal_activities.activate
for i in xrange(0, object_list_len, batch_size):
  current_path_list = payment_relative_url_list[i:i+batch_size]
  activate(activity='SQLQueue', activate_kw=activate_kw,).callMethodOnObjectList(
      current_path_list,
      method_id,
      aggregate=aggregate,
      activate_kw=activate_kw)
