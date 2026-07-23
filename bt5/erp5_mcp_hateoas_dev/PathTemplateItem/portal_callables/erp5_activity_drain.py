def mcp_ret(o, *a, **k):
  return json.dumps(_mcp_unicode(o), ensure_ascii=False), o
def _mcp_unicode(value):
  # json.dumps(ensure_ascii=False) joins its output chunks on Python 2, so a
  # payload mixing unicode with utf-8 str makes that join decode the bytes as
  # ascii and die on the first umlaut: "'ascii' codec can't decode byte 0xc3".
  # Anything read from ZODB or through Localizer is such a native str, while
  # everything from getHateoas is unicode, so the mix is the norm on a
  # localised instance and never shows up on an all-ascii one.
  if isinstance(value, str):
    decode = getattr(value, "decode", None)
    if decode is None:
      return value  # Python 3: str is already text
    try:
      return decode("utf-8")
    except Exception:
      return decode("utf-8", "replace")
  if isinstance(value, dict):
    return dict([(_mcp_unicode(k), _mcp_unicode(v)) for k, v in value.items()])
  if isinstance(value, (list, tuple)):
    return [_mcp_unicode(x) for x in value]
  return value
import json
from erp5.component.module.MCPDevHelpers import drainActivities
retry_stuck = retry_stuck if isinstance(retry_stuck, bool) else (
  str(retry_stuck).lower() in ("1", "true", "yes"))
cancel_stuck = cancel_stuck if isinstance(cancel_stuck, bool) else (
  str(cancel_stuck).lower() in ("1", "true", "yes"))
try:
  max_seconds = int(max_seconds)
except Exception:
  max_seconds = 240
max_seconds = max(5, min(max_seconds, 3600))
return mcp_ret(drainActivities(context.getPortalObject(),
                               max_seconds=max_seconds,
                               retry_stuck=retry_stuck,
                               cancel_stuck=cancel_stuck))
