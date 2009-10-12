from Products.ERP5Type.Globals import get_request
import time
from zLOG import LOG

CACHE_DURATION = 600

cached_template = {}
expires_date = {}

def getCachedPageTemplate(self, id=None, REQUEST=None):
  global cached_template
  global expires_date
  if id is not None:
    # Get the user id and request
    if not REQUEST:
      REQUEST = get_request()
    user_id = self.portal_membership.getAuthenticatedMember().getUserName()
    key = (user_id, id)
    # lookup the cache for time
    now = time.time()
    # if cache exists and time is OK, return cache
    expires = expires_date.get(key, now)
    if expires > now:
      LOG('CACHED:',0, str(id))
      return cached_template[key]
    # else recompute cache
    method = getattr(self, id, None)
    if method is not None:
      cached_template[key] = method(REQUEST=REQUEST)
      expires_date[key] = now + CACHE_DURATION
    return cached_template[key]
  else:
    return ''

