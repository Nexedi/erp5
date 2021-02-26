from DateTime import DateTime
from datetime import timedelta
import calendar

source = False
if context.getPortalType() in ('Purchase Invoice', 'Purchase Invoice Transaction',):
  source = False
elif context.getPortalType() in ('Sale Invoice', 'Sale Invoice Transaction',):
  source = True
else: # internal invoices
  source = context.AccountingTransaction_isSourceView()

delivery = context
trade_condition = delivery.getSpecialiseValue()
if trade_condition is None:
  return None
payment_condition = trade_condition.getDefaultPaymentConditionValue()
if payment_condition is None:
  return None

# Absolute payment date has priority
if payment_condition.getPaymentDate():
  return payment_condition.getPaymentDate()

def OrderDateGetter(invoice):
  def getter():
    packing_list = invoice.getCausalityValue(
                     portal_type=context.getPortalDeliveryTypeList())
    if packing_list is not None:
      order = packing_list.getCausalityValue(
                     portal_type=context.getPortalOrderTypeList())
      return order.getStartDate()
  return getter

def PackingListDateGetter(invoice):
  def getter():
    packing_list = invoice.getCausalityValue(
                     portal_type=context.getPortalDeliveryTypeList())
    if packing_list is not None:
      return packing_list.getStopDate()
  return getter

date_getter = {
  'invoice': delivery.getStartDate if source else delivery.getStopDate,
  'order': OrderDateGetter(delivery),
  'packing_list': PackingListDateGetter(delivery),
}

due_date = date_getter.get(payment_condition.getTradeDate(), lambda: None)()
if not due_date:
  return None

due_date = due_date.asdatetime()

due_date += timedelta(days=payment_condition.getPaymentTerm(0))

if payment_condition.getPaymentEndOfMonth():
  last_day_of_month = calendar.monthrange(due_date.year, due_date.month)[1]
  due_date = due_date.replace(day=last_day_of_month)

due_date += timedelta(days=payment_condition.getPaymentAdditionalTerm(0))

return DateTime(due_date)
