portal = context.getPortalObject()

if mode is None:
  # To show an empty listbox the first time the dialog is open
  return []
elif mode == 'stopped_or_delivered':
  simulation_state = ('delivered', 'stopped')
else:
  assert mode == 'planned_or_confirmed', "Unknown mode, %r" % mode
  simulation_state = ('planned', 'confirmed')

search_kw = dict(
  parent_portal_type='Payment Transaction',
  limit=None,
  simulation_state=simulation_state,
  section_uid=context.getSourceSection()
     and portal.Base_getSectionUidListForSectionCategory(
       context.getSourceSectionValue().getGroup(base=True)),
  payment_uid=context.getSourcePaymentUid(),
  resource_uid=context.getPriceCurrencyUid(),
  node_category='account_type/asset/cash/bank',
#  group_by=('parent_uid', ), # The limit is not applied on the number of payment transactions, but on the number of lines (to simplify setting aggregate relation).

  # we have 'aggregate/payment_transaction_module/xxx' in sub_variation_text if the line is already grouped.
  sub_variation_text='',
)

if context.getPaymentMode():
  search_kw['payment_transaction_line_payment_mode_uid'] = context.getPaymentModeUid()

if select_limit:
  search_kw['limit'] = select_limit

if start_date_range_max:
  search_kw['at_date'] = start_date_range_max.latestTime()
if start_date_range_min:
  search_kw['from_date'] = start_date_range_min

if Movement_getMirrorSectionTitle:
  search_kw['stock_mirror_section_title'] = Movement_getMirrorSectionTitle

if sign in ('outgoing', 'out'):
  search_kw['omit_asset_increase'] = True
elif sign in ('incoming', 'in'):
  search_kw['omit_asset_decrease'] = True

movement_history_list = portal.portal_simulation.getMovementHistoryList(**search_kw)

# XXX this will be read by PaymentTransactionGroup_statGroupablePaymentTransactionLineList
# ( we could be using getInventoryStat there but this does not support limit
# parameter )
stat_total_quantity = 0
if movement_history_list:
  stat_total_quantity = movement_history_list[-1].running_total_quantity
container.REQUEST.set(
  'PaymentTransactionGroup_statGroupablePaymentTransactionLineList.total_quantity',
  stat_total_quantity)

return movement_history_list
