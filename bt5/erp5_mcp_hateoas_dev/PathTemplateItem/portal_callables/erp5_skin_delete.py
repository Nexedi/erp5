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
portal = context.getPortalObject()
skins = portal.portal_skins
if skin_folder not in skins.objectIds():
  return mcp_ret({"error": "no such skin folder: %s" % skin_folder})
folder = skins[skin_folder]
if script_id not in folder.objectIds():
  return mcp_ret({"error": "not found: %s/%s" % (skin_folder, script_id)})
meta_type = getattr(folder[script_id], "meta_type", "")
try:
  folder.manage_delObjects([str(script_id)])
except Exception, e:
  return mcp_ret({"error": "delete failed for %s/%s: %s" % (skin_folder, script_id, e)})
# manage_delObjects can report no error and still leave the object behind,
# which is exactly how erp5_delete misleads on portal_skins, so confirm.
if script_id in folder.objectIds():
  return mcp_ret({"error": "still present after delete: %s/%s" % (skin_folder, script_id)})
result = {"status": "success", "script_id": script_id,
  "skin_folder": skin_folder, "meta_type": meta_type,
  "deleted": "portal_skins/%s/%s" % (skin_folder, script_id)}
if skin_folder != "custom":
  # Not refused, but the caller should know the instance has just diverged
  # from the business template that owns this folder.
  result["warning"] = ("%s is owned by a business template: the instance now "
    "differs from its bt5, and reinstalling it restores this object."
    % skin_folder)
return mcp_ret(result)
