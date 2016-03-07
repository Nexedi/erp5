if alternative_url is not None:
  return alternative_url

test_environement = context.getLayoutProperty('ecommerce_test_environment_enabled', None)

if test_environement is not None and test_environement == 1:
  if api == 'nvp':
    return 'https://api-3t.sandbox.paypal.com/nvp'
  return 'https://www.sandbox.paypal.com/cgi-bin/webscr'

if api == 'nvp':
  return 'https://api-3t.paypal.com/nvp'
return 'https://www.paypal.com/cgi-bin/webscr'
