import requests

# Extremely aggressive and hardcoded value
TIMEOUT = 2

def request(self, url, REQUEST):
  RESPONSE = REQUEST.RESPONSE

  portal = self.getPortalObject()

  proxy_query_header = {}
#  proxy_query_header = {"Host": "demo.linshare.org", "Origin": url}
#  proxy_query_header["Cookie"] = "_ga=GA1.2.1545486834.1543309354; _gid=GA1.2.1334680899.1543309354; JSESSIONID=0CAD9667CF441E2B212FE5EE2B9CB062"
  for k in ["Accept", "Accept-Language", "Range","Content-Type"
            "If-Modified-Since", "If-None-Match"]:
    v = REQUEST.getHeader(k, None)
    if v is not None:
      proxy_query_header[k] = v

  result = proxy_query_header
  try:
    if REQUEST.other['method'] != 'POST':
      proxy_response = requests.request(
        REQUEST.other['method'],
        url,
        # Propage the HTTP body (for POST)
        data=REQUEST.get('BODY'),
        # Propagate to headers to use HTTP cache as much as possible
        headers=proxy_query_header,
        # Do not block ERP5 if queried server is too slow
        auth=("user1@linshare.org", "password1"),
        timeout=TIMEOUT,
        verify=False
      )
    else:
      files = []
      for prop in REQUEST.form:
        if prop != 'url':
          files.append((prop, REQUEST.form.get(prop)))
      proxy_response = requests.request(
        'POST',
        url,
        # Propage the HTTP body (for POST)
        data=REQUEST.get('BODY'),
        files=files,

        # Propagate to headers to use HTTP cache as much as possible
        headers=proxy_query_header,
        # Do not block ERP5 if queried server is too slow
        auth=("user1@linshare.org", "password1"),
        timeout=TIMEOUT,
        verify=False
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
    for k, v in proxy_response.headers.items():
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