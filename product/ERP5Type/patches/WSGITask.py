# -*- coding: utf-8 -*-

import ZPublisher.HTTPRequest
from waitress.task import WSGITask

WSGITask_parse_proxy_headers = WSGITask.parse_proxy_headers

def parse_proxy_headers(
  self,
  environ,
  headers,
  trusted_proxy_count=1,
  trusted_proxy_headers=None,
):
  if ZPublisher.HTTPRequest.trusted_proxies == ('0.0.0.0',): # Magic value to enable this functionality
    # Frontend-facing proxy is responsible for sanitising
    # X_FORWARDED_FOR, and only trusted accesses should bypass
    # that proxy. So trust first entry.
    forwarded_for = headers.get('X_FORWARDED_FOR', '').split(',', 1)[0].strip()
  else:
    forwarded_for = None

  untrusted_headers = WSGITask_parse_proxy_headers(
    self,
    environ=environ,
    headers=headers,
    trusted_proxy_count=trusted_proxy_count,
    trusted_proxy_headers=trusted_proxy_headers,
  )

  if forwarded_for:
    environ['REMOTE_ADDR'] = forwarded_for

  return untrusted_headers

WSGITask.parse_proxy_headers = parse_proxy_headers

