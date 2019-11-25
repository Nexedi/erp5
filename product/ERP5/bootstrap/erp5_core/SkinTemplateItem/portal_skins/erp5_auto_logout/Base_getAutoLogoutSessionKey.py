from zExceptions import Unauthorized
if REQUEST is not None: # Cheap "do not call from URL" protection - not that the session key is secret
  raise Unauthorized
return 'ac_cookie_' + username
