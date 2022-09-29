translateString = context.Base_translateString

token = context.REQUEST.get('token')
payer_id = context.REQUEST.get('PayerID')

parameter_dict = context.WebSection_getExpressCheckoutDetails(token)

if parameter_dict['ACK'] != 'Success':
  return "Identification failed.1 : %s" % parameter_dict['ACK']

if parameter_dict['PAYERID'] != payer_id:
  return "Identification failed.2 : %s" % parameter_dict['PAYERID']

#redirect user to the checkout section
website = context.getWebSiteValue()
section_url = website.getLayoutProperty('ecommerce_checkout_section_id',"checkout")
website.Base_redirect(section_url, \
                       keep_items={'portal_status_message':translateString("The payment procedure went well on Paypal."),
                                      'token':token})
