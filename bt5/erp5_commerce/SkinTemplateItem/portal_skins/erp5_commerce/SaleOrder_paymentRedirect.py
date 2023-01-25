# check if the user is Anonymous, if yes it must be redirected to Registration Dialog
# otherwise it will redirect to the appropriated payment form based on Payment Mode selected
request = context.REQUEST
isAnon = context.portal_membership.isAnonymousUser()
translateString = context.Base_translateString

if field_my_comment is not None:
  shopping_cart = context.SaleOrder_getShoppingCart()
  shopping_cart.setComment(field_my_comment)

if isAnon:
  # create first an account for user
  web_site = context.getWebSiteValue()
  msg = translateString("You need to create an account to continue. If you already have please login.")
  web_site.Base_redirect('register', \
                      keep_items={'portal_status_message': msg})
  return

if field_my_payment_mode is None:
  msg = translateString("You must select a payment mode.")
else:
  if field_my_payment_mode.lower() == 'credit card':
    return context.getWebSectionValue().SaleOrder_viewAsWebConfirmCreditCardPayment()
  elif field_my_payment_mode.lower() == 'paypal':
    return context.getWebSectionValue().SaleOrder_viewAsWebConfirmPayPalPayment()
  else:
    msg = translateString("This payment mode is actually not activated, sorry: ${payment_mode}",
                          mapping=dict(payment_mode=field_my_payment_mode))

context.Base_redirect('SaleOrder_viewAsWeb', \
                        keep_items={'portal_status_message': msg})
