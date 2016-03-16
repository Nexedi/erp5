price = context.ERP5Banking_getExchangeValue()
if price is None:
  return price

commission_ratio = context.getDiscountRatio()
commission_price = context.getDiscount()
if commission_ratio is not None and commission_ratio !=0 and commission_price is not None and commission_price !=0:
  price = None
elif commission_ratio == 0 or commission_price == 0:
  price = round(price,0)
elif commission_ratio is None and commission_price is None:
  price = round(price,0)

commission_value = 0
if commission_ratio is not None:
  commission_value = commission_ratio * price

if commission_price is not None:
  commission_value = commission_price

if price is None:
  return price

quantity = price + commission_value
quantity = round(quantity,0)
if quantity!=context.getQuantity():
  context.setQuantity(quantity)
return quantity
