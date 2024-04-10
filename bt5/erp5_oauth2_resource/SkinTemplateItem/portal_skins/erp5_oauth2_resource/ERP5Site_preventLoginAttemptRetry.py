"""
Modify given URL so that the resulting one prevents further login attempts when accessed.

Useful to break redirection loops.
"""
from six.moves.urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
PARAMETER_NAME = 'disable_cookie_login__'
parsed_url = urlsplit(url)
return urlunsplit((
  parsed_url.scheme,
  parsed_url.netloc,
  parsed_url.path,
  urlencode([
    (x, y)
    for x, y in parse_qsl(parsed_url.query)
    if x != PARAMETER_NAME
  ] + [
    (PARAMETER_NAME, '1'),
  ]),
  parsed_url.fragment,
))
