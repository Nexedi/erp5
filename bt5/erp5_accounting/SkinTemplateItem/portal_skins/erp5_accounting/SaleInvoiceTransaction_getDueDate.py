packing_list_list = context.getCausalityValueList(portal_type='Sale Packing List')

if len(packing_list_list) > 0:
  packing_list = packing_list_list[0]
  order = packing_list.getCausalityValue(portal_type='Sale Order')
  from DateTime import DateTime
  due_date = order.getPaymentConditionPaymentDate( DateTime() )
  pat = None #order.getPaymentAdditionalTerm()
else:
  due_date = context.getStartDate()
  pat = None

due_date += context.getPaymentConditionPaymentTerm(30)
peom = context.getPaymentEndOfMonth()

if peom:
  i = 0
  month = due_date.month()
  while (month == (due_date + i).month()):
    i += 1
  due_date = (due_date + i - 1)

  if pat != None:
    due_date += pat

else:
  if pat != None:
    i = 0
    month = due_date.month()
    while (month == (due_date + i).month()):
      i -= 1
    due_date = (due_date + i + pat)

return due_date
