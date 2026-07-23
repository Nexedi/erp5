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

def _enc(v):
  if v is None:
    return ""
  if isinstance(v, unicode):
    return v.encode("utf-8")
  if isinstance(v, str):
    return v
  return str(v)

def _compile_error(script):
  for attr in ("errors", "_v_error", "_error", "err_tb"):
    try:
      tb = getattr(script, attr, None)
      if tb:
        if isinstance(tb, (list, tuple)):
          tb = "\n".join(str(x) for x in tb)
        return "%s" % tb
    except Exception:
      pass
  return None

import json
import re as _re
from erp5.component.module.MCPDevHelpers import sha256Hex

# Framework callables we refuse to overwrite unless explicitly allowed.
CORE = ("Base_edit", "Base_view", "Base_doAction", "Base_redirect", "Base_callDialogMethod",
        "Base_callAction", "Base_makeWorkflowMethod", "ERP5Site_view", "Localizer_translate",
        "Workflow_statusModify", "portal_edit", "portal_view")
is_core = script_id in CORE or (str(script_id).startswith("Base_") and "Workflow" in str(script_id))
aoc = allow_overwrite_core if isinstance(allow_overwrite_core, bool) else (str(allow_overwrite_core).lower() in ("1", "true", "yes"))
if is_core and not aoc:
  return mcp_ret({"error": "refusing to write core framework callable '%s' (set allow_overwrite_core=true)" % script_id})

portal = context.getPortalObject()
callables = portal.portal_callables
sid = str(script_id)
pt = str(portal_type) if portal_type not in (None, "") else "Python Script"

spec_updated = False
warning = None

existing = sid in callables.objectIds()
status = "updated" if existing else "created"
if not existing:
  if pt == "MCP Tool":
    callables.newContent(id=sid, portal_type=pt, callable_type="script")
  else:
    callables.newContent(id=sid, portal_type=pt)
target = callables[sid]
if title not in (None, ""):
  target.setTitle(_enc(title))

applied = 0
body_write = False
if replacements:
  reps = json.loads(replacements) if isinstance(replacements, (str, unicode)) else replacements
  src = target.getBody() or ""
  src = src.encode("utf-8") if isinstance(src, unicode) else src
  for rep in reps:
    old = rep.get("old_string", "")
    new = rep.get("new_string", "")
    old_s = old.encode("utf-8") if isinstance(old, unicode) else old
    new_s = new.encode("utf-8") if isinstance(new, unicode) else new
    count = src.count(old_s)
    if rep.get("replace_all"):
      if count == 0:
        return mcp_ret({"error": "replacement not found: %r" % old_s[:100]})
    elif count != 1:
      return mcp_ret({"error": "replacement must match exactly once (matched %d): %r" % (count, old_s[:100]),
        "hint": "add surrounding context to make it unique, or set replace_all=true"})
    src = src.replace(old_s, new_s)
    applied += 1
  target.write(src)
  body_write = True
elif body not in (None, "") or text_content not in (None, ""):
  b = body if body not in (None, "") else text_content
  target.write(_enc(b))
  body_write = True

# --- parameter signature: direct _params, or derived from a JSON-form spec ---
has_spec_sync = pt == "MCP Tool" or hasattr(target, "setParameterSignatureFromSpecification")
if isinstance(input_schema, (str, unicode)):
  try:
    input_schema = json.loads(input_schema)
  except Exception, e:
    return mcp_ret({"error": "input_schema is not valid JSON: %s" % e})
if isinstance(output_schema, (str, unicode)):
  try:
    output_schema = json.loads(output_schema)
  except Exception, e:
    return mcp_ret({"error": "output_schema is not valid JSON: %s" % e})
if input_schema is not None or output_schema is not None:
  if not has_spec_sync:
    warning = ("input_schema/output_schema ignored: '%s' is a %s, not a JSON-form-backed "
               "MCP Tool" % (sid, target.getPortalType()))
  else:
    spec_id = _re.sub(r"[^A-Za-z0-9_.-]", "_", sid) + "_spec"
    if spec_id in callables.objectIds():
      spec = callables[spec_id]
      if spec.getPortalType() != "JSON Form":
        return mcp_ret({"error": "'%s' exists but is not a JSON Form; cannot use it as %s's "
                        "specification" % (spec_id, sid)})
    else:
      spec = callables.newContent(id=spec_id, portal_type="JSON Form",
                                  reference=spec_id, title="%s input/output schema" % sid)
    if input_schema is not None:
      spec.setTextContent(json.dumps(input_schema, ensure_ascii=False))
    if output_schema is not None:
      spec.setResponseSchema(json.dumps(output_schema, ensure_ascii=False))
    target.setSpecificationValue(spec)
    spec_updated = True
    if update_signature_from_spec:
      try:
        target.setParameterSignatureFromSpecification()
      except Exception as e:
        warning = "signature refresh failed: %s" % e
elif params not in (None, ""):
  # An explicitly passed signature wins over the spec-derived one.
  target.setParameterSignature(_enc(params))
elif has_spec_sync:
  if update_signature_from_spec:
    try:
      target.setParameterSignatureFromSpecification()
    except Exception as e:
      warning = "signature refresh failed: %s" % e

error_detail = _compile_error(target) if body_write else None

do_rsc = reset_skins_cache if isinstance(reset_skins_cache, bool) else (str(reset_skins_cache).lower() not in ("0", "false", "no", ""))
if do_rsc:
  try:
    portal.portal_skins._updateCacheEntry("portal_callables", sid)
  except Exception:
    pass

resp = {
  "status": status,
  "script_id": sid,
  "portal_type": target.getPortalType(),
  "body_length": len(target.getBody() or ""),
  "body_sha256": sha256Hex(target.getBody() or ""),
  "params": str(target.getParameterSignature()).strip(),
  "spec_updated": spec_updated,
  "replacements_applied": applied,
  "reset_skins_cache": do_rsc,
}
if error_detail:
  resp["error"] = "script body did not compile:\n%s" % error_detail
if warning:
  resp["warning"] = warning
return mcp_ret(resp)
