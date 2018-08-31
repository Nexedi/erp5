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

HTTPRequest.__init__ = __init__
