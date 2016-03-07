rate_list = context.CurrencyExchange_getExchangeRateList()
rate = None
if len(rate_list) > 0:
 rate = rate_list[1]
if rate is None:
  return None

base_price = context.getSourceTotalAssetPrice()
if base_price is None:
  return None

price = rate * base_price

commission_ratio = context.getDiscountRatio()
commission_price = context.getDiscount()
if commission_ratio is not None and commission_ratio !=0 and commission_price is not None and commission_price !=0:
  return None
if (commission_ratio is None or commission_ratio == 0) and (commission_price is None or commission_price == 0):
  return None

if commission_ratio is not None:
  commission_value = commission_ratio * price

if commission_price is not None:
  commission_value = commission_price


quantity = price + commission_value
context.setQuantity(quantity)
return quantity
