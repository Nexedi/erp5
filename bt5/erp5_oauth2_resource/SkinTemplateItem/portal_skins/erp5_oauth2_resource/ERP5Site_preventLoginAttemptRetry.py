"""
Modify given URL so that the resulting one prevents further login attempts when accessed.

Useful to break redirection loops.
"""
import urllib
import urlparse
PARAMETER_NAME = 'disable_cookie_login__'
parsed_url = urlparse.urlsplit(url)
return urlparse.urlunsplit((
  parsed_url.scheme,
  parsed_url.netloc,
  parsed_url.path,
  urllib.urlencode([
    (x, y)
    for x, y in urlparse.parse_qsl(parsed_url.query)
    if x != PARAMETER_NAME
  ] + [
    (PARAMETER_NAME, '1'),
  ]),
  parsed_url.fragment,
))
