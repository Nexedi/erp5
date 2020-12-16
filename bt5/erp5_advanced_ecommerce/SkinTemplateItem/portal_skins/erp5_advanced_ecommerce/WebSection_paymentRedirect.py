"""
  Redirect to relevant payment mode and force if necessary user
  to register first.
"""
# check if the user is Anonymous, if yes he/she must be redirected to Registration Dialog
# otherwise it will redirect to the appropriated payment form based on Payment Mode selected
isAnon = context.portal_membership.isAnonymousUser()
translateString = context.Base_translateString

# Make sure we save shopping cart informations modified on last minute.
context.WebSection_editShoppingCart(redirect=False, **kw)

shopping_cart = context.SaleOrder_getShoppingCart()
field_my_comment = shopping_cart.getComment()
trade_condition = shopping_cart.getSpecialiseValue()
field_my_payment_mode = trade_condition.getPaymentConditionPaymentMode()

if field_my_payment_mode is None:
  field_my_payment_mode = trade_condition.getSpecialiseValue().getPaymentConditionPaymentMode()

if isAnon:
  # create first an account for user
  web_site = context.getWebSiteValue()
  msg = translateString("You need to login or create an account to continue.")
  from ZTUtils import make_query
  parameter_string = make_query(field_my_comment=field_my_comment, field_my_payment_mode=field_my_payment_mode)
  coming_from_url = '%s/WebSection_paymentRedirect?%s' % (context.absolute_url(), parameter_string)
  return web_site.Base_redirect('login_form', \
                      keep_items={'portal_status_message': msg,
                                  'came_from': coming_from_url})

if context.SaleOrder_getSelectedShippingResource() is None:
  msg = translateString("You must select a payment mode.")
  return context.Base_redirect('', keep_items={'portal_status_message': msg})
else:
  return context.getWebSectionValue().WebSection_viewConfirmPayment(field_my_payment_mode, shopping_cart)
