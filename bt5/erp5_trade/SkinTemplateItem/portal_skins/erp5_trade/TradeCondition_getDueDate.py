# TODO: this script is not well tested and not fully implemented
# TODO: this is actually PaymentCondition_getDueDate

from DateTime import DateTime

if context.getPortalType() == 'Payment Condition':
  delivery = context.getParentValue()
  payment_condition = context
else:
  delivery = context
  payment_condition = context.getDefaultPaymentConditionValue()

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
      return order.getStartDate() # TODO start or stop ? -> based on source/destination
  return getter

def PackingListDateGetter(invoice):
  def getter():
    packing_list = invoice.getCausalityValue(
                     portal_type=context.getPortalDeliveryTypeList())
    if packing_list:
      return packing_list.getStartDate() # TODO start or stop ? -> based on source/destination
  return getter

case = {
  'invoice':      delivery.getStartDate,
  'order':        OrderDateGetter(delivery),
  'packing list': PackingListDateGetter(delivery),
}

due_date = case.get(payment_condition.getTradeDate(), delivery.getStartDate)()
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
