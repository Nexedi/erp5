response_parameter_dict = context.WebSection_submitPaypalNVPRequest(parameter_dict=context.WebSite_getPaypalOrderParameterDict(),
                                                                  nvp_url=context.WebSite_getPaypalUrl(api='nvp', alternative_url=alternative_url))

if response_parameter_dict is None:
  return None

if response_parameter_dict['ACK'] == 'Success':
  return response_parameter_dict['TOKEN']
return ''
