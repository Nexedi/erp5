# -*- coding: utf-8 -*-

from ZPublisher.HTTPRequest import HTTPRequest, sane_environment
import ZPublisher.HTTPRequest
import sys
import weakref
import _thread as thread

HTTPRequest__init__ = HTTPRequest.__init__
def __init__(self, stdin, environ, response, clean=0):
  if ZPublisher.HTTPRequest.trusted_proxies == ('0.0.0.0',): # Magic value to enable this functionality
    # Frontend-facing proxy is responsible for sanitising
    # HTTP_X_FORWARDED_FOR, and only trusted accesses should bypass
    # that proxy. So trust first entry.
    forwarded_for = (
      sane_environment(environ)
      if not clean else
      environ
    ).get('HTTP_X_FORWARDED_FOR', '').split(',', 1)[0].strip()
  else:
    forwarded_for = None

  HTTPRequest__init__(self, stdin=stdin, environ=environ, response=response, clean=clean)

  import erp5.component
  erp5.component.ref_manager.add_request(self)

  if forwarded_for:
    self._client_addr = forwarded_for

HTTPRequest.__init__ = __init__
