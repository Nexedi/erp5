## Script (Python) "Invoice_zGetTotalNetPrice"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
# price = context.getTotalPrice()
price = context.Invoice_zGetTotal()[0].total_price

discount_list_tmp = context.contentValues(filter={'portal_type':'Remise'})
discount_list = filter(lambda x: x not in [None,0] ,discount_list_tmp)

if len(discount_list) > 1:
  discount_list.sort(lambda x,y: cmp(x.getIntIndex(),y.getIntIndex()))

for discount_line in discount_list:
  if discount_line.getImmediateDiscount():
    price *= (1 - discount_line.getDiscountRatio())

return price
