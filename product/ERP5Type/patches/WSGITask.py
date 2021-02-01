# -*- coding: utf-8 -*-

import ZPublisher.HTTPRequest
try:
  from waitress.task import WSGITask
except ImportError:
  WSGITask = None

# Patch should be enabled only if waitress egg is available
if WSGITask is not None:
  WSGITask_get_environment = WSGITask.get_environment

  def get_environment(self):
    if ZPublisher.HTTPRequest.trusted_proxies == ('0.0.0.0',): # Magic value to enable this functionality
      # Frontend-facing proxy is responsible for sanitising
      # X_FORWARDED_FOR, and only trusted accesses should bypass
      # that proxy. So trust first entry.
      forwarded_for = dict(self.request.headers).get('X_FORWARDED_FOR', '').split(',', 1)[0].strip()
    else:
      forwarded_for = None

    environ = WSGITask_get_environment(self)

    if forwarded_for:
      environ['REMOTE_HOST'] = environ['REMOTE_ADDR'] = forwarded_for

    return environ

  WSGITask.get_environment = get_environment
