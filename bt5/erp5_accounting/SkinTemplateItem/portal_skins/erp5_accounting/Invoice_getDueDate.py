from DateTime import DateTime

source = False
if context.getPortalType() in ('Purchase Invoice', 'Purchase Invoice Transaction',):
  source = False
elif context.getPortalType() in ('Sale Invoice', 'Sale Invoice Transaction',):
  source = True
else: # internal invoices
  source = context.AccountingTransaction_isSourceView()

delivery = context
payment_condition = context.getSpecialiseValue().getDefaultPaymentConditionValue()

# Absolute payment date has priority
if payment_condition.getPaymentDate():
  return payment_condition.getPaymentDate()

def OrderDateGetter(invoice):
  def getter():
    packing_list = invoice.getCausalityValue(
                     portal_type=context.getPortalDeliveryTypeList())
    if packing_list:
      order = packing_list.getCausalityValue(
                     portal_type=context.getPortalOrderTypeList())
      return order.getStartDate() if source else order.getStopDate()
  return getter

def PackingListDateGetter(invoice):
  def getter():
    packing_list = invoice.getCausalityValue(
                     portal_type=context.getPortalDeliveryTypeList())
    if packing_list:
      return packing_list.getStartDate() if source else packing_list.getStopDate()
  return getter

case = {
  'invoice': delivery.getStartDate if source else delivery.getStopDate,
  'order': OrderDateGetter(delivery),
  'packing list': PackingListDateGetter(delivery),
}

due_date = case.get(payment_condition.getTradeDate(), delivery.getStartDate)()
if not due_date:
  return None
due_date += payment_condition.getPaymentTerm(0)

pat = payment_condition.getPaymentAdditionalTerm()

if payment_condition.getPaymentEndOfMonth():
  i = 0
  month = due_date.month()
  while (month == (due_date + i).month()):
    i += 1
  due_date = (due_date + i - 1)
  if pat:
    due_date += pat
else:
  if pat:
    i = 0
    month = due_date.month()
    while (month == (due_date + i).month()):
      i -= 1
    due_date = (due_date + i + pat)

return due_date
