if context.getLayoutProperty('ecommerce_test_environment_enabled', False):
  security_parameter_dict = {'USER':context.getLayoutProperty('ecommerce_paypal_sandbox_username', None),
                             'PWD':context.getLayoutProperty('ecommerce_paypal_sandbox_password', None),
                             'SIGNATURE':context.getLayoutProperty('ecommerce_paypal_sandbox_signature', None),
                             }
else:
  security_parameter_dict = {'USER':context.getLayoutProperty('ecommerce_paypal_username', None),
                             'PWD':context.getLayoutProperty('ecommerce_paypal_password', None),
                             'SIGNATURE':context.getLayoutProperty('ecommerce_paypal_signature', None),
                             }

security_parameter_dict['VERSION'] = '58.0'

for parameter in security_parameter_dict:
  if parameter is None:
    return None
return security_parameter_dict
