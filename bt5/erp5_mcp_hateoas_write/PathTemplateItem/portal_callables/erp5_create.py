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
fv = field_values
if isinstance(fv, str):
  fv = json.loads(fv) if fv else {}
if not isinstance(fv, dict):
  fv = {}
portal = context.getPortalObject()
container = portal.restrictedTraverse(relative_url, None)
if container is None:
  return mcp_ret({"error": "container not found: %s" % relative_url})
try:
  doc = container.newContent(portal_type=str(portal_type))
except Exception, e:
  return mcp_ret({"error": "newContent failed: %s" % e})
new_url = doc.getRelativeUrl()
result = {"status": "success", "relative_url": new_url, "portal_type": portal_type}
if fv:
  wr = portal.portal_callables.erp5_write(relative_url=new_url, field_values=fv)
  try:
    wr_data = json.loads(wr) if isinstance(wr, str) else wr
  except Exception:
    wr_data = {"raw": str(wr)}
  result["field_update"] = wr_data
  if isinstance(wr_data, dict) and wr_data.get("error"):
    result["status"] = "created_with_field_errors"
return mcp_ret(result, ensure_ascii=False)
