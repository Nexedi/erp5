## Script (Python) "Invoice_zGetPaymentTime"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
packing_list = context.getCausalityValueList(portal_type=['Sale Packing List','Sales Packing List'])[0]

#order = packing_list.getCausalityValueList(portal_type=['Sale Order','Sales Order'])[0]
order = packing_list.SalesPackingList_getCausalitySalesOrder()
payment_term = context.getPaymentTerm(30)

payment_end_of_month = context.getPaymentEndOfMonth()

pat = order.getPaymentAdditionalTerm()

result = '%i jours ' % payment_term

if pat == None:
  if payment_end_of_month:
    result += 'en fin de mois'
  else:
    result += 'net'
else:
  result += 'le %i' % pat


return result
