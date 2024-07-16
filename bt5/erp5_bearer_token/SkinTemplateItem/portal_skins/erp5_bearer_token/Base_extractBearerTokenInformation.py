from DateTime import DateTime
try:
  token_dict = context.Base_getBearerToken(token)
except KeyError:
  # not found
  return None

from Products.ERP5Type.Utils import str2bytes
key = str2bytes(context.getPortalObject().portal_preferences.getPreferredBearerTokenKey())

if context.Base_getHMAC(key, str2bytes(str(token_dict))) != token:
  # bizzare, not valid
  return None

if DateTime().timeTime() > token_dict['expiration_timestamp']:
  # expired
  return None

if token_dict['user-agent'] == context.REQUEST.getHeader('User-Agent') and token_dict['remote-addr'] == context.REQUEST.get('REMOTE_ADDR'):
  # correct
  return token_dict['reference']
return None
