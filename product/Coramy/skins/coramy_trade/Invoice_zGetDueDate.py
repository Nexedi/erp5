## Script (Python) "Invoice_zGetDueDate"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
packing_list = context.getCausalityValueList(portal_type=['Sale Packing List','Sales Packing List'])[0]
order = packing_list.getCausalityValueList(portal_type=['Sale Order','Sales Order'])[0]

"""
trade_ref = order.getTradeDateId()
case = {
  'Facture':context.getStartDate,
  'Commande':order.getStartDate,
  'Livraison':packing_list.getTargetStopDate
}
ref_date = case[trade_ref]()
"""
from DateTime import DateTime

due_date = packing_list.getTargetStopDate( DateTime() )

due_date += context.getPaymentTerm(30)

peom = context.getPaymentEndOfMonth()
pat = order.getPaymentAdditionalTerm()

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
