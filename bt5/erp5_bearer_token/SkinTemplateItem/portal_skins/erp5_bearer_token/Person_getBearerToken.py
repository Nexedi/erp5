if context.getPortalType() != 'Person':
  raise TypeError('Person object is required')
from DateTime import DateTime
from erp5.component.module.DateUtils import addToDate

key = context.Base_getBearerTokenKey()
if not key:
  raise ValueError('Bearer Key Token is not defined')

token = {
  'expiration_timestamp': addToDate(DateTime(), to_add={'hour': 1}).timeTime(),
  'reference': context.Person_getUserId(),
  'user-agent': context.REQUEST.getHeader('User-Agent'),
  'remote-addr': context.REQUEST.get('REMOTE_ADDR')
}

hmac = context.Base_getHMAC(key, str(token).encode('utf-8'))

context.Base_setBearerToken(hmac, token)

return hmac, token['expiration_timestamp']
