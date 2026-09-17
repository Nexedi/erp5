import ipaddress
import json
import socket
import urllib.parse

import requests

# Extremely aggressive and hardcoded value, same rationale as erp5_http_proxy's
# HTTPProxy: do not block ERP5 if the queried server is too slow.
TIMEOUT = 60


def check_target(target_url):
  """Validate a forwarding target, raising ValueError if it is not an
  acceptable https:// URL pointing at a public host."""
  parts = urllib.parse.urlsplit(target_url)
  if parts.scheme != "https":
    raise ValueError("target must be an https URL")
  if not parts.hostname:
    raise ValueError("target has no host")

  try:
    info_list = socket.getaddrinfo(parts.hostname, parts.port or 443,
                                    proto=socket.IPPROTO_TCP)
  except socket.gaierror as exc:
    raise ValueError("cannot resolve %s: %s" % (parts.hostname, exc))

  for info in info_list:
    ip = ipaddress.ip_address(info[4][0])
    if (ip.is_private or ip.is_loopback or ip.is_link_local or
        ip.is_multicast or ip.is_reserved or ip.is_unspecified):
      raise ValueError("refusing to forward to non-public address %s" % ip)


def forward(self, REQUEST):
  """Blindly forward a JSON POST body to an external HTTPS URL, SSRF-guarded.

  Expects REQUEST body: {"target_url": "https://...", "authorization":
  "Bearer ...", "payload": {...}}. Relays the upstream JSON response back
  verbatim. Used by the officejs_harness_ai client-side agent to call an
  OpenAI-compatible LLM endpoint directly from the browser without exposing
  the browser to the target's CORS policy.
  """
  RESPONSE = REQUEST.RESPONSE

  portal = self.getPortalObject()
  if portal.portal_membership.isAnonymousUser():
    RESPONSE.setStatus(403)
    return json.dumps({"error": "anonymous access is not allowed"})

  try:
    body = json.loads(REQUEST.get("BODY") or "{}")
  except ValueError:
    RESPONSE.setStatus(400)
    return json.dumps({"error": "invalid JSON body"})

  target_url = body.get("target_url")
  authorization = body.get("authorization")
  payload = body.get("payload")
  if not target_url or not isinstance(payload, dict):
    RESPONSE.setStatus(400)
    return json.dumps({"error": "target_url and payload are required"})

  try:
    check_target(target_url)
  except ValueError as exc:
    RESPONSE.setStatus(403)
    return json.dumps({"error": str(exc)})

  headers = {"Content-Type": "application/json"}
  if authorization:
    headers["Authorization"] = authorization

  try:
    upstream_response = requests.post(
      target_url,
      json=payload,
      headers=headers,
      timeout=TIMEOUT,
      allow_redirects=False,
    )
  except requests.exceptions.SSLError:
    RESPONSE.setStatus(526)
    return json.dumps({"error": "invalid SSL certificate on upstream"})
  except requests.exceptions.ConnectionError as exc:
    RESPONSE.setStatus(523)
    return json.dumps({"error": "upstream connection failed: %s" % exc})
  except requests.exceptions.Timeout:
    RESPONSE.setStatus(524)
    return json.dumps({"error": "upstream timeout"})
  except requests.exceptions.RequestException as exc:
    RESPONSE.setStatus(502)
    return json.dumps({"error": "upstream request failed: %s" % exc})

  RESPONSE.setStatus(upstream_response.status_code)
  RESPONSE.setHeader(
    "Content-Type",
    upstream_response.headers.get("Content-Type", "application/json"))
  return upstream_response.content
