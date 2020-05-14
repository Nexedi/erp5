payment_mode = payment_mode.lower()
person = context.ERP5Site_getAuthenticatedMemberPersonValue()

sale_order = context.WebSection_persistShoppingCart(shopping_cart, person)
if payment_mode == 'paypal':
  return context.Base_redirect('view',
                      keep_items={
                        "portal_status_message": "payment confirmed"
                      })
if payment_mode == 'wechat':
  return context.Base_redirect('wechat_payment',
                      keep_items={
                        'trade_no':sale_order.getReference().encode('utf-8'),
                        'price': int(round((shopping_cart.SaleOrder_getFinalPrice() * 100), 0)),
                        'payment_url': 'weixin'
                      })
