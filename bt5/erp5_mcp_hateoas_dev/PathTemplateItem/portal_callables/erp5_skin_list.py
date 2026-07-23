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
try:
  folder = context.getPortalObject().portal_skins[skin_folder]
except Exception, e:
  return mcp_ret({"error": "skin folder '%s' not found: %s" % (skin_folder, e)})
objs = []
for oid in folder.objectIds():
  try:
    mt = getattr(folder[oid], "meta_type", "")
  except Exception:
    mt = ""
  if meta_type and mt != meta_type:
    continue
  objs.append({"id": oid, "meta_type": mt})
return mcp_ret({"skin_folder": skin_folder, "count": len(objs), "objects": objs}, ensure_ascii=False)
