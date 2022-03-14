from builtins import str
order_parameter_dict = context.WebSite_getPaypalSecurityParameterDict()
if order_parameter_dict is None:
  return None

web_site = context.getWebSiteValue()
shopping_cart = context.SaleOrder_getShoppingCart()
shopping_cart_product_list = shopping_cart.SaleOrder_getShoppingCartItemList()
shopping_cart_price = float(web_site.SaleOrder_getShoppingCartTotalPrice())
taxes_amount = float(shopping_cart.SaleOrder_getShoppingCartTotalPrice(include_taxes=True, include_shipping=True)) - \
               float(shopping_cart.SaleOrder_getShoppingCartTotalPrice(include_shipping=True));
if shopping_cart.SaleOrder_isShippingRequired():
  shipping = shopping_cart.SaleOrder_getSelectedShippingResource()
  shipping_price = shipping.getPrice()
else:
  shipping_price = 0

customer = context.SaleOrder_getShoppingCartCustomer()
site_url = web_site.absolute_url()

order_parameter_dict['METHOD'] = 'SetExpressCheckout'
order_parameter_dict['RETURNURL'] = '%s/WebSection_checkPaypalIdentification' % site_url
order_parameter_dict['CANCELURL'] = site_url
order_parameter_dict['PAYMENTACTION'] = 'Sale'

actual_product_index = 0
for product in shopping_cart_product_list:
  resource = context.restrictedTraverse(product.getResource())
  quantity = int(product.getQuantity())
  price = resource.getPrice()
  order_parameter_dict['L_NAME%s' % actual_product_index] = resource.getTitle()
  order_parameter_dict['L_NUMBER%s' % actual_product_index] = resource.getId()
  order_parameter_dict['L_AMT%s' % actual_product_index] = price
  order_parameter_dict['L_QTY0%s' % actual_product_index] = quantity
  actual_product_index += 1

order_parameter_dict['ITEMAMT'] = shopping_cart_price
order_parameter_dict['TAXAMT'] = taxes_amount
order_parameter_dict['SHIPPINGAMT'] = shipping_price
order_parameter_dict['AMT'] = shopping_cart_price + taxes_amount + shipping_price
order_parameter_dict['CURRENCYCODE'] = context.WebSite_getShoppingCartDefaultCurrencyCode()
order_parameter_dict['NOSHIPPING'] = str(not shopping_cart.SaleOrder_isShippingRequired())
order_parameter_dict['ALLOWNOTE'] = '0'

return order_parameter_dict
