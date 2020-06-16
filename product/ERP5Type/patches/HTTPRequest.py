# -*- coding: utf-8 -*-

from ZPublisher.HTTPRequest import HTTPRequest
import sys
import weakref
import thread

HTTPRequest__init__ = HTTPRequest.__init__
def __init__(self, *args, **kw):
  HTTPRequest__init__(self, *args, **kw)

  import erp5.component
  erp5.component.ref_manager.add_request(self)

  # Frontend-facing proxy is responsible for sanitising
  # HTTP_X_FORWARDED_FOR, and only trusted accesses should bypass
  # that proxy. So trust first entry.
  forwarded_for = self.environ.get('HTTP_X_FORWARDED_FOR', '').split(',', 1)[0].strip()
  if forwarded_for:
    self._client_addr = forwarded_for

HTTPRequest.__init__ = __init__
