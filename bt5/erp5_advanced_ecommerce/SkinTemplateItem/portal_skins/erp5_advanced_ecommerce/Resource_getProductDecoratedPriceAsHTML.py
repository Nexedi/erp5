"""
DRESSING DAILS<br />By TOM TAYLOR<br />
                  <span class="price">14,89 &euro;</span>
                  <span class="old_price">29,95 &euro;</span>
"""
clean = 0
if context.REQUEST.get("variation", None) is None:
  context.REQUEST.set("variation", context.REQUEST.get("default_displayed_variation"))
  clean = 1

price = cell.Resource_getShopPrice()
old_price = cell.getDefaultSaleSupplyLineBasePrice()
currency = here.WebSite_getShoppingCartDefaultCurrencyCode()
title = cell.getTitle()
if currency == 'EUR':
  currency = '&euro;'

output = """%s<br /><br />"""  % (title.upper(),)

if old_price is not None and price != old_price:
  output += """<span class="new_price">%s %s</span>""" % (price, currency)
  output += """<br /><span class="old_price">%s %s</span>""" % (old_price, currency)
else:
  output += """<span class="price">%s %s</span>""" % (price, currency)

if clean:
  context.REQUEST.set("variation", None)
return output
