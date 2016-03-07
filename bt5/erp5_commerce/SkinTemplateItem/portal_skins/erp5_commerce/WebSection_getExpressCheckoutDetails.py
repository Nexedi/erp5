security_parameter_dict = context.WebSite_getPaypalSecurityParameterDict()
if security_parameter_dict is None:
  return None
security_parameter_dict['TOKEN'] = token
security_parameter_dict['METHOD'] = 'GetExpressCheckoutDetails'

response_parameter_dict = context.WebSection_submitPaypalNVPRequest(parameter_dict=security_parameter_dict,
                                                                  nvp_url=context.WebSite_getPaypalUrl(api='nvp', alternative_url=alternative_url))
return response_parameter_dict
