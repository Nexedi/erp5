# -*- coding: utf-8 -*-
from functools import wraps
from ZPublisher.HTTPResponse import HTTPResponse

HTTPResponse_listHeaders = HTTPResponse.listHeaders
@wraps(HTTPResponse_listHeaders)
def listHeaders(self):
  # Remove Zope's publicity header.
  # Nothing wrong with Zope, but headers like this make auditors unhappy.
  return [
    x
    for x in HTTPResponse_listHeaders(self)
    if x[0] != 'X-Powered-By'
  ]
HTTPResponse.listHeaders = listHeaders

# Do not bother adding bobo-exception-* headers.
# Either the rendered page wishes to convey the error details, and then it
# should be responsible for doing so, or it wishes to not convey error
# details, and then HTTPResponse should not work behind its back and stuff
# details in the response.
def _setBCIHeaders(self, *args, **kw):
  del args, kw
HTTPResponse._setBCIHeaders = _setBCIHeaders
