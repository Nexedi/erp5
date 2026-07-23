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
doc = portal.restrictedTraverse(relative_url, None)
if doc is None:
  return mcp_ret({"error": "not found: %s" % relative_url})
parent = doc.getParentValue()
try:
  cp = parent.manage_copyObjects([doc.getId()])
  res = parent.manage_pasteObjects(cp)
  new_doc = parent[res[0]["new_id"]]
except Exception, e:
  return mcp_ret({"error": "clone failed: %s" % e})
new_url = new_doc.getRelativeUrl()
result = {"status": "success", "relative_url": new_url, "source": relative_url}
if fv:
  wr = portal.portal_callables.erp5_write(relative_url=new_url, field_values=fv)
  try:
    wr_data = json.loads(wr) if isinstance(wr, str) else wr
  except Exception:
    wr_data = {"raw": str(wr)}
  result["field_update"] = wr_data
  if isinstance(wr_data, dict) and wr_data.get("error"):
    result["status"] = "cloned_with_field_errors"
return mcp_ret(result, ensure_ascii=False)
