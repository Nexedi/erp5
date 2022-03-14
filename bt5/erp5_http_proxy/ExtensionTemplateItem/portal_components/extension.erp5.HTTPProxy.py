import requests

# Extremely aggressive and hardcoded value
TIMEOUT = 1

def request(self, url, REQUEST):
  RESPONSE = REQUEST.RESPONSE

  portal = self.getPortalObject()
  if (portal.portal_membership.isAnonymousUser()):
    RESPONSE.setStatus(403)
    return ""
  elif REQUEST.other['method'] != "GET":
    RESPONSE.setStatus(405)
    return ""

  proxy_query_header = {}
  for k in ["Content-Type", "Accept", "Accept-Language", "Range",
            "If-Modified-Since", "If-None-Match"]:
    v = REQUEST.getHeader(k, None)
    if v is not None:
      proxy_query_header[k] = v

  result = ''
  try:
    proxy_response = requests.request(
      REQUEST.other['method'],
      url,
      # Propage the HTTP body (for POST)
      data=REQUEST.get('BODY'),
      # Propagate to headers to use HTTP cache as much as possible
      headers=proxy_query_header,
      # Do not block ERP5 if queried server is too slow
      timeout=TIMEOUT
    )
  except requests.exceptions.SSLError:
    # Invalid SSL Certificate
    status_code = 526
  except requests.exceptions.ConnectionError:
    status_code = 523
  except requests.exceptions.Timeout:
    status_code = 524
  except requests.exceptions.TooManyRedirects:
    status_code = 520
  else:
    result = proxy_response.content
    status_code = proxy_response.status_code
    if status_code == 500:
      status_code = 520

    for k, v in list(proxy_response.headers.items()):
      k = k.title()
      if k in ["Content-Disposition", "Content-Type", "Date", "Last-Modified",
               "Vary", "Cache-Control", "Etag", "Accept-Ranges",
               "Content-Range"]:
        RESPONSE.setHeader(k, v)
      """
      elif k == "Location":
        # In case of redirect, allow to directly fetch from proxy
      """

  RESPONSE.setStatus(status_code)
  return result