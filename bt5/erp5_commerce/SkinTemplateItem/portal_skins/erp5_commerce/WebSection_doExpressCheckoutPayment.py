order_parameter_dict = context.WebSite_getPaypalOrderParameterDict()
if order_parameter_dict is None:
  return None
order_parameter_dict['TOKEN'] = token
order_parameter_dict['PAYERID'] = payer_id
order_parameter_dict['METHOD'] = 'DoExpressCheckoutPayment'

response_parameter_dict = context.WebSection_submitPaypalNVPRequest(parameter_dict=order_parameter_dict,
                                                                  nvp_url=context.WebSite_getPaypalUrl(api='nvp'))
return response_parameter_dict
