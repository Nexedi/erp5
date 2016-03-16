price = context.ERP5Banking_getExchangeValue()

commission_ratio = context.getDiscountRatio()
commission_price = context.getDiscount()

if commission_ratio is not None and commission_ratio !=0 and commission_price is not None and commission_price !=0:
  price = None
if price is None:
  return price
if commission_ratio == 0 or commission_price == 0:
  price = round(price,0)
if commission_ratio is None and commission_price is None:
  price = round(price,0)

commission_value = 0
if commission_ratio is not None:
  commission_value = commission_ratio * price

if commission_price is not None:
  commission_value = commission_price

quantity = price - commission_value
quantity = round(quantity,0)
if quantity!=context.getQuantity():
  #verify that when the quantity is already calculated by another user,it does not need
  # to be calculated again, just return the value already calculated 
  if context.Base_userHasModidyPortalContentPermission()==False and context.getQuantity() is not None:
    return quantity
  else:
    context.setQuantity(quantity)
return quantity
