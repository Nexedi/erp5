request_other = {}

for k, v in request.other.items() + request.form.items():
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
    request_other[k] = v

return request_other
