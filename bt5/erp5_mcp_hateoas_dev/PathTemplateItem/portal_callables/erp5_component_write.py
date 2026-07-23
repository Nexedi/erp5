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
from erp5.component.module.MCPDevHelpers import sha256Hex
portal = context.getPortalObject()
comps = portal.portal_components
cid = str(component_id)
existing = cid in comps.objectIds()
if not existing:
  if not (reference and portal_type):
    return mcp_ret({"error": "component '%s' does not exist; pass reference, version and portal_type to create it" % cid})
  comp = comps.newContent(id=cid, portal_type=str(portal_type),
                          reference=str(reference), version=str(version or "erp5"))
else:
  comp = comps[cid]

applied = 0
if replacements:
  reps = json.loads(replacements) if isinstance(replacements, (str, unicode)) else replacements
  src = comp.getTextContent() or ""
  if isinstance(src, unicode):
    src = src.encode("utf-8")
  for rep in reps:
    old = rep["old_string"]
    new = rep["new_string"]
    old_s = old.encode("utf-8") if isinstance(old, unicode) else old
    new_s = new.encode("utf-8") if isinstance(new, unicode) else new
    count = src.count(old_s)
    if rep.get("replace_all"):
      if count == 0:
        return mcp_ret({"error": "replacement not found: %r" % old[:100]})
    elif count != 1:
      return mcp_ret({"error": "replacement must match exactly once (matched %d): %r" % (count, old[:100]),
        "hint": "add surrounding context to make it unique, or set replace_all=true"})
    src = src.replace(old_s, new_s)
    applied += 1
  comp.setTextContent(src)
elif body_file:
  # Read the full source from a local (server-reachable) path: authoring stays
  # out of the tool argument, and the response sha256/length let the caller
  # verify byte-exact deployment against the local file.
  from erp5.component.module.MCPDevHelpers import readFile
  try:
    data = readFile(str(body_file))
  except Exception, e:
    return mcp_ret({"error": "body_file unreadable: %s" % e, "body_file": str(body_file)})
  try:
    text = data.decode("utf-8")
  except UnicodeDecodeError:
    text = data.decode("utf-8", "replace")
  comp.setTextContent(text)
elif text_content not in (None, ""):
  tc = text_content.encode("utf-8") if isinstance(text_content, unicode) else text_content
  comp.setTextContent(tc)
else:
  return mcp_ret({"error": "pass either body_file (a local path), text_content (full source) or replacements (a list of {old_string,new_string,replace_all})"})

try:
  comp.clearRecordedProperty("text_content")
except Exception:
  pass
if comp.getValidationState() != "validated":
  comp.validate()
do_reset = reset if isinstance(reset, bool) else (str(reset).lower() not in ("0", "false", "no", ""))
if do_reset:
  portal.portal_components.reset()
content = comp.getTextContent() or ""
return mcp_ret({"status": "created" if not existing else "updated", "component_id": cid,
  "validation_state": comp.getValidationState(), "length": len(content),
  "sha256": sha256Hex(content),
  "replacements_applied": applied, "reset": do_reset})
