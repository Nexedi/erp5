request = context.REQUEST
isAnon = context.portal_membership.isAnonymousUser()
translateString = context.Base_translateString

## check if user is authenticated
if isAnon:
  msg = translateString("You need to create an account to continue. If you already have one, please login.")
  context.Base_redirect('WebSite_viewRegistrationDialog', \
                        keep_items={'portal_status_message': msg,
                                    'editable_mode': 1})
  return

## check if the id of the token correspond to the good products
parameter_dict = context.WebSection_getExpressCheckoutDetails(token)
if parameter_dict['ACK'] != 'Success':
  msg = translateString("This paypal session is not initialised with the actual card.")
  context.Base_redirect('', \
                        keep_items={'portal_status_message': msg,})

payer_id = parameter_dict['PAYERID']
response_dict = context.WebSection_doExpressCheckoutPayment(token, payer_id)

if response_dict['ACK'] != 'Success':
  msg = translateString("Your payment failed because of ")
  context.Base_redirect('WebSite_viewRegistrationDialog', \
                        keep_items={'portal_status_message': '%s : %s' % (msg, str(response_dict)),
                                    'editable_mode': 1})
  return

#Payment is ok. Set shopping cart is payed
context.SaleOrder_setShoppingCartBuyer()

return context.SaleOrder_finalizeShopping()
