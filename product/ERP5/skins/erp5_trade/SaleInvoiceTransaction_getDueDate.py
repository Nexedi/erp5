## Script (Python) "SaleInvoiceTransaction_getDueDate"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
packing_list_list = context.getCausalityValueList(portal_type=['Sale Packing List','Sales Packing List'])

if len(packing_list_list) > 0:
  packing_list = context.getCausalityValueList(portal_type=['Sale Packing List','Sales Packing List'])[0]
  order = packing_list.SalesPackingList_getCausalitySalesOrder()
  from DateTime import DateTime
  due_date = packing_list.getTargetStopDate( DateTime() )
  pat = order.getPaymentAdditionalTerm()
else:
  due_date = context.getStartDate()
  pat = None

due_date += context.getPaymentTerm(30)
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
