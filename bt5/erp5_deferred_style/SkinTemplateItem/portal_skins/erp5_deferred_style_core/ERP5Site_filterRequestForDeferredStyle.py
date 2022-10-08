from Products.ERP5Type.Utils import ensure_list
new_request = {}

for k, v in ensure_list(request.other.items()) + ensure_list(request.form.items()):
  if k not in ('TraversalRequestNameStack', 'AUTHENTICATED_USER', 'URL',
      'SERVER_URL', 'AUTHENTICATION_PATH', 'USER_PREF_LANGUAGES', 'PARENTS',
      'PUBLISHED', 'AcceptLanguage', 'AcceptCharset', 'RESPONSE', 'SESSION',
      'ACTUAL_URL', 'HTTP_COOKIE'):
    # XXX proxy fields stores a cache in request.other that cannot be pickled
    if same_type(k, '') and k.startswith('field__proxyfield'):
      continue
    # Remove FileUpload parameters
    elif getattr(v, 'headers', ''):
      continue
    new_request[k] = v

return new_request
