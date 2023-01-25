"""
OAuth2's /authorize endpoint produces a very specific format of came_from, with very specific meaning (not a real URL).
This script returns True value if given such came_from, and False otherwise.
"""
import urlparse
parsed_came_from = urlparse.urlsplit(came_from)
return bool(
  not parsed_came_from.scheme and
  not parsed_came_from.netloc and
  parsed_came_from.path and
  parsed_came_from.query
)
