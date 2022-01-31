# -*- coding: utf-8 -*-
from functools import wraps
try:
  from ZPublisher.HTTPResponse import HTTPBaseResponse
except ImportError:
  # BBB: Zope2
  from ZPublisher.HTTPResponse import HTTPResponse as HTTPBaseResponse

HTTPBaseResponse_listHeaders = HTTPBaseResponse.listHeaders
@wraps(HTTPBaseResponse_listHeaders)
def listHeaders(self):
  # Remove Zope's publicity header.
  # Nothing wrong with Zope, but headers like this make auditors unhappy.
  return [
    x
    for x in HTTPBaseResponse_listHeaders(self)
    if x[0] != 'X-Powered-By'
  ]
HTTPBaseResponse.listHeaders = listHeaders
