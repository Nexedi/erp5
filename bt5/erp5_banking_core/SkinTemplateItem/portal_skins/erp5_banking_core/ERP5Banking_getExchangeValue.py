rate = None
method = getattr(context, 'getCurrencyExchangeRate', None)
if method is not None:
  rate = method()
if rate is None:
  rate_list = context.CurrencyExchange_getExchangeRateList(from_currency=from_currency,
                 to_currency=to_currency, 
                 currency_exchange_type=currency_exchange_type,
                 start_date=start_date)
  if len(rate_list) > 0:
    rate = rate_list[0]

price = context.getSourceTotalAssetPrice()

if None in (rate, price):
  return None

price = float(price)

return round(rate * price)
