from six.moves import range
portal = context.getPortalObject()
batch_size = 100
priority = 1

activate_kw = dict(tag=tag, priority=priority)

aggregate = context.getRelativeUrl()

if uids:
  payment_relative_url_list = [brain.relative_url for brain
    in portal.portal_catalog(uid=uids, select_dict={'relative_url': None})]
else:
  payment_relative_url_list = [brain.relative_url for brain
    in context.PaymentTransactionGroup_getGroupablePaymentTransactionLineList(
        select_limit=select_limit,
        start_date_range_min=start_date_range_min,
        start_date_range_max=start_date_range_max,
        sign=sign,
        select_mode=select_mode,
        Movement_getMirrorSectionTitle=Movement_getMirrorSectionTitle,)]

if select_mode == 'stopped_or_delivered':
  method_id = 'AccountingTransactionLine_addPaymentTransactionGroup'
else:
  assert select_mode == 'planned_or_confirmed', "Unknown select_mode, %r" % select_mode
  method_id = 'AccountingTransactionLine_stopAndAddPaymentTransactionGroup'


object_list_len = len(payment_relative_url_list)
activate = portal.portal_activities.activate
for i in range(0, object_list_len, batch_size):
  current_path_list = payment_relative_url_list[i:i+batch_size]
  activate(activity='SQLQueue', activate_kw=activate_kw,).callMethodOnObjectList(
      current_path_list,
      method_id,
      aggregate=aggregate,
      activate_kw=activate_kw)
