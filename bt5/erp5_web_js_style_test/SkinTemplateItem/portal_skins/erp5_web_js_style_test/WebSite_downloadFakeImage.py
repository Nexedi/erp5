import random
response = REQUEST.RESPONSE

cache_value = DateTime().HTML4() + str(random.random())

def getCacheValue(cachekey):
  return cache_value

from Products.ERP5Type.Cache import CachingMethod
getCacheValue = CachingMethod(getCacheValue, id=script.getId())

old_cache_value = getCacheValue(cachekey)
if cache_value == old_cache_value:
  emoji = 'never accessed'
  response.setHeader('Content-Type', 'image/svg+xml')
  return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90%">' + emoji + '</text></svg>'
else:
  emoji = 'already accessed'
  response.setStatus(410)
  return emoji
